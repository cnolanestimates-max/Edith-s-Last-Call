# Pass 119c: the eye-side keys were measured from her_info's "eye_centre", which the sphere fit put on the side of her
# nose.  The game's own numbers (WCEntity.h EyeRef / EyeRadius) are right: centre (6.0, -21.9, 246.6), radius 4.3.
# Brow keys now sit above the ball, the lid keys ride its rim, and a real BrowDown is added (the old "Brow" pulls the
# lower lid and stays as it is, because that is the look that has been in the game).  Twenty keys.
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from patchlib import edit

B = r"C:\GameDev\Unreal\WellnessCheck\Scripts\her\build_her.py"
edit(B, [
    ("""EYE_X = float(ecen[0])
FACE_KEYS = {"Scream": sk_scream, "Sneer": sk_sneer, "Brow": sk_brow}
""",
     """EX, EYF, EZ, ER = 6.0, -21.9, 246.6, 4.3          # her eye as the game has it (WCEntity.h EyeRef, EyeRadius): the fit above lands on her nose
FACE_KEYS = {"Scream": sk_scream, "Sneer": sk_sneer, "Brow": sk_brow}
"""),
    ("""def _brow_w(x, z):
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
""",
     """def _brow_w(x, z):
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
"""),
    ("""def _k_browknit(x, y, z, f):
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
""",
     """def _k_browknit(x, y, z, f):
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
"""),
    ("""    return sstep(3.5, 6.0, a) * (1.0 - sstep(8.5, 11.5, a)) * sstep(LIP_Z - 7.0, LIP_Z - 3.0, z) * (1.0 - sstep(EYE_Z - 3.5, EYE_Z - 0.5, z)) * (1.0 - sstep(-16.0, -11.0, y))


def _k_stretch""",
     """    return sstep(3.5, 6.0, a) * (1.0 - sstep(8.5, 11.5, a)) * sstep(LIP_Z - 7.0, LIP_Z - 3.0, z) * (1.0 - sstep(237.0, 241.0, z)) * (1.0 - sstep(-16.0, -11.0, y))


def _k_stretch"""),
    ("""    w = sstep(3.5, 6.0, a) * (1.0 - sstep(8.5, 11.5, a)) * sstep(LIP_Z - 7.0, LIP_Z - 3.0, z) * (1.0 - sstep(EYE_Z - 3.5, EYE_Z - 0.5, z)) * (1.0 - sstep(-16.0, -11.0, y))
    return (-x * 0.10 * w, 1.6 * w, 0.0)
""",
     """    w = sstep(3.5, 6.0, a) * (1.0 - sstep(8.5, 11.5, a)) * sstep(LIP_Z - 7.0, LIP_Z - 3.0, z) * (1.0 - sstep(237.0, 241.0, z)) * (1.0 - sstep(-16.0, -11.0, y))
    return (-x * 0.10 * w, 1.6 * w, 0.0)
"""),
    ("""for _nm, _fn in (("BrowUp", _k_browup), ("BrowKnit", _k_browknit), ("EyeWide", _k_eyewide),""",
     """for _nm, _fn in (("BrowUp", _k_browup), ("BrowKnit", _k_browknit), ("BrowDown", _k_browdown), ("EyeWide", _k_eyewide),"""),
    ("""        if y > -11.0 or z < LIP_Z - 28.0 or z > EYE_Z + 12.0:
            continue""",
     """        if y > -11.0 or z < LIP_Z - 32.0 or z > EZ + 16.0:
            continue"""),
    ("""    "snarl": {"Snarl": 1.0, "Sneer": 0.8, "SneerR": 0.55, "BrowKnit": 0.8, "Brow": 0.5, "JawSide": 0.35, "Scream": 0.18},
    "rage": {"Scream": 0.7, "BrowKnit": 1.0, "Brow": 0.6, "Snarl": 1.0, "EyeWide": 1.0, "Stretch": 0.45, "CheekRaise": 0.5},
    "scream": {"Scream": 1.0, "Unhinge": 1.0, "Stretch": 1.0, "BrowKnit": 0.8, "Snarl": 0.8, "EyeWide": 1.0, "CheekSuck": 0.5},
    "wince": {"CheekL": 1.0, "Sneer": 0.8, "Squint": 0.7, "JawSide": 0.5, "BrowKnit": 0.5},
    "grief": {"BrowUp": 1.0, "BrowKnit": 0.5, "Frown": 1.0, "Squint": 0.45, "Scream": 0.14, "CheekSuck": 0.4},
""",
     """    "snarl": {"Snarl": 1.0, "Sneer": 0.8, "SneerR": 0.55, "BrowKnit": 0.8, "BrowDown": 0.7, "JawSide": 0.35, "Scream": 0.18},
    "rage": {"Scream": 0.7, "BrowKnit": 1.0, "BrowDown": 0.8, "Snarl": 1.0, "Stretch": 0.45, "CheekRaise": 0.5},
    "scream": {"Scream": 1.0, "Unhinge": 1.0, "Stretch": 1.0, "BrowKnit": 0.8, "Snarl": 0.8, "EyeWide": 1.0, "CheekSuck": 0.5},
    "wince": {"CheekL": 1.0, "Sneer": 0.8, "Squint": 0.7, "JawSide": 0.5, "BrowKnit": 0.5},
    "grief": {"BrowUp": 1.0, "BrowKnit": 0.5, "Frown": 1.0, "Squint": 0.45, "Scream": 0.14, "CheekSuck": 0.4, "Brow": 0.6},
"""),
    # the preview: the ball the game puts in her socket, a wider frame, absolute paths
    ("""    _tgt = Vector((0.5, -14.0, 236.5))
    _dir_out = os.path.join(OUT, "preview", "face")
    os.makedirs(_dir_out, exist_ok=True)
""",
     """    _tgt = Vector((1.5, -14.0, 237.5))
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
"""),
    ("""        _cam.location = _tgt + Vector(_d).normalized() * 78
""",
     """        _cam.location = _tgt + Vector(_d).normalized() * 108
"""),
])
print("pass 119c applied")
