"""Trailer camera moves for -WCFloat (WCAuto.cpp).  Writes float.txt (the moves) and float_stills.txt (start and end frame of
each, for -WCShotFile) next to the given path.  Coordinates: x, y, z (actor height: 92 ground floor, 442 upstairs, 792 attic,
-258 cellar; the eye is 66 cm higher), yaw (0 = +X, 90 = +Y), pitch.  Cheyenne, 2026-11-24: floating shots of the house, the
cellar and the props; no scares and no Edith."""
import sys, os

SHOTS = [
    # name, start, end, seconds, options
    ("hall_push",      (100, -100, 92, 0, -4),     (600, -100, 92, 0, -2),     9),
    ("piano",          (450, -300, 92, -160, -10), (320, -360, 92, -172, -8),  8),
    ("dining_table",   (720, 260, 92, 150, -22),   (640, 300, 92, 165, -18),   8),
    ("kitchen",        (880, 270, 92, 40, -14),    (1040, 320, 92, 55, -12),   8),
    ("sitting_drawings", (1300, -300, 92, -160, -6), (1050, -420, 92, -175, -4), 8),
    ("sickroom",       (2080, 260, 92, 40, -14),   (2240, 320, 92, 50, -12),   8),
    ("den",            (1700, -260, 92, -40, -10), (1880, -330, 92, -50, -8),  8),
        ("kids_room",      (700, -270, 442, -160, -16), (560, -330, 442, -170, -12), 8),
    ("master",         (700, 270, 442, 160, -14),  (560, 330, 442, 170, -10),  8),
    ("prayer_altar",   (950, 280, 442, 40, -14),   (1060, 360, 442, 70, -12),  8),
    ("attic",          (900, -200, 792, 120, -10), (700, -100, 792, 108, -8),  9),
    ("cellar",         (300, 0, -258, 0, -6),      (700, 0, -258, 0, -4),      9),
    ("cellar_jars",    (900, 40, -258, 70, -12),   (1000, 80, -258, 60, -10),  7),
]

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    f = lambda p: ",".join(str(v) for v in p)
    with open(os.path.join(out, "float.txt"), "w", encoding="utf-8") as fh:
        for s in SHOTS:
            fh.write(f"{s[0]}|{f(s[1])}|{f(s[2])}|{s[3]}" + (f"|{s[4]}" if len(s) > 4 else "") + "\n")
    with open(os.path.join(out, "float_stills.txt"), "w", encoding="utf-8") as fh:
        for s in SHOTS:
            fh.write(f"{s[0]}_a|{f(s[1])}\n{s[0]}_b|{f(s[2])}\n")
    print(len(SHOTS), "shots")
