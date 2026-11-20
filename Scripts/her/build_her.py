"""Blender: turn the raw Meshy GLB of "her" into game assets.

  blender -b --factory-startup -P build_her.py -- <raw.glb> <out_dir> [clip names... | all] [--preview]

Writes  SK_Her.fbx (mesh + skeleton), A_Her_<Clip>.fbx (animation only), T_Her_*.png, her_info.json,
and preview/<Clip>.png contact sheets.  Units are centimetres, she faces -Y in Blender.

Animation is authored procedurally: every clip is a function pose(t) that returns spine/head rotations and
hand/foot targets; limbs are solved with analytic two-bone IK so planted feet do not slide.
"""
import bpy, sys, os, math, json
from mathutils import Vector, Matrix, Euler, Quaternion

argv = sys.argv[sys.argv.index("--") + 1:]
SRC, OUT = argv[0], argv[1]
WANT = [a for a in argv[2:] if not a.startswith("--")] or ["all"]
PREVIEW = "--preview" in argv
os.makedirs(OUT, exist_ok=True)
FPS = 30
rad = math.radians

# ------------------------------------------------------------------ scene + import
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
sc.render.fps = FPS
sc.unit_settings.system = "METRIC"
sc.unit_settings.scale_length = 0.01
bpy.ops.import_scene.gltf(filepath=SRC)
arm = [o for o in sc.objects if o.type == "ARMATURE"][0]
mesh = [o for o in sc.objects if o.type == "MESH" and o.parent == arm][0]
for o in list(sc.objects):
    if o not in (arm, mesh):
        bpy.data.objects.remove(o, do_unlink=True)
bpy.context.view_layer.update()
print("HER import scale", tuple(arm.scale), tuple(mesh.scale), tuple(round(d, 1) for d in mesh.dimensions))
bpy.ops.object.select_all(action="DESELECT")
arm.select_set(True); mesh.select_set(True)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)   # bake the importer's 0.01 into the data
arm.name = "Armature"; arm.data.name = "Armature"; mesh.name = "SK_Her"
if arm.animation_data:
    arm.animation_data.action = None
for a in list(bpy.data.actions):
    bpy.data.actions.remove(a)
bpy.context.view_layer.update()
print("HER dims", tuple(round(d, 1) for d in mesh.dimensions))

# ------------------------------------------------------------------ tidy bones (tails -> child heads so lengths mean something)
bpy.context.view_layer.objects.active = arm
bpy.ops.object.mode_set(mode="EDIT")
eb = arm.data.edit_bones
CH = {"Hips": "Spine02", "Spine02": "Spine01", "Spine01": "Spine", "Spine": "neck", "neck": "Head", "Head": "head_end"}
for s in ("Left", "Right"):
    CH.update({s + "Shoulder": s + "Arm", s + "Arm": s + "ForeArm", s + "ForeArm": s + "Hand",
               s + "UpLeg": s + "Leg", s + "Leg": s + "Foot", s + "Foot": s + "ToeBase"})
for b, c in CH.items():
    eb[b].tail = eb[c].head.copy()
for s in ("Left", "Right"):
    d = (eb[s + "Hand"].head - eb[s + "ForeArm"].head).normalized()
    eb[s + "Hand"].tail = eb[s + "Hand"].head + d * 20
    eb[s + "ToeBase"].tail = eb[s + "ToeBase"].head + Vector((0, -8, 0))
eb["head_end"].tail = eb["head_end"].head + Vector((0, 0, 5))
eb["headfront"].tail = eb["headfront"].head + Vector((0, -5, 0))
for b in eb:
    b.use_connect = False
bpy.ops.object.mode_set(mode="OBJECT")
bpy.context.view_layer.update()

B = arm.data.bones
P = arm.pose.bones
for pb in P:
    pb.rotation_mode = "QUATERNION"
REST = {b.name: b.matrix_local.copy() for b in B}
RROT = {n: m.to_3x3() for n, m in REST.items()}
HEAD = {n: m.to_translation() for n, m in REST.items()}
LEN = {n: B[n].length for n in REST}
print("HER leg", round(LEN["LeftUpLeg"], 1), round(LEN["LeftLeg"], 1), "arm", round(LEN["LeftArm"], 1), round(LEN["LeftForeArm"], 1))
HIP0 = HEAD["Hips"].copy()
ANK_Z = (HEAD["LeftFoot"].z + HEAD["RightFoot"].z) / 2
SH_L, SH_R = HEAD["LeftArm"].copy(), HEAD["RightArm"].copy()
ARM = LEN["LeftArm"] + LEN["LeftForeArm"]
LEG = LEN["LeftUpLeg"] + LEN["LeftLeg"]

# ------------------------------------------------------------------ the eye (fit a sphere to the bulge on her left side)
import numpy as np
mw = mesh.matrix_world
co = np.array([tuple(mw @ v.co) for v in mesh.data.vertices])
zc = HEAD["Head"].z
sel = co[(co[:, 2] > zc + 4) & (co[:, 2] < zc + 34) & (co[:, 0] > 2.0) & (co[:, 0] < 16.0)]
apex = sel[np.argmin(sel[:, 1])]
near = sel[np.linalg.norm(sel - apex, axis=1) < 4.2]
A = np.c_[2 * near, np.ones(len(near))]
sol, *_ = np.linalg.lstsq(A, (near ** 2).sum(axis=1), rcond=None)
ecen = sol[:3]; erad = float(np.sqrt(sol[3] + (ecen ** 2).sum()))
print("HER eye apex", apex.round(2), "centre", ecen.round(2), "radius", round(erad, 2), "n", len(near))
info = {"eye_apex": [float(v) for v in apex], "eye_centre": [float(v) for v in ecen], "eye_radius": erad,
        "head_bone": [float(v) for v in HEAD["Head"]], "height": float(co[:, 2].max()),
        "bones": {n: [float(v) for v in h] for n, h in HEAD.items()}, "clips": {}}

# ------------------------------------------------------------------ SCREAM: an unhinged, elongated open mouth
# Measured on the model (mouth_probe.py): lip line z = 234.0, mouth centre x = 0.3, about 8.5 cm wide, lips at y = -26.8.
LIP_Z, MOUTH_X, MOUTH_HALF, JAW_DROP = 234.0, 0.3, 4.4, 11.5
me_ = mesh.data
if not me_.shape_keys:
    mesh.shape_key_add(name="Basis", from_mix=False)
sk_scream = mesh.shape_key_add(name="Scream", from_mix=False)
inv_ = mesh.matrix_world.inverted()
n_jaw = n_gap = 0


