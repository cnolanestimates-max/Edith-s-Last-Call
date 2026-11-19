"""Blender: the small things he carries, as real little models for the inventory's 3D view (and for the world, where they
used to be plain bars).  No paid generation.

  blender -b --factory-startup -P build_items.py -- <out_dir> [--preview]

Writes SM_Item_<Name>.fbx (metres in Blender = centimetres in Unreal), one material slot per material name:
Brass, Iron, Gold, Steel, Glass, Ceramic, Ribbon.  Each lies flat with its underside at z = 0.
"""
import bpy, math, os, sys
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
OUT = argv[0]
PREVIEW = "--preview" in argv
os.makedirs(OUT, exist_ok=True)
COL = {"Brass": (0.55, 0.38, 0.12, 1), "Iron": (0.09, 0.08, 0.075, 1), "Gold": (0.83, 0.62, 0.2, 1), "Steel": (0.5, 0.5, 0.5, 1),
       "Glass": (0.6, 0.72, 0.7, 1), "Ceramic": (0.78, 0.74, 0.66, 1), "Ribbon": (0.3, 0.03, 0.04, 1)}


def mat(name):
    m = bpy.data.materials.get(name)
    if not m:
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        b = m.node_tree.nodes.get("Principled BSDF")
        if b:
            b.inputs["Base Color"].default_value = COL[name]
            b.inputs["Metallic"].default_value = 0.0 if name in ("Glass", "Ceramic", "Ribbon") else 1.0
            b.inputs["Roughness"].default_value = 0.35
    return m


def done(m):
    ob = bpy.context.object
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    ob.data.materials.append(mat(m))
    return ob


def torus(R, r, loc, rot=(0, 0, 0), m="Iron", seg=40, rseg=12, squash=1.0):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, major_segments=seg, minor_segments=rseg, location=loc, rotation=rot)
    bpy.context.object.scale = (1, 1, squash)
    return done(m)


def cyl(r, h, loc, rot=(0, 0, 0), m="Iron", v=24, r2=None):
    if r2 is None:
        bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, vertices=v, location=loc, rotation=rot)
    else:
        bpy.ops.mesh.primitive_cone_add(radius1=r, radius2=r2, depth=h, vertices=v, location=loc, rotation=rot)
    return done(m)


def box(sx, sy, sz, loc, rot=(0, 0, 0), m="Iron", bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    ob = bpy.context.object
    ob.scale = (sx, sy, sz)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    if bevel > 0:
        md = ob.modifiers.new("b", "BEVEL")
        md.width = bevel
        md.segments = 2
        bpy.ops.object.modifier_apply(modifier="b")
    ob.data.materials.append(mat(m))
    return ob


def sphere(r, loc, m="Steel"):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=10, ring_count=6, location=loc)
    return done(m)


def blade(length, w0, w1, t, m="Steel"):
    """A tapered flat blade along +X from the origin, cutting edge on -Y."""
    v = [(0, -w0 / 2, -t / 2), (0, w0 / 2, -t / 2), (0, w0 / 2, t / 2), (0, -w0 / 2, t / 2),
         (length, -w0 / 2, -t / 4), (length, -w0 / 2 + w1, -t / 4), (length, -w0 / 2 + w1, t / 4), (length, -w0 / 2, t / 4)]
    f = [(0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)]
    me = bpy.data.meshes.new("blade")
    me.from_pydata(v, [], f)
    ob = bpy.data.objects.new("blade", me)
    bpy.context.collection.objects.link(ob)
    ob.data.materials.append(mat(m))
    return ob


def turn(ob, rz=0.0, loc=(0, 0, 0)):
    ob.rotation_euler = (0, 0, rz)
    ob.location = loc
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return ob


