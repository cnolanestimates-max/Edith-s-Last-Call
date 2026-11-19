# The bin at the back of the house and everything that comes out of it (Cheyenne, 2026-11-19 21:31 / 21:33 UTC: "a
# waste management type of trash can ... big ... a full bin strung all out, and it needs to be nasty: rotting meat and
# fruit, newspapers, all kinds and manner of nasty ... don't skimp").
# Run inside build_items_fine.py (exec'd at its end, so every helper and the bake are the same as for the items).
from mathutils import noise as mnoise


# ------------------------------------------------------------------------------------------------ materials
def m_bingreen(g):
    worn(g, (0.012, 0.045, 0.026), 0.0, 0.50, ns=70.0, tarnish=(0.045, 0.036, 0.022), tarn=0.85, bright=(0.06, 0.13, 0.09), edges=0.55, scratch=0.9, aod=0.02, er=0.004, bump=0.5, dust=0.7)


def m_bag(g):
    crease = g.noise(34.0, 5.0, 0.7)
    fine = g.noise(240.0, 4.0)
    c = g.mix((0.006, 0.006, 0.007), (0.032, 0.032, 0.036), g.ramp(crease, 0.45, 0.75))
    c = g.mix(c, (0.05, 0.04, 0.03), g.ramp(g.noise(9.0, 3.0), 0.62, 0.8, 0.0, 0.5))          # mud
    r = g.math("ADD", 0.16, g.math("MULTIPLY", fine, 0.25))
    g.finish(c, r, 0.0, g.math("ADD", crease, g.math("MULTIPLY", fine, 0.2)), 0.9, 0.004)


def m_meat(g):
    big = g.noise(20.0, 4.0)
    fine = g.noise(170.0, 5.0)
    mould = g.noise(38.0, 5.0, vec=g.mapping(loc=(0.3, 0.8, 0.1)))
    c = g.mix((0.10, 0.018, 0.016), (0.035, 0.014, 0.017), g.ramp(big, 0.35, 0.7))              # dark red to purple-black
    c = g.mix(c, (0.32, 0.26, 0.10), g.ramp(g.wave(26.0, 22.0, 4.0), 0.90, 0.97))               # threads of yellow fat
    c = g.mix(c, (0.09, 0.12, 0.06), g.ramp(mould, 0.52, 0.64))                                 # where it has turned green
    c = g.mix(c, (0.44, 0.46, 0.42), g.math("MULTIPLY", g.ramp(mould, 0.66, 0.74), g.ramp(fine, 0.38, 0.6)))   # white fur on that
    c = g.mix(c, (0.012, 0.008, 0.006), g.math("MULTIPLY", g.ramp(g.ao(0.02), 0.9, 0.4), 0.8))
    r = g.ramp(mould, 0.5, 0.7, 0.10, 0.7)
    g.finish(c, r, 0.0, g.math("ADD", g.math("MULTIPLY", big, 0.6), g.math("MULTIPLY", fine, 0.3)), 0.8, 0.004)


def m_bone(g):
    fine = g.noise(150.0, 4.0)
    c = g.mix((0.50, 0.44, 0.32), (0.26, 0.20, 0.12), g.ramp(g.noise(18.0, 4.0), 0.4, 0.7))
    c = g.mix(c, (0.10, 0.03, 0.025), g.ramp(g.noise(40.0, 3.0, vec=g.mapping(loc=(0.5, 0.1, 0.9))), 0.60, 0.72))      # what is still on it
    c = g.mix(c, (0.02, 0.015, 0.01), g.math("MULTIPLY", g.ramp(g.ao(0.01), 0.9, 0.45), 0.8))
    g.finish(c, g.math("ADD", 0.45, g.math("MULTIPLY", fine, 0.2)), 0.0, fine, 0.4, 0.001)


