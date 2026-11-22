# The tipped drum and its spill by the back of the house (Cheyenne, 2026-11-21: "there's a barrel that's knocked over right
# outside of the shed, that has some liquid on the ground, but it looks like shit and needs attention").
# A 55-gallon steel drum, painted once and rusted through, dented where it fell, the small bung gone; and what came out of
# it: old motor oil gone to a black tar at the middle of the pool, thinning to a brown stain, soaked into the dirt round it.
# Exec'd by build_items_fine.py after trash_models.py (uses blob, puddle, sheet from there).
from mathutils import noise as mnoise


def m_drum(g):
    # navy enamel gone chalky, worn to rust along the chimes and hoops and in broad blooms where water sat; streaks of rust
    # run down from the hoops along the staves (the drum stood for years before it went over)
    big = g.noise(6.0, 5.0, 0.6)
    fine = g.noise(160.0, 5.0)
    streak = g.noise(1.0, 3.0, vec=g.mapping(scale=(3.0, 40.0, 40.0)))           # long along the drum's axis (X), thin round it
    paint = g.mix((0.008, 0.014, 0.022), (0.014, 0.02, 0.028), g.ramp(g.noise(25.0, 3.0), 0.3, 0.7))
    paint = g.mix(paint, (0.035, 0.035, 0.034), g.math("MULTIPLY", g.ramp(fine, 0.55, 0.8), 0.4))     # chalking
    rust = g.mix((0.075, 0.03, 0.012), (0.03, 0.014, 0.007), g.ramp(fine, 0.3, 0.75))
    a = g.ao(0.02)
    gone = g.ramp(big, 0.46, 0.58)
    gone = g.math("MAXIMUM", gone, g.math("MULTIPLY", g.edge(0.006), 0.95))
    gone = g.math("MAXIMUM", gone, g.ramp(a, 0.82, 0.5))
    stain = g.math("MULTIPLY", g.ramp(streak, 0.52, 0.68), 0.8)
    c = g.mix(paint, rust, gone)
    c = g.mix(c, (0.05, 0.022, 0.01), stain)
    c = g.mix(c, (0.012, 0.01, 0.008), g.math("MULTIPLY", g.ramp(a, 0.95, 0.5), 0.8))
    c = g.mix(c, (0.02, 0.016, 0.011), g.math("MULTIPLY", g.ramp(g.noise(3.0, 4.0, vec=g.mapping(loc=(0.4, 0.1, 0.8))), 0.45, 0.7), 0.6))   # mud and grime in broad patches
    geo = g.N.new("ShaderNodeNewGeometry")
    sn = g.N.new("ShaderNodeSeparateXYZ")
    g.L.new(geo.outputs["Normal"], sn.inputs[0])
    under = g.ramp(sn.outputs[2], -0.2, -0.75)
    c = g.mix(c, (0.022, 0.017, 0.011), g.math("MULTIPLY", under, 0.9))           # the side it has lain on: mud
    r = g.math("ADD", g.mix(0.70, 0.9, gone), g.math("MULTIPLY", fine, 0.1))
    m = g.math("MULTIPLY", g.math("SUBTRACT", 1.0, g.math("MAXIMUM", gone, under)), 0.1)
    g.finish(c, r, m, g.math("ADD", g.math("MULTIPLY", gone, 0.7), g.math("MULTIPLY", fine, 0.25)), 0.8, 0.003)


def m_oil(g):
    # the pool: black and glassy where it is deep, a dull brown film at its edge, grit and needles in it
    big = g.noise(5.0, 3.0)
    grit = g.ramp(g.noise(320.0, 3.0), 0.68, 0.74)
    c = g.mix((0.006, 0.0045, 0.003), (0.035, 0.022, 0.012), g.ramp(big, 0.55, 0.75))
    c = g.mix(c, (0.06, 0.05, 0.035), grit)
    r = g.math("ADD", g.ramp(big, 0.5, 0.8, 0.02, 0.22), g.math("MULTIPLY", grit, 0.6))
    g.finish(c, r, 0.0, g.math("MULTIPLY", grit, 0.4), 0.3, 0.001)


def m_soaked(g):
    # the dirt round the pool, dark and wet with it, with pine needles and stones pressed in
    fine = g.noise(90.0, 5.0)
    stones = g.ramp(g.cells(28.0, feature="F1"), 0.18, 0.08)
    c = g.mix((0.03, 0.022, 0.015), (0.06, 0.045, 0.03), g.ramp(fine, 0.3, 0.7))
    c = g.mix(c, (0.13, 0.11, 0.09), g.math("MULTIPLY", stones, 0.8))
    needles = g.ramp(g.wave(70.0, 14.0, 2.0, "X", vec=g.mapping(rot=(0, 0, 0.6))), 0.88, 0.95)
    c = g.mix(c, (0.09, 0.05, 0.02), g.math("MULTIPLY", needles, 0.7))
    r = g.math("ADD", 0.30, g.math("MULTIPLY", fine, 0.3))
    g.finish(c, r, 0.0, g.math("ADD", g.math("MULTIPLY", stones, 0.8), g.math("MULTIPLY", fine, 0.4)), 0.8, 0.004)


