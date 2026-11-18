"""Blender: import a GLB, print what is in it and render review views.
blender -b -P inspect_glb.py -- <in.glb> <out_dir>
"""
import bpy, sys, math, os
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
src, out = argv[0], argv[1]
os.makedirs(out, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)

lo = Vector((1e9,) * 3); hi = Vector((-1e9,) * 3)
for o in bpy.data.objects:
    print("OBJ", o.type, o.name, "parent=", o.parent.name if o.parent else None, "scale=", tuple(round(s, 3) for s in o.scale))
    if o.type == "MESH":
        m = o.data
        print("  verts", len(m.vertices), "polys", len(m.polygons), "mats", [s.material.name if s.material else None for s in o.material_slots],
              "vgroups", len(o.vertex_groups), "uv", [u.name for u in m.uv_layers])
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            lo = Vector(map(min, lo, w)); hi = Vector(map(max, hi, w))
    if o.type == "ARMATURE":
        print("  bones", len(o.data.bones))
        for b in o.data.bones:
            print("   BONE", b.name, "parent=", b.parent.name if b.parent else None, "head=", tuple(round(v, 3) for v in (o.matrix_world @ b.head_local)), "len=", round(b.length, 3))
print("BOUNDS", tuple(round(v, 3) for v in lo), tuple(round(v, 3) for v in hi))
for img in bpy.data.images:
    print("IMG", img.name, tuple(img.size))
print("ACTIONS", [a.name for a in bpy.data.actions])

# review renders
scene = bpy.context.scene
scene.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE"
scene.render.resolution_x = 900; scene.render.resolution_y = 1400
world = bpy.data.worlds.new("w"); scene.world = world; world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.25, 0.25, 0.27, 1)
world.node_tree.nodes["Background"].inputs[1].default_value = 1.0
c = (lo + hi) / 2; size = hi - lo; H = max(size)
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); sun.data.energy = 3
sun.rotation_euler = (math.radians(55), 0, math.radians(25)); scene.collection.objects.link(sun)
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); scene.collection.objects.link(cam); scene.camera = cam
cam.data.lens = 60


def shot(name, direction, target, dist, res=(900, 1400)):
    scene.render.resolution_x, scene.render.resolution_y = res
    d = Vector(direction).normalized()
    cam.location = target + d * dist
    cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
    scene.render.filepath = os.path.join(out, name + ".png")
    bpy.ops.render.render(write_still=True)

# figure out which axis is "front": glTF import -> Blender -Y is front
shot("front", (0, -1, 0.05), c, H * 2.3)
shot("side", (1, 0, 0.05), c, H * 2.3)
shot("back", (0, 1, 0.05), c, H * 2.3)
shot("threeq", (0.7, -1, 0.25), c, H * 2.3)
head = Vector((c.x, c.y, hi.z - H * 0.07))
shot("face", (0.15, -1, 0.0), head, H * 0.45, (1000, 1000))
hand = Vector((hi.x - size.x * 0.06, c.y, lo.z + H * 0.33))
shot("hand", (0.2, -1, 0.1), hand, H * 0.4, (1000, 1000))