def sstep(a, b, v):
    t = min(1.0, max(0.0, (v - a) / (b - a)))
    return t * t * (3.0 - 2.0 * t)


gap_verts = set()
for i, p in enumerate(co):
    x, y, z = float(p[0]), float(p[1]), float(p[2])
    if z > LIP_Z + 0.9 or z < LIP_Z - 26.0 or y > -9.0:
        continue
    dx = abs(x - MOUTH_X)
    side = 1.0 - sstep(MOUTH_HALF * 0.75, MOUTH_HALF * 2.1, dx)          # the corners of the mouth are pinned
    depth = 1.0 - sstep(-17.0, -10.5, y)                                 # only the front of the face, not the neck
    below = sstep(0.0, 1.3, LIP_Z - z)                                   # everything under the lip line goes with the jaw
    low = 1.0 - sstep(15.0, 26.0, LIP_Z - z)                             # fades out down the throat
    w_ = side * depth * below * low
    dz_ = -JAW_DROP * w_
    dy_ = 0.0
    dxs = 0.0
    if dx < MOUTH_HALF and abs(z - LIP_Z) < 0.75 and y < -21.0:
        # the lip line itself becomes the inside of the mouth: stretched, and pushed back into the head
        k = 1.0 - sstep(MOUTH_HALF * 0.55, MOUTH_HALF, dx)
        dy_ = 4.2 * k
        dz_ = -JAW_DROP * 0.5 * k
        gap_verts.add(i)
        n_gap += 1
    elif w_ > 0.02:
        # the open jaw narrows a little toward the chin: a long O, not a square
        dxs = -(x - MOUTH_X) * 0.10 * w_
        n_jaw += 1
    if dz_ or dy_:
        v_ = sk_scream.data[i]
        wp_ = Vector((x + dxs, y + dy_, z + dz_))
        v_.co = inv_ @ wp_
print("HER scream: jaw verts", n_jaw, "gap verts", n_gap)
# SNEER: the upper lip on her left side lifts off the mouth.  BROW: the brow comes down over the eye.
sk_sneer = mesh.shape_key_add(name="Sneer", from_mix=False)
sk_brow = mesh.shape_key_add(name="Brow", from_mix=False)
EYE_Z = float(ecen[2])
n_sneer = n_brow = 0
for i, p in enumerate(co):
    x, y, z = float(p[0]), float(p[1]), float(p[2])
    if y > -14.0:
        continue
    front = 1.0 - sstep(-19.0, -14.0, y)
    u = z - LIP_Z
    sx_ = x - MOUTH_X
    if 0.75 <= u <= 5.2 and sx_ > -1.0:
        w_ = sstep(-1.0, 2.0, sx_) * (1.0 - sstep(5.0, 9.5, sx_)) * (1.0 - sstep(2.4, 5.2, u)) * front
        if w_ > 0.02:
            sk_sneer.data[i].co = inv_ @ Vector((x + 0.5 * w_, y - 0.9 * w_, z + 2.4 * w_))
            n_sneer += 1
    bz = z - (EYE_Z + 1.6)
    if 0.0 <= bz <= 8.0 and abs(x) < 11.0:
        w_ = sstep(0.0, 1.2, bz) * (1.0 - sstep(3.5, 8.0, bz)) * (1.0 - sstep(7.0, 11.0, abs(x))) * front
        if w_ > 0.02:
            sk_brow.data[i].co = inv_ @ Vector((x * (1.0 - 0.10 * w_), y - 1.5 * w_, z - 3.0 * w_))
            n_brow += 1
print("HER face: sneer verts", n_sneer, "brow verts", n_brow)
# ------------------------------------------------------------------ MORE FACE: eleven further keys
# Everything is a soft push on a region of the face, measured from the mouth and from her one eye.  She is half as big
# again as a person, so a centimetre here is a small movement.
EX, EYF, EZ, ER = 6.0, -21.9, 246.6, 4.3          # her eye as the game has it (WCEntity.h EyeRef, EyeRadius): the fit above lands on her nose
FACE_KEYS = {"Scream": sk_scream, "Sneer": sk_sneer, "Brow": sk_brow}



def face_key(name, fn):
    """fn(x, y, z, front) -> (dx, dy, dz) in cm or None.  front is 1 on the face and 0 by the ears."""
    sk = mesh.shape_key_add(name=name, from_mix=False)
    n = 0
    for i, p in enumerate(co):
        x, y, z = float(p[0]), float(p[1]), float(p[2])
        if y > -11.0 or z < LIP_Z - 32.0 or z > EZ + 16.0:
            continue
        d = fn(x, y, z, 1.0 - sstep(-19.0, -14.0, y))
        if d and abs(d[0]) + abs(d[1]) + abs(d[2]) > 0.02:
            sk.data[i].co = inv_ @ Vector((x + d[0], y + d[1], z + d[2]))
            n += 1
    FACE_KEYS[name] = sk
    print("HER face key", name, n, "verts")
    return sk


def _brow_w(x, z):
    bz = z - (EZ + ER - 0.8)
    if bz < 0.0 or bz > 9.0:
        return 0.0
    return sstep(0.0, 1.5, bz) * (1.0 - sstep(4.0, 9.0, bz)) * (1.0 - sstep(7.0, 12.0, abs(x - 3.0)))


def _eye_ring(x, z):
    # the rim of skin round the ball: nothing inside it (the ball is its own piece in the game), fading out over the cheek and brow
    r = math.hypot(x - EX, z - EZ)
    if r < ER - 0.9 or r > ER + 5.0:
        return 0.0, 0.0, 0.0
    w = sstep(ER - 0.9, ER + 0.3, r) * (1.0 - sstep(ER + 1.5, ER + 5.0, r))
    return w, (x - EX) / r, (z - EZ) / r



def _corner_w(x, z):
    a, u = abs(x - MOUTH_X), abs(z - LIP_Z)
    return sstep(2.0, 4.4, a) * (1.0 - sstep(6.5, 11.0, a)) * (1.0 - sstep(1.5, 5.5, u))


def _k_browup(x, y, z, f):
    w = _brow_w(x, z) * f
    return (0.0, -0.3 * w, 2.6 * w)


def _k_browknit(x, y, z, f):
    w = _brow_w(x, z) * f
    inner = 1.0 - sstep(2.0, 8.0, abs(x))
    return (-x * 0.25 * w, -1.0 * w * inner, -1.4 * w * inner)


