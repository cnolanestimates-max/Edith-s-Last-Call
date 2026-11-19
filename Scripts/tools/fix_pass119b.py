# Pass 119b (Cheyenne, 20:18 UTC: "i want her cheeks to get controls so when she screams her mouth opens like down and wide
# as hell").  Five more keys: Stretch (mouth and cheeks pulled wide), Unhinge (the jaw goes on down past the scream),
# CheekL, CheekR (each cheek by itself), CheekRaise.  Nineteen in all.
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from patchlib import edit

B = r"C:\GameDev\Unreal\WellnessCheck\Scripts\her\build_her.py"
edit(B, [
    ("""for _nm, _fn in (("BrowUp", _k_browup), ("BrowKnit", _k_browknit), ("EyeWide", _k_eyewide), ("Squint", _k_squint), ("Snarl", _k_snarl),
                 ("SneerR", _k_sneer_r), ("Grin", _k_grin), ("Frown", _k_frown), ("JawSide", _k_jawside), ("Pucker", _k_pucker), ("CheekSuck", _k_cheeksuck)):
    face_key(_nm, _fn)
""",
     """def _cheek_w(x, y, z):
    a = abs(x)
    return sstep(3.5, 6.0, a) * (1.0 - sstep(8.5, 11.5, a)) * sstep(LIP_Z - 7.0, LIP_Z - 3.0, z) * (1.0 - sstep(EYE_Z - 3.5, EYE_Z - 0.5, z)) * (1.0 - sstep(-16.0, -11.0, y))


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


for _nm, _fn in (("BrowUp", _k_browup), ("BrowKnit", _k_browknit), ("EyeWide", _k_eyewide), ("Squint", _k_squint), ("Snarl", _k_snarl),
                 ("SneerR", _k_sneer_r), ("Grin", _k_grin), ("Frown", _k_frown), ("JawSide", _k_jawside), ("Pucker", _k_pucker), ("CheekSuck", _k_cheeksuck),
                 ("Stretch", _k_stretch), ("Unhinge", _k_unhinge), ("CheekL", _k_cheek_l), ("CheekR", _k_cheek_r), ("CheekRaise", _k_cheekraise)):
    face_key(_nm, _fn)
"""),
    ("""    "rage": {"Scream": 1.0, "BrowKnit": 1.0, "Brow": 0.6, "Snarl": 1.0, "EyeWide": 1.0, "Grin": 0.45},
""",
     """    "rage": {"Scream": 0.7, "BrowKnit": 1.0, "Brow": 0.6, "Snarl": 1.0, "EyeWide": 1.0, "Stretch": 0.45, "CheekRaise": 0.5},
    "scream": {"Scream": 1.0, "Unhinge": 1.0, "Stretch": 1.0, "BrowKnit": 0.8, "Snarl": 0.8, "EyeWide": 1.0, "CheekSuck": 0.5},
    "wince": {"CheekL": 1.0, "Sneer": 0.8, "Squint": 0.7, "JawSide": 0.5, "BrowKnit": 0.5},
"""),
])
print("pass 119b applied")
