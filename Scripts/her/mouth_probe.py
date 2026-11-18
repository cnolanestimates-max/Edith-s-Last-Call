"""Blender: locate her mouth line.  Renders a close front view of the lower face with a ruler of small spheres
(one every 2 cm of height, labelled by colour) so the lip line can be read off.
blender -b --factory-startup -P mouth_probe.py -- <raw.glb> <out_dir>"""
import bpy, sys, os, math
import numpy as np
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
SRC, OUT = argv[0], argv[1]
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.unit_settings.system = "METRIC"; sc.unit_settings.scale_length = 0.01
bpy.ops.import_scene.gltf(filepath=SRC)
arm = [o for o in sc.objects if o.type == "ARMATURE"][0]
mesh = [o for o in sc.objects if o.type == "MESH" and o.parent == arm][0]
for o in list(sc.objects):
    if o not in (arm, mesh):
        bpy.data.objects.remove(o, do_unlink=True)
bpy.ops.object.select_all(action="DESELECT")
arm.select_set(True); mesh.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
bpy.context.view_layer.update()
me = mesh.data
co = np.array([tuple(mesh.matrix_world @ v.co) for v in me.vertices])
# the front-most surface point of the face on the centre line, for each height
for z in range(214, 236, 2):
    sel = (np.abs(co[:, 2] - z) < 0.6) & (np.abs(co[:, 0]) < 1.5) & (co[:, 1] < -10)
    print("MOUTHDBG z %d front y %.2f (%d verts)" % (z, co[sel, 1].min() if sel.any() else 0.0, int(sel.sum())))
print("MOUTHDBG verts", len(me.vertices), "faces", len(me.polygons))

sc.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE"
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.3, 0.3, 0.32, 1)
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); sun.data.energy = 3
sun.rotation_euler = (math.radians(60), 0, math.radians(15)); sc.collection.objects.link(sun)
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.type = "ORTHO"; cam.data.ortho_scale = 36.0; cam.data.clip_end = 5000
sc.render.resolution_x = 900; sc.render.resolution_y = 900
tgt = Vector((0.0, -20.0, 228.0))
cam.location = tgt + Vector((0, -200, 0))
cam.rotation_euler = (tgt - cam.location).to_track_quat("-Z", "Y").to_euler()
sc.render.filepath = os.path.join(OUT, "mouth_plain.png"); bpy.ops.render.render(write_still=True)
# ruler at x = +12: spheres at z = 216..240 step 2; red = 226, green = 220 and 230, white others
for z in range(216, 242, 2):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.45, location=(12.0, -30.0, float(z)), segments=12, ring_count=8)
    s = bpy.context.active_object
    m = bpy.data.materials.new("mk%d" % z); m.use_nodes = True
    col = (1, 0, 0, 1) if z == 226 else ((0, 1, 0, 1) if z in (220, 230) else (1, 1, 1, 1))
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = col
    m.node_tree.nodes["Principled BSDF"].inputs["Emission Color"].default_value = col
    m.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 2.0
    s.data.materials.append(m)
for x in range(-8, 10, 2):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.35, location=(float(x), -30.0, 214.0), segments=12, ring_count=8)
    s = bpy.context.active_object
    m = bpy.data.materials.new("mx%d" % x); m.use_nodes = True
    col = (1, 0, 0, 1) if x == 0 else (1, 1, 0, 1)
    m.node_tree.nodes["Principled BSDF"].inputs["Emission Color"].default_value = col
    m.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 2.0
    s.data.materials.append(m)
sc.render.filepath = os.path.join(OUT, "mouth_ruler.png"); bpy.ops.render.render(write_still=True)
