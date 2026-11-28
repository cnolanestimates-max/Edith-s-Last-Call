# The yard and forest props (Cheyenne, 2026-11-28: the wheelbarrow "looks like it's out of Roblox", the stumps "need to
# look like stumps", "the grass needs to be revamped and actually look like grass").  Replaces the kit's 458-triangle
# wheelbarrow and 626-triangle stump, and gives the ground real tufts of grass.
#   Wheelbarrow   a steel-tray contractor's barrow left out for years: rusted green tray, grey ash shafts, a flat tyre,
#                 a load of manure with straw in it and the muck fork still standing in the heap
#   Stump, StumpRot, StumpAxe   felled trunks with root flare, furrowed bark, growth rings and the felling hinge on the
#                 cut face, moss on the weather side; the last one is the chopping block with the axe left in it
#   (the grass clumps are in Scripts/art/outdoor_grass.py: vertex-coloured, not baked)
#   RockA..C      field stones with lichen, to replace the kit's 100-triangle slabs
#   Woodpile      a cord of split firewood between two stakes, the top tier slumped
# Exec'd by build_items_fine.py after yard_models.py (uses its helpers, blob from trash_models.py and mnoise).
#   blender -b --factory-startup -P build_items_fine.py -- <out> --only Wheelbarrow,Stump,StumpRot,StumpAxe,RockA,RockB,RockC --preview


def _objz(g):
    sep = g.N.new("ShaderNodeSeparateXYZ")
    g.L.new(g.P, sep.inputs[0])
    return sep


def _upness(g):
    geo = g.N.new("ShaderNodeNewGeometry")
    sn = g.N.new("ShaderNodeSeparateXYZ")
    g.L.new(geo.outputs["Normal"], sn.inputs[0])
    return sn.outputs[2]


def m_tray(g):
    # green enamel, most of it gone: rust along the rolled rim and in broad blooms, streaks down the sides, dried muck inside
    big = g.noise(5.0, 5.0, 0.6)
    mid = g.noise(22.0, 4.0, vec=g.mapping(loc=(0.3, 0.8, 0.1)))
    fine = g.noise(170.0, 5.0)
    paint = g.mix((0.020, 0.045, 0.026), (0.034, 0.060, 0.036), g.ramp(g.noise(30.0, 3.0), 0.3, 0.7))
    paint = g.mix(paint, (0.07, 0.085, 0.07), g.math("MULTIPLY", g.ramp(fine, 0.5, 0.8), 0.5))          # chalked by the sun
    rust = g.mix((0.115, 0.045, 0.016), (0.040, 0.018, 0.009), g.ramp(fine, 0.3, 0.75))
    rust = g.mix(rust, (0.16, 0.075, 0.025), g.math("MULTIPLY", g.ramp(mid, 0.55, 0.75), 0.6))          # fresher orange in spots
    a = g.ao(0.03)
    gone = g.ramp(g.math("ADD", big, g.math("MULTIPLY", g.math("SUBTRACT", mid, 0.5), 0.5)), 0.40, 0.56)
    gone = g.math("MAXIMUM", gone, g.math("MULTIPLY", g.edge(0.008), 1.0))
    gone = g.math("MAXIMUM", gone, g.ramp(a, 0.85, 0.5))
    streak = g.math("MULTIPLY", g.ramp(g.noise(1.0, 3.0, vec=g.mapping(scale=(38.0, 38.0, 2.5))), 0.5, 0.68), 0.7)
    c = g.mix(paint, rust, gone)
    c = g.mix(c, (0.060, 0.026, 0.011), streak)
    up = _upness(g)
    muck = g.math("MULTIPLY", g.ramp(up, 0.15, 0.8), g.ramp(g.noise(9.0, 4.0, vec=g.mapping(loc=(0.6, 0.2, 0.9))), 0.30, 0.62))
    muck = g.math("MAXIMUM", muck, g.math("MULTIPLY", g.ramp(a, 0.92, 0.55), 0.9))
    c = g.mix(c, g.mix((0.030, 0.021, 0.012), (0.055, 0.040, 0.024), fine), g.math("MULTIPLY", muck, 0.92))
    r = g.math("ADD", g.mix(0.62, 0.92, gone), g.math("MULTIPLY", fine, 0.1))
    r = g.math("MAXIMUM", r, g.math("MULTIPLY", muck, 0.95), clamp=True)
    m = g.math("MULTIPLY", g.math("SUBTRACT", 1.0, g.math("MAXIMUM", gone, muck)), 0.12)
    h = g.math("ADD", g.math("MULTIPLY", gone, 0.8), g.math("MULTIPLY", fine, 0.3))
    h = g.math("ADD", h, g.math("MULTIPLY", muck, 0.9))
    g.finish(c, r, m, h, 0.9, 0.003)


def m_woodgrey(g):
    # ash left out in the weather: silver-grey, the grain opened into long checks, dark where hands and rain kept it wet
    w = g.noise(1.0, 3.0, 0.6, vec=g.mapping(scale=(5.0, 5.0, 5.0)))          # broad weathering, no direction: the shafts, haft and fork lie every way
    fine = g.noise(420.0, 4.0, 0.6)
    c = g.mix((0.042, 0.037, 0.031), (0.098, 0.088, 0.074), g.ramp(w, 0.3, 0.75))
    c = g.mix(c, (0.125, 0.115, 0.098), g.math("MULTIPLY", g.ramp(fine, 0.55, 0.8), 0.35))
    checks = g.ramp(g.cells(60.0, vec=g.mapping(scale=(0.25, 1.0, 1.0))), 0.0, 0.02, 1.0, 0.0)
    checks = g.math("MULTIPLY", checks, g.ramp(g.noise(30.0, 3.0, vec=g.mapping(loc=(0.2, 0.5, 0.1))), 0.45, 0.62))
    c = g.mix(c, (0.018, 0.015, 0.012), g.math("MULTIPLY", checks, 0.9))
    c = g.mix(c, (0.024, 0.019, 0.014), g.math("MULTIPLY", g.ramp(g.noise(7.0, 4.0), 0.45, 0.7), 0.7))          # damp, dirty patches
    c = g.mix(c, (0.035, 0.050, 0.028), g.math("MULTIPLY", g.ramp(g.noise(13.0, 4.0, vec=g.mapping(loc=(0.7, 0.3, 0.2))), 0.60, 0.74), 0.55))   # a little green
    a = g.ao(0.01)
    c = g.mix(c, (0.020, 0.016, 0.012), g.math("MULTIPLY", g.ramp(a, 0.9, 0.5), 0.8))
    c = g.mix(c, (0.15, 0.14, 0.12), g.math("MULTIPLY", g.edge(0.002), 0.35))
    r = g.math("ADD", 0.78, g.math("MULTIPLY", fine, 0.15), clamp=True)
    h = g.math("SUBTRACT", g.math("ADD", g.math("MULTIPLY", w, 0.3), g.math("MULTIPLY", fine, 0.5)), g.math("MULTIPLY", checks, 1.5))
    g.finish(c, r, 0.0, h, 0.9, 0.0012)


