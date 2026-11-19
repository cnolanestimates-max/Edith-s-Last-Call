"""Blender: skin options for Edith in the directions of Cheyenne's eight texture references (2026-11-19 17:04 UTC: "all of
these are nicer textures than what she has on her right now ... retrofit one of these onto her, give me some different
options").  The references are other artists' pictures, so nothing is copied from them: each look is rebuilt as an original
procedural skin in her own space, in her dark tone.  The face Codex fitted from the approved C portrait is kept where it lies
(portrait_mask.png); the options dress everything else, unless --face is given (then the option covers the face as well).

  blender -b --factory-startup -P her_tex.py -- <project root> <work dir> <out dir> [--face] [--views face,bust] names...

Previews only.  Nothing is written into the game.
Looks: now (what is in the game), A crosshatch, B scales, C pores, D crust, E blisters, F flesh, G veins."""
import bpy, math, os, sys
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
ROOT, WORK, OUT = argv[0], argv[1], argv[2]
rest = argv[3:]
FACE = "--face" in rest
VIEWS = ("face", "bust")
if "--views" in rest:
    VIEWS = tuple(rest[rest.index("--views") + 1].split(","))
    del rest[rest.index("--views"):rest.index("--views") + 2]
NAMES = [n for n in rest if not n.startswith("--")]
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=ROOT + "/SourceArt/Her/export/SK_Her.fbx")
sc = bpy.context.scene
mesh = max((o for o in sc.objects if o.type == "MESH"), key=lambda o: len(o.data.vertices))
bb = [mesh.matrix_world @ Vector(c) for c in mesh.bound_box]
zmin, zmax = min(v.z for v in bb), max(v.z for v in bb)
K = (zmax - zmin) / 270.0
KO = (max(c[2] for c in mesh.bound_box) - min(c[2] for c in mesh.bound_box)) / 270.0
TINT = 0.46            # the game darkens her maps; her_look.py previews use the same factor


def cm(x, y, z):
    return Vector((x * K, y * K, zmin + z * K))


def image(nt, path, non_color):
    n = nt.nodes.new("ShaderNodeTexImage")
    n.image = bpy.data.images.load(path, check_existing=True)
    if non_color:
        n.image.colorspace_settings.name = "Non-Color"
    return n


BAKE = {}