def m_stone(g):
    big = g.noise(12.0, 5.0)
    c = g.mix((0.10, 0.095, 0.085), (0.22, 0.21, 0.19), g.ramp(big, 0.3, 0.7))
    c = g.mix(c, (0.04, 0.035, 0.03), g.math("MULTIPLY", g.ramp(g.ao(0.01), 0.9, 0.5), 0.7))
    g.finish(c, g.math("ADD", 0.6, g.math("MULTIPLY", big, 0.2)), 0.0, g.noise(80.0, 4.0), 0.6, 0.002)


MATS.update({"Drum": m_drum, "Oil": m_oil, "Soaked": m_soaked, "Stone": m_stone})


def oil_drum():
    # 55 US gallons: 0.572 m across the chimes, 0.851 m long; two rolling hoops, two chimes, a 2" and a 3/4" bung in one head
    R, L = 0.286, 0.851
    prof = [(0.0, 0.0), (0.0, R - 0.006), (0.004, R + 0.004), (0.012, R + 0.006), (0.018, R)]          # bottom head and chime
    for zc in (L / 3, 2 * L / 3):                                                                     # the rolling hoops
        prof += [(zc - 0.03, R), (zc - 0.012, R + 0.012), (zc + 0.012, R + 0.012), (zc + 0.03, R)]
    prof += [(L - 0.018, R), (L - 0.012, R + 0.006), (L - 0.004, R + 0.004), (L, R - 0.006), (L, 0.0)]
    body = lathe(prof, "Drum", 64)
    # dents: one big where it fell, and small ones from forty years of being kicked
    me = body.data
    for v in me.vertices:
        p = v.co
        rr = math.hypot(p.y, p.z)
        if rr < R * 0.7:
            continue
        a = math.atan2(p.z, p.y)
        d1 = max(0.0, 1.0 - math.hypot((p.x - 0.30) / 0.16, (a - 0.9) * R / 0.12)) ** 2 * 0.035
        d2 = 0.004 * mnoise.noise(Vector((p.x * 9, a * 3, 1.3)))
        k = (rr - d1 + d2) / rr
        p.y *= k; p.z *= k
    me.update()
    P = [moved(body, rot=(0, -PI / 2, 0))]                                                             # lathe is round X: stand it up
    for (bx, by, br) in ((0.15, 0.0, 0.03), (-0.17, 0.05, 0.016)):                                     # the bung flanges in the top head
        P.append(cyl(br + 0.008, 0.008, (bx, by, L + 0.002), m="Steel", v=20))
    P.append(cyl(0.022, 0.012, (-0.17, 0.05, L + 0.01), m="Drum", v=6))                                # the small cap still in
    P = moved(P, (0, 0, R + 0.012), (0, PI / 2, 0.0))                                                  # over on its side, the top head toward +X
    return P


def pool(R, m, seed, lump=0.008, sx=1.0, sy=1.0, seg=110, rings=12):
    """A pool of liquid: a soft-edged, slightly domed sheet whose outline wanders (more segments than puddle())."""
    verts, faces = [(0.0, 0.0, lump)], []
    for k in range(1, rings + 1):
        t = k / rings
        for i in range(seg):
            a = 2 * PI * i / seg
            ca, sa = math.cos(a), math.sin(a)
            e = 0.78 + 0.22 * mnoise.noise(Vector((ca * 1.3 + seed, sa * 1.3, seed))) + 0.08 * mnoise.noise(Vector((ca * 4.0, sa * 4.0 + seed, 3.0)))
            rr = R * e * t
            z = lump * (1.0 - t ** 3)
            verts.append((rr * ca * sx, rr * sa * sy, z))
    for i in range(seg):
        faces.append((0, 1 + i, 1 + (i + 1) % seg))
    for k in range(rings - 1):
        for i in range(seg):
            a_, b_ = 1 + k * seg + i, 1 + k * seg + (i + 1) % seg
            faces.append((a_, a_ + seg, b_ + seg, b_))
    ob = mesh(verts, faces, m)
    for f in ob.data.polygons:
        f.use_smooth = True
    return ob


def oil_spill():
    # the pool where it ran out of the open bung and spread on the packed dirt (the dark soaked ground round it is decals
    # in the level, so its edge is soft), a couple of outlying splashes, and needles and grit fallen into it
    P = [pool(0.72, "Oil", 3.0, 0.009, 1.18, 0.82)]
    for i, (x, y, r) in enumerate(((0.92, -0.30, 0.15), (0.98, 0.22, 0.10), (-0.70, 0.40, 0.09), (0.55, -0.55, 0.06))):
        s_ = pool(r, "Oil", 20.0 + i, 0.005, 1.0, 0.8, 48, 6)
        s_.location = (x, y, 0.0)
        _fin(s_, "Oil")
        P.append(s_)
    for i in range(30):
        a, d = random.uniform(0, 2 * PI), random.uniform(0.05, 0.95)
        x, y = d * math.cos(a) * 1.05, d * math.sin(a) * 0.75
        P.append(moved(cyl(0.0012, 0.06, (0, 0, 0), (0, PI / 2, 0), "WoodDark", 4), (x, y, 0.010), (0, 0, random.uniform(0, PI))))
    for i in range(7):
        a, d = random.uniform(0, 2 * PI), random.uniform(0.3, 0.8)
        P.append(blob(random.uniform(0.01, 0.022), "Stone", (d * math.cos(a), d * math.sin(a) * 0.7, 0.006), (1, 1, 0.6), 0.25, 3.0, i * 3.1, sub=2, sag=0.4))
    return P


for _n, _f in (("OilDrum", oil_drum), ("OilSpill", oil_spill)):
    build(_n, _f)