def m_rubber(g):
    # a perished tyre: grey-black, cracked in a web on the wall, dried mud packed in the tread
    fine = g.noise(240.0, 4.0)
    crack = g.ramp(g.cells(95.0), 0.0, 0.035, 1.0, 0.0)
    c = g.mix((0.016, 0.016, 0.017), (0.045, 0.043, 0.040), g.ramp(g.noise(30.0, 4.0), 0.3, 0.75))
    c = g.mix(c, (0.006, 0.006, 0.006), g.math("MULTIPLY", crack, 0.85))
    a = g.ao(0.012)
    mud = g.math("MAXIMUM", g.ramp(a, 0.93, 0.6), g.ramp(g.noise(8.0, 4.0, vec=g.mapping(loc=(0.4, 0.7, 0.2))), 0.52, 0.70))
    c = g.mix(c, g.mix((0.075, 0.058, 0.038), (0.045, 0.034, 0.022), fine), g.math("MULTIPLY", mud, 0.85))
    r = g.math("ADD", 0.80, g.math("MULTIPLY", mud, 0.15), clamp=True)
    h = g.math("SUBTRACT", g.math("ADD", g.math("MULTIPLY", fine, 0.2), g.math("MULTIPLY", mud, 0.5)), crack)
    g.finish(c, r, 0.0, h, 0.8, 0.0015)


def m_manure(g):
    # rotted stable muck: black-brown and clodded, a wet shine in the hollows, paler dried crust on the high lumps
    big = g.noise(9.0, 5.0, 0.6)
    fine = g.noise(220.0, 5.0, 0.65)
    fib = g.noise(1.0, 3.0, vec=g.mapping(scale=(60.0, 900.0, 300.0), rot=(0.3, 0.5, 0.8)))
    clod = g.ramp(g.cells(46.0, feature="F1"), 0.05, 0.30)
    c = g.mix((0.006, 0.0035, 0.002), (0.020, 0.012, 0.006), g.ramp(big, 0.35, 0.7))
    c = g.mix(c, (0.034, 0.022, 0.011), g.math("MULTIPLY", g.ramp(fine, 0.58, 0.82), 0.4))               # dried crust and chaff
    c = g.mix(c, (0.085, 0.060, 0.028), g.math("MULTIPLY", g.ramp(fib, 0.73, 0.79), 0.55))               # bits of straw worked into it
    a = g.ao(0.02)
    c = g.mix(c, (0.008, 0.006, 0.004), g.math("MULTIPLY", g.ramp(a, 0.9, 0.45), 0.85))
    wet = g.math("MULTIPLY", g.ramp(a, 0.95, 0.6), g.ramp(big, 0.6, 0.35))
    r = g.math("SUBTRACT", g.math("ADD", 0.80, g.math("MULTIPLY", fine, 0.14)), g.math("MULTIPLY", wet, 0.50), clamp=True)
    h = g.math("ADD", g.math("ADD", g.math("MULTIPLY", clod, 0.9), g.math("MULTIPLY", fine, 0.5)), g.math("MULTIPLY", fib, 0.3))
    g.finish(c, r, 0.0, h, 1.0, 0.006)


def m_straw(g):
    fine = g.noise(500.0, 3.0)
    c = g.mix((0.11, 0.082, 0.036), (0.21, 0.17, 0.082), g.ramp(g.noise(40.0, 3.0), 0.3, 0.7))
    c = g.mix(c, (0.055, 0.038, 0.019), g.math("MULTIPLY", g.ramp(g.noise(18.0, 3.0, vec=g.mapping(loc=(0.5, 0.1, 0.3))), 0.38, 0.62), 0.85))   # rotted and stained
    g.finish(c, g.math("ADD", 0.7, g.math("MULTIPLY", fine, 0.15)), 0.0, fine, 0.3, 0.0005)


