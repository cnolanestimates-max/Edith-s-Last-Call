"""Pass 103a: the rag doll (models), added to the item art script.
Cheyenne 2026-11-19 15:59 UTC: "you inspect them and turn them over ... and bam a different item is inside them ... on the back of
the toy there could be a slit and inside will be a key the player needs"."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit

R = "C:/GameDev/Unreal/WellnessCheck/"
edit(R + "Scripts/art/build_items_fine.py", [
    ('''MATS = {"Brass": m_brass,''', '''def m_cloth(g):
    """Unbleached muslin, grubby from years in a small pair of hands and then years in a duct."""
    weave = g.math("MULTIPLY", g.wave(4200.0, 0.0, 0.0, "X"), g.wave(4200.0, 0.0, 0.0, "Y"))
    c = g.mix((0.40, 0.34, 0.24), (0.27, 0.22, 0.15), g.ramp(weave, 0.1, 0.6))
    worn(g, (0.40, 0.34, 0.24), 0.0, 0.9, col=c, tarnish=(0.13, 0.095, 0.055), tarn=0.8, bright=(0.45, 0.40, 0.30), edges=0.15, scratch=0.0, aod=0.006, dirty=0.85,
         ns=160.0, bump=0.5, tarn_lo=0.42, tarn_hi=0.62)


def m_dress(g):
    """Faded blue calico with a small pale sprig."""
    dots = g.ramp(g.cells(520.0, feature="F1"), 0.10, 0.17, 1.0, 0.0)
    c = g.mix((0.065, 0.095, 0.165), (0.33, 0.32, 0.27), dots)
    c = g.mix(c, (0.10, 0.12, 0.16), g.ramp(g.wave(3600.0, 0.0, 0.0, "X"), 0.3, 0.7, 0.0, 0.35))
    worn(g, (0.07, 0.10, 0.17), 0.0, 0.9, col=c, tarnish=(0.10, 0.09, 0.07), tarn=0.75, bright=(0.20, 0.22, 0.26), edges=0.3, scratch=0.0, aod=0.006, dirty=0.85,
         ns=160.0, bump=0.5, tarn_lo=0.44, tarn_hi=0.62)


def m_yarn(g):
    ply = g.wave(2600.0, 1.5, 1.0, "X")
    c = g.mix((0.17, 0.055, 0.02), (0.06, 0.018, 0.008), g.ramp(ply, 0.3, 0.7))
    c = g.mix(c, (0.03, 0.02, 0.012), g.ramp(g.ao(0.004), 0.9, 0.4, 0.0, 0.8))
    g.finish(c, 0.95, 0.0, ply, 0.7)


def m_thread(g):
    g.finish(g.mix((0.24, 0.02, 0.02), (0.10, 0.01, 0.01), g.ramp(g.noise(900.0, 3.0), 0.3, 0.7)), 0.8, 0.0)


def m_stuffing(g):
    c = g.mix((0.46, 0.44, 0.38), (0.26, 0.24, 0.19), g.ramp(g.noise(900.0, 4.0), 0.3, 0.7))
    g.finish(c, 1.0, 0.0, g.noise(1500.0, 4.0), 0.9)


MATS = {"Cloth": m_cloth, "Dress": m_dress, "Yarn": m_yarn, "Thread": m_thread, "Stuffing": m_stuffing, "Brass": m_brass,'''),
    ('''def vent_cover_flat():''', '''def doll(empty=False):
    # Ruth's rag doll, lying on her back with her head toward +X: muslin, a faded calico dress, wool hair in two plaits, one
    # button eye gone.  The seam down her back has been cut and sewn up again; the small key is inside (empty: it has been taken).
    hc, hr = Vector((0.052, 0.0, 0.0125)), (0.0190, 0.0180, 0.0118)

    def hz(x, y, lift=0.0003):                                  # the height of the face at (x, y)
        k = 1.0 - ((x - hc.x) / hr[0]) ** 2 - (y / hr[1]) ** 2
        return hc.z + hr[2] * math.sqrt(max(k, 0.0)) + lift
    dp = [(0.034, 0.0105), (0.030, 0.0150), (0.018, 0.0225), (0.000, 0.0265), (-0.020, 0.0315), (-0.036, 0.0370), (-0.038, 0.0375)]

    def dr(x):                                                  # the dress's radius at x
        for (xa, ra), (xb, rb) in zip(dp, dp[1:]):
            if xb <= x <= xa:
                return ra + (rb - ra) * (xa - x) / (xa - xb)
        return dp[-1][1]

    def bz(x, y=0.0):                                           # the height of her back (the underside) at x
        r = dr(x)
        return 0.0125 - 0.36 * math.sqrt(max(r * r - y * y, 0.0))
    P = [sphere(hr[0], tuple(hc), "Cloth", 32, 16, (1.0, hr[1] / hr[0], hr[2] / hr[0]))]
    P.append(sphere(0.0200, (0.010, 0, 0.0120), "Cloth", 32, 16, (1.55, 0.95, 0.55)))
    dress = lathe(dp, "Dress", 44, lambda a, x: 1.0 + 0.05 * math.cos(9 * a) * max(0.0, min(1.0, (0.02 - x) / 0.05)))
    for v in dress.data.vertices:
        v.co.z *= 0.36
    P.append(moved(dress, (0, 0, 0.0125)))
    P.append(tube([(0.0335, 0.0105 * math.cos(a), 0.0125 + 0.0105 * 0.40 * math.sin(a)) for a in [2 * PI * k / 24 for k in range(24)]], 0.0011, "Thread", True, 3))     # the collar
    for sy in (-1, 1):
        P.append(tube([(0.030, sy * 0.012, 0.0125), (0.026, sy * 0.028, 0.0125), (0.010, sy * 0.040, 0.0115), (-0.010, sy * 0.043, 0.0105)], 0.0058, "Cloth", False, 5))
        P.append(sphere(0.0068, (-0.0125, sy * 0.0432, 0.0105), "Cloth", 16, 8, (1.2, 1.0, 0.8)))
        P.append(tube([(0.0295, sy * 0.0135, 0.0125), (0.027, sy * 0.022, 0.0125), (0.020, sy * 0.031, 0.0120)], 0.0074, "Dress", False, 5))                              # the sleeve
        P.append(tube([(-0.030, sy * 0.011, 0.0125), (-0.055, sy * 0.014, 0.0120), (-0.078, sy * 0.016, 0.0115)], 0.0066, "Cloth", False, 5))
        P.append(sphere(0.0078, (-0.0815, sy * 0.0165, 0.0128), "Polymer", 16, 8, (1.05, 0.9, 1.3)))                                                                    # a felt shoe
        # a plait
        pl = [(0.047 - 0.036 * u, sy * (0.0175 + 0.014 * u) + 0.0016 * math.sin(u * 22.0), 0.0150 - 0.004 * u + 0.0016 * math.cos(u * 22.0)) for u in [k / 30.0 for k in range(31)]]
        P.append(tube(pl, 0.0031, "Yarn", False, 4))
        P.append(torus(0.0036, 0.0010, pl[-3], (0, PI / 2, 0.5 * sy), "Thread", 16, 6))
        P.append(sphere(0.0036, pl[-1], "Yarn", 12, 6, (1.6, 1, 1)))
    for k in range(13):                                         # wool over the crown
        b = math.radians(-78 + 156 * k / 12)
        st = []
        for j in range(15):
            th = math.radians(-112 + 160 * j / 14)
            st.append((hc.x + hr[0] * 1.05 * math.cos(th), hc.y + hr[1] * 1.05 * math.sin(th) * math.sin(b), hc.z + hr[2] * 1.07 * math.sin(th) * math.cos(b)))
        P.append(tube(st, 0.0017, "Yarn", False, 3))
    # her face: one black button on its threads, the other gone (two loose ends), a stitched mouth
    ex, ey = 0.0565, 0.0068
    P.append(cyl(0.0036, 0.0011, (ex, ey, hz(ex, ey, 0.0006)), (0.25, 0.12, 0), "Polymer", 20, bevel=0.0003))
    for a in (0.6, 2.2):
        P.append(tube([(ex + 0.0016 * math.cos(a), ey + 0.0016 * math.sin(a), hz(ex, ey, 0.0013)), (ex - 0.0016 * math.cos(a), ey - 0.0016 * math.sin(a), hz(ex, ey, 0.0013))], 0.00028, "Thread", False, 2))
    P.append(tube([(ex + 0.0010, -ey - 0.0020, hz(ex, -ey)), (ex, -ey, hz(ex, -ey, 0.0008)), (ex - 0.0030, -ey + 0.0012, hz(ex - 0.003, -ey + 0.0012, 0.0002))], 0.00028, "Thread", False, 2))
    P.append(tube([(ex - 0.0008, -ey + 0.0018, hz(ex, -ey)), (ex, -ey, hz(ex, -ey, 0.0009)), (ex + 0.0022, -ey - 0.0006, hz(ex, -ey, 0.0014))], 0.00028, "Thread", False, 2))
    mo = [(0.0468, -0.0062), (0.0452, -0.0034), (0.0446, 0.0), (0.0452, 0.0034), (0.0468, 0.0062)]
    P.append(tube([(x, y, hz(x, y)) for x, y in mo], 0.00042, "Thread", False, 3))
    for x, y in mo[1:-1]:
        P.append(tube([(x - 0.0012, y, hz(x - 0.0012, y)), (x + 0.0012, y, hz(x + 0.0012, y))], 0.00030, "Thread", False, 2))
    # the seam down her back
    x0, x1 = -0.020, 0.022
    wide = 0.0105 if empty else 0.0046
    seam = []
    for k in range(13):
        u = k / 12.0
        seam.append((x0 + (x1 - x0) * u, wide * math.sin(PI * u)))
    out = [(x, w / 2) for x, w in seam[1:12]] + [(x, -w / 2) for x, w in reversed(seam[1:12])]
    out = [(x0, 0.0)] + out[:11] + [(x1, 0.0)] + out[11:]
    sl = plate(out, 0.0004, "Black", z=0.0)
    for v in sl.data.vertices:
        v.co.z += bz(v.co.x, v.co.y) - 0.0005
    P.append(sl)
    for k in range(7):                                          # coarse stitches across it (cut, where the key came out)
        x = x0 + (x1 - x0) * (0.12 + 0.76 * k / 6.0)
        if empty and 1 <= k <= 4:
            for sy in (-1, 1):
                P.append(tube([(x, sy * 0.0075, bz(x, 0.0075) - 0.0004), (x + 0.0008, sy * 0.0052, bz(x, 0.005) - 0.0016), (x + 0.0022 * sy, sy * 0.0040, bz(x, 0.004) - 0.0030)], 0.00035, "String", False, 2))
        else:
            P.append(tube([(x - 0.0012, -0.0062, bz(x, 0.0062) - 0.0004), (x, 0.0, bz(x, 0.0) - (0.0011 if not empty else 0.0006)), (x + 0.0012, 0.0062, bz(x, 0.0062) - 0.0004)], 0.00035, "String", False, 2))
    if not empty:
        P.append(torus(0.0040, 0.0009, (0.001, 0, bz(0.001) + 0.0012), (PI / 2, 0, 0.35), "Brass", 28, 8))                                                               # the bow of the key, showing
    else:
        for (dx, dy, r) in ((-0.008, 0.001, 0.0046), (0.000, -0.0012, 0.0052), (0.008, 0.0008, 0.0044), (0.004, 0.0022, 0.0034)):
            P.append(sphere(r, (dx, dy, bz(dx) + r * 0.45), "Stuffing", 14, 8, (1.2, 0.9, 0.8)))
    return P


def vent_cover_flat():'''),
    ('''    if frame and cover:
        P.append(box(0.034, 0.006, 0.004, (0.03, -0.016, 0.037), m="Brass"))
    return P''', '''    if frame and cover:
        # what can be made out behind the slats: something pale, pushed in, with one black button
        P.append(sphere(0.019, (0.061, -0.0135, 0.079), "Cloth", 20, 10, (1.0, 0.55, 0.95)))
        P.append(sphere(0.020, (0.010, -0.0125, 0.079), "Cloth", 20, 10, (2.6, 0.5, 1.5)))
        P.append(cyl(0.0036, 0.0011, (0.066, -0.0245, 0.072), (PI / 2, 0, 0), "Polymer", 16))
    return P'''),
    ('''build("KeyHeart", key_heart)''', '''build("Doll", doll)
build("DollEmpty", lambda: doll(True))
build("KeyHeart", key_heart)'''),
])
print("pass 103a applied")
