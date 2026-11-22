"""Model the shared beveled oak door plaque in Blender and export to Unreal."""
from pathlib import Path
import math

import bpy

ROOT = Path(__file__).resolve().parents[2]
DEST = ROOT / "SourceArt/Props/HarrowFurniture"
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

verts, faces = [], []


def ring(half_width, half_height, radius, depth):
    for sx, sz, start in ((1, 1, 0), (-1, 1, 90), (-1, -1, 180), (1, -1, 270)):
        for sample in range(9):
            theta = math.radians(start + 90 * sample / 8)
            x = sx * (half_width - radius) + radius * math.cos(theta)
            z = sz * (half_height - radius) + radius * math.sin(theta)
            verts.append((x / 100, -depth / 100, z / 100))


ring(15.5, 5.8, 1.55, 0)
ring(15.5, 5.8, 1.55, .75)
ring(15.24, 5.54, 1.28, 1.06)
ring(14.95, 5.25, 1.04, 1.13)
n = len(verts) // 4
faces.append(tuple(reversed(range(n))))
for start in range(0, 3*n, n):
    for i in range(n):
        nxt = (i + 1) % n
        faces.append((start+i, start+nxt, start+n+nxt, start+n+i))
faces.append(tuple(range(3*n, 4*n)))
mesh = bpy.data.meshes.new("Beveled oak")
mesh.from_pydata(verts, [], faces)
mesh.update()
plaque = bpy.data.objects.new("SM_HarrowDoorPlaque", mesh)
bpy.context.collection.objects.link(plaque)
bpy.context.view_layer.objects.active = plaque
plaque.select_set(True)
uv = mesh.uv_layers.new(name="Paint")
for polygon in mesh.polygons:
    polygon.use_smooth = 0 < polygon.index < len(mesh.polygons)-1
    for loop in polygon.loop_indices:
        px, _, pz = mesh.vertices[mesh.loops[loop].vertex_index].co
        uv.data[loop].uv = (px / .31 + .5, pz / .116 + .5)
material = bpy.data.materials.new("Painted oak")
material.use_nodes = True
image = material.node_tree.nodes.new("ShaderNodeTexImage")
image.image = bpy.data.images.load(str(DEST / "T_HarrowPlaqueRuth.png"), check_existing=True)
material.node_tree.links.new(image.outputs["Color"], material.node_tree.nodes.get("Principled BSDF").inputs["Base Color"])
plaque.data.materials.append(material)
bpy.ops.export_scene.fbx(filepath=str(DEST / "SM_HarrowDoorPlaque.fbx"), use_selection=True,
                         axis_forward="-Y", axis_up="Z", add_leaf_bones=False)