def m_bark(g):
    # old pine bark: long ridges running up the trunk, split by deep furrows and broken across into plates; grey-brown on
    # the faces, near black in the furrows, red-brown where a plate has scaled off, moss low down and on what faces the sky
    sep = _objz(g)
    warp = g.mapping(scale=(1.0, 1.0, 0.10))
    n1 = g.noise(26.0, 5.0, 0.62, vec=warp)                                  # ridges: noise pulled long up the trunk
    n2 = g.noise(61.0, 4.0, 0.60, vec=g.mapping(scale=(1.0, 1.0, 0.16), loc=(0.3, 0.7, 0.2)))
    ridge = g.math("ABSOLUTE", g.math("SUBTRACT", g.math("ADD", g.math("MULTIPLY", n1, 0.7), g.math("MULTIPLY", n2, 0.3)), 0.5))
    fur = g.ramp(ridge, 0.0, 0.055, 1.0, 0.0)                                # 1 in a furrow
    cross = g.ramp(g.cells(22.0, vec=g.mapping(scale=(1.0, 1.0, 0.45))), 0.0, 0.03, 1.0, 0.0)      # the breaks across the ridges
    fur = g.math("MAXIMUM", fur, g.math("MULTIPLY", cross, 0.55))
    fine = g.noise(340.0, 5.0, 0.65)
    flake = g.noise(48.0, 4.0, 0.6, vec=g.mapping(scale=(1.0, 1.0, 0.3), loc=(0.6, 0.1, 0.4)))
    c = g.mix((0.021, 0.016, 0.013), (0.066, 0.054, 0.044), g.ramp(flake, 0.25, 0.75))
    c = g.mix(c, (0.066, 0.031, 0.016), g.math("MULTIPLY", g.ramp(flake, 0.60, 0.76), 0.6))               # scaled plates
    c = g.mix(c, (0.100, 0.095, 0.085), g.math("MULTIPLY", g.ramp(g.noise(70.0, 3.0, vec=g.mapping(loc=(0.8, 0.2, 0.5))), 0.64, 0.76), 0.45))   # grey lichen
    c = g.mix(c, (0.008, 0.006, 0.004), g.math("MULTIPLY", fur, 0.95))
    a = g.ao(0.04)
    c = g.mix(c, (0.007, 0.005, 0.004), g.math("MULTIPLY", g.ramp(a, 0.88, 0.45), 0.85))
    up = _upness(g)
    low = g.ramp(sep.outputs[2], 0.16, 0.0)
    mossn = g.noise(13.0, 6.0, 0.68, vec=g.mapping(loc=(0.2, 0.9, 0.4)))
    moss = g.math("MULTIPLY", g.math("MAXIMUM", g.ramp(up, 0.35, 0.85), g.math("MULTIPLY", low, 0.8)), g.ramp(mossn, 0.46, 0.60))
    mossc = g.mix((0.010, 0.024, 0.006), (0.036, 0.058, 0.014), g.ramp(g.noise(190.0, 4.0), 0.3, 0.75))
    c = g.mix(c, mossc, g.math("MULTIPLY", moss, 0.9))
    dirt = g.math("MULTIPLY", g.ramp(sep.outputs[2], 0.06, -0.02), 0.9)                                    # earth splashed up the root flare
    c = g.mix(c, (0.026, 0.020, 0.013), dirt)
    r = g.math("ADD", 0.84, g.math("MULTIPLY", fine, 0.12), clamp=True)
    h = g.math("SUBTRACT", g.math("ADD", g.math("MULTIPLY", flake, 0.5), g.math("MULTIPLY", fine, 0.25)), g.math("MULTIPLY", fur, 2.2))
    h = g.math("ADD", h, g.math("MULTIPLY", moss, 0.5))
    g.finish(c, r, 0.0, h, 1.0, 0.014)


def m_heartwood(g):
    # the cut face after a couple of winters: grey, the rings still to be read, checks opening from the pith, the
    # chainsaw's passes across it, green and black where water stands
    sep = _objz(g)
    wob = g.noise(6.0, 3.0)
    rad = g.math("SQRT", g.math("ADD", g.math("MULTIPLY", sep.outputs[0], sep.outputs[0]), g.math("MULTIPLY", sep.outputs[1], sep.outputs[1])))
    rad = g.math("ADD", rad, g.math("MULTIPLY", g.math("SUBTRACT", wob, 0.5), 0.035))
    ring = g.math("SINE", g.math("MULTIPLY", rad, 560.0))
    ring2 = g.math("SINE", g.math("MULTIPLY", rad, 83.0))
    fine = g.noise(420.0, 4.0)
    c = g.mix((0.078, 0.068, 0.056), (0.056, 0.048, 0.039), g.ramp(g.noise(9.0, 4.0), 0.3, 0.7))
    c = g.mix(c, (0.024, 0.019, 0.014), g.math("MULTIPLY", g.ramp(ring, 0.45, 0.95), 0.75))             # the dark late wood of each year, in thin lines
    c = g.mix(c, (0.060, 0.047, 0.033), g.math("MULTIPLY", g.ramp(ring2, 0.2, 0.9), 0.3))
    c = g.mix(c, (0.060, 0.036, 0.021), g.math("MULTIPLY", g.ramp(rad, 0.10, 0.0), 0.6))                 # darker heart
    c = g.mix(c, (0.045, 0.039, 0.032), g.math("MULTIPLY", g.ramp(g.noise(5.0, 5.0, 0.6, vec=g.mapping(loc=(0.1, 0.6, 0.3))), 0.42, 0.66), 0.7))   # grey weathering in patches
    ang = g.math("ARCTAN2", sep.outputs[1], sep.outputs[0])
    spoke = g.math("SINE", g.math("ADD", g.math("MULTIPLY", ang, 7.0), g.math("MULTIPLY", g.noise(9.0, 2.0), 2.5)))
    check = g.math("MULTIPLY", g.ramp(spoke, 0.965, 0.995), g.ramp(rad, 0.01, 0.07))
    check = g.math("MULTIPLY", check, g.ramp(g.noise(14.0, 3.0, vec=g.mapping(loc=(0.4, 0.4, 0.4))), 0.35, 0.6))
    c = g.mix(c, (0.012, 0.009, 0.007), g.math("MULTIPLY", check, 0.95))
    saw = g.wave(260.0, 1.5, 2.0, "X", vec=g.mapping(rot=(0, 0, 0.5)))
    c = g.mix(c, (0.075, 0.064, 0.050), g.math("MULTIPLY", g.ramp(saw, 0.75, 0.95), 0.35))
    stain = g.ramp(g.noise(8.0, 5.0, 0.6, vec=g.mapping(loc=(0.9, 0.3, 0.6))), 0.50, 0.68)
    c = g.mix(c, g.mix((0.014, 0.020, 0.009), (0.030, 0.044, 0.014), fine), g.math("MULTIPLY", stain, 0.7))   # algae and moss
    a = g.ao(0.012)
    c = g.mix(c, (0.014, 0.011, 0.008), g.math("MULTIPLY", g.ramp(a, 0.9, 0.5), 0.8))
    c = g.mix(c, (0.14, 0.125, 0.10), g.math("MULTIPLY", g.edge(0.002), 0.3))
    r = g.math("ADD", 0.80, g.math("MULTIPLY", fine, 0.14), clamp=True)
    h = g.math("SUBTRACT", g.math("ADD", g.math("MULTIPLY", ring, 0.15), g.math("MULTIPLY", saw, 0.25)), g.math("MULTIPLY", check, 2.0))
    g.finish(c, r, 0.0, h, 0.9, 0.0015)


def m_chip(g):
    # fresh-split wood, only a season old: pale yellow going grey
    fine = g.noise(1.0, 3.0, vec=g.mapping(scale=(30.0, 500.0, 500.0)))
    c = g.mix((0.105, 0.085, 0.058), (0.20, 0.17, 0.12), g.ramp(fine, 0.3, 0.75))
    c = g.mix(c, (0.055, 0.047, 0.037), g.math("MULTIPLY", g.ramp(g.noise(25.0, 3.0), 0.40, 0.66), 0.75))
    g.finish(c, 0.8, 0.0, fine, 0.6, 0.0008)