def _k_browdown(x, y, z, f):
    # the top of the socket comes down over the ball, and forward so it rides over it and not through it
    w, rx, rz = _eye_ring(x, z)
    w *= f * max(0.0, rz)
    return (0.0, -2.0 * w, -2.6 * w)


def _k_eyewide(x, y, z, f):
    w, rx, rz = _eye_ring(x, z)
    w *= f
    return (1.3 * w * rx, 0.5 * w, 1.3 * w * rz)


def _k_squint(x, y, z, f):
    w, rx, rz = _eye_ring(x, z)
    w *= f
    return (-0.4 * w * rx, -2.2 * w * abs(rz), (-1.3 if rz > 0 else 2.2) * w * abs(rz))


def _k_snarl(x, y, z, f):
    sx = x - MOUTH_X
    w = sstep(LIP_Z + 0.6, LIP_Z + 2.0, z) * (1.0 - sstep(243.0, 248.0, z)) * (1.0 - sstep(3.0, 7.0, abs(sx))) * f
    return (sx * 0.18 * w, -0.4 * w, 1.3 * w)



def _k_sneer_r(x, y, z, f):
    u, sx = z - LIP_Z, -(x - MOUTH_X)
    if not (0.75 <= u <= 5.2) or sx < -1.0:
        return None
    w = sstep(-1.0, 2.0, sx) * (1.0 - sstep(5.0, 9.5, sx)) * (1.0 - sstep(2.4, 5.2, u)) * f
    return (-0.5 * w, -0.9 * w, 2.4 * w)


def _k_grin(x, y, z, f):
    w = _corner_w(x, z) * f
    s = 1.0 if x > MOUTH_X else -1.0
    return (s * 2.4 * w, 1.4 * w, 1.3 * w)


def _k_frown(x, y, z, f):
    w = _corner_w(x, z) * f
    s = 1.0 if x > MOUTH_X else -1.0
    return (s * 0.6 * w, 0.4 * w, -2.2 * w)


def _k_jawside(x, y, z, f):
    w = sstep(0.0, 1.3, LIP_Z - z) * (1.0 - sstep(15.0, 26.0, LIP_Z - z)) * (1.0 - sstep(-17.0, -10.5, y)) * (1.0 - sstep(8.0, 12.0, abs(x)))
    return (2.6 * w, 0.0, 0.0)


def _k_pucker(x, y, z, f):
    sx, u = x - MOUTH_X, abs(z - LIP_Z)
    w = (1.0 - sstep(4.5, 7.5, abs(sx))) * (1.0 - sstep(2.0, 4.5, u)) * f
    return (-sx * 0.32 * w, -1.5 * w, 0.0)


def _k_cheeksuck(x, y, z, f):
    a = abs(x)
    w = sstep(3.5, 6.0, a) * (1.0 - sstep(8.5, 11.5, a)) * sstep(LIP_Z - 7.0, LIP_Z - 3.0, z) * (1.0 - sstep(237.0, 241.0, z)) * (1.0 - sstep(-16.0, -11.0, y))
    return (-x * 0.10 * w, 1.6 * w, 0.0)



def _cheek_w(x, y, z):
    a = abs(x)
    return sstep(3.5, 6.0, a) * (1.0 - sstep(8.5, 11.5, a)) * sstep(LIP_Z - 7.0, LIP_Z - 3.0, z) * (1.0 - sstep(237.0, 241.0, z)) * (1.0 - sstep(-16.0, -11.0, y))


def _k_stretch(x, y, z, f):
    # the whole mouth pulled wide, and the cheeks with it: with Scream, a hole as wide as it is long
    sx = x - MOUTH_X
    a, d = abs(sx), LIP_Z - z
    w = sstep(0.4, 4.4, a) * (1.0 - sstep(8.0, 14.0, a)) * (1.0 - sstep(13.0, 23.0, d)) * (1.0 - sstep(2.0, 6.0, -d)) * (1.0 - sstep(-16.0, -10.0, y))
    s = 1.0 if sx > 0 else -1.0
    return (s * 4.2 * w, 1.1 * w * sstep(3.0, 7.0, a), 0.0)


def _k_unhinge(x, y, z, f):
    # the jaw goes on down: the same parts of her as Scream, further, and the cheeks drawn long after it
    dx, d = abs(x - MOUTH_X), LIP_Z - z
    if d < -0.9 or d > 30.0:
        return None
    side = 1.0 - sstep(MOUTH_HALF * 1.1, MOUTH_HALF * 2.6, dx)
    w = side * (1.0 - sstep(-17.0, -10.5, y)) * sstep(0.0, 1.3, d) * (1.0 - sstep(17.0, 30.0, d))
    if dx < MOUTH_HALF and abs(d) < 0.75 and y < -21.0:
        k = 1.0 - sstep(MOUTH_HALF * 0.55, MOUTH_HALF, dx)
        return (0.0, 1.5 * k, -4.5 * k)
    return (-(x - MOUTH_X) * 0.06 * w, 0.8 * w, -9.0 * w)


def _k_cheek_l(x, y, z, f):
    w = _cheek_w(x, y, z) if x > 0 else 0.0
    return (1.8 * w, 0.8 * w, 1.4 * w)


def _k_cheek_r(x, y, z, f):
    w = _cheek_w(x, y, z) if x < 0 else 0.0
    return (-1.8 * w, 0.8 * w, 1.4 * w)


def _k_cheekraise(x, y, z, f):
    w = _cheek_w(x, y, z)
    return (0.0, -0.5 * w, 2.0 * w)


for _nm, _fn in (("BrowUp", _k_browup), ("BrowKnit", _k_browknit), ("BrowDown", _k_browdown), ("EyeWide", _k_eyewide), ("Squint", _k_squint), ("Snarl", _k_snarl),
                 ("SneerR", _k_sneer_r), ("Grin", _k_grin), ("Frown", _k_frown), ("JawSide", _k_jawside), ("Pucker", _k_pucker), ("CheekSuck", _k_cheeksuck),
                 ("Stretch", _k_stretch), ("Unhinge", _k_unhinge), ("CheekL", _k_cheek_l), ("CheekR", _k_cheek_r), ("CheekRaise", _k_cheekraise)):
    face_key(_nm, _fn)