def m_fruit(g):
    big = g.noise(30.0, 4.0)
    fine = g.noise(220.0, 4.0)
    spot = g.noise(70.0, 4.0, vec=g.mapping(loc=(0.7, 0.2, 0.5)))
    skin = g.mix((0.15, 0.022, 0.015), (0.19, 0.13, 0.03), g.ramp(g.noise(9.0, 2.0), 0.42, 0.58))   # some were red, some yellow or orange
    c = g.mix(skin, (0.06, 0.03, 0.013), g.ramp(big, 0.36, 0.5))                                # brown where it has gone soft
    c = g.mix(c, (0.012, 0.01, 0.008), g.ramp(big, 0.56, 0.68))                                   # black where it has gone further
    c = g.mix(c, (0.05, 0.09, 0.075), g.math("MULTIPLY", g.ramp(spot, 0.55, 0.62), 0.8))           # blue-green mould
    c = g.mix(c, (0.30, 0.32, 0.30), g.math("MULTIPLY", g.ramp(spot, 0.64, 0.70), g.ramp(fine, 0.35, 0.6)))   # white in its middle
    r = g.ramp(big, 0.4, 0.7, 0.22, 0.75)
    g.finish(c, r, 0.0, g.math("SUBTRACT", fine, g.math("MULTIPLY", g.ramp(big, 0.42, 0.7), 2.0)), 0.7, 0.003)


def m_peel(g):
    c = g.mix((0.30, 0.24, 0.03), (0.02, 0.015, 0.01), g.ramp(g.noise(26.0, 4.0), 0.36, 0.55))
    g.finish(c, 0.5, 0.0, g.noise(160.0, 3.0), 0.4, 0.001)


def m_news(g):
    rows = g.ramp(g.wave(250.0, 0.0, 0.0, "Y"), 0.35, 0.55)                                       # lines of type
    cols = g.ramp(g.wave(21.0, 0.0, 0.0, "X"), 0.08, 0.14)                                        # the gutters between columns
    ink = g.math("MULTIPLY", g.math("MULTIPLY", rows, cols), g.ramp(g.noise(600.0, 2.0), 0.3, 0.6))
    head = g.math("MULTIPLY", g.ramp(g.wave(9.0, 0.0, 0.0, "Y", vec=g.mapping(loc=(0.0, 0.031, 0.0))), 0.86, 0.9), g.ramp(g.noise(55.0, 1.0), 0.42, 0.5))   # a headline or two
    paper = g.mix((0.46, 0.42, 0.33), (0.29, 0.24, 0.15), g.ramp(g.noise(8.0, 4.0), 0.4, 0.7))    # yellowed
    c = g.mix(paper, (0.05, 0.05, 0.05), g.math("MAXIMUM", g.math("MULTIPLY", ink, 0.85), head))
    c = g.mix(c, (0.06, 0.04, 0.02), g.ramp(g.noise(5.0, 3.0, vec=g.mapping(loc=(0.4, 0.4, 0.4))), 0.58, 0.74))   # wet through
    g.finish(c, 0.8, 0.0, g.noise(120.0, 3.0), 0.3, 0.001)


def m_glassbrown(g):
    c = g.mix((0.075, 0.032, 0.008), (0.03, 0.014, 0.004), g.ramp(g.noise(40.0, 3.0), 0.4, 0.7))
    c = g.mix(c, (0.10, 0.09, 0.07), g.ramp(g.noise(14.0, 4.0), 0.62, 0.8, 0.0, 0.6))             # dried mud
    g.finish(c, g.ramp(g.noise(14.0, 4.0), 0.62, 0.8, 0.07, 0.6), 0.0, None)


def m_slime(g):
    big = g.noise(14.0, 4.0)
    c = g.mix((0.035, 0.028, 0.012), (0.10, 0.085, 0.03), g.ramp(big, 0.35, 0.7))
    c = g.mix(c, (0.22, 0.20, 0.13), g.ramp(g.noise(90.0, 3.0), 0.70, 0.78))                      # grains of rice, or not rice
    g.finish(c, g.ramp(big, 0.3, 0.7, 0.20, 0.5), 0.0, g.math("ADD", big, g.noise(120.0, 3.0)), 0.7, 0.003)


def m_tinlabel(g):
    c = g.mix((0.16, 0.03, 0.025), (0.22, 0.19, 0.12), g.ramp(g.wave(60.0, 1.0, 1.0, "X"), 0.5, 0.52))
    c = g.mix(c, (0.17, 0.15, 0.11), g.ramp(g.noise(30.0, 4.0), 0.36, 0.56))                      # the paper coming away, the print gone
    c = g.mix(c, (0.09, 0.035, 0.015), g.ramp(g.noise(55.0, 3.0, vec=g.mapping(loc=(0.2, 0.2, 0.7))), 0.6, 0.72))       # rust bleeding through
    g.finish(c, 0.7, 0.0, g.noise(200.0, 3.0), 0.3, 0.001)