def join(name, parts):
    bpy.ops.object.select_all(action="DESELECT")
    for p in parts:
        p.select_set(True)
    bpy.context.view_layer.objects.active = parts[0]
    bpy.ops.object.join()
    ob = bpy.context.object
    ob.name = name
    ob.data.name = name
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    zs = [(ob.matrix_world @ v.co).z for v in ob.data.vertices]
    xs = [(ob.matrix_world @ v.co).x for v in ob.data.vertices]
    ys = [(ob.matrix_world @ v.co).y for v in ob.data.vertices]
    off = Vector((-(min(xs) + max(xs)) / 2, -(min(ys) + max(ys)) / 2, -min(zs)))
    for v in ob.data.vertices:
        v.co += off
    for fn in ("shade_auto_smooth", "shade_smooth_by_angle"):
        try:
            getattr(bpy.ops.object, fn)(angle=math.radians(40))
            break
        except Exception:
            continue
    else:
        bpy.ops.object.shade_smooth()
    return ob


def key_parts(m="Brass", s=1.0, at=(0, 0, 0), rz=0.0):
    """An old skeleton key lying flat: bow at the origin, shaft along +X, bit hanging toward -Y."""
    P = []
    P.append(torus(0.0105 * s, 0.0021 * s, (0, 0, 0), m=m, squash=0.8))
    P.append(torus(0.0048 * s, 0.0016 * s, (0, 0, 0), m=m, seg=20, rseg=8, squash=0.8))
    P.append(cyl(0.0021 * s, 0.050 * s, (0.0355 * s, 0, 0), (0, math.pi / 2, 0), m, 12))
    P.append(cyl(0.0033 * s, 0.0035 * s, (0.0135 * s, 0, 0), (0, math.pi / 2, 0), m, 16))
    P.append(cyl(0.0029 * s, 0.0025 * s, (0.0185 * s, 0, 0), (0, math.pi / 2, 0), m, 16))
    P.append(box(0.0035 * s, 0.0105 * s, 0.0022 * s, (0.0500 * s, -0.0058 * s, 0), m=m))
    P.append(box(0.0035 * s, 0.0075 * s, 0.0022 * s, (0.0548 * s, -0.0044 * s, 0), m=m))
    P.append(box(0.0030 * s, 0.0115 * s, 0.0022 * s, (0.0590 * s, -0.0062 * s, 0), m=m))
    P.append(box(0.0125 * s, 0.0030 * s, 0.0022 * s, (0.0545 * s, -0.0018 * s, 0), m=m))
    for p in P:
        turn(p, rz, at)
    return P


ITEMS = {}


def build(name, fn):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    ob = join("SM_Item_" + name, fn())
    ITEMS[name] = ob
    path = os.path.join(OUT, f"SM_Item_{name}.fbx")
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={"MESH"}, mesh_smooth_type="FACE", add_leaf_bones=False,
                             bake_anim=False, apply_scale_options="FBX_SCALE_NONE")
    d = ob.dimensions
    print(f"ITEM {name}: {len(ob.data.vertices)} verts, {d.x * 100:.1f} x {d.y * 100:.1f} x {d.z * 100:.1f} cm")
    if PREVIEW:
        sc = bpy.context.scene
        try:
            sc.render.engine = "BLENDER_EEVEE_NEXT"
        except Exception:
            sc.render.engine = "BLENDER_EEVEE"
        w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
        w.node_tree.nodes["Background"].inputs[0].default_value = (0.05, 0.05, 0.055, 1)
        w.node_tree.nodes["Background"].inputs[1].default_value = 2.0
        sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); sun.data.energy = 4
        sun.rotation_euler = (math.radians(40), 0, math.radians(30)); sc.collection.objects.link(sun)
        cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
        cam.data.lens = 70; cam.data.clip_start = 0.001; cam.data.clip_end = 10
        size = max(d.x, d.y, d.z)
        tgt = Vector((0, 0, d.z / 2))
        cam.location = tgt + Vector((0.25, -0.75, 0.9)).normalized() * size * 2.6
        cam.rotation_euler = (tgt - cam.location).to_track_quat("-Z", "Y").to_euler()
        sc.render.resolution_x = 640; sc.render.resolution_y = 480
        os.makedirs(os.path.join(OUT, "preview"), exist_ok=True)
        sc.render.filepath = os.path.join(OUT, "preview", name + ".png")
        bpy.ops.render.render(write_still=True)


