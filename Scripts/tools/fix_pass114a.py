"""Pass 114a: models for the VHS tapes, the video recorder and the trash can (Cheyenne 2026-11-19 19:33 to 19:36 UTC)."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
p = "C:/GameDev/Unreal/WellnessCheck/Scripts/art/build_items_fine.py"
edit(p, [
    ('''def vent_cover_flat():''', '''def tape(title, sub):
    # a VHS cassette lying label up: black shell, two reel windows, a paper label written on by hand, the flap along the front
    W, D, H = 0.187, 0.103, 0.025
    P = [box(W, D, H, (0, 0, H / 2), m="Polymer", bevel=0.0015)]
    P.append(box(W - 0.006, 0.006, H - 0.004, (0, -D / 2 + 0.002, H / 2), m="Polymer", bevel=0.001))             # the flap
    for sx in (-1, 1):
        P.append(box(0.052, 0.034, 0.0006, (sx * 0.050, 0.004, H + 0.0002), m="Glass"))                         # reel windows
        P.append(cyl(0.013, 0.0012, (sx * 0.050, 0.004, H + 0.0004), m="Cream", v=24))
        for k in range(6):
            a = k * PI / 3
            P.append(box(0.004, 0.0015, 0.0014, (sx * 0.050 + 0.008 * math.cos(a), 0.004 + 0.008 * math.sin(a), H + 0.0006), (0, 0, a), "Polymer"))
    P.append(box(0.120, 0.022, 0.0005, (0, -0.032, H + 0.0002), m="Paper"))                                     # the label
    P.append(text(title, 0.0105, 0.0004, (0, -0.029, H + 0.0006), m="Ink", spacing=1.02))
    P.append(text(sub, 0.0058, 0.0004, (0, -0.0385, H + 0.0006), m="Ink", spacing=1.05))
    P.append(box(0.150, 0.0005, 0.016, (0, D / 2 + 0.0002, H / 2), m="Paper"))                                   # the spine label
    P.append(text(title, 0.0095, 0.0004, (0, D / 2 + 0.0006, H / 2), (PI / 2, 0, PI), "Ink"))
    for sx in (-1, 1):
        for sy in (-1, 1):
            P.append(cyl(0.0022, 0.0006, (sx * (W / 2 - 0.008), sy * (D / 2 - 0.008), H + 0.0002), m="Steel", v=10))
    return P


def vcr():
    # a top-loading video recorder of about 1984: a long dark box, the tape slot, a row of piano keys, a clock window
    W, D, H = 0.42, 0.30, 0.095
    P = [box(W, D, H, (0, 0, H / 2 + 0.006), m="Polymer", bevel=0.003)]
    for sx in (-1, 1):
        for sy in (-1, 1):
            P.append(cyl(0.012, 0.006, (sx * (W / 2 - 0.03), sy * (D / 2 - 0.03), 0.003), m="Polymer", v=16))
    P.append(box(W - 0.01, 0.004, 0.030, (0, -D / 2 - 0.001, 0.070), m="Steel", bevel=0.0008))                    # the brushed strip
    P.append(box(0.200, 0.006, 0.022, (-0.085, -D / 2 - 0.002, 0.070), m="Black"))                               # the tape slot
    P.append(box(0.196, 0.004, 0.019, (-0.085, -D / 2 - 0.0035, 0.0705), (0.12, 0, 0), "Polymer"))                # its flap
    P.append(box(0.070, 0.004, 0.018, (0.085, -D / 2 - 0.002, 0.070), m="Glass"))                                # the clock window
    P.append(text("12:00", 0.011, 0.0005, (0.085, -D / 2 - 0.0045, 0.070), (PI / 2, 0, 0), "Label"))
    for k in range(6):                                                                                            # piano keys
        P.append(box(0.026, 0.012, 0.010, (-0.155 + k * 0.031, -D / 2 - 0.004, 0.030), m="Cream" if k != 2 else "Label", bevel=0.001))
    for k in range(2):
        P.append(cyl(0.011, 0.012, (0.125 + k * 0.034, -D / 2 - 0.006, 0.032), (PI / 2, 0, 0), "Steel", 20, bevel=0.001))
    for k in range(9):                                                                                            # vents on the lid
        P.append(box(0.110, 0.004, 0.0015, (0.11, -0.09 + k * 0.022, H + 0.006), m="Black"))
    return P


def trashcan(down=False):
    # a galvanised steel trash can, dented, rust at the bottom rim.  Upright with its lid on, or on its side with the lid gone.
    def ribs(a, x):
        return 1.0 + 0.012 * math.cos(22 * a)
    body = lathe([(0.0, 0.215), (0.012, 0.222), (0.02, 0.215), (0.30, 0.238), (0.31, 0.244), (0.32, 0.238), (0.60, 0.262), (0.612, 0.270), (0.62, 0.262),
                  (0.62, 0.252), (0.03, 0.205), (0.03, 0.0)], "Steel", 44, ribs)
    P = [moved(body, rot=(0, -PI / 2, 0))]                                    # the lathe turns round X; stand it up
    for sx in (-1, 1):                                                        # the two drop handles
        P.append(tube([(sx * 0.262, -0.05, 0.47), (sx * 0.292, -0.05, 0.45), (sx * 0.292, 0.05, 0.45), (sx * 0.262, 0.05, 0.47)], 0.006, "Steel", False, 4))
    lid = [moved(lathe([(0.0, 0.285), (0.012, 0.290), (0.03, 0.280), (0.05, 0.20), (0.075, 0.06), (0.08, 0.0)], "Steel", 44), rot=(0, -PI / 2, 0))]
    lid.append(tube([(-0.05, 0, 0.076), (-0.05, 0, 0.105), (0.05, 0, 0.105), (0.05, 0, 0.076)], 0.007, "Steel", False, 4))
    if not down:
        P += moved(lid, (0, 0, 0.615))
        return P
    P = moved(P, (0, 0, 0.262), (PI / 2, 0, 0))                               # on its side, mouth toward -Y
    P += moved(lid, (0.34, -0.55, 0.0), (0.0, 0.10, 0.5))                     # the lid, rolled off
    return P


def vent_cover_flat():'''),
    ('''build("Doll", doll)''', '''build("Tape1", lambda: tape("Ruthie - bedtime", "Oct. 1991"))
build("Tape2", lambda: tape("Living room", "Thanksgiving 1991"))
build("Tape3", lambda: tape("Mother - porch", "Nov. 1991"))
build("VCR", vcr)
build("TrashCan", trashcan)
build("TrashCanDown", lambda: trashcan(True))
build("Doll", doll)'''),
])
print("pass 114a applied")