MATS.update({"BinGreen": m_bingreen, "Bag": m_bag, "Meat": m_meat, "Bone": m_bone, "Fruit": m_fruit, "Peel": m_peel, "News": m_news,
             "GlassBrown": m_glassbrown, "Slime": m_slime, "TinLabel": m_tinlabel})


# ------------------------------------------------------------------------------------------------ shapes
def blob(r, m, loc=(0, 0, 0), scale=(1, 1, 1), amp=0.25, freq=3.0, seed=0.0, sub=4, sag=0.0, rot=(0, 0, 0), flat=False):
    """A lump: a sphere pushed about by noise, flattened underneath where it lies."""
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=sub, radius=r, location=(0, 0, 0))
    ob = bpy.context.object
    off = Vector((seed * 3.1, seed * 1.7, seed * 0.9))
    for v in ob.data.vertices:
        p = v.co.copy()
        n = mnoise.noise(p * (freq / r) + off) + 0.5 * mnoise.noise(p * (freq * 2.3 / r) + off * 2.0)
        p = p * (1.0 + amp * n)
        p.x *= scale[0]; p.y *= scale[1]; p.z *= scale[2]
        if sag > 0.0 and p.z < 0.0:
            p.z *= 1.0 - sag
        v.co = p
    for f in ob.data.polygons:
        f.use_smooth = not flat
    ob.rotation_euler = rot
    ob.location = loc
    return _fin(ob, m)


def sheet(w, h, m, nx=22, ny=15, amp=0.012, seed=0.0, loc=(0, 0, 0), rot=(0, 0, 0), curl=0.0):
    """A sheet of paper lying where it fell: creased, a corner turned up."""
    verts, faces = [], []
    for j in range(ny + 1):
        for i in range(nx + 1):
            x, y = (i / nx - 0.5) * w, (j / ny - 0.5) * h
            z = amp * (mnoise.noise(Vector((x * 9.0 + seed, y * 9.0, seed))) + 0.5 * mnoise.noise(Vector((x * 30.0, y * 30.0 + seed, 1.0))))
            z += curl * max(0.0, (x / w + y / h)) ** 2 * w
            verts.append((x, y, z))
    for j in range(ny):
        for i in range(nx):
            a = j * (nx + 1) + i
            faces.append((a, a + 1, a + nx + 2, a + nx + 1))
    ob = mesh(verts, faces, m)
    for f in ob.data.polygons:
        f.use_smooth = True
    ob.rotation_euler = rot
    ob.location = loc
    return _fin(ob, m)


def puddle(R, m, seed=0.0, lump=0.012):
    verts, faces = [(0.0, 0.0, lump * 1.4)], []
    rings, seg = 7, 44
    for k in range(1, rings + 1):
        for s in range(seg):
            a = 2 * PI * s / seg
            edge_r = R * (0.72 + 0.34 * mnoise.noise(Vector((math.cos(a) * 1.6 + seed, math.sin(a) * 1.6, seed))) + 0.12 * mnoise.noise(Vector((math.cos(a) * 5.0, math.sin(a) * 5.0 + seed, 2.0))))
            rr = edge_r * k / rings
            z = lump * (1.0 - (k / rings) ** 2) * (1.0 + 0.9 * mnoise.noise(Vector((rr * math.cos(a) * 14.0, rr * math.sin(a) * 14.0, seed))))
            verts.append((rr * math.cos(a), rr * math.sin(a), max(0.0, z)))
    for s in range(seg):
        faces.append((0, 1 + s, 1 + (s + 1) % seg))
    for k in range(rings - 1):
        for s in range(seg):
            a, b = 1 + k * seg + s, 1 + k * seg + (s + 1) % seg
            faces.append((a, a + seg, b + seg, b))
    ob = mesh(verts, faces, m)
    for f in ob.data.polygons:
        f.use_smooth = True
    return ob