# the faces the game makes out of them (the same table is in WCEntity.cpp: keep the two alike)
MOODS = {
    "rest": {},
    "watch": {"EyeWide": 0.8, "BrowUp": 0.35, "CheekSuck": 0.5},
    "grin": {"Grin": 1.0, "Squint": 0.6, "Sneer": 0.4, "SneerR": 0.4, "BrowUp": 0.25},
    "snarl": {"Snarl": 1.0, "Sneer": 0.8, "SneerR": 0.55, "BrowKnit": 0.8, "BrowDown": 0.7, "JawSide": 0.35, "Scream": 0.18},
    "rage": {"Scream": 0.7, "BrowKnit": 1.0, "BrowDown": 0.8, "Snarl": 1.0, "Stretch": 0.45, "CheekRaise": 0.5},
    "scream": {"Scream": 1.0, "Unhinge": 1.0, "Stretch": 1.0, "BrowKnit": 0.8, "Snarl": 0.8, "EyeWide": 1.0, "CheekSuck": 0.5},
    "wince": {"CheekL": 1.0, "Sneer": 0.8, "Squint": 0.7, "JawSide": 0.5, "BrowKnit": 0.5},
    "grief": {"BrowUp": 1.0, "BrowKnit": 0.5, "Frown": 1.0, "Squint": 0.45, "Scream": 0.14, "CheekSuck": 0.4, "Brow": 0.6},

    "hush": {"Pucker": 1.0, "BrowKnit": 0.4, "Squint": 0.3, "EyeWide": 0.2},
}
info["face_keys"] = sorted(FACE_KEYS)

# black inside: paint every face on the lip line black in the base colour (it is a hair-thin line until she screams)
_bsdf = next(n for n in me_.materials[0].node_tree.nodes if n.type == "BSDF_PRINCIPLED")
_node = _bsdf.inputs["Base Color"].links[0].from_node
while _node.type != "TEX_IMAGE":
    _node = next(i.links[0].from_node for i in _node.inputs if i.is_linked)
_img = _node.image
_W, _H = _img.size
_px = np.array(_img.pixels[:], dtype=np.float32).reshape(_H, _W, 4)
_uv = me_.uv_layers.active.data
n_tri = 0
for poly in me_.polygons:
    if sum(1 for vi in poly.vertices if vi in gap_verts) < 2:
        continue
    uvs = [(_uv[li].uv.x % 1.0 * _W, _uv[li].uv.y % 1.0 * _H) for li in poly.loop_indices]
    for t in range(1, len(uvs) - 1):
        (x0, y0), (x1, y1), (x2, y2) = uvs[0], uvs[t], uvs[t + 1]
        xa, xb = int(max(0, min(x0, x1, x2) - 1)), int(min(_W - 1, max(x0, x1, x2) + 1))
        ya, yb = int(max(0, min(y0, y1, y2) - 1)), int(min(_H - 1, max(y0, y1, y2) + 1))
        if xb - xa > 200 or yb - ya > 200:
            continue                                    # a face that wraps a UV seam
        den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
        if abs(den) < 1e-9:
            _px[ya:yb + 1, xa:xb + 1, :3] = 0.004
            continue
        ys, xs = np.mgrid[ya:yb + 1, xa:xb + 1]
        a_ = ((y1 - y2) * (xs + 0.5 - x2) + (x2 - x1) * (ys + 0.5 - y2)) / den
        b_ = ((y2 - y0) * (xs + 0.5 - x2) + (x0 - x2) * (ys + 0.5 - y2)) / den
        inside = (a_ >= -0.12) & (b_ >= -0.12) & (a_ + b_ <= 1.12)
        sub = _px[ya:yb + 1, xa:xb + 1, :3]
        sub[inside] = 0.004
        n_tri += 1
_img.pixels[:] = _px.ravel()
_img.update()
print("HER scream: painted", n_tri, "lip-line triangles black")
info["mouth"] = [MOUTH_X, -26.8, LIP_Z]
if "--faceshot" in argv:
    # one close picture of every key at full, and of every mood, for a contact sheet
    sc.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE"
    _w = bpy.data.worlds.new("w"); sc.world = _w; _w.use_nodes = True
    _w.node_tree.nodes["Background"].inputs[0].default_value = (0.3, 0.3, 0.32, 1)
    _sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); _sun.data.energy = 3
    _sun.rotation_euler = (math.radians(62), 0, math.radians(22)); sc.collection.objects.link(_sun)
    _cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(_cam); sc.camera = _cam
    _cam.data.lens = 85; _cam.data.clip_end = 5000
    sc.render.resolution_x = 640; sc.render.resolution_y = 640
    _tgt = Vector((1.5, -14.0, 237.5))
    _dir_out = os.path.join(os.path.abspath(OUT), "preview", "face")
    os.makedirs(_dir_out, exist_ok=True)
    for _f in os.listdir(_dir_out):
        os.remove(os.path.join(_dir_out, _f))
    def _ball(r, loc, col):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=32, ring_count=16)
        _o = bpy.context.active_object
        bpy.ops.object.shade_smooth()
        _m = bpy.data.materials.new("eye"); _m.use_nodes = True
        _b = next(n for n in _m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        _b.inputs["Base Color"].default_value = col
        _b.inputs["Roughness"].default_value = 0.15
        _o.data.materials.append(_m)
    _ball(ER, (EX, EYF, EZ), (0.004, 0.004, 0.004, 1))
    _ball(ER * 0.32, (EX, EYF - ER * 0.80, EZ), (0.75, 0.78, 0.8, 1))
    _ball(ER * 0.15, (EX, EYF - ER * 0.985, EZ), (0.004, 0.004, 0.004, 1))

    _shots = [("00_rest", {})] + [(f"{i + 1:02d}_{n}", {n: 1.0}) for i, n in enumerate(sorted(FACE_KEYS))] + [(f"m{i}_{n}", v) for i, (n, v) in enumerate(MOODS.items()) if v]
    for _view, _d in (("f", (0.12, -1, 0.02)), ("q", (0.75, -1, 0.05))):
        _cam.location = _tgt + Vector(_d).normalized() * 108

        _cam.rotation_euler = (_tgt - _cam.location).to_track_quat("-Z", "Y").to_euler()
        for _nm, _vals in _shots:
            if _view == "q" and not _nm.startswith("m"):
                continue
            for _k, _sk in FACE_KEYS.items():
                _sk.value = _vals.get(_k, 0.0)
            mesh.data.update()
            bpy.context.view_layer.update()
            sc.render.filepath = os.path.join(_dir_out, f"{_nm}_{_view}.png")
            bpy.ops.render.render(write_still=True)
    for _sk in FACE_KEYS.values():
        _sk.value = 0.0
    raise SystemExit(0)
if "--screamshot" in argv:

    sc.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE"
    _w = bpy.data.worlds.new("w"); sc.world = _w; _w.use_nodes = True
    _w.node_tree.nodes["Background"].inputs[0].default_value = (0.3, 0.3, 0.32, 1)
    _sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); _sun.data.energy = 3
    _sun.rotation_euler = (math.radians(60), 0, math.radians(15)); sc.collection.objects.link(_sun)
    _cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(_cam); sc.camera = _cam
    _cam.data.lens = 85; _cam.data.clip_end = 5000
    sc.render.resolution_x = 900; sc.render.resolution_y = 900
    _tgt = Vector((1.0, -10.0, 236.0))
    os.makedirs(os.path.join(OUT, "preview"), exist_ok=True)
    for _nm, _val, _d in (("scream_0", 0.0, (0.15, -1, 0.0)), ("scream_1", 1.0, (0.15, -1, 0.0)), ("scream_1_side", 1.0, (1, -0.35, 0.0))):
        sk_scream.value = _val
        _cam.location = _tgt + Vector(_d).normalized() * 150
        _cam.rotation_euler = (_tgt - _cam.location).to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = os.path.join(OUT, "preview", _nm + ".png")
        bpy.ops.render.render(write_still=True)
    sk_scream.value = 0.0
    for _nm, _sn, _br, _scr in (("sneer_1", 1.0, 0.0, 0.0), ("brow_1", 0.0, 1.0, 0.0), ("talk_1", 0.2, 0.4, 0.3), ("rest_1", 0.0, 0.0, 0.0)):
        sk_sneer.value, sk_brow.value, sk_scream.value = _sn, _br, _scr
        mesh.data.update()
        bpy.context.view_layer.update()
        _cam.location = _tgt + Vector((0.15, -1, 0.0)).normalized() * 150
        _cam.rotation_euler = (_tgt - _cam.location).to_track_quat("-Z", "Y").to_euler()
        sc.render.filepath = os.path.join(OUT, "preview", _nm + ".png")
        bpy.ops.render.render(write_still=True)
    sk_sneer.value = sk_brow.value = 0.0
    sk_scream.value = 0.0
    raise SystemExit(0)