def m_rock(g):
    # field stone: dark grey granite, mottled, rust-stained, pale lichen in round patches, moss only in what faces the sky
    big = g.noise(7.0, 6.0, 0.62)
    mid = g.noise(38.0, 5.0, 0.65, vec=g.mapping(loc=(0.5, 0.2, 0.8)))
    fine = g.noise(300.0, 5.0, 0.7)
    c = g.mix((0.014, 0.013, 0.012), (0.058, 0.055, 0.050), g.ramp(g.math("ADD", g.math("MULTIPLY", big, 0.6), g.math("MULTIPLY", mid, 0.4)), 0.3, 0.72))
    c = g.mix(c, (0.105, 0.100, 0.092), g.math("MULTIPLY", g.ramp(fine, 0.64, 0.82), 0.5))               # crystals catching the light
    c = g.mix(c, (0.060, 0.040, 0.024), g.math("MULTIPLY", g.ramp(g.noise(19.0, 4.0, vec=g.mapping(loc=(0.3, 0.1, 0.7))), 0.54, 0.70), 0.5))     # iron stain
    crack = g.math("MULTIPLY", g.ramp(g.cells(9.0), 0.0, 0.012, 1.0, 0.0), g.ramp(g.noise(6.0, 3.0, vec=g.mapping(loc=(0.7, 0.3, 0.2))), 0.50, 0.62))
    c = g.mix(c, (0.010, 0.009, 0.008), g.math("MULTIPLY", crack, 0.8))
    lich = g.ramp(g.cells(34.0, feature="F1", vec=g.mapping(loc=(0.2, 0.5, 0.8))), 0.13, 0.04)
    lich = g.math("MULTIPLY", lich, g.ramp(g.noise(8.0, 3.0, vec=g.mapping(loc=(0.6, 0.6, 0.1))), 0.50, 0.64))
    c = g.mix(c, g.mix((0.115, 0.120, 0.095), (0.080, 0.092, 0.055), fine), g.math("MULTIPLY", lich, 0.75))
    up = _upness(g)
    sep = _objz(g)
    moss = g.math("MULTIPLY", g.ramp(up, 0.40, 0.88), g.ramp(g.noise(10.0, 6.0, 0.68, vec=g.mapping(loc=(0.1, 0.4, 0.9))), 0.44, 0.58))
    c = g.mix(c, g.mix((0.010, 0.024, 0.006), (0.034, 0.055, 0.014), fine), g.math("MULTIPLY", moss, 0.9))
    c = g.mix(c, (0.022, 0.017, 0.011), g.ramp(sep.outputs[2], 0.10, 0.0))                                   # earth round the foot
    a = g.ao(0.03)
    c = g.mix(c, (0.008, 0.007, 0.006), g.math("MULTIPLY", g.ramp(a, 0.9, 0.5), 0.8))
    r = g.math("ADD", 0.76, g.math("MULTIPLY", fine, 0.18), clamp=True)
    pit = g.ramp(g.cells(70.0, feature="F1", vec=g.mapping(loc=(0.4, 0.9, 0.1))), 0.10, 0.02)
    c = g.mix(c, (0.014, 0.013, 0.012), g.math("MULTIPLY", pit, 0.6))
    h = g.math("SUBTRACT", g.math("ADD", g.math("MULTIPLY", mid, 1.2), g.math("MULTIPLY", fine, 0.6)), g.math("MULTIPLY", crack, 1.8))
    h = g.math("SUBTRACT", h, g.math("MULTIPLY", pit, 0.9))
    h = g.math("ADD", h, g.math("MULTIPLY", moss, 0.6))
    g.finish(c, r, 0.0, h, 1.0, 0.02)


MATS.update({"Tray": m_tray, "WoodGrey": m_woodgrey, "Rubber": m_rubber, "Manure": m_manure, "Straw": m_straw, "Bark": m_bark,
             "Heartwood": m_heartwood, "Chip": m_chip, "Rock": m_rock})


# ============================================================================================ the wheelbarrow
def beam(p0, p1, w, h, m, bevel=0.0, over=0.0):
    """A rectangular bar from p0 to p1, w across and h deep."""
    a, b = Vector(p0), Vector(p1)
    d = b - a
    bpy.ops.mesh.primitive_cube_add(size=1, location=(a + b) / 2)
    ob = bpy.context.object
    ob.scale = (d.length + over, w, h)
    ob.rotation_euler = Vector((1, 0, 0)).rotation_difference(d.normalized()).to_euler()
    _fin(ob, m)
    if bevel > 0:
        bev(ob, bevel, 2, 50.0)
    return ob


def rod(p0, p1, r, m, v=14):
    a, b = Vector(p0), Vector(p1)
    d = b - a
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=d.length, vertices=v, location=(a + b) / 2)
    ob = bpy.context.object
    ob.rotation_euler = Vector((0, 0, 1)).rotation_difference(d.normalized()).to_euler()
    for f in ob.data.polygons:
        f.use_smooth = len(f.vertices) == 4
    return _fin(ob, m)


def rrect(w, l, r, n=8, cx=0.0, z=0.0):
    """Rounded rectangle, l long (X) and w wide (Y), counter-clockwise from the +X side."""
    pts = []
    for qx, qy, a0 in ((1, 1, 0), (-1, 1, 90), (-1, -1, 180), (1, -1, 270)):
        for k in range(n + 1):
            a = math.radians(a0 + 90.0 * k / n)
            pts.append((cx + qx * (l / 2 - r) + r * math.cos(a), qy * (w / 2 - r) + r * math.sin(a), z))
    return pts