# ------------------------------------------------------------------------------------------------ the bin
def bigbin(down=False):
    # A ninety-six gallon wheeled cart, the kind the county hauler leaves: dark green, scuffed pale along every edge, mud
    # up the back of it.  Upright with the lid shut; or over on its front with the lid thrown open on the ground.
    H, bx, by, tx, ty, th = 0.98, 0.25, 0.29, 0.31, 0.37, 0.012

    def ring(hx, hy, z):
        return [(-hx, -hy, z), (hx, -hy, z), (hx, hy, z), (-hx, hy, z)]
    v = ring(bx, by, 0.06) + ring(tx, ty, H) + ring(tx - th, ty - th, H) + ring(bx - th, by - th, 0.06 + th)
    f = [(0, 1, 2, 3), (12, 13, 14, 15)]
    for k in range(4):
        a, b = k, (k + 1) % 4
        f += [(a, b, 4 + b, 4 + a), (4 + a, 4 + b, 8 + b, 8 + a), (8 + a, 8 + b, 12 + b, 12 + a)]
    body = mesh(v, f, "BinGreen")
    bev(body, 0.014, 2, 40.0)
    P = [body]
    lean = math.atan2(ty - by, H - 0.06)
    for sy_, ang in ((-1, lean), (1, -lean)):                                 # a thick lip round the top, front and back
        P.append(box(2 * tx + 0.05, 0.035, 0.04, (0, sy_ * (ty + 0.012), H - 0.022), m="BinGreen", bevel=0.008))
    for sx_ in (-1, 1):
        P.append(box(0.035, 2 * ty + 0.05, 0.04, (sx_ * (tx + 0.012), 0, H - 0.022), m="BinGreen", bevel=0.008))
        for yy in (-0.16, 0.0, 0.16):                                         # moulded ribs down the sides
            P.append(box(0.014, 0.05, 0.62, (sx_ * ((bx + tx) / 2 + 0.004), yy, 0.52), (0, -sx_ * math.atan2(tx - bx, H - 0.06), 0), "BinGreen", 0.004))
    for xx in (-0.15, 0.0, 0.15):                                             # and down the front
        P.append(box(0.05, 0.014, 0.62, (xx, -((by + ty) / 2 + 0.004), 0.52), (lean, 0, 0), "BinGreen", 0.004))
    P.append(box(0.20, 0.004, 0.12, (0.0, -((by + ty) / 2 + 0.013) - 0.012, 0.70), (lean, 0, 0), "Label"))    # the hauler's sticker, what is left of it
    for sx_ in (-1, 1):                                                       # two wheels on a steel axle at the back, two feet at the front
        P.append(cyl(0.105, 0.06, (sx_ * (bx + 0.045), by - 0.03, 0.105), (0, PI / 2, 0), "Black", 28, bevel=0.012))
        P.append(cyl(0.042, 0.066, (sx_ * (bx + 0.045), by - 0.03, 0.105), (0, PI / 2, 0), "Steel", 16))
        P.append(box(0.07, 0.06, 0.06, (sx_ * 0.15, -by + 0.05, 0.03), m="BinGreen", bevel=0.006))
    P.append(cyl(0.012, 2 * (bx + 0.07), (0, by - 0.03, 0.105), (0, PI / 2, 0), "Steel", 12))
    P.append(tube([(-0.22, ty + 0.01, H - 0.03), (-0.22, ty + 0.10, H - 0.005), (0.22, ty + 0.10, H - 0.005), (0.22, ty + 0.01, H - 0.03)], 0.014, "BinGreen", False, 4))
    lid = [box(2 * tx + 0.06, 2 * ty + 0.07, 0.03, (0, 0, 0.015), m="BinGreen", bevel=0.012),
           box(2 * tx - 0.10, 2 * ty - 0.12, 0.022, (0, -0.01, 0.036), m="BinGreen", bevel=0.01),
           box(0.16, 0.03, 0.03, (0, -(ty + 0.03), 0.02), m="BinGreen", bevel=0.008)]
    for xx in (-0.2, 0.2):
        lid.append(cyl(0.016, 0.07, (xx, ty + 0.035, 0.014), (0, PI / 2, 0), "BinGreen", 12))
    if not down:
        # full to the top and past it: the lid cannot shut on what is in there (Cheyenne: "full ... almost overflowing";
        # and what comes out of it when it goes over is the same bag, the same joint, the same newspaper)
        a = 1.78                                                                  # thrown right back on its hinge, against the wall
        P += moved(lid, (0, ty * (1.0 - math.cos(a)), H + ty * math.sin(a) + 0.004), (-a, 0, 0))
        P.append(blob(0.20, "Bag", (-0.06, 0.06, H + 0.03), (1.0, 1.3, 0.8), 0.11, 1.9, 4.2))
        P.append(blob(0.07, "Meat", (0.16, -0.20, H + 0.07), (1.4, 1.0, 0.7), 0.3, 4.0, 2.2))
        P.append(cyl(0.015, 0.22, (0.20, -0.12, H + 0.14), (0.5, 0.45, 0), "Bone", 12))
        P.append(sheet(0.40, 0.56, "News", seed=3.0, loc=(0.02, -ty - 0.03, H - 0.12), rot=(1.25, 0.0, 0.08), amp=0.02))
        P.append(sheet(0.38, 0.30, "News", seed=6.0, loc=(-tx - 0.02, 0.0, H - 0.06), rot=(0.0, -1.2, 0.1), amp=0.02))
        P.append(blob(0.075, "News", (-0.14, -0.20, H + 0.10), amp=0.26, freq=3.4, seed=1.0, sub=3, flat=True))
        P.append(blob(0.06, "News", (0.05, 0.02, H + 0.20), amp=0.28, freq=3.8, seed=3.0, sub=3, flat=True))
        P.append(blob(0.045, "Fruit", (-0.20, -0.02, H + 0.14), (1, 1, 0.75), 0.18, 3.0, 2.0))
        P.append(blob(0.04, "Fruit", (0.02, -0.28, H + 0.08), (1, 1, 0.7), 0.2, 3.0, 4.0))
        P.append(blob(0.05, "Fruit", (0.12, 0.12, H + 0.16), (1, 1, 0.7), 0.2, 3.0, 8.0))
        P.append(box(0.072, 0.072, 0.19, (-0.02, -0.14, H + 0.16), (0.9, 0.5, 0.3), "Cream", 0.004))      # a milk carton stood on end in the top of it
        for i, (cx, cy, cz) in enumerate(((0.21, 0.05, 0.12), (-0.22, 0.16, 0.10), (0.10, -0.30, 0.05))):
            P.append(cyl(0.033, 0.108, (cx, cy, H + cz), (0.4 * i, PI / 2, 0.7 * i), "Steel", 16))
            P.append(cyl(0.0338, 0.078, (cx, cy, H + cz), (0.4 * i, PI / 2, 0.7 * i), "TinLabel", 16))
        P.append(blob(0.06, "Bag", (0.24, 0.16, H + 0.06), (1.2, 1.0, 1.4), 0.18, 2.2, 6.0, sub=3))
        P.append(puddle(0.16, "Slime", 3.0, 0.006))                              # what has run down the front of it and under
        P[-1].location = (0.05, -by - 0.16, 0.0)
        _fin(P[-1], "Slime")
        return P
    P = moved(P, (0, 0, 0.36), (PI / 2 - lean, 0, 0))                         # over on its front, mouth toward -Y
    P += moved(lid, (0.10, -(H + 0.42), 0.0), (PI, 0.0, 0.22))                # the lid thrown open, upside down on the ground beyond the mouth
    # and what did not come all the way out
    P.append(blob(0.20, "Bag", (-0.06, -0.86, 0.17), (1.0, 1.3, 0.8), 0.11, 1.9, 4.2, sag=0.4))
    P.append(blob(0.07, "Meat", (0.16, -1.0, 0.05), (1.4, 1.0, 0.7), 0.3, 4.0, 2.2, sag=0.4))
    P.append(sheet(0.40, 0.56, "News", seed=3.0, loc=(0.02, -1.12, 0.012), rot=(0.05, 0.0, 0.5), amp=0.02))
    return P