# ------------------------------------------------------------------ textures
names = {}
for mat in mesh.data.materials:
    nt = mat.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")

    def img_of(sock):
        if not sock.is_linked:
            return None
        n = sock.links[0].from_node
        seen = 0
        while n and n.type != "TEX_IMAGE" and seen < 6:
            nxt = next((i.links[0].from_node for i in n.inputs if i.is_linked), None)
            n = nxt; seen += 1
        return n.image if n and n.type == "TEX_IMAGE" else None
    for key, sock in (("BaseColor", "Base Color"), ("Normal", "Normal"), ("Roughness", "Roughness"), ("Metallic", "Metallic")):
        im = img_of(bsdf.inputs[sock])
        if im and im.name not in names:
            names[im.name] = key
            p = os.path.join(OUT, "T_Her_%s.png" % key)
            im.filepath_raw = p; im.file_format = "PNG"; im.save()
            print("HER tex", key, im.name, tuple(im.size))


# ------------------------------------------------------------------ pose toolkit
def upd():
    bpy.context.view_layer.update()


def reset_pose():
    for pb in P:
        pb.location = (0, 0, 0); pb.rotation_quaternion = (1, 0, 0, 0); pb.scale = (1, 1, 1)


def fk(name, rx=0.0, ry=0.0, rz=0.0):
    """Rotate a bone by angles (deg) about armature axes: +X bends forward, +Y tilts to her left, +Z turns left."""
    R = RROT[name]
    Q = Euler((rad(rx), rad(ry), rad(rz)), "ZYX").to_matrix()
    P[name].rotation_quaternion = (R.inverted() @ Q @ R).to_quaternion()


def hips(dx=0.0, dy=0.0, dz=0.0, rx=0.0, ry=0.0, rz=0.0):
    fk("Hips", rx, ry, rz)
    P["Hips"].location = RROT["Hips"].inverted() @ Vector((dx, dy, dz))


def aim(name, direction, twist_ref=None):
    """Point a bone (already following its parents) along `direction` with the smallest turn."""
    pb = P[name]
    M = pb.matrix.copy()
    R = M.to_3x3().normalized()
    cur = (R @ Vector((0, 1, 0))).normalized()
    q = cur.rotation_difference(Vector(direction).normalized())
    R2 = q.to_matrix() @ R
    M2 = R2.to_4x4(); M2.translation = M.translation
    pb.matrix = M2
    upd()


def two_bone(upper, lower, target, hint):
    """Analytic IK: bend toward `hint` (a direction in armature space)."""
    a = P[upper].head.copy()
    l1, l2 = LEN[upper], LEN[lower]
    d = Vector(target) - a
    dist = max(1e-3, min(d.length, (l1 + l2) * 0.999))
    dirn = d.normalized()
    x = (l1 * l1 - l2 * l2 + dist * dist) / (2 * dist)
    h = math.sqrt(max(l1 * l1 - x * x, 0.0))
    hv = Vector(hint) - dirn * Vector(hint).dot(dirn)
    hv = hv.normalized() if hv.length > 1e-4 else Vector((0, -1, 0))
    knee = a + dirn * x + hv * h
    aim(upper, knee - a)
    aim(lower, (a + dirn * dist) - knee)


def set_world_rot(name, rot3):
    pb = P[name]
    M = rot3.to_4x4(); M.translation = pb.matrix.translation
    pb.matrix = M
    upd()


def foot(side, target, pitch=0.0, yaw=0.0, knee=(0, -1, 0.15)):
    two_bone(side + "UpLeg", side + "Leg", target, knee)
    R = Euler((rad(pitch), 0, rad(yaw)), "ZYX").to_matrix() @ RROT[side + "Foot"]
    set_world_rot(side + "Foot", R)


def hand(side, target, elbow=(0, 1, -0.2), rot=None):
    two_bone(side + "Arm", side + "ForeArm", target, elbow)
    if rot is not None:
        R = Euler((rad(rot[0]), rad(rot[1]), rad(rot[2])), "ZYX").to_matrix() @ RROT[side + "Hand"]
        set_world_rot(side + "Hand", R)


def spine(bend, side=0.0, twist=0.0, split=(0.34, 0.33, 0.33)):
    for n, f in zip(("Spine02", "Spine01", "Spine"), split):
        fk(n, bend * f, side * f, twist * f)


def head(pitch=0.0, roll=0.0, yaw=0.0, neck=0.4):
    fk("neck", pitch * neck, roll * neck, yaw * neck)
    fk("Head", pitch * (1 - neck), roll * (1 - neck), yaw * (1 - neck))