def barrow_tray():
    levels = [(0.000, 0.44, 0.30, 0.085, -0.020), (0.022, 0.53, 0.385, 0.105, -0.010), (0.110, 0.70, 0.52, 0.12, 0.030),
              (0.200, 0.84, 0.62, 0.13, 0.070), (0.238, 0.90, 0.665, 0.135, 0.086)]
    rings = [rrect(w, l, r, 8, cx, z) for z, l, w, r, cx in levels]
    n = len(rings[0])
    verts = [p for ring in rings for p in ring]
    faces = [tuple(range(n - 1, -1, -1))]                                    # the floor
    for j in range(len(rings) - 1):
        for i in range(n):
            a, b = j * n + i, j * n + (i + 1) % n
            faces.append((a, b, b + n, a + n))
    ob = mesh(verts, faces, "Tray")
    bpy.context.view_layer.objects.active = ob
    md = ob.modifiers.new("sub", "SUBSURF"); md.levels = 1
    bpy.ops.object.modifier_apply(modifier="sub")
    for v in ob.data.vertices:                                               # forty years of knocks
        p = v.co
        k = 0.006 * mnoise.noise(Vector((p.x * 7.0, p.y * 7.0, p.z * 9.0 + 2.0))) + 0.012 * max(0.0, mnoise.noise(Vector((p.x * 2.5 + 4.0, p.y * 2.5, p.z * 3.0)))) ** 2
        if p.z > 0.01:
            p.x += k * (1 if p.x > 0 else -1)
            p.y += k * (1 if p.y > 0 else -1)
    md = ob.modifiers.new("s", "SOLIDIFY"); md.thickness = 0.004; md.offset = 1.0
    bpy.ops.object.modifier_apply(modifier="s")
    for f in ob.data.polygons:
        f.use_smooth = True
    rim = tube([(x, y, z + 0.004) for x, y, z in rrect(0.672, 0.907, 0.138, 8, 0.086, 0.238)], 0.0085, "Tray", closed=True, res=3)
    return [ob, rim]


def barrow_wheel(flat=0.022):
    P = []
    R, r = 0.158, 0.043
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, major_segments=64, minor_segments=18, rotation=(PI / 2, 0, 0))
    tyre = bpy.context.object
    _fin(tyre, "Rubber")
    for v in tyre.data.vertices:                                             # tread blocks round the crown
        p = v.co
        rad = math.hypot(p.x, p.z)
        a = math.atan2(p.z, p.x)
        if rad > R + r * 0.55:
            k = 1.0 + 0.012 * (1 if math.sin(a * 34.0 + (2.2 if p.y > 0 else 0.0)) > 0.1 else -0.4)
            p.x *= k; p.z *= k
    for f in tyre.data.polygons:
        f.use_smooth = True
    P.append(tyre)
    prof = [(-0.060, 0.0), (-0.060, 0.026), (-0.024, 0.030), (-0.013, 0.058), (-0.013, 0.104), (-0.036, 0.112), (-0.036, 0.124),
            (0.036, 0.124), (0.036, 0.112), (0.013, 0.104), (0.013, 0.058), (0.024, 0.030), (0.060, 0.026), (0.060, 0.0)]
    rim = lathe(prof, "CastIron", 40)
    P.append(moved(rim, rot=(0, 0, PI / 2)))
    for k in range(5):                                                       # the bolts round the hub
        a = 2 * PI * k / 5
        for s in (-1, 1):
            P.append(rod((0.044 * math.cos(a), s * 0.012, 0.044 * math.sin(a)), (0.044 * math.cos(a), s * 0.022, 0.044 * math.sin(a)), 0.006, "Iron", 6))
    P.append(rod((0, -0.105, 0), (0, 0.105, 0), 0.009, "Iron", 12))          # the axle
    P = moved(P, (0, 0, R + r - flat))
    for v in tyre.data.vertices:                                             # no air in it: the tyre sits flat on the ground and bulges
        p = v.co
        if p.z < 0.045:
            t = (0.045 - p.z) / (0.045 + flat)
            p.y *= 1.0 + 0.35 * t
            p.z = max(p.z, 0.0) * (1.0 - 0.3 * t)
    return P, R + r - flat


def muck_heap(seed=3.0):
    P = [blob(0.30, "Manure", (0.0, 0.0, 0.0), (1.12, 0.80, 0.46), 0.11, 2.6, seed, sub=5)]
    rr = random.Random(11)

    def top(x, y):
        k = 1.0 - (x / 0.336) ** 2 - (y / 0.24) ** 2
        return 0.138 * math.sqrt(k) if k > 0 else None
    for i in range(30):                                                      # clods
        x, y = rr.uniform(-0.30, 0.30), rr.uniform(-0.21, 0.21)
        z = top(x, y)
        if z is None:
            continue
        s = rr.uniform(0.018, 0.046)
        P.append(blob(s, "Manure", (x, y, z - s * 0.15), (1.15, rr.uniform(0.75, 1.15), rr.uniform(0.45, 0.7)), 0.22, 2.4, i * 1.37, sub=2, rot=(0, 0, rr.uniform(0, PI))))
    for i in range(80):                                                      # straw
        x, y = rr.uniform(-0.31, 0.31), rr.uniform(-0.22, 0.22)
        z = top(x, y)
        if z is None:
            continue
        L = rr.uniform(0.05, 0.15)
        a, tilt = rr.uniform(0, PI), rr.uniform(-0.16, 0.16)
        d = Vector((math.cos(a) * math.cos(tilt), math.sin(a) * math.cos(tilt), math.sin(tilt))) * L / 2
        c = Vector((x, y, z + 0.004 + abs(d.z)))
        P.append(rod(c - d, c + d, rr.uniform(0.0010, 0.0017), "Straw", 3))
    return P


def muck_fork():
    """A four-tine manure fork, the head sunk in the heap; built standing on its tines along -Z, then leaned."""
    P = [rod((0, 0, 0.13), (0, 0, 0.98), 0.0165, "WoodGrey", 14)]
    P.append(sphere(0.0175, (0, 0, 0.98), "WoodGrey", 14, 8, (1, 1, 0.7)))
    P.append(cyl(0.021, 0.11, (0, 0, 0.165), m="Iron", v=16, r2=0.0185))      # the socket
    P.append(rod((-0.09, 0, 0.09), (0.09, 0, 0.09), 0.008, "Iron", 8))        # the head bar
    P.append(rod((0, 0, 0.09), (0, 0, 0.125), 0.010, "Iron", 8))
    for x in (-0.09, -0.03, 0.03, 0.09):
        P.append(tube([(x, 0, 0.09), (x, 0.012, 0.0), (x, 0.03, -0.12), (x, 0.035, -0.20)], 0.0045, "Iron", res=2))
    return P