# ------------------------------------------------------------------------------------------------ what was in it
def trashbag(split=False):
    P = [blob(0.27, "Bag", (0, 0, 0.19), (1.0, 0.9, 0.78), 0.11, 1.9, 7.0 if split else 1.0, sag=0.5)]
    P.append(cyl(0.03, 0.09, (0.03, 0.0, 0.42), (0.2, 0.3, 0), "Bag", 10, r2=0.07))            # the knot and its two ears
    P.append(blob(0.05, "Bag", (0.10, 0.02, 0.47), (1.6, 0.5, 0.8), 0.2, 2.5, 3.0, sub=3))
    P.append(blob(0.05, "Bag", (-0.03, -0.03, 0.49), (0.5, 1.5, 0.9), 0.2, 2.5, 5.0, sub=3))
    if split:                                                                 # torn down one side, and its insides coming out of the tear
        P.append(blob(0.11, "Meat", (0.27, 0.05, 0.07), (1.3, 1.0, 0.6), 0.35, 4.0, 1.3, sag=0.5))
        P.append(blob(0.045, "Fruit", (0.33, -0.10, 0.04), (1, 1, 0.75), 0.18, 3.0, 2.0, sag=0.3))
        P.append(blob(0.04, "Fruit", (0.38, 0.14, 0.035), (1, 1, 0.7), 0.2, 3.0, 4.0, sag=0.3))
        P.append(puddle(0.34, "Slime", 2.0, 0.01))
        P[-1].location = (0.30, 0.02, 0.0)
        _fin(P[-1], "Slime")
        P.append(sheet(0.30, 0.42, "News", seed=5.0, loc=(0.36, -0.22, 0.02), rot=(0.1, 0.0, 1.1), amp=0.025, curl=0.2))
    return P


