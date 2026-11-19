# Pass 119 (Cheyenne, 20:16 UTC: "can we add more controls on her face again to make her more emotive, like if there's 10
# double it").  She had three face keys (Scream, Sneer, Brow).  This adds eleven: BrowUp, BrowKnit, EyeWide, Squint, Snarl,
# SneerR, Grin, Frown, JawSide, Pucker, CheekSuck; and a --faceshot preview of every key and of the moods built from them.
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from patchlib import edit

ROOT = r"C:\GameDev\Unreal\WellnessCheck"
B = ROOT + r"\Scripts\her\build_her.py"

edit(B, [
    ("""print("HER face: sneer verts", n_sneer, "brow verts", n_brow)
""",
     """print("HER face: sneer verts", n_sneer, "brow verts", n_brow)
# ------------------------------------------------------------------ MORE FACE: eleven further keys
# Everything is a soft push on a region of the face, measured from the mouth and from her one eye.  She is half as big
# again as a person, so a centimetre here is a small movement.
EYE_X = float(ecen[0])
FACE_KEYS = {"Scream": sk_scream, "Sneer": sk_sneer, "Brow": sk_brow}


def face_key(name, fn):
    \"\"\"fn(x, y, z, front) -> (dx, dy, dz) in cm or None.  front is 1 on the face and 0 by the ears.\"\"\"
    sk = mesh.shape_key_add(name=name, from_mix=False)
    n = 0
    for i, p in enumerate(co):
        x, y, z = float(p[0]), float(p[1]), float(p[2])
        if y > -11.0 or z < LIP_Z - 28.0 or z > EYE_Z + 12.0:
            continue
        d = fn(x, y, z, 1.0 - sstep(-19.0, -14.0, y))
        if d and abs(d[0]) + abs(d[1]) + abs(d[2]) > 0.02:
            sk.data[i].co = inv_ @ Vector((x + d[0], y + d[1], z + d[2]))
            n += 1
    FACE_KEYS[name] = sk
    print("HER face key", name, n, "verts")
    return sk


def _brow_w(x, z):
    bz = z - (EYE_Z + 1.6)
    if bz < 0.0 or bz > 8.0:
        return 0.0
    return sstep(0.0, 1.2, bz) * (1.0 - sstep(3.5, 8.0, bz)) * (1.0 - sstep(7.0, 11.0, abs(x)))


def _eye_ring(x, z):
    r = math.hypot(x - EYE_X, z - EYE_Z)
    if r < 1.4 or r > 5.5:
        return 0.0, 0.0, 0.0
    w = sstep(1.4, 2.2, r) * (1.0 - sstep(3.0, 5.5, r))
    return w, (x - EYE_X) / r, (z - EYE_Z) / r


def _corner_w(x, z):
    a, u = abs(x - MOUTH_X), abs(z - LIP_Z)
    return sstep(2.0, 4.4, a) * (1.0 - sstep(6.5, 11.0, a)) * (1.0 - sstep(1.5, 5.5, u))


def _k_browup(x, y, z, f):
    w = _brow_w(x, z) * f
    return (0.0, -0.3 * w, 2.6 * w)


def _k_browknit(x, y, z, f):
    w = _brow_w(x, z) * f
    inner = 1.0 - sstep(1.5, 7.0, abs(x))
    return (-x * 0.28 * w, -1.0 * w * inner, -1.6 * w * inner)


def _k_eyewide(x, y, z, f):
    w, rx, rz = _eye_ring(x, z)
    w *= f
    return (1.0 * w * rx, 0.35 * w, 1.1 * w * rz)


def _k_squint(x, y, z, f):
    w, rx, rz = _eye_ring(x, z)
    w *= f
    return (-0.3 * w * rx, -1.0 * w, (-0.9 if rz > 0 else 1.4) * w * abs(rz))


def _k_snarl(x, y, z, f):
    sx = x - MOUTH_X
    w = sstep(LIP_Z + 0.6, LIP_Z + 2.0, z) * (1.0 - sstep(EYE_Z - 1.5, EYE_Z + 0.5, z)) * (1.0 - sstep(2.5, 5.0, abs(sx))) * f
    return (sx * 0.22 * w, -0.4 * w, 1.5 * w)


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
    w = sstep(3.5, 6.0, a) * (1.0 - sstep(8.5, 11.5, a)) * sstep(LIP_Z - 7.0, LIP_Z - 3.0, z) * (1.0 - sstep(EYE_Z - 3.5, EYE_Z - 0.5, z)) * (1.0 - sstep(-16.0, -11.0, y))
    return (-x * 0.10 * w, 1.6 * w, 0.0)


for _nm, _fn in (("BrowUp", _k_browup), ("BrowKnit", _k_browknit), ("EyeWide", _k_eyewide), ("Squint", _k_squint), ("Snarl", _k_snarl),
                 ("SneerR", _k_sneer_r), ("Grin", _k_grin), ("Frown", _k_frown), ("JawSide", _k_jawside), ("Pucker", _k_pucker), ("CheekSuck", _k_cheeksuck)):
    face_key(_nm, _fn)
# the faces the game makes out of them (the same table is in WCEntity.cpp: keep the two alike)
MOODS = {
    "rest": {},
    "watch": {"EyeWide": 0.8, "BrowUp": 0.35, "CheekSuck": 0.5},
    "grin": {"Grin": 1.0, "Squint": 0.6, "Sneer": 0.4, "SneerR": 0.4, "BrowUp": 0.25},
    "snarl": {"Snarl": 1.0, "Sneer": 0.8, "SneerR": 0.55, "BrowKnit": 0.8, "Brow": 0.5, "JawSide": 0.35, "Scream": 0.18},
    "rage": {"Scream": 1.0, "BrowKnit": 1.0, "Brow": 0.6, "Snarl": 1.0, "EyeWide": 1.0, "Grin": 0.45},
    "grief": {"BrowUp": 1.0, "BrowKnit": 0.5, "Frown": 1.0, "Squint": 0.45, "Scream": 0.14, "CheekSuck": 0.4},
    "hush": {"Pucker": 1.0, "BrowKnit": 0.4, "Squint": 0.3, "EyeWide": 0.2},
}
info["face_keys"] = sorted(FACE_KEYS)
"""),
    ("""if "--screamshot" in argv:
""",
     """if "--faceshot" in argv:
    # one close picture of every key at full, and of every mood, for a contact sheet
    sc.render.engine = "BLENDER_EEVEE_NEXT" if "BLENDER_EEVEE_NEXT" in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE"
    _w = bpy.data.worlds.new("w"); sc.world = _w; _w.use_nodes = True
    _w.node_tree.nodes["Background"].inputs[0].default_value = (0.3, 0.3, 0.32, 1)
    _sun = bpy.data.objects.new("sun", bpy.data.lights.new("sun", "SUN")); _sun.data.energy = 3
    _sun.rotation_euler = (math.radians(62), 0, math.radians(22)); sc.collection.objects.link(_sun)
    _cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(_cam); sc.camera = _cam
    _cam.data.lens = 85; _cam.data.clip_end = 5000
    sc.render.resolution_x = 640; sc.render.resolution_y = 640
    _tgt = Vector((0.5, -14.0, 236.5))
    _dir_out = os.path.join(OUT, "preview", "face")
    os.makedirs(_dir_out, exist_ok=True)
    _shots = [("00_rest", {})] + [(f"{i + 1:02d}_{n}", {n: 1.0}) for i, n in enumerate(sorted(FACE_KEYS))] + [(f"m{i}_{n}", v) for i, (n, v) in enumerate(MOODS.items()) if v]
    for _view, _d in (("f", (0.12, -1, 0.02)), ("q", (0.75, -1, 0.05))):
        _cam.location = _tgt + Vector(_d).normalized() * 78
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
"""),
])
print("pass 119 applied")