def wheelbarrow():
    P = []
    wheel, axle_z = barrow_wheel()
    AX = 0.62
    P += moved(wheel, (AX, 0, 0))
    GR = Vector((-0.88, 0.315, 0.585))                                       # grip end of a shaft (the other is mirrored)
    FE = Vector((AX + 0.03, 0.082, axle_z + 0.028))                          # its front end, over the axle

    def on_shaft(x, s, dz=0.0):
        t = (x - GR.x) / (FE.x - GR.x)
        p = GR.lerp(FE, t)
        return (p.x, s * p.y, p.z + dz)
    for s in (-1, 1):
        g0, f0 = Vector((GR.x + 0.13, s * on_shaft(GR.x + 0.13, 1)[1], on_shaft(GR.x + 0.13, 1)[2])), Vector((FE.x, s * FE.y, FE.z))
        P.append(beam(g0, f0, 0.036, 0.046, "WoodGrey", 0.004, 0.0))
        gp = Vector((GR.x, s * GR.y, GR.z))
        P.append(rod(gp, g0 + (g0 - gp).normalized() * 0.02, 0.0185, "WoodGrey", 16))   # the grip, turned round
        P.append(sphere(0.019, tuple(gp), "WoodGrey", 14, 8))
        # the axle hanger
        P.append(box(0.055, 0.006, 0.075, (AX, s * 0.104, axle_z + 0.005), m="Iron", bevel=0.0015))
        for bx in (-0.015, 0.02):
            P.append(rod((AX + bx, s * 0.060, FE.z), (AX + bx, s * 0.112, FE.z), 0.0045, "Iron", 6))
        # the leg: a steel strap down from the shaft, along the ground and back up
        y0 = on_shaft(-0.06, 1)[1]
        leg = [on_shaft(-0.06, s, -0.020), (-0.36, s * 0.285, 0.014), (-0.47, s * 0.285, 0.010), on_shaft(-0.56, s, -0.020)]
        P.append(tube(leg, 0.0115, "Iron", res=3))
        # tray stays at the front
        P.append(rod(on_shaft(0.47, s, 0.02), (0.385, s * 0.185, 0.470), 0.007, "Iron", 8))
    P.append(rod((-0.245, -0.262, 0.165), (-0.245, 0.262, 0.165), 0.008, "Iron", 8))       # the brace between the legs
    # two cross straps on the shafts carry the tray
    for x in (-0.20, 0.21):
        a, b = on_shaft(x, -1, 0.029), on_shaft(x, 1, 0.029)
        P.append(beam(a, b, 0.045, 0.012, "Iron", 0.002, 0.03))
    TZ = 0.412
    tray = moved(barrow_tray(), (0.02, 0, TZ), (0, math.radians(-3.5), 0))
    P += tray
    for x in (-0.20, 0.21):                                                                # bolt heads through the floor
        for y in (-0.09, 0.09):
            P.append(cyl(0.009, 0.006, (x, y, TZ + 0.012 + 0.061 * (x + 0.2) * 0.06), m="Iron", v=8))
    heap = moved(muck_heap(), (0.075, 0.0, TZ + 0.215), (0, math.radians(-3.5), 0))
    P += heap
    P += moved(muck_fork(), (0.0, 0.03, TZ + 0.29), (math.radians(-16), math.radians(-38), math.radians(12)))
    # what slopped over the side when it was set down
    rr = random.Random(5)
    for i in range(7):
        s = rr.uniform(0.02, 0.05)
        P.append(blob(s, "Manure", (rr.uniform(-0.25, 0.45), rr.choice((-1, 1)) * rr.uniform(0.40, 0.56), s * 0.45), (1.1, 0.9, 0.6), 0.3, 3.0, 40 + i, sub=3, sag=0.5))
    return P