def meat_joint():
    # a ham on the bone, three weeks in a warm bin
    P = [blob(0.115, "Meat", (0, 0, 0.07), (1.5, 1.0, 0.72), 0.32, 4.0, 0.7, sag=0.45)]
    P.append(cyl(0.017, 0.30, (0.13, 0.0, 0.065), (0, PI / 2 + 0.12, 0.1), "Bone", 14))
    for dy in (-0.014, 0.014):
        P.append(blob(0.022, "Bone", (0.285, dy, 0.085), amp=0.2, freq=3.0, seed=dy * 90, sub=3))
    P.append(blob(0.05, "Meat", (-0.16, 0.05, 0.03), (1.6, 0.9, 0.5), 0.4, 5.0, 3.3, sag=0.4))         # a flap of skin come away
    for i in range(34):                                                       # and it is moving
        u, w_ = random.uniform(-0.8, 0.8), random.uniform(-0.8, 0.8)
        if u * u + w_ * w_ > 0.8:
            continue
        z = 0.07 + 0.080 * math.sqrt(1.0 - u * u - w_ * w_)
        s_ = sphere(0.0042, (0, 0, 0), "Cream", 6, 4, (2.4, 1.0, 1.0))
        P.append(moved(s_, (0.17 * u, 0.115 * w_, z), (0, 0, random.uniform(0, PI))))
    P.append(puddle(0.26, "Slime", 4.0, 0.008))
    return P


def meat_ribs():
    # a rack of ribs, mostly bone now
    P = [tube([(-0.17, 0, 0.03), (0.0, 0.01, 0.045), (0.17, 0, 0.03)], 0.014, "Bone", False, 4)]
    for i in range(7):
        x = -0.15 + i * 0.05
        ln = 0.13 + 0.02 * math.sin(i * 1.3)
        for s_ in (-1, 1):
            P.append(tube([(x, 0, 0.035), (x + 0.005, s_ * ln * 0.5, 0.075), (x + 0.012, s_ * ln, 0.03), (x + 0.014, s_ * (ln + 0.03), 0.006)], 0.0065, "Bone", False, 3))
    for i in range(5):
        x = -0.13 + i * 0.055
        P.append(blob(0.035, "Meat", (x, random.choice((-1, 1)) * random.uniform(0.03, 0.09), 0.045), (0.9, 1.9, 0.45), 0.4, 4.0, i * 1.7, sub=3))
    P.append(blob(0.06, "Meat", (0.0, 0.0, 0.025), (2.6, 0.8, 0.4), 0.3, 4.0, 9.0, sag=0.5))
    return P