def shoulder_pos(side):
    return P[side + "Arm"].head.copy()


def wob(t, f, ph=0.0):
    return math.sin(2 * math.pi * f * t + ph)


def jit(t, seed):
    """Small irregular twitchy noise in -1..1."""
    return 0.5 * wob(t, 1.7, seed) + 0.3 * wob(t, 4.3, seed * 2.1) + 0.2 * wob(t, 9.1, seed * 3.7)


def smooth(u):
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


def step_cycle(ph, stance):
    """-> (along, lift, toe) for one foot. along runs +0.5 (front) to -0.5 (back) during stance, then swings forward."""
    ph %= 1.0
    if ph < stance:
        u = ph / stance
        return 0.5 - u, 0.0, max(0.0, (u - 0.75) / 0.25)
    u = (ph - stance) / (1 - stance)
    return -0.5 + smooth(u), math.sin(math.pi * u), 1.0 - u


FOOT_X = 15.0
FOOT_Y0 = 10.0


# ------------------------------------------------------------------ clips.  Each returns nothing; it poses the rig for time t.
def hunch_base(t, drop=9.0, bend=36.0, look=-40.0, sway=1.0):
    br = wob(t, 0.22)                     # breathing
    hips(dx=1.2 * sway * wob(t, 0.11), dy=6.0, dz=-drop + 0.8 * br, rx=6.0)
    spine(bend + 2.0 * br, side=3.0 * wob(t, 0.13) * sway, twist=2.0 * wob(t, 0.09))
    head(look - 2.0 * br + 2.5 * jit(t * 0.5, 1.0), roll=14.0 + 3.0 * wob(t, 0.17), yaw=4.0 * wob(t, 0.07))
    fk("LeftShoulder", 0, 6, 0); fk("RightShoulder", 0, -6, 0)
    upd()


def dangle(side, t, swing=0.0, reach=0.965, out=4.0):
    s = shoulder_pos(side)
    sx = 1 if side == "Left" else -1
    tgt = s + Vector((sx * out, swing + 2.0 * wob(t, 0.31, sx), -ARM * reach))
    hand(side, tgt, elbow=(sx * 0.3, 1, 0.1), rot=(8.0, 0, 0))


def clip_idle(t):
    hunch_base(t)
    foot("Left", (FOOT_X, FOOT_Y0 - 6, ANK_Z)); foot("Right", (-FOOT_X - 2, FOOT_Y0 + 8, ANK_Z), yaw=-8)
    dangle("Left", t, 2.0 * wob(t, 0.2)); dangle("Right", t, 2.0 * wob(t, 0.2, 1.3))


WALK_T, WALK_S, WALK_ST = 1.8, 74.0, 0.62


def clip_walk(t):
    ph = (t / WALK_T) % 1.0
    lurch = wob(ph, 1.0)                 # side to side once per cycle
    drop = 10.0 + 4.0 * math.cos(4 * math.pi * ph)
    hips(dx=5.0 * lurch, dy=6.0, dz=-drop, rx=6.0, ry=-3.0 * lurch, rz=5.0 * wob(ph, 1.0, 1.57))
    spine(36.0 + 3.0 * wob(ph, 2.0), side=5.0 * lurch, twist=-7.0 * wob(ph, 1.0, 1.57))
    head(-40.0 + 3.0 * wob(ph, 2.0, 0.8), roll=14.0 - 6.0 * lurch, yaw=3.0 * wob(ph, 1.0))
    fk("LeftShoulder", 0, 6, 0); fk("RightShoulder", 0, -6, 0)
    upd()
    for side, off, sx in (("Left", 0.0, 1), ("Right", 0.5, -1)):
        al, lift, toe = step_cycle(ph + off, WALK_ST)
        foot(side, (sx * FOOT_X, FOOT_Y0 - al * WALK_S, ANK_Z + 9.0 * lift), pitch=22.0 * toe * (1 if lift == 0 else 0.6))
    dangle("Left", t, swing=-13.0 * wob(ph, 1.0, 0.5 * math.pi - 0.6))
    dangle("Right", t, swing=13.0 * wob(ph, 1.0, 0.5 * math.pi - 0.6))


RUN_T, RUN_S, RUN_ST = 0.60, 150.0, 0.40


def clip_run(t):
    ph = (t / RUN_T) % 1.0
    bob = math.cos(4 * math.pi * ph)
    lurch = wob(ph, 1.0)
    hips(dx=3.0 * lurch, dy=10.0, dz=-24.0 + 5.0 * bob, rx=14.0, ry=-4.0 * lurch, rz=9.0 * wob(ph, 1.0, 1.57))
    spine(46.0 + 4.0 * bob, side=6.0 * lurch, twist=-12.0 * wob(ph, 1.0, 1.57))
    head(-66.0 + 4.0 * jit(t, 2.0), roll=20.0 + 8.0 * jit(t, 5.0), yaw=6.0 * jit(t, 9.0))
    fk("LeftShoulder", -10, 0, 0); fk("RightShoulder", -10, 0, 0)
    upd()
    for side, off, sx in (("Left", 0.0, 1), ("Right", 0.5, -1)):
        al, lift, toe = step_cycle(ph + off, RUN_ST)
        foot(side, (sx * (FOOT_X - 3), FOOT_Y0 + 4 - al * RUN_S, ANK_Z + 34.0 * lift + (6.0 if lift > 0 else 0)),
             pitch=30.0 * toe + 25.0 * lift, knee=(0, -1, 0.3))
    for side, sx, pp in (("Left", 1, 0.0), ("Right", -1, math.pi)):
        s = shoulder_pos(side)
        hand(side, s + Vector((sx * (10 + 5 * wob(ph, 2.0, pp)), -ARM * 0.90, -ARM * 0.18 + 12.0 * wob(ph, 1.0, pp))),
             elbow=(sx * 0.7, 0.2, -1), rot=(-25.0 + 15.0 * wob(ph, 2.0, pp), 0, 0))