def build(name):
    m = bpy.data.materials.new("her_" + name)
    m.use_nodes = True
    nt = m.node_tree
    N, L = nt.nodes, nt.links
    b = N["Principled BSDF"]

    def math_(op, a, c=None, clamp=False):
        n = N.new("ShaderNodeMath"); n.operation = op; n.use_clamp = clamp
        for i, v in enumerate((a, c)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = v
            else:
                L.new(v, n.inputs[i])
        return n.outputs[0]

    def ramp(v, lo, hi, smooth=True):
        n = N.new("ShaderNodeMapRange"); n.inputs["From Min"].default_value = lo; n.inputs["From Max"].default_value = hi
        n.interpolation_type = "SMOOTHSTEP" if smooth else "LINEAR"; L.new(v, n.inputs["Value"]); return n.outputs[0]

    def inv(v):
        return math_("SUBTRACT", 1.0, v)

    def mix(c1, c2, f, blend="MIX"):
        n = N.new("ShaderNodeMixRGB"); n.blend_type = blend
        for i, v in ((0, f), (1, c1), (2, c2)):
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = v if i == 0 else (v, v, v, 1)
            elif isinstance(v, tuple):
                n.inputs[i].default_value = (v[0], v[1], v[2], 1)
            else:
                L.new(v, n.inputs[i])
        return n.outputs[0]

    tc = N.new("ShaderNodeTexCoord")
    tocm = N.new("ShaderNodeMapping"); tocm.inputs["Scale"].default_value = (1 / KO, 1 / KO, 1 / KO)        # object space in centimetres
    L.new(tc.outputs["Object"], tocm.inputs["Vector"])
    P = tocm.outputs[0]

    def mapped(scale, vec=None):
        n = N.new("ShaderNodeMapping"); n.inputs["Scale"].default_value = scale; L.new(vec if vec is not None else P, n.inputs["Vector"]); return n.outputs[0]

    def noise(vec, scale, detail=3.0, rough=0.55, color=False):
        n = N.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = scale; n.inputs["Detail"].default_value = detail
        n.inputs["Roughness"].default_value = rough; L.new(vec, n.inputs["Vector"]); return n.outputs[1 if color else 0]

    def cells(vec, scale, feature="DISTANCE_TO_EDGE", rand=1.0, out="Distance", smooth=0.5):
        n = N.new("ShaderNodeTexVoronoi"); n.feature = feature; n.inputs["Scale"].default_value = scale
        n.inputs["Randomness"].default_value = rand; L.new(vec, n.inputs["Vector"])
        if feature == "SMOOTH_F1":
            n.inputs["Smoothness"].default_value = smooth
        return n.outputs[out]

    def waves(vec, scale, distortion, direction="Z"):
        n = N.new("ShaderNodeTexWave"); n.wave_type = "BANDS"; n.bands_direction = direction; n.wave_profile = "SIN"
        n.inputs["Scale"].default_value = scale; n.inputs["Distortion"].default_value = distortion
        n.inputs["Detail"].default_value = 3.0; n.inputs["Detail Scale"].default_value = 1.6; n.inputs["Detail Roughness"].default_value = 0.6
        L.new(vec, n.inputs["Vector"]); return n.outputs["Fac"]

    def warped(amount, scale):
        w = noise(P, scale, 2.0, color=True)
        wv = N.new("ShaderNodeVectorMath"); wv.operation = "SCALE"; wv.inputs["Scale"].default_value = amount
        L.new(w, wv.inputs[0])
        add = N.new("ShaderNodeVectorMath"); add.operation = "ADD"; L.new(P, add.inputs[0]); L.new(wv.outputs[0], add.inputs[1])
        return add.outputs[0]
    Pw = warped(3.2, 0.22)           # slow: wrinkles wander
    Pf = warped(0.35, 1.3)           # quick and small: cell edges are not ruler-straight

    def gray(v):
        n = N.new("ShaderNodeRGBToBW"); L.new(v, n.inputs[0]); return n.outputs[0]

    # ---- what each bit of her is (from her original map): hair, dress, inside the mouth, skin
    old = image(nt, ROOT + "/SourceArt/Her/export/T_Her_BaseColor.png", False)
    gam = N.new("ShaderNodeGamma"); gam.inputs["Gamma"].default_value = 1 / 2.2; L.new(old.outputs["Color"], gam.inputs["Color"])
    sep = N.new("ShaderNodeSeparateColor"); L.new(gam.outputs[0], sep.inputs[0])
    val = math_("MAXIMUM", sep.outputs[0], math_("MAXIMUM", sep.outputs[1], sep.outputs[2]))
    m_hair = ramp(math_("DIVIDE", math_("SUBTRACT", sep.outputs[0], sep.outputs[2]), math_("MAXIMUM", sep.outputs[0], 0.05)), 0.078, 0.102)
    sp = N.new("ShaderNodeSeparateXYZ"); L.new(P, sp.inputs[0])
    ax = math_("ABSOLUTE", sp.outputs[0])
    m_dress = math_("MULTIPLY", math_("MULTIPLY", ramp(sp.outputs[2], 97.0, 103.0), inv(ramp(sp.outputs[2], 201.0, 207.0))), inv(ramp(ax, 25.0, 30.0)))
    m_dress = math_("MULTIPLY", m_dress, inv(m_hair))
    m_dark = inv(ramp(val, 0.10, 0.26))
    m_skin = math_("SUBTRACT", 1.0, math_("MAXIMUM", m_hair, m_dress), clamp=True)
    # ---- what is in the game now: Codex's maps (the approved C portrait on the front of her face)
    cur = image(nt, ROOT + "/SourceArt/Her/look_c/T_Her_BaseColor.png", False)
    curc = mix(cur.outputs["Color"], (TINT, TINT * 0.92, TINT * 0.84), 1.0, "MULTIPLY")
    pm = image(nt, WORK + "/portrait_mask.png", True).outputs["Color"]
    pmask = gray(pm) if not FACE else math_("MULTIPLY", gray(pm), 0.0)
    if name != "now":
        # the portrait was laid on from straight ahead, so below the nose it is dragged into streaks down her long jaw:
        # keep it for the brow, eye, cheek and nose, and let the option take over from the nose down
        pmask = math_("MULTIPLY", pmask, ramp(sp.outputs[2], 229.0, 235.0))
    nm = N.new("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value = 0.8
    L.new(image(nt, ROOT + "/SourceArt/Her/look_c/T_Her_Normal.png", True).outputs["Color"], nm.inputs["Color"])
    ao = N.new("ShaderNodeAmbientOcclusion"); ao.inputs["Distance"].default_value = 7.0 * K; ao.samples = 4
    crev = inv(ao.outputs["AO"])
    # shared: the long folds of an old body
    fold = math_("MULTIPLY", waves(Pw, 0.55, 5.5), ramp(noise(P, 0.3, 2.0), 0.25, 0.7))
    fold = math_("MAXIMUM", fold, math_("MULTIPLY", waves(Pw, 1.25, 7.0), 0.55))
    fold = inv(math_("POWER", fold, 3.0))                       # 0 down in the crease, 1 on the flat
    c_fold = inv(ramp(fold, 0.15, 0.75))
    mott = noise(P, 0.085, 5.0, 0.62)
    wetmask = ramp(noise(P, 0.11, 3.0), 0.40, 0.62)

    bump, dist = 1.0, 0.30
    sss, coat = 0.25, math_("MULTIPLY", wetmask, 0.35)
    if name == "now":
        col, h, rough = curc, math_("MULTIPLY", fold, 0.0), math_("ADD", 0.55, 0.0)
        pmask = math_("ADD", pmask, 1.0, clamp=True)
    elif name == "A":
        # crosshatched old skin (references 1 and 2): a lattice of fine creases in two sizes, lying along the body, over the long folds
        pa = mapped((1.0, 1.0, 0.62), Pf)
        e1 = cells(pa, 4.2)                                    # about 2.4 mm
        e2 = cells(mapped((1.0, 1.0, 0.7), Pf), 9.5)           # about 1 mm
        tone = gray(cells(pa, 4.2, feature="F1", out="Color"))
        cr1, cr2 = inv(ramp(e1, 0.0, 0.075)), inv(ramp(e2, 0.0, 0.09))
        col = mix((0.070, 0.038, 0.024), (0.150, 0.092, 0.060), ramp(mott, 0.34, 0.66))
        col = mix(col, (0.5, 0.5, 0.5), ramp(tone, 0.0, 1.0), "OVERLAY")
        col = mix(col, (0.022, 0.010, 0.007), math_("MULTIPLY", cr1, 0.85))
        col = mix(col, (0.030, 0.014, 0.010), math_("MULTIPLY", cr2, 0.40))
        col = mix(col, (0.050, 0.012, 0.009), math_("MULTIPLY", c_fold, 0.55))
        h = math_("ADD", math_("MULTIPLY", fold, 1.0), math_("MULTIPLY", ramp(e1, 0.0, 0.16), 0.42))
        h = math_("ADD", h, math_("MULTIPLY", ramp(e2, 0.0, 0.14), 0.14))
        rough = math_("SUBTRACT", 0.58, math_("MULTIPLY", wetmask, 0.22))
        rough = math_("ADD", rough, math_("MULTIPLY", cr1, 0.15))
    elif name == "B":
        # dry cracked scales (reference 2 taken dry, toward 4): plates the size of a fingernail, domed, split by dark red cracks
        e1 = cells(Pf, 1.55)                                   # about 6.5 mm
        e2 = cells(Pf, 4.8)
        tone = gray(cells(Pf, 1.55, feature="F1", out="Color"))
        cr1, cr2 = inv(ramp(e1, 0.0, 0.085)), inv(ramp(e2, 0.0, 0.07))
        col = mix((0.085, 0.050, 0.033), (0.185, 0.125, 0.088), ramp(tone, 0.15, 0.85))
        col = mix(col, (0.24, 0.19, 0.15), math_("MULTIPLY", ramp(noise(Pf, 2.2, 3.0), 0.55, 0.75), 0.5))      # dead, lifting skin, paler
        col = mix(col, (0.060, 0.007, 0.006), math_("MULTIPLY", cr1, 0.92))
        col = mix(col, (0.035, 0.016, 0.012), math_("MULTIPLY", cr2, 0.5))
        col = mix(col, (0.040, 0.010, 0.008), math_("MULTIPLY", c_fold, 0.45))
        h = math_("ADD", math_("MULTIPLY", fold, 0.8), math_("MULTIPLY", ramp(e1, 0.0, 0.38), 1.1))
        h = math_("ADD", h, math_("MULTIPLY", ramp(e2, 0.0, 0.12), 0.16))
        rough = math_("ADD", 0.74, math_("MULTIPLY", cr1, -0.25))
        coat = math_("MULTIPLY", cr1, 0.5)                     # the cracks are wet, the plates dry
        bump = 1.25
    elif name == "C":
        # pored, blotched skin (reference 3): open pores, red blotches, broken veins, a few dark moles
        f1 = cells(Pf, 7.5, feature="F1")
        pit = inv(ramp(f1, 0.0, 0.26))
        fine = cells(mapped((1.0, 1.0, 0.7), Pf), 6.0)
        blot = ramp(noise(P, 0.16, 4.0, 0.6), 0.50, 0.68)
        speck = ramp(noise(P, 3.2, 2.0), 0.66, 0.74)
        mole = ramp(noise(P, 0.9, 2.0), 0.74, 0.78)
        col = mix((0.105, 0.062, 0.044), (0.185, 0.120, 0.090), ramp(mott, 0.34, 0.66))
        col = mix(col, (0.150, 0.022, 0.018), math_("MULTIPLY", blot, 0.55))
        col = mix(col, (0.130, 0.012, 0.012), math_("MULTIPLY", speck, 0.6))
        col = mix(col, (0.030, 0.012, 0.008), math_("MULTIPLY", pit, 0.75))
        col = mix(col, (0.012, 0.007, 0.005), math_("MULTIPLY", mole, 0.85))
        col = mix(col, (0.040, 0.014, 0.010), math_("MULTIPLY", inv(ramp(fine, 0.0, 0.06)), 0.35))
        col = mix(col, (0.050, 0.012, 0.009), math_("MULTIPLY", c_fold, 0.5))
        h = math_("SUBTRACT", math_("MULTIPLY", fold, 1.0), math_("MULTIPLY", pit, 0.42))
        h = math_("ADD", h, math_("MULTIPLY", ramp(fine, 0.0, 0.1), 0.14))
        rough = math_("SUBTRACT", 0.50, math_("MULTIPLY", wetmask, 0.22))
        sss = 0.35
    elif name == "D":
        # crusted scabs (reference 4): beds of granular red-purple crust standing on blue-black cracked skin
        bed = ramp(math_("ADD", noise(Pw, 0.42, 4.0, 0.6), math_("MULTIPLY", math_("SUBTRACT", noise(P, 2.0, 2.0), 0.5), 0.25)), 0.44, 0.54)
        g1 = cells(Pf, 5.5, feature="F1")
        gran = inv(ramp(g1, 0.0, 0.46))                         # each grain a little dome
        gtone = gray(cells(Pf, 5.5, feature="F1", out="Color"))
        e1 = cells(Pf, 2.0)
        crk = inv(ramp(e1, 0.0, 0.07))
        base = mix((0.016, 0.016, 0.030), (0.040, 0.034, 0.050), ramp(mott, 0.3, 0.7))
        base = mix(base, (0.004, 0.004, 0.006), math_("MULTIPLY", crk, 0.9))
        crust = mix((0.130, 0.016, 0.040), (0.215, 0.030, 0.028), ramp(gtone, 0.1, 0.9))
        crust = mix(crust, (0.045, 0.006, 0.012), inv(ramp(gran, 0.05, 0.5)))
        col = mix(base, crust, bed)
        h = math_("ADD", math_("MULTIPLY", fold, 0.5), math_("MULTIPLY", bed, 0.9))
        h = math_("ADD", h, math_("MULTIPLY", math_("MULTIPLY", bed, gran), 0.9))
        h = math_("ADD", h, math_("MULTIPLY", math_("MULTIPLY", inv(bed), ramp(e1, 0.0, 0.2)), 0.4))
        rough = mix(0.36, 0.82, bed)
        coat = math_("MULTIPLY", inv(bed), 0.5)
        bump = 1.35
    elif name == "E":
        # wet blisters (reference 5): raw red skin with a fine weave, glossy blisters of two sizes risen out of it
        n1 = N.new("ShaderNodeTexVoronoi"); n1.feature = "F1"; n1.inputs["Scale"].default_value = 2.1; L.new(Pf, n1.inputs["Vector"])
        r1 = math_("ADD", 0.10, math_("MULTIPLY", ramp(gray(n1.outputs["Color"]), 0.45, 1.0), 0.26))
        dome1 = math_("SQRT", math_("MAXIMUM", inv(math_("POWER", math_("DIVIDE", n1.outputs["Distance"], r1), 2.0)), 0.0))
        dome1 = math_("MULTIPLY", dome1, ramp(gray(n1.outputs["Color"]), 0.42, 0.48))
        n2 = N.new("ShaderNodeTexVoronoi"); n2.feature = "F1"; n2.inputs["Scale"].default_value = 5.2; L.new(Pf, n2.inputs["Vector"])
        dome2 = math_("SQRT", math_("MAXIMUM", inv(math_("POWER", math_("DIVIDE", n2.outputs["Distance"], 0.22), 2.0)), 0.0))
        dome2 = math_("MULTIPLY", dome2, ramp(gray(n2.outputs["Color"]), 0.62, 0.68))
        dome = math_("MAXIMUM", dome1, math_("MULTIPLY", dome2, 0.6))
        weave = math_("MULTIPLY", waves(P, 22.0, 0.0, "X"), waves(P, 22.0, 0.0, "Z"))
        col = mix((0.105, 0.012, 0.010), (0.180, 0.030, 0.022), ramp(mott, 0.3, 0.7))
        col = mix(col, (0.045, 0.006, 0.006), math_("MULTIPLY", ramp(weave, 0.2, 0.7), 0.35))
        col = mix(col, (0.260, 0.050, 0.038), math_("MULTIPLY", ramp(dome, 0.0, 0.5), 0.8))
        col = mix(col, (0.035, 0.005, 0.005), math_("MULTIPLY", c_fold, 0.5))
        h = math_("ADD", math_("MULTIPLY", fold, 0.6), math_("MULTIPLY", dome, 1.5))
        h = math_("ADD", h, math_("MULTIPLY", weave, 0.06))
        rough = mix(0.48, 0.06, ramp(dome, 0.0, 0.4))
        coat = ramp(dome, 0.0, 0.3)
        sss, bump, dist = 0.4, 1.3, 0.34
    elif name == "F":
        # raw wet flesh (reference 7): swollen lumps of two sizes, deep red-brown, dark in the gaps, wet all over
        l1 = cells(Pw, 0.55, feature="SMOOTH_F1", smooth=0.35)  # about 1.8 cm
        l2 = cells(Pf, 1.5, feature="SMOOTH_F1", smooth=0.35)
        lump1, lump2 = inv(ramp(l1, 0.05, 0.80)), inv(ramp(l2, 0.05, 0.75))
        lump = math_("ADD", math_("MULTIPLY", lump1, 0.7), math_("MULTIPLY", lump2, 0.3))
        col = mix((0.040, 0.005, 0.004), (0.200, 0.036, 0.016), ramp(lump, 0.15, 0.8))
        col = mix(col, (0.260, 0.110, 0.045), math_("MULTIPLY", ramp(noise(Pf, 1.1, 3.0), 0.6, 0.78), 0.45))      # fat showing yellow
        col = mix(col, (0.090, 0.006, 0.010), math_("MULTIPLY", ramp(noise(P, 0.4, 3.0), 0.55, 0.7), 0.5))
        h = math_("ADD", math_("MULTIPLY", lump1, 1.6), math_("MULTIPLY", lump2, 0.7))
        rough = math_("ADD", 0.10, math_("MULTIPLY", ramp(noise(P, 3.0, 2.0), 0.4, 0.7), 0.10))
        coat = math_("ADD", 0.9, 0.0)
        sss, bump, dist = 0.45, 1.5, 0.5
    elif name == "G":
        # pale flesh with raised veins (reference 8): a web of dark red vessels standing up under thin, wet, pinkish skin
        v1 = cells(Pw, 0.42)                                    # trunks
        v2 = cells(warped(1.2, 0.6), 1.25)                      # branches
        v3 = cells(Pf, 3.4)                                     # threads
        t1, t2, t3 = inv(ramp(v1, 0.0, 0.050)), inv(ramp(v2, 0.0, 0.050)), inv(ramp(v3, 0.0, 0.045))
        vein = math_("MAXIMUM", t1, math_("MAXIMUM", math_("MULTIPLY", t2, 0.85), math_("MULTIPLY", t3, 0.45)))
        col = mix((0.150, 0.075, 0.070), (0.250, 0.150, 0.140), ramp(mott, 0.3, 0.7))
        col = mix(col, (0.200, 0.030, 0.030), math_("MULTIPLY", ramp(noise(P, 0.25, 4.0), 0.5, 0.7), 0.5))
        col = mix(col, (0.085, 0.004, 0.008), math_("MULTIPLY", vein, 0.92))
        col = mix(col, (0.060, 0.010, 0.010), math_("MULTIPLY", c_fold, 0.4))
        h = math_("ADD", math_("MULTIPLY", fold, 0.6), math_("MULTIPLY", t1, 1.0))
        h = math_("ADD", h, math_("ADD", math_("MULTIPLY", t2, 0.6), math_("MULTIPLY", t3, 0.2)))
        rough = math_("ADD", 0.20, math_("MULTIPLY", vein, 0.1))
        coat = math_("ADD", 0.7, 0.0)
        sss, bump = 0.6, 1.2
    else:
        raise RuntimeError("no such look: " + name)

    # ---- keep Codex's portrait where it lies; hair and dress as they are in the game; the mouth dark
    col = mix(col, (0, 0, 0), math_("MULTIPLY", crev, 0.7))
    # the same colour as a map for the game: the game darkens her maps by TINT, so the new skin is stored brighter by as much,
    # and Codex's map goes through untouched wherever it is kept
    cb_ = mix(col, (1 / TINT, 1 / (TINT * 0.92), 1 / (TINT * 0.84)), 1.0, "MULTIPLY")
    cb_ = mix(cb_, cur.outputs["Color"], pmask)
    cb_ = mix(mix(cb_, cur.outputs["Color"], m_dress), cur.outputs["Color"], m_hair)
    cb_ = mix(cb_, (0.03, 0.006, 0.006), m_dark)
    col = mix(col, curc, pmask)
    col = mix(mix(col, curc, m_dress), curc, m_hair)
    col = mix(col, (0.012, 0.002, 0.002), m_dark)
    L.new(col, b.inputs["Base Color"])
    keep = math_("MULTIPLY", m_skin, inv(math_("MULTIPLY", pmask, 0.85)))
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.75 * bump; bp.inputs["Distance"].default_value = dist * K
    L.new(math_("MULTIPLY", h, keep), bp.inputs["Height"]); L.new(nm.outputs[0], bp.inputs["Normal"])
    L.new(bp.outputs[0], b.inputs["Normal"])
    curr = gray(image(nt, ROOT + "/SourceArt/Her/look_c/T_Her_Roughness.png", True).outputs["Color"])
    rb_ = mix(mix(mix(rough, curr, pmask), curr, m_dress), curr, m_hair)
    rb_ = mix(rb_, 0.12, m_dark)
    rough = mix(mix(mix(rough, 0.55, pmask), 0.9, m_dress), 0.45, m_hair)
    rough = mix(rough, 0.12, m_dark)
    L.new(rough, b.inputs["Roughness"])
    m["_bake"] = 1
    BAKE[m.name] = {"color": cb_, "rough": rb_, "nt": nt, "bsdf": b}
    for key, v in (("Subsurface Scale", 0.6 * K), ("Specular IOR Level", 0.6), ("Coat Roughness", 0.10)):
        if key in b.inputs:
            b.inputs[key].default_value = v
    if "Subsurface Weight" in b.inputs:
        L.new(math_("MULTIPLY", m_skin, sss), b.inputs["Subsurface Weight"])
    if "Subsurface Radius" in b.inputs:
        b.inputs["Subsurface Radius"].default_value = (1.0, 0.35, 0.22)
    if "Coat Weight" in b.inputs:
        L.new(math_("MULTIPLY", math_("MULTIPLY", coat, keep), 1.0), b.inputs["Coat Weight"])
    return m


sc.render.engine = "CYCLES"
sc.cycles.device = "CPU"
sc.render.threads_mode = "FIXED"; sc.render.threads = 8
sc.cycles.samples = 40
sc.cycles.use_denoising = True
try:
    sc.view_settings.view_transform = "Standard"; sc.view_settings.look = "Medium High Contrast"
except Exception as exc:
    print("HERTEX view", exc)
sc.render.resolution_x = 640; sc.render.resolution_y = 720
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.010, 0.012, 0.016, 1)
cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
cam.data.clip_start = 0.5 * K; cam.data.clip_end = 5000 * K


def light(name, kind, loc, target, watts, color, size):
    d = bpy.data.lights.new(name, kind); d.energy = watts; d.color = color
    if kind == "SPOT":
        d.spot_size = math.radians(70); d.spot_blend = 0.6
    d.shadow_soft_size = size * K
    o = bpy.data.objects.new(name, d); sc.collection.objects.link(o)
    o.location = loc; o.rotation_euler = (target - loc).to_track_quat("-Z", "Y").to_euler()
    return o


face = cm(1.0, -22.0, 236.0)
light("flash", "SPOT", cm(-22, -115, 205), cm(0, -15, 215), 190.0, (1.0, 0.90, 0.76), 1.5)
light("rim", "POINT", cm(60, 55, 262), face, 25.0, (0.55, 0.70, 1.0), 6.0)


def ball(r, loc, colr, rough_):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r * K, segments=40, ring_count=20, location=loc)
    o = bpy.context.object; bpy.ops.object.shade_smooth()
    mm = bpy.data.materials.new("eye"); mm.use_nodes = True
    bb_ = mm.node_tree.nodes["Principled BSDF"]; bb_.inputs["Base Color"].default_value = (colr[0], colr[1], colr[2], 1); bb_.inputs["Roughness"].default_value = rough_
    o.data.materials.append(mm)
    return o