def fish_bones():
    P = [blob(0.03, "Bone", (-0.11, 0, 0.022), (1.5, 0.8, 0.7), 0.2, 3.0, 1.0, sub=3)]
    P.append(tube([(-0.09, 0, 0.015), (0.0, 0.004, 0.012), (0.10, 0, 0.012)], 0.0035, "Bone", False, 3))
    for i in range(13):
        x = -0.07 + i * 0.012
        ln = 0.032 * (1.0 - abs(i - 5) / 11.0)
        for s_ in (-1, 1):
            P.append(tube([(x, 0, 0.013), (x + 0.006, s_ * ln, 0.006)], 0.0012, "Bone", False, 2))
    P.append(plate([(0.10, 0.0), (0.145, 0.034), (0.132, 0.0), (0.145, -0.034)], 0.0015, "Bone", z=0.008))
    P.append(blob(0.022, "Meat", (-0.03, 0.006, 0.012), (2.2, 0.9, 0.4), 0.4, 5.0, 2.0, sub=3))
    return P


def rotten_fruit():
    P = []
    for i, (x, y, r, sq) in enumerate(((0.0, 0.0, 0.043, 0.78), (0.10, 0.03, 0.040, 0.6), (-0.06, 0.09, 0.045, 0.85), (0.05, -0.09, 0.038, 0.5), (-0.11, -0.04, 0.050, 0.7), (0.16, -0.06, 0.036, 0.8))):
        P.append(blob(r, "Fruit", (x, y, r * sq * 0.82), (1.0, 1.0, sq), 0.16 + 0.1 * (1 - sq), 3.0, i * 2.3, sag=0.35))
        if i % 2 == 0:
            P.append(tube([(x, y, r * sq * 1.5), (x + 0.004, y + 0.003, r * sq * 1.5 + 0.016)], 0.0018, "WoodDark", False, 2))
    for k, a0 in enumerate((0.3, 2.4, 4.3)):                                  # a banana skin, black
        pts = [(-0.14 + 0.07 * math.cos(a0) * t, 0.12 + 0.07 * math.sin(a0) * t, 0.004 + 0.012 * math.sin(t * 2.2)) for t in (0.0, 0.5, 1.0, 1.5, 2.0)]
        P.append(strip(pts, 0.028, 0.003, "Peel"))
    P.append(puddle(0.22, "Slime", 7.0, 0.006))
    return P


def news_flat():
    return [sheet(0.56, 0.38, "News", seed=1.0, loc=(0, 0, 0.012), amp=0.014),
            sheet(0.56, 0.38, "News", seed=2.0, loc=(0.09, 0.07, 0.03), rot=(0.02, 0.03, 0.5), amp=0.02, curl=0.12),
            sheet(0.38, 0.28, "News", seed=3.0, loc=(-0.20, -0.16, 0.022), rot=(0.0, 0.05, -0.8), amp=0.03, curl=0.3)]


def news_balls():
    return [blob(0.075, "News", (0, 0, 0.06), amp=0.26, freq=3.4, seed=1.0, sub=3, sag=0.2, flat=True),
            blob(0.06, "News", (0.17, 0.05, 0.05), amp=0.28, freq=3.8, seed=3.0, sub=3, sag=0.2, flat=True),
            blob(0.09, "News", (-0.05, 0.19, 0.07), (1.2, 0.9, 0.8), 0.26, 3.4, 5.0, sub=3, sag=0.2, flat=True)]


def cans():
    P = []
    for i, (x, y, yaw, sq, open_) in enumerate(((0.0, 0.0, 0.3, 1.0, True), (0.12, 0.05, 1.4, 0.55, False), (-0.10, 0.09, 2.2, 1.0, True), (0.05, -0.13, 0.9, 0.4, False), (-0.14, -0.08, 2.9, 0.8, True), (0.20, -0.06, 0.1, 1.0, False))):
        c = [cyl(0.033, 0.108, (0, 0, 0), (0, PI / 2, 0), "Steel", 20), cyl(0.0338, 0.078, (0, 0, 0), (0, PI / 2, 0), "TinLabel", 20)]
        if open_:
            c.append(cyl(0.031, 0.004, (0.062, 0.02, 0.01), (0.5, PI / 2, 0), "Steel", 18))       # the lid bent back
            c.append(blob(0.022, "Slime", (0.056, 0, -0.012), (0.5, 1.2, 0.7), 0.3, 4.0, i, sub=2))
        for o in c:
            o.scale = (1.0, 1.0, sq)
        P += moved(c, (x, y, 0.033 * sq), (0, 0, yaw))
    return P