def ring():
    return [torus(0.0098, 0.0017, (0, 0, 0), m="Gold", seg=48, rseg=12, squash=1.5)]


def keyring():
    P = [torus(0.017, 0.0011, (0, 0, 0), m="Iron", seg=40, rseg=8)]
    for i, (a, m_, s) in enumerate(((-0.55, "Iron", 1.0), (0.05, "Brass", 0.85), (0.62, "Iron", 0.92))):
        d = Vector((math.cos(a), math.sin(a), 0))
        P += key_parts(m_, s, tuple(d * (0.017 + 0.0105 * s)), a)
    return P


def fuse():
    # a screw-in plug fuse: glass window, ceramic body, threaded brass base, contact tip
    P = [cyl(0.0135, 0.004, (0, 0, 0.034), m="Brass", v=32)]
    P.append(cyl(0.0118, 0.0012, (0, 0, 0.0365), m="Glass", v=32))
    P.append(cyl(0.0135, 0.012, (0, 0, 0.026), m="Ceramic", v=32, r2=0.0135))
    P.append(cyl(0.0112, 0.017, (0, 0, 0.0115), m="Brass", v=32))
    for k in range(4):
        P.append(torus(0.0112, 0.0011, (0, 0, 0.006 + k * 0.0037), m="Brass", seg=32, rseg=6))
    P.append(cyl(0.0075, 0.003, (0, 0, 0.0015), m="Ceramic", v=24, r2=0.0105))
    P.append(cyl(0.0035, 0.0016, (0, 0, -0.0005), m="Brass", v=16))
    return P


def shears():
    P = []
    for sgn in (1, -1):
        a = sgn * math.radians(9)
        b = blade(0.105, 0.016, 0.003, 0.0022)
        b.scale = (1, sgn, 1)
        turn(b, a, (0, 0, sgn * 0.0012))
        P.append(b)
        # shank behind the pivot, and the finger loop
        sh = box(0.050, 0.006, 0.0024, (-0.025, 0, 0), m="Iron")
        turn(sh, a + sgn * math.radians(14), (0, 0, sgn * 0.0012))
        P.append(sh)
        d = Vector((math.cos(a + sgn * math.radians(14) + math.pi), math.sin(a + sgn * math.radians(14) + math.pi), 0))
        lp = torus(0.016 if sgn > 0 else 0.013, 0.0028, tuple(d * 0.064 + Vector((0, sgn * 0.004, sgn * 0.0012))), m="Iron", seg=32, rseg=10, squash=0.8)
        P.append(lp)
    P.append(cyl(0.0042, 0.006, (0, 0, 0), m="Brass", v=16))
    return P


def tags():
    P = []
    for i, (x, y, rz, z) in enumerate(((0.0, 0.0, 0.25, 0.0), (0.012, -0.009, -0.35, 0.0016))):
        t = box(0.050, 0.028, 0.0011, (0, 0, 0), m="Steel", bevel=0.0058)
        turn(t, rz, (x, y, z))
        P.append(t)
        rim = torus(0.0023, 0.0007, (0, 0, 0), m="Steel", seg=14, rseg=6)
        turn(rim, 0, (x - 0.020 * math.cos(rz), y - 0.020 * math.sin(rz), z + 0.0008))
        P.append(rim)
    # ball chain: a loop of little beads
    n = 46
    for k in range(n):
        a = 2 * math.pi * k / n
        P.append(sphere(0.0011, (-0.020 - 0.034 + 0.034 * math.cos(a), 0.004 + 0.027 * math.sin(a), 0.0011)))
    return P


build("Key", lambda: key_parts("Brass"))
build("KeyIron", lambda: key_parts("Iron", 1.1) + [box(0.060, 0.0085, 0.0006, (-0.036, 0.004, -0.0012), (0, 0, 0.3), "Ribbon"), box(0.050, 0.0085, 0.0006, (-0.030, -0.010, -0.0012), (0, 0, -0.45), "Ribbon")])
build("Keyring", keyring)
build("Ring", ring)
build("Fuse", fuse)
build("Shears", shears)
build("Tags", tags)
print("ITEMS done:", ", ".join(ITEMS))