def clip_peek(t):
    # doorway edge is the plane x = 0; her body stays at x < 0 and the head leans out past it.
    br = wob(t, 0.2)
    hips(dx=-30.0, dy=8.0, dz=-3.0 + 0.6 * br, rx=2.0, ry=5.0)
    spine(10.0 + 1.5 * br, side=26.0, twist=4.0)
    head(-16.0 + 1.5 * jit(t * 0.4, 3.0), roll=12.0 + 1.5 * wob(t, 0.15), yaw=-6.0, neck=0.5)
    fk("LeftShoulder", 0, 10, 0); fk("RightShoulder", 0, 0, 0)
    upd()
    foot("Left", (-22.0, FOOT_Y0, ANK_Z), yaw=6); foot("Right", (-58.0, FOOT_Y0 + 6, ANK_Z), yaw=-10)
    hand("Right", (3.0, -30.0, 176.0 + 0.8 * br), elbow=(-1, 0.3, -0.6), rot=(-70.0, 0, 60.0))
    dangle("Left", t, 0.0, reach=0.93, out=-8.0)


def clip_tall(t, rise=None):
    """Standing at full height. rise 0..1 blends up from the hunch."""
    k = 1.0 if rise is None else smooth(rise)
    br = wob(t, 0.2)
    hips(dy=6.0 * (1 - k), dz=-9.0 * (1 - k) + 0.8 * br, rx=6.0 * (1 - k))
    spine(36.0 * (1 - k) + 2.0 * br + 4.0 * k, side=2.0 * wob(t, 0.13))
    head((-40.0) * (1 - k) + 16.0 * k + 2.0 * jit(t * 0.5, 1.0), roll=14.0 + 10.0 * k, yaw=3.0 * wob(t, 0.07))
    fk("LeftShoulder", 0, 6 - 4 * k, 0); fk("RightShoulder", 0, -6 + 4 * k, 0)
    upd()
    foot("Left", (FOOT_X, FOOT_Y0 - 6, ANK_Z)); foot("Right", (-FOOT_X - 2, FOOT_Y0 + 8, ANK_Z), yaw=-8)
    for side, sx in (("Left", 1), ("Right", -1)):
        s = shoulder_pos(side)
        hand(side, s + Vector((sx * (4 + 16 * k), 2.0 * wob(t, 0.3, sx) - 6 * k, -ARM * (0.965 - 0.01 * k))),
             elbow=(sx * 0.3, 1, 0.1), rot=(8.0, 0, 0))


def clip_rise(t):
    clip_tall(t, rise=(t - 0.4) / 2.4)


CRAWL_T, CRAWL_S, CRAWL_ST = 0.62, 78.0, 0.5


def clip_crawl(t):
    ph = (t / CRAWL_T) % 1.0
    lurch = wob(ph, 1.0)
    hips(dx=4.0 * lurch, dy=38.0, dz=-66.0 + 3.0 * math.cos(4 * math.pi * ph), rx=38.0, rz=8.0 * wob(ph, 1.0, 1.57))
    spine(50.0, side=7.0 * lurch, twist=-8.0 * wob(ph, 1.0, 1.57))
    head(-84.0 + 5.0 * jit(t, 4.0), roll=22.0 + 10.0 * jit(t, 7.0), yaw=8.0 * jit(t, 11.0), neck=0.5)
    fk("LeftShoulder", -20, -8, 0); fk("RightShoulder", -20, 8, 0)
    upd()
    for side, off, sx in (("Left", 0.0, 1), ("Right", 0.5, -1)):
        al, lift, toe = step_cycle(ph + off, CRAWL_ST)
        foot(side, (sx * 30.0, 78.0 - al * CRAWL_S, ANK_Z + 4 + 12.0 * lift), pitch=35.0, yaw=sx * -25, knee=(sx * 0.9, -1, 0.5))
        al, lift, toe = step_cycle(ph + off + 0.5, CRAWL_ST)
        s = shoulder_pos(side)
        hand(side, (sx * 38.0, s.y - 26.0 - al * CRAWL_S, 9.0 + 16.0 * lift), elbow=(sx * 1.0, 0.5, 0.6), rot=(-80.0, 0, sx * 20.0))


def clip_sit(t):
    # seat height ~46 cm; knees forward, hands flat on a table top at ~76 cm
    br = wob(t, 0.2)
    hips(dy=34.0, dz=-(HIP0.z - 62.0) + 0.5 * br, rx=-6.0)
    spine(26.0 + 2.0 * br, side=2.0 * wob(t, 0.1))
    head(8.0 + 2.0 * jit(t * 0.4, 2.0), roll=18.0, yaw=0.0)
    upd()
    foot("Left", (FOOT_X + 3, -52.0, ANK_Z), knee=(0, -1, 1.0)); foot("Right", (-FOOT_X - 3, -44.0, ANK_Z), knee=(0, -1, 1.0))
    hand("Left", (26.0, -62.0, 82.0), elbow=(1, 0.6, -0.3), rot=(-78.0, 0, 0))
    hand("Right", (-24.0, -66.0, 82.0), elbow=(-1, 0.6, -0.3), rot=(-78.0, 0, 0))


def clip_wheelchair(t):
    breath = wob(t, .18)
    hips(dz=-(HIP0.z - 59.) + .25*breath, rx=-3.)
    spine(8. + .7*breath)
    head(-6. + .25*breath, roll=3.)
    upd()
    foot("Left", (FOOT_X, -46., ANK_Z), knee=(0,-1,1.))
    foot("Right", (-FOOT_X, -43., ANK_Z), knee=(0,-1,1.))
    hand("Left", (25., -22., 66.), elbow=(1,.6,-.4), rot=(-68,0,0))
    hand("Right", (-24., -25., 66.), elbow=(-1,.6,-.4), rot=(-68,0,0))


def clip_threshold(t):
    # She folds her knees under the lintel so her face meets the deputy at eye level.
    breath = wob(t, .22)
    hips(dy=7.,dz=-57.+.65*breath,rx=8.)
    spine(30.+breath)
    head(-33.,roll=-7.)
    upd()
    foot("Left",(FOOT_X+5.,FOOT_Y0-15.,ANK_Z),knee=(.2,-1,.5))
    foot("Right",(-FOOT_X-3.,FOOT_Y0+8.,ANK_Z),knee=(-.22,-1,.5))
    dangle("Left",t,1.,reach=.83)
    dangle("Right",t,-1.,reach=.84)


def clip_under(t):
    # lying on her front, chin near the floor, one arm reaching toward the viewer
    br = wob(t, 0.25)
    hips(dy=96.0, dz=-(HIP0.z - 17.0), rx=84.0)
    spine(6.0, side=4.0)
    head(-64.0 + 2.0 * jit(t * 0.5, 2.0), roll=24.0, yaw=0.0, neck=0.5)
    upd()
    foot("Left", (22.0, 214.0, 9.0), pitch=70, knee=(0.6, 0, 1)); foot("Right", (-20.0, 208.0, 9.0), pitch=70, knee=(-0.6, 0, 1))
    reach = 6.0 * wob(t, 0.35)
    hand("Left", (30.0, -92.0 + reach, 7.0), elbow=(1, 0.2, 0.5), rot=(-86.0, 0, 0))
    hand("Right", (-40.0, 8.0, 7.0), elbow=(-1, 0.2, 0.6), rot=(-86.0, 0, 0))