def bottles():
    prof = [(0.0, 0.0), (0.0, 0.031), (0.004, 0.033), (0.13, 0.033), (0.165, 0.016), (0.215, 0.0125), (0.218, 0.0145), (0.228, 0.0145), (0.228, 0.010)]
    P = []
    for x, y, yaw in ((0.0, 0.0, 0.4), (0.13, 0.09, 2.0), (-0.12, -0.05, 1.1)):
        P.append(moved(lathe(prof, "GlassBrown", 22), (x, y, 0.033), (0, 0, yaw)))
        P.append(moved(cyl(0.0335, 0.07, (0, 0, 0), (0, PI / 2, 0), "TinLabel", 20), (x + 0.075 * math.cos(yaw), y + 0.075 * math.sin(yaw), 0.033), (0, 0, yaw)))
    P.append(moved(lathe(prof[:4] + [(0.09, 0.033), (0.09, 0.03)], "GlassBrown", 22), (0.02, -0.19, 0.033), (0, 0, 2.6)))    # one with the neck off
    for i in range(7):
        a = i * 0.9
        P.append(plate([(0, 0), (0.02 + 0.01 * (i % 3), 0.004), (0.012, 0.02)], 0.003, "GlassBrown", z=0.0))
        moved(P[-1], (0.06 + 0.07 * math.cos(a), -0.24 + 0.05 * math.sin(a), 0.001), (0.1 * (i % 2), 0, a))
    return P


def cartons():
    P = [box(0.072, 0.072, 0.19, (0, 0, 0), (0.0, PI / 2 - 0.06, 0.4), "Cream", 0.004)]            # a milk carton, on its side, swollen
    P[0].location = (0, 0, 0.04)
    _fin(P[0], "Cream")
    P.append(blob(0.03, "Slime", (0.13, 0.05, 0.008), (1.8, 1.4, 0.3), 0.3, 4.0, 1.0, sub=3))
    P.append(box(0.30, 0.105, 0.05, (-0.05, 0.20, 0.03), (0.04, 0.0, -0.3), "Card", 0.012))        # an egg box, trodden on
    for i in range(6):
        P.append(blob(0.022, "Card", (-0.17 + i * 0.048, 0.215 - i * 0.014, 0.058), (1, 1, 0.5), 0.2, 3.0, i, sub=2))
    P.append(box(0.31, 0.21, 0.02, (0.10, -0.20, 0.012), (0.03, 0.02, 0.7), "Card", 0.004))        # a cereal box, flat
    P.append(box(0.20, 0.13, 0.002, (0.10, -0.20, 0.024), (0.03, 0.02, 0.7), "Label"))
    P.append(sheet(0.24, 0.24, "Cream", seed=4.0, loc=(-0.24, -0.12, 0.01), amp=0.012, nx=10, ny=10))   # a paper plate, and what was on it
    P.append(blob(0.05, "Meat", (-0.24, -0.12, 0.02), (1.3, 1.0, 0.35), 0.4, 5.0, 6.0, sub=3))
    return P


def slop():
    P = [puddle(0.55, "Slime", 1.0, 0.014)]
    for i in range(9):
        a, d = i * 0.7, 0.12 + 0.04 * i
        P.append(blob(0.02 + 0.004 * (i % 3), "Fruit" if i % 3 else "Meat", (d * math.cos(a), d * math.sin(a), 0.012), (1.2, 1.0, 0.5), 0.35, 4.0, i * 1.1, sub=2))
    return P


for _n, _f in (("BigBin", bigbin), ("BigBinDown", lambda: bigbin(True)), ("TrashBag", trashbag), ("TrashBagSplit", lambda: trashbag(True)),
               ("MeatJoint", meat_joint), ("MeatRibs", meat_ribs), ("FishBones", fish_bones), ("RottenFruit", rotten_fruit), ("NewsFlat", news_flat),
               ("NewsBalls", news_balls), ("Cans", cans), ("Bottles", bottles), ("Cartons", cartons), ("Slop", slop)):
    build(_n, _f)