# ============================================================================================ stumps
def stump_parts(R=0.27, H=0.42, seed=1.0, roots=6, hinge=True, tilt=0.05, broken=None, seg=112, rings=34):
    """A felled trunk: root flare at the ground, furrowed bark, a cut face with the felling hinge standing proud."""
    hx = 0.28 * R                                                            # the hinge runs across the face at x = hx

    def ztop(x, y):
        z = H + tilt * R * (x * math.cos(seed) + y * math.sin(seed)) / R
        if hinge:
            z -= 0.045 * min(1.0, max(0.0, (x - hx) / 0.012)) * (1.0 + 0.9 * (x - hx) / R)      # the face cut: lower, and sloping away
        z += 0.004 * mnoise.noise(Vector((x * 14.0, y * 14.0, seed)))
        if broken:
            a = math.atan2(y, x)
            d = math.atan2(math.sin(a - broken[0]), math.cos(a - broken[0]))
            k = math.exp(-(d / broken[1]) ** 2) * min(1.0, math.hypot(x, y) / (0.55 * R))
            z -= broken[2] * H * k * (0.75 + 0.5 * mnoise.noise(Vector((a * 9.0, math.hypot(x, y) * 30.0, seed + 3.0))))
        return z
    lobes = []
    for k in range(roots):
        lobes.append((2 * PI * (k + 0.70 * mnoise.noise(Vector((k * 1.7, seed, 0.0)))) / roots + seed, 0.55 + 0.75 * mnoise.noise(Vector((k * 3.1, seed * 2.0, 1.0))),
                      0.17 + 0.07 * mnoise.noise(Vector((k * 2.3, seed, 4.0)))))

    def rad(a, t):
        r = R * (1.0 + 0.34 * (1 - t) ** 2.4)
        lob = 0.0
        for ak, amp, wid in lobes:
            d = math.atan2(math.sin(a - ak), math.cos(a - ak))
            lob = max(lob, math.exp(-(abs(d) / wid) ** 1.5) * max(amp, 0.0))
        r += R * 0.62 * lob * (1 - t) ** 3.6
        z = H * t
        fur = 1.0 - 2.0 * abs(mnoise.noise(Vector((a * 7.0 + 0.8 * mnoise.noise(Vector((z * 4.0, a * 2.0, seed))), z * 1.2, seed))))     # ridged: sharp furrows
        fur2 = mnoise.noise(Vector((a * 19.0, z * 4.0, seed + 5.0)))
        lump = mnoise.noise(Vector((math.cos(a) * 2.2 + seed, math.sin(a) * 2.2, z * 5.0)))
        r += R * (0.050 * fur + 0.020 * fur2 + 0.060 * lump)
        return r * (1.0 + 0.07 * mnoise.noise(Vector((math.cos(a) * 0.8 + seed, math.sin(a) * 0.8, 0.3))))
    verts, faces = [], []
    for j in range(rings + 1):
        t = j / rings
        for i in range(seg):
            a = 2 * PI * i / seg
            r = rad(a, t)
            x, y = r * math.cos(a), r * math.sin(a)
            z = -0.05 + (H + 0.05) * t
            if j == rings:
                z = ztop(x, y)
            elif t > 0.6:
                z = min(z, ztop(x, y) - (1 - t) * 0.05)
            verts.append((x, y, z))
    for j in range(rings):
        for i in range(seg):
            a, b = j * seg + i, j * seg + (i + 1) % seg
            faces.append((a, b, b + seg, a + seg))
    top0 = rings * seg
    # the bark's thickness seen on the cut
    for i in range(seg):
        a = 2 * PI * i / seg
        r = rad(a, 1.0) * 0.945
        x, y = r * math.cos(a), r * math.sin(a)
        verts.append((x, y, ztop(x, y) + 0.004))
    for i in range(seg):
        a, b = top0 + i, top0 + (i + 1) % seg
        faces.append((a, b, b + seg, a + seg))
    side = mesh(verts, faces, "Bark")
    for f in side.data.polygons:
        f.use_smooth = True
    # the face
    verts, faces = [], []
    cr = 16
    for k in range(cr + 1):
        f = 1.0 - k / cr
        for i in range(seg):
            a = 2 * PI * i / seg
            r = rad(a, 1.0) * 0.945 * f
            x, y = r * math.cos(a), r * math.sin(a)
            verts.append((x, y, ztop(x, y) + 0.004 * f))
    for k in range(cr):
        for i in range(seg):
            a, b = k * seg + i, k * seg + (i + 1) % seg
            faces.append((a, b, b + seg, a + seg))
    face = mesh(verts, faces, "Heartwood")
    bpy.ops.object.select_all(action="DESELECT")
    face.select_set(True)
    bpy.context.view_layer.objects.active = face
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.remove_doubles(threshold=0.0004)
    bpy.ops.object.mode_set(mode="OBJECT")
    for f in face.data.polygons:
        f.use_smooth = True
    P = [side, face]
    rr = random.Random(int(seed * 100))
    if hinge:                                                                # fibres torn where the trunk went over
        yw = R * 0.80
        for i in range(16):
            y = rr.uniform(-yw, yw)
            hgt = rr.uniform(0.012, 0.075) * (1.0 - 0.6 * abs(y) / yw)
            w = rr.uniform(0.006, 0.022)
            x = hx - 0.006 + rr.uniform(-0.004, 0.004)
            z = ztop(x - 0.02, y)
            P.append(mesh([(x - 0.006, y - w, z - 0.01), (x + 0.008, y - w, z - 0.01), (x + 0.008, y + w, z - 0.01), (x - 0.006, y + w, z - 0.01),
                           (x - 0.001 + rr.uniform(-0.004, 0.006), y + rr.uniform(-w, w) * 0.4, z + hgt)],
                          [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)], "Heartwood"))
    return P, ztop


def stump():
    return stump_parts(0.27, 0.40, 1.3, 6, True, 0.05)[0]


def stump_rot():
    return stump_parts(0.22, 0.34, 4.1, 5, False, 0.10, broken=(2.2, 0.9, 0.62))[0]


def axe():
    """Built lying along X, the edge toward +X at the origin, the handle running back along -X... then stood in the block."""
    out = [(0.0, -0.062), (-0.045, -0.050), (-0.085, -0.032), (-0.150, -0.030), (-0.185, -0.034), (-0.185, 0.034), (-0.150, 0.030),
           (-0.085, 0.030), (-0.045, 0.046), (0.0, 0.062), (0.006, 0.0)]
    head = plate(out, 0.040, "Iron", 0.0, -0.020)
    for v in head.data.vertices:                                            # a wedge: full thickness at the eye, an edge at the bit
        p = v.co
        k = 0.06 + 0.94 * min(1.0, max(0.0, -p.x / 0.11)) ** 0.8
        p.z *= k
    head = moved(head, rot=(PI / 2, 0, 0))                                   # the blade now stands in the XZ plane
    for f in head.data.polygons:
        f.use_smooth = False
    P = [head]
    pts = []
    for k in range(13):
        t = k / 12
        pts.append((-0.150 + 0.012 * math.sin(t * PI) - 0.02 * t * t, 0.0, 0.03 - 0.80 * t))
    haft = tube(pts, 0.0165, "WoodGrey", res=3)
    for v in haft.data.vertices:
        v.co.y *= 0.72
        if v.co.z < -0.66:                                                   # the swell at the end
            v.co.x += 0.0; v.co.y *= 1.25
    P.append(haft)
    return P


def stump_axe():
    P, ztop = stump_parts(0.31, 0.52, 2.2, 7, False, 0.025)
    a = moved(axe(), (0.0, 0.0, 0.0), (0, math.radians(118), 0))             # edge down, haft up and back
    a = moved(a, (0.03, 0.02, ztop(0.03, 0.02) - 0.028), (0, 0, math.radians(35)))
    P += a
    rr = random.Random(9)
    for i in range(22):                                                      # chips: on the block and thrown round its foot
        on = i < 6
        d, ang = (rr.uniform(0.03, 0.24), rr.uniform(0, 2 * PI)) if on else (rr.uniform(0.42, 0.85), rr.uniform(0, 2 * PI))
        x, y = d * math.cos(ang), d * math.sin(ang)
        z = (ztop(x, y) + 0.006) if on else 0.006
        L, w, t = rr.uniform(0.03, 0.10), rr.uniform(0.012, 0.035), rr.uniform(0.003, 0.009)
        c = box(L, w, t, (0, 0, 0), m="Chip")
        for v in c.data.vertices:
            v.co.z += 0.25 * t * (1 if v.co.x > 0 else -1) * (1 if v.co.y > 0 else -1)      # a twist, as split wood has
        P.append(moved(c, (x, y, z), (rr.uniform(-0.2, 0.2), rr.uniform(-0.2, 0.2), rr.uniform(0, PI))))
    return P