ball(4.3, cm(6.0, -21.9, 246.6), (0.002, 0.002, 0.002), 0.04)
ir = ball(1.0, cm(6.0, -21.9 - 4.3 * 0.80, 246.6), (0.30, 0.36, 0.40), 0.3); ir.scale = (1.46, 1.3, 1.46)
pu = ball(1.0, cm(6.0, -21.9 - 4.3 * 0.985, 246.6), (0.001, 0.001, 0.001), 0.05); pu.scale = (0.69, 0.6, 0.69)
if "--bake" in argv:
    # 4K maps of one look, written beside (not over) the maps the game uses now
    look = NAMES[0]
    mat = build(look)
    mesh.data.materials.clear(); mesh.data.materials.append(mat)
    for o in list(sc.objects):
        if o.type == "MESH" and o is not mesh:
            bpy.data.objects.remove(o)                     # the preview eye must not shade the bake
    bpy.ops.object.select_all(action="DESELECT")
    mesh.select_set(True); bpy.context.view_layer.objects.active = mesh
    info = BAKE[mat.name]; nt = info["nt"]
    outn = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    SIZE = 4096
    sc.render.bake.margin = 8
    sc.cycles.use_denoising = False

    def target(tag, non_color):
        img = bpy.data.images.new("bake_" + tag, SIZE, SIZE, alpha=False)
        if non_color:
            img.colorspace_settings.name = "Non-Color"
        n = nt.nodes.new("ShaderNodeTexImage"); n.image = img
        for x in nt.nodes:
            x.select = False
        n.select = True; nt.nodes.active = n
        return img

    def save(img, fname):
        img.filepath_raw = os.path.join(OUT, fname); img.file_format = "PNG"; img.save()
        print("HERTEX baked", fname)
    em = nt.nodes.new("ShaderNodeEmission")
    sc.cycles.samples = 10
    nt.links.new(info["color"], em.inputs["Color"]); nt.links.new(em.outputs[0], outn.inputs["Surface"])
    img = target("color", False); bpy.ops.object.bake(type="EMIT"); save(img, "T_Her_BaseColor.png")
    sc.cycles.samples = 2
    nt.links.new(info["rough"], em.inputs["Color"])
    img = target("rough", True); bpy.ops.object.bake(type="EMIT"); save(img, "T_Her_Roughness.png")
    nt.links.new(info["bsdf"].outputs[0], outn.inputs["Surface"])
    sc.render.bake.normal_space = "TANGENT"
    img = target("normal", True); bpy.ops.object.bake(type="NORMAL"); save(img, "T_Her_Normal.png")
    print("HERTEX bake done")
    NAMES = []
views = {"face": (cm(10, -92, 233), cm(1.5, -22, 237), 62), "bust": (cm(30, -150, 215), cm(0, -10, 205), 42),
         "neck": (cm(14, -75, 212), cm(2, -16, 212), 70), "arm": (cm(-78, -105, 160), cm(-36, -6, 160), 60)}
for look in NAMES:
    mesh.data.materials.clear()
    mesh.data.materials.append(build(look))
    for vname in VIEWS:
        loc, tgt, lens = views[vname]
        cam.location = loc; cam.rotation_euler = (tgt - loc).to_track_quat("-Z", "Y").to_euler(); cam.data.lens = lens
        sc.render.filepath = os.path.join(OUT, f"{look}{'_face' if FACE else ''}_{vname}.png")
        bpy.ops.render.render(write_still=True)
        print("HERTEX rendered", look, vname)
print("HERTEX done")
