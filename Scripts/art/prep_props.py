"""Blender: normalise generated prop GLBs for Unreal (scale in cm, front = -Y, sensible origin, decimated, textures as PNG).
blender -b --factory-startup -P prep_props.py -- <props_dir>
Writes <props_dir>/export/SM_<Name>.fbx and T_<Name>_{BaseColor,Normal,MR}.png
"""
import bpy, sys, os, math
from mathutils import Vector, Matrix

D = sys.argv[sys.argv.index("--") + 1]
OUT = os.path.join(D, "export")
os.makedirs(OUT, exist_ok=True)
# name: (file, long-axis length in cm, rotate Z deg so the front faces -Y, target tris, texture size, origin mode)
PROPS = {
    "Cruiser": ("cruiser.glb", 540.0, 0.0, 45000, 2048, "bottom"),
    "HandPistol": ("hand_pistol.glb", 56.0, 90.0, 26000, 2048, "centre"),
    "Toilet": ("toilet.glb", 78.0, 0.0, 22000, 2048, "bottom"),
    "Fridge": ("fridge.glb", 165.0, 0.0, 26000, 2048, "bottom"),
    "HandFlashlight": ("hand_flashlight.glb", 36.0, 90.0, 24000, 2048, "centre"),
}
only = [a for a in sys.argv[sys.argv.index("--") + 2:]]

for name, (fn, length, rz, tris, tsize, origin) in PROPS.items():
    if only and name not in only:
        continue
    src = os.path.join(D, fn)
    if not os.path.exists(src):
        print("PROP missing", src); continue
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = "METRIC"; sc.unit_settings.scale_length = 0.01
    bpy.ops.import_scene.gltf(filepath=src)
    obs = [o for o in sc.objects if o.type == "MESH"]
    for o in list(sc.objects):
        if o.type != "MESH":
            bpy.data.objects.remove(o, do_unlink=True)
    bpy.ops.object.select_all(action="DESELECT")
    for o in obs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = obs[0]
    if len(obs) > 1:
        bpy.ops.object.join()
    ob = bpy.context.view_layer.objects.active
    ob.name = "SM_" + name
    bpy.ops.object.parent_clear(type="CLEAR_KEEP_TRANSFORM")
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    dims = ob.dimensions
    if name == "HandFlashlight":
        k = length / max(dims.x, dims.y)          # the flashlight length, not the forearm
    else:
        k = length / max(dims)
    ob.scale = (k, k, k)
    ob.rotation_euler = (0, 0, math.radians(rz))
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    bb = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
    lo = Vector((min(v.x for v in bb), min(v.y for v in bb), min(v.z for v in bb)))
    hi = Vector((max(v.x for v in bb), max(v.y for v in bb), max(v.z for v in bb)))
    c = (lo + hi) / 2
    off = Vector((c.x, c.y, lo.z)) if origin == "bottom" else c
    ob.data.transform(Matrix.Translation(-off))
    n = len(ob.data.polygons)
    if n > tris:
        m = ob.modifiers.new("dec", "DECIMATE"); m.ratio = tris / n
        bpy.ops.object.modifier_apply(modifier="dec")
    print("PROP", name, "dims", tuple(round(d, 1) for d in ob.dimensions), "tris", len(ob.data.polygons))
    # textures
    mat = ob.data.materials[0]
    bsdf = next(nd for nd in mat.node_tree.nodes if nd.type == "BSDF_PRINCIPLED")

    def img_of(sock):
        if not sock.is_linked:
            return None
        nd = sock.links[0].from_node; hops = 0
        while nd and nd.type != "TEX_IMAGE" and hops < 6:
            nd = next((i.links[0].from_node for i in nd.inputs if i.is_linked), None); hops += 1
        return nd.image if nd and nd.type == "TEX_IMAGE" else None
    for key, sock in (("BaseColor", "Base Color"), ("Normal", "Normal"), ("MR", "Roughness")):
        im = img_of(bsdf.inputs[sock])
        if not im:
            print("PROP", name, "no", key); continue
        if im.size[0] > tsize:
            im.scale(tsize, tsize)
        im.filepath_raw = os.path.join(OUT, "T_%s_%s.png" % (name, key)); im.file_format = "PNG"; im.save()
    bpy.ops.object.select_all(action="DESELECT"); ob.select_set(True)
    bpy.ops.export_scene.fbx(filepath=os.path.join(OUT, "SM_%s.fbx" % name), use_selection=True, object_types={"MESH"},
                             apply_unit_scale=True, apply_scale_options="FBX_SCALE_UNITS", global_scale=1.0, mesh_smooth_type="FACE", use_tspace=True)
print("PROP done")