# ============================================================================================ field stones
def rock(r, scale, seed, sink=0.25):
    b = blob(r, "Rock", (0, 0, 0), scale, 0.20, 1.3, seed, sub=5)
    for v in b.data.vertices:                                                # a second, finer roughness: knobs and hollows the size of a fist
        p = v.co
        v.co = p * (1.0 + 0.05 * mnoise.noise(p * (5.0 / r) + Vector((seed, 2.0, 7.0))) + 0.022 * mnoise.noise(p * (13.0 / r) + Vector((1.0, seed, 3.0))))
    for v in b.data.vertices:                                                # break the roundness: a few flat cleavage planes
        p = v.co
        for k in range(4):
            nrm = Vector((mnoise.noise(Vector((k * 3.3, seed, 0.1))), mnoise.noise(Vector((k * 1.9, seed, 5.2))), 0.4 + 0.5 * mnoise.noise(Vector((k * 2.7, seed, 9.9))))).normalized()
            dd = p.dot(nrm) - r * scale[2] * 0.80
            if dd > 0:
                p -= nrm * dd * 0.7
    for v in b.data.vertices:
        v.co.z += r * scale[2] * (1.0 - sink)
        v.co.z = max(v.co.z, -0.03)
    return [b]


# ============================================================================================ the woodpile
def split_log(L, R, arc, seed, loc=(0, 0, 0), rot=(0, 0, 0)):
    """A length of trunk split with the axe: bark on the round, bare wood on the split faces and the sawn ends.
    Lies along X.  arc = how much of the round is left (radians): pi = a half, pi/2 = a quarter."""
    seg, n = 12, 9
    bark_v, bark_f, wood_v, wood_f = [], [], [], []
    rr = random.Random(seed)
    for i in range(n + 1):
        x = L * (i / n - 0.5)
        for k in range(seg + 1):
            a = -arc / 2 + arc * k / seg
            r = R * (1.0 + 0.07 * mnoise.noise(Vector((x * 6.0, a * 3.0, seed))) + 0.03 * mnoise.noise(Vector((x * 2.0, a * 9.0, seed + 3.0))))
            bark_v.append((x, r * math.sin(a), r * math.cos(a)))
    for i in range(n):
        for k in range(seg):
            q = i * (seg + 1) + k
            bark_f.append((q, q + seg + 1, q + seg + 2, q + 1))
    # split faces and ends: the edge of the bark, joined to a wandering line through the heart
    for i in range(n + 1):
        x = L * (i / n - 0.5)
        hz = R * 0.04 * mnoise.noise(Vector((x * 9.0, seed, 1.0)))
        wood_v += [bark_v[i * (seg + 1)], (x, 0.0 + R * 0.05 * mnoise.noise(Vector((x * 7.0, seed, 2.0))), hz), bark_v[i * (seg + 1) + seg]]
    for i in range(n):
        q = i * 3
        wood_f += [(q, q + 1, q + 4, q + 3), (q + 1, q + 2, q + 5, q + 4)]
    for end, i in ((0, 0), (1, n)):
        base = len(wood_v)
        ring = [bark_v[i * (seg + 1) + k] for k in range(seg + 1)]
        wood_v += ring + [wood_v[i * 3 + 1]]
        for k in range(seg):
            wood_f.append((base + k, base + k + 1, base + seg + 1) if end else (base + k + 1, base + k, base + seg + 1))
    b = mesh(bark_v, bark_f, "Bark")
    w = mesh(wood_v, wood_f, "Heartwood")
    for f in b.data.polygons:
        f.use_smooth = True
    return moved([b, w], loc, rot)


def woodpile():
    """A cord of split firewood stacked between two stakes and left to rot: three tiers, the top one slumped, a few
    lengths rolled off the end."""
    P = []
    rr = random.Random(21)
    L = 0.42
    y = -0.62
    z = 0.075
    tier = 0
    while tier < 4:
        y = -0.62 + (0.07 if tier % 2 else 0.0)
        while y < 0.62 - 0.02 * tier * tier:
            R = rr.uniform(0.07, 0.105)
            arc = rr.choice((PI, PI, PI * 0.5, PI * 0.66, PI * 1.25))
            roll = rr.uniform(0, 2 * PI)
            if tier == 3 and rr.random() < 0.45:
                y += R * 1.6
                continue
            P += split_log(L * rr.uniform(0.9, 1.08), R, arc, rr.random() * 50, (rr.uniform(-0.025, 0.025), y, z + rr.uniform(-0.01, 0.012)),
                           (roll, rr.uniform(-0.05, 0.05), rr.uniform(-0.09, 0.09)))
            y += R * rr.uniform(1.55, 1.9)
        z += 0.135
        tier += 1
    for (x, y, zr, a) in ((0.34, 0.30, 0.3, 0.9), (0.42, -0.25, 1.9, -0.5), (-0.38, 0.52, 0.2, 2.2), (0.30, 0.78, 2.6, 1.3), (-0.05, -0.84, 1.1, 0.3)):   # rolled off
        P += split_log(L, rr.uniform(0.07, 0.10), rr.choice((PI, PI * 0.5)), rr.random() * 50, (x, y, 0.055), (zr, 0.0, a))
    for sy in (-0.70, 0.70):                                                 # the stakes that held the ends
        P.append(moved(rod((0, 0, -0.02), (0, 0, 0.78), 0.028, "WoodGrey", 10), (0.0, sy, 0.0), (0.0, math.radians(4 if sy > 0 else -3), 0.0)))
    return P


UV_ANGLE.update({"Wheelbarrow": 89, "RockA": 89, "RockB": 89, "RockC": 89, "Stump": 80, "StumpRot": 80, "StumpAxe": 80, "Woodpile": 80})
for _n, _f, _s in (("Wheelbarrow", wheelbarrow, 2048), ("Stump", stump, 2048), ("StumpRot", stump_rot, 2048), ("StumpAxe", stump_axe, 2048),
                   ("RockA", lambda: rock(0.34, (1.25, 0.95, 0.62), 1.0), 1024), ("RockB", lambda: rock(0.22, (1.0, 1.15, 0.7), 2.0), 1024),
                   ("RockC", lambda: rock(0.55, (1.1, 0.8, 0.5), 3.0, 0.35), 1024), ("Woodpile", woodpile, 2048)):
    build(_n, _f, _s)