def clip_lunge(t):
    k = smooth(t / 0.28)
    hips(dy=6.0 - 22.0 * k, dz=-9.0 - 4.0 * k, rx=6.0 + 10.0 * k)
    spine(36.0 + 4.0 * k)
    head(-40.0 - 10.0 * k + 3.0 * jit(t, 3.0), roll=14.0 + 12.0 * k)
    fk("LeftShoulder", -18 * k, 6, 0); fk("RightShoulder", -18 * k, -6, 0)
    upd()
    foot("Left", (FOOT_X, FOOT_Y0 - 6 - 30 * k, ANK_Z)); foot("Right", (-FOOT_X - 2, FOOT_Y0 + 8 + 10 * k, ANK_Z), pitch=20 * k)
    for side, sx in (("Left", 1), ("Right", -1)):
        s = shoulder_pos(side)
        down = s + Vector((sx * 4, 0, -ARM * 0.965))
        out = s + Vector((sx * 16, -ARM * 0.93, 4.0))
        hand(side, down.lerp(out, k), elbow=(sx * 0.6, 0.6, -0.6), rot=(8.0 - 60.0 * k, 0, 0))


CLIPS = {
    # name: (function, seconds, loop, ground speed cm/s or 0)
    "Idle": (clip_idle, 9.0, True, 0.0),
    "Walk": (clip_walk, WALK_T, True, WALK_S / (WALK_ST * WALK_T)),
    "Run": (clip_run, RUN_T, True, RUN_S / (RUN_ST * RUN_T)),
    "Peek": (clip_peek, 6.6, True, 0.0),
    "Rise": (clip_rise, 3.4, False, 0.0),
    "Tall": (clip_tall, 9.0, True, 0.0),
    "Crawl": (clip_crawl, CRAWL_T, True, CRAWL_S / (CRAWL_ST * CRAWL_T)),
    "Sit": (clip_sit, 10.0, True, 0.0),
    "Wheelchair": (clip_wheelchair, 5.5, True, 0.0),
    "Threshold": (clip_threshold, 4., True, 0.0),
    "Under": (clip_under, 8.0, True, 0.0),
    "Lunge": (clip_lunge, 0.6, False, 0.0),
}


# ------------------------------------------------------------------ export helpers
def export_fbx(path, with_mesh, with_anim):
    bpy.ops.object.select_all(action="DESELECT")
    arm.select_set(True)
    if with_mesh:
        mesh.select_set(True)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={"ARMATURE", "MESH"} if with_mesh else {"ARMATURE"},
                             add_leaf_bones=False, bake_anim=with_anim, bake_anim_use_all_actions=False,
                             bake_anim_use_nla_strips=False, bake_anim_force_startend_keying=True,
                             bake_anim_simplify_factor=0.0, armature_nodetype="NULL", primary_bone_axis="Y",
                             secondary_bone_axis="X", apply_unit_scale=True, apply_scale_options="FBX_SCALE_UNITS",
                             global_scale=1.0, mesh_smooth_type="FACE", use_tspace=True)


def setup_preview():
    sc.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE"
    w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.2, 0.2, 0.22, 1)
    sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); sun.data.energy = 3
    sun.rotation_euler = (rad(55), 0, rad(25)); sc.collection.objects.link(sun)
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
    cam.data.lens = 50; cam.data.clip_end = 5000
    # floor + door-edge reference
    bpy.ops.mesh.primitive_plane_add(size=900, location=(0, 0, 0))
    return cam


def render_views(cam, name, frames):
    import tempfile
    tiles = []
    views = (((0.9, -1, 0.12), "q"), ((1, 0.02, 0.05), "s"))
    for f in frames:
        sc.frame_set(f)
        for d, tag in views:
            dv = Vector(d).normalized()
            tgt = Vector((0, 20, 120))
            cam.location = tgt + dv * 620
            cam.rotation_euler = (tgt - cam.location).to_track_quat("-Z", "Y").to_euler()
            sc.render.resolution_x = 420; sc.render.resolution_y = 520
            p = os.path.join(OUT, "preview", "_%s_%03d_%s.png" % (name, f, tag))
            sc.render.filepath = p
            bpy.ops.render.render(write_still=True)
            tiles.append(p)
    return tiles


if "mesh" in WANT or "all" in WANT:
    reset_pose(); upd()
    export_fbx(os.path.join(OUT, "SK_Her.fbx"), True, False)
    print("HER wrote SK_Her.fbx")

cam = setup_preview() if PREVIEW else None
os.makedirs(os.path.join(OUT, "preview"), exist_ok=True)
tiles_all = {}
for name, (fn, secs, loop, speed) in CLIPS.items():
    if "all" not in WANT and name not in WANT:
        continue
    n = int(round(secs * FPS))
    act = bpy.data.actions.new("A_Her_" + name)
    arm.animation_data_create(); arm.animation_data.action = act
    sc.frame_start, sc.frame_end = 0, n
    prev = {}
    for f in range(n + 1):
        t = (f % n if loop else f) / FPS
        reset_pose(); upd()
        fn(t)
        upd()
        for pb in P:
            q = pb.rotation_quaternion.copy()
            if pb.name in prev and prev[pb.name].dot(q) < 0:
                q.negate(); pb.rotation_quaternion = q
            prev[pb.name] = q
            pb.keyframe_insert("rotation_quaternion", frame=f)
        P["Hips"].keyframe_insert("location", frame=f)
    info["clips"][name] = {"seconds": secs, "loop": loop, "speed": speed, "frames": n}
    export_fbx(os.path.join(OUT, "A_Her_%s.fbx" % name), False, True)
    print("HER clip", name, n, "frames, speed", round(speed, 1))
    if PREVIEW:
        fr = [0, n // 4, n // 2, (3 * n) // 4] if loop and speed > 0 else [0, n // 2, n]
        tiles_all[name] = render_views(cam, name, fr)

json.dump(info, open(os.path.join(OUT, "her_info.json"), "w"), indent=1)
json.dump(tiles_all, open(os.path.join(OUT, "preview", "tiles.json"), "w"))
print("HER done")
