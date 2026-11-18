"""Blender: find her left eyeball on the raw mesh (by texture colour + shape) and render a check image.
blender -b --factory-startup -P eye_probe.py -- <raw.glb> <out_dir>
Prints  EYE centre x y z radius  (cm, Blender space, same convention as build_her.py)."""
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
mw = mesh.matrix_world
co = np.array([tuple(mw @ v.co) for v in me.vertices])
# per-vertex colour from the base colour texture
mat = me.materials[0]
bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
node = bsdf.inputs["Base Color"].links[0].from_node
while node.type != "TEX_IMAGE":
    node = next(i.links[0].from_node for i in node.inputs if i.is_linked)
img = node.image
W, H = img.size
px = np.array(img.pixels[:], dtype=np.float32).reshape(H, W, 4)
uvl = me.uv_layers.active.data
vcol = np.zeros((len(me.vertices), 3), dtype=np.float32)
vcnt = np.zeros(len(me.vertices), dtype=np.int32)
for loop in me.loops:
    uv = uvl[loop.index].uv
    x = min(W - 1, max(0, int(uv.x % 1.0 * W))); y = min(H - 1, max(0, int(uv.y % 1.0 * H)))
    vcol[loop.vertex_index] += px[y, x, :3]; vcnt[loop.vertex_index] += 1
vcol /= np.maximum(vcnt, 1)[:, None]
head_z = arm.data.bones["Head"].head_local.z
zmax = co[:, 2].max()
front = (co[:, 2] > head_z + 2) & (co[:, 1] < -8) & (co[:, 0] > -2) & (co[:, 0] < 18)
lum = vcol @ np.array([0.3, 0.59, 0.11])
sat = vcol.max(axis=1) - vcol.min(axis=1)
print("EYEDBG head z", round(head_z, 1), "top", round(zmax, 1), "front verts", int(front.sum()))
# the eyeball is the most forward-bulging smooth blob on her left side: take forward-most points in a grid and look for the roundest patch
cand = np.where(front)[0]
best = None
# prior from the first check render: the eye sits about (6.5, ?, 245.8); fit the bulge there
sel = cand[(np.abs(co[cand, 2] - 245.8) < 4.0) & (np.abs(co[cand, 0] - 6.5) < 4.0) & (co[cand, 1] < -18.0)]
P = co[sel]
# keep the forward-facing cap only (points within 2.2 cm depth of the apex)
apex_y = P[:, 1].min()
P = P[P[:, 1] < apex_y + 2.2]
A = np.c_[2 * P, np.ones(len(P))]
sol, res, *_ = np.linalg.lstsq(A, (P ** 2).sum(axis=1), rcond=None)
c = sol[:3]; r = math.sqrt(max(sol[3] + (c ** 2).sum(), 1e-6))
err = np.abs(np.linalg.norm(P - c, axis=1) - r).mean()
print("EYEDBG apex_y %.2f cap verts %d" % (apex_y, len(P)))
best = (0, c, r, err, len(P), 0.0)
score, c, r, err, n, wh = best
print("EYE %.2f %.2f %.2f %.2f   (fit err %.3f cm, %d verts, whiteness %.2f)" % (c[0], c[1], c[2], r, err, n, wh))

# check render: red sphere where we think the eye is
sc.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE"
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.3, 0.3, 0.32, 1)
sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); sun.data.energy = 3
sun.rotation_euler = (math.radians(60), 0, math.radians(15)); sc.collection.objects.link(sun)
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.lens = 85; cam.data.clip_end = 5000
sc.render.resolution_x = 900; sc.render.resolution_y = 900
tgt = Vector((2.0, -10.0, head_z + 18))


def shot(name, d):
    dv = Vector(d).normalized()
    cam.location = tgt + dv * 150
    cam.rotation_euler = (tgt - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.filepath = os.path.join(OUT, name + ".png")
    bpy.ops.render.render(write_still=True)


shot("face_plain", (0.25, -1, 0.02))
bpy.ops.mesh.primitive_uv_sphere_add(radius=r * 1.02, location=tuple(c), segments=32, ring_count=16)
s = bpy.context.active_object
m = bpy.data.materials.new("mark"); m.use_nodes = True
m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1)
m.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.08
s.data.materials.append(m)
shot("face_marked", (0.25, -1, 0.02))
shot("face_marked_side", (1, -0.25, 0.02))
