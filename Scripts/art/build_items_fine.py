"""Blender: everything he can pick up, modelled properly and textured (Cheyenne 2026-11-19: "the items you actually get to
pick up are usually very detailed and intricate, even the little keys ... don't cheap out").

  blender -b --factory-startup -P build_items_fine.py -- <out_dir> [--only Name,Name] [--size 1024] [--preview]

For each item: real geometry (turned shafts, cut bits, hinges, stamped lettering), procedural worn materials (tarnish in
patches, dirt in the crevices, bright metal on the edges, scratches), baked to one texture set:
  <out_dir>/SM_Item_<Name>.fbx          one material slot ("Item"), UVs
  <out_dir>/tex/T_Item_<Name>_C.png     base colour
  <out_dir>/tex/T_Item_<Name>_N.png     normal (tangent space)
  <out_dir>/tex/T_Item_<Name>_ORM.png   R = 1, G = roughness, B = metallic
Metres in Blender = centimetres in Unreal.  Each item is centred in X and Y with its underside at z = 0, as build_items.py does.
No paid generation.  Run after build_items.py (it replaces that script's plain versions of the same names)."""
import bpy, bmesh, math, os, sys, random
import numpy as np
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
OUT = argv[0]
ONLY = set(argv[argv.index("--only") + 1].split(",")) if "--only" in argv else None
SIZE = int(argv[argv.index("--size") + 1]) if "--size" in argv else 1024
PREVIEW = "--preview" in argv
TEX = os.path.join(OUT, "tex")
PRE = os.path.join(OUT, "preview")
os.makedirs(TEX, exist_ok=True)
os.makedirs(PRE, exist_ok=True)
PI = math.pi

# ============================================================================================ materials
SOCK = {}          # material name -> the sockets that are baked


class Graph:
    def __init__(s, m):
        s.m = m
        s.nt = m.node_tree
        s.N = s.nt.nodes
        s.L = s.nt.links
        s.bsdf = next(n for n in s.N if n.type == "BSDF_PRINCIPLED")
        s.out = next(n for n in s.N if n.type == "OUTPUT_MATERIAL")
        s.P = s.N.new("ShaderNodeTexCoord").outputs["Object"]
        s._ao = {}
        s._edge = {}

    def _in(s, sock, v):
        if v is None:
            return
        if hasattr(v, "is_linked") or hasattr(v, "links"):
            s.L.new(v, sock)
        elif isinstance(v, (tuple, list)):
            sock.default_value = (v[0], v[1], v[2], 1.0) if len(sock.default_value) == 4 else tuple(v)
        elif hasattr(sock.default_value, "__len__"):
            sock.default_value = (v, v, v, 1.0) if len(sock.default_value) == 4 else (v, v, v)
        else:
            sock.default_value = v

    def rgb(s, c):
        n = s.N.new("ShaderNodeRGB")
        n.outputs[0].default_value = (c[0], c[1], c[2], 1.0)
        return n.outputs[0]

    def math(s, op, a, b=None, clamp=False):
        n = s.N.new("ShaderNodeMath")
        n.operation = op
        n.use_clamp = clamp
        s._in(n.inputs[0], a)
        s._in(n.inputs[1], b)
        return n.outputs[0]

    def ramp(s, v, lo, hi, to0=0.0, to1=1.0):
        n = s.N.new("ShaderNodeMapRange")
        n.clamp = True
        s._in(n.inputs["Value"], v)
        n.inputs["From Min"].default_value = lo
        n.inputs["From Max"].default_value = hi
        n.inputs["To Min"].default_value = to0
        n.inputs["To Max"].default_value = to1
        return n.outputs[0]

    def mix(s, a, b, f, blend="MIX"):
        n = s.N.new("ShaderNodeMixRGB")
        n.blend_type = blend
        s._in(n.inputs[0], f)
        s._in(n.inputs[1], a)
        s._in(n.inputs[2], b)
        return n.outputs[0]

    def mapping(s, scale=(1, 1, 1), rot=(0, 0, 0), loc=(0, 0, 0), vec=None):
        n = s.N.new("ShaderNodeMapping")
        n.inputs["Scale"].default_value = scale
        n.inputs["Rotation"].default_value = rot
        n.inputs["Location"].default_value = loc
        s.L.new(vec if vec is not None else s.P, n.inputs["Vector"])
        return n.outputs[0]

    def noise(s, scale, detail=4.0, rough=0.55, vec=None, color=False):
        n = s.N.new("ShaderNodeTexNoise")
        n.inputs["Scale"].default_value = scale
        n.inputs["Detail"].default_value = detail
        n.inputs["Roughness"].default_value = rough
        s.L.new(vec if vec is not None else s.P, n.inputs["Vector"])
        return n.outputs[1 if color else 0]

    def cells(s, scale, vec=None, feature="DISTANCE_TO_EDGE", rand=1.0):
        n = s.N.new("ShaderNodeTexVoronoi")
        n.feature = feature
        n.inputs["Scale"].default_value = scale
        n.inputs["Randomness"].default_value = rand
        s.L.new(vec if vec is not None else s.P, n.inputs["Vector"])
        return n.outputs[0]

    def wave(s, scale, distortion, detail=2.0, direction="Y", vec=None, dscale=1.0):
        n = s.N.new("ShaderNodeTexWave")
        n.wave_type = "BANDS"
        n.bands_direction = direction
        n.inputs["Scale"].default_value = scale
        n.inputs["Distortion"].default_value = distortion
        n.inputs["Detail"].default_value = detail
        n.inputs["Detail Scale"].default_value = dscale
        s.L.new(vec if vec is not None else s.P, n.inputs["Vector"])
        return n.outputs[1]

    def ao(s, dist, samples=12):
        if dist not in s._ao:
            n = s.N.new("ShaderNodeAmbientOcclusion")
            n.samples = samples
            n.only_local = True
            n.inputs["Distance"].default_value = dist
            s._ao[dist] = n.outputs["AO"]
        return s._ao[dist]

    def edge(s, radius, samples=8):
        """1 on a sharp edge, 0 on a flat or smoothly curved face."""
        if radius not in s._edge:
            b = s.N.new("ShaderNodeBevel")
            b.samples = samples
            b.inputs["Radius"].default_value = radius
            g = s.N.new("ShaderNodeNewGeometry")
            d = s.N.new("ShaderNodeVectorMath")
            d.operation = "DOT_PRODUCT"
            s.L.new(b.outputs["Normal"], d.inputs[0])
            s.L.new(g.outputs["Normal"], d.inputs[1])
            s._edge[radius] = s.ramp(s.math("SUBTRACT", 1.0, d.outputs["Value"]), 0.004, 0.10)
        return s._edge[radius]

    def finish(s, col, rough, metal, height=None, bump=0.4, dist=0.0002):
        s._in(s.bsdf.inputs["Base Color"], col)
        s._in(s.bsdf.inputs["Roughness"], rough)
        s._in(s.bsdf.inputs["Metallic"], metal)
        if height is not None:
            b = s.N.new("ShaderNodeBump")
            b.inputs["Strength"].default_value = bump
            b.inputs["Distance"].default_value = dist
            s._in(b.inputs["Height"], height)
            s.L.new(b.outputs["Normal"], s.bsdf.inputs["Normal"])

        def sock(v):
            if hasattr(v, "links"):
                return v
            if isinstance(v, (tuple, list)):
                return s.rgb(v)
            n = s.N.new("ShaderNodeValue")
            n.outputs[0].default_value = v
            return n.outputs[0]
        SOCK[s.m.name] = dict(g=s, col=sock(col), rough=sock(rough), metal=sock(metal))


def worn(g, base, metal, rough, ns=500.0, tarnish=(0.08, 0.06, 0.03), tarn=0.6, tarn_metal=0.3, dirt=(0.018, 0.015, 0.011), dirty=0.7,
         bright=None, edges=0.7, scratch=0.3, aod=0.003, er=0.0006, bump=0.35, col=None, tarn_lo=0.50, tarn_hi=0.64, dust=0.45, verdigris=0.0):
    """The usual story of an old object: patches of tarnish, dirt where a thumb cannot reach, bright metal on the edges, scratches."""
    c = col if col is not None else g.rgb(base)
    fine = g.noise(ns * 3.0, 6.0)
    fine2 = g.noise(ns * 1.3, 4.0, vec=g.mapping(loc=(0.37, 0.11, 0.73)))
    big = g.noise(ns * 0.28, 3.0, vec=g.mapping(loc=(0.11, 0.53, 0.29)))
    c = g.mix(c, (0.62, 0.62, 0.62), g.ramp(fine, 0.35, 0.75, 0.0, 0.6), "MULTIPLY")
    t = g.math("MULTIPLY", g.ramp(g.math("ADD", big, g.math("MULTIPLY", g.math("SUBTRACT", fine2, 0.5), 0.35)), tarn_lo, tarn_hi), tarn)
    c = g.mix(c, tarnish, t)
    a = g.ao(aod)
    cav = g.math("MULTIPLY", g.ramp(a, 0.92, 0.45), dirty)
    c = g.mix(c, dirt, cav)
    e = g.math("MULTIPLY", g.math("MULTIPLY", g.edge(er), g.ramp(a, 0.55, 0.9)), g.ramp(fine2, 0.25, 0.6, 0.25, 1.0))
    e = g.math("MULTIPLY", e, edges)
    br = bright if bright is not None else tuple(min(1.0, v * 1.7 + 0.03) for v in base)
    c = g.mix(c, br, e)
    s1 = g.ramp(g.noise(1.0, 2.0, vec=g.mapping(scale=(ns * 0.5, ns * 22.0, ns * 0.5), rot=(0.0, 0.3, 0.7))), 0.655, 0.70)
    s2 = g.ramp(g.noise(1.0, 2.0, vec=g.mapping(scale=(ns * 16.0, ns * 0.4, ns * 0.4), rot=(0.4, 0.0, -0.5), loc=(3.1, 1.7, 0.4))), 0.67, 0.71)
    sc = g.math("MULTIPLY", g.math("MAXIMUM", s1, s2), scratch)
    c = g.mix(c, br, g.math("MULTIPLY", sc, 0.6))
    # age: green in the crevices of brass; dust on what faced up and in the recesses
    vd = None
    if verdigris > 0.0:
        vd = g.math("MULTIPLY", g.ramp(g.noise(ns * 0.55, 4.0, vec=g.mapping(loc=(0.91, 0.17, 0.43))), 0.50, 0.64), g.ramp(a, 0.97, 0.62))
        vd = g.math("MULTIPLY", vd, verdigris)
        c = g.mix(c, g.mix((0.050, 0.130, 0.100), (0.110, 0.200, 0.150), fine), vd)
    dm = None
    if dust > 0.0:
        geo = g.N.new("ShaderNodeNewGeometry")
        sn = g.N.new("ShaderNodeSeparateXYZ")
        g.L.new(geo.outputs["Normal"], sn.inputs[0])
        up = g.math("MULTIPLY", g.ramp(sn.outputs[2], 0.30, 0.92), g.ramp(g.noise(ns * 0.45, 4.0, vec=g.mapping(loc=(0.71, 0.23, 0.87))), 0.28, 0.72))
        dm = g.math("MULTIPLY", g.math("MAXIMUM", up, g.math("MULTIPLY", g.ramp(a, 0.90, 0.50), 0.8)), dust, clamp=True)
        c = g.mix(c, g.mix((0.150, 0.128, 0.098), (0.105, 0.088, 0.066), fine2), g.math("MULTIPLY", dm, 0.85))
    r = g.math("ADD", rough, g.math("MULTIPLY", t, 0.25))
    r = g.math("ADD", r, g.math("MULTIPLY", cav, 0.35))
    r = g.math("SUBTRACT", r, g.math("MULTIPLY", e, 0.15))
    r = g.math("ADD", r, g.math("MULTIPLY", g.math("SUBTRACT", fine, 0.5), 0.16))
    r = g.math("ADD", r, g.math("MULTIPLY", sc, 0.12), clamp=True)
    r = g.math("MAXIMUM", r, 0.06)
    m = g.math("MULTIPLY", metal, g.math("SUBTRACT", 1.0, g.math("MULTIPLY", cav, 0.9)))
    m = g.math("MULTIPLY", m, g.math("SUBTRACT", 1.0, g.math("MULTIPLY", t, tarn_metal)), clamp=True)
    if vd is not None:
        r = g.math("ADD", r, g.math("MULTIPLY", vd, 0.5), clamp=True)
        m = g.math("MULTIPLY", m, g.math("SUBTRACT", 1.0, vd), clamp=True)
    if dm is not None:
        r = g.math("ADD", r, g.math("MULTIPLY", dm, 0.45), clamp=True)
        m = g.math("MULTIPLY", m, g.math("SUBTRACT", 1.0, g.math("MULTIPLY", dm, 0.9)), clamp=True)
    h = g.math("SUBTRACT", g.math("MULTIPLY", fine, 0.18), g.math("MULTIPLY", sc, 0.8))
    h = g.math("SUBTRACT", h, g.math("MULTIPLY", t, 0.25))
    g.finish(c, r, m, h, bump)
    return dict(t=t, cav=cav, e=e, sc=sc, fine=fine, big=big)


def grain(g, dark, light, ns=180.0, along="X"):
    """Wood: long bands in the direction of the grain, with fine pores."""
    sc = {"X": (ns * 0.06, ns, ns), "Y": (ns, ns * 0.06, ns), "Z": (ns, ns, ns * 0.06)}[along]
    v = g.mapping(scale=sc)
    w = g.wave(1.6, 5.0, 3.0, "Y" if along != "Y" else "X", vec=v, dscale=1.5)
    pores = g.ramp(g.noise(1.0, 3.0, vec=g.mapping(scale=tuple(k * 6 for k in sc))), 0.55, 0.75)
    c = g.mix(dark, light, g.ramp(w, 0.2, 0.85))
    return g.mix(c, tuple(v_ * 0.45 for v_ in dark), g.math("MULTIPLY", pores, 0.5))


def m_brass(g):
    worn(g, (0.36, 0.235, 0.075), 1.0, 0.40, tarnish=(0.048, 0.034, 0.017), tarn=0.95, tarn_metal=0.65, bright=(0.74, 0.55, 0.22), edges=0.6, scratch=0.45, aod=0.002, bump=0.6,
         tarn_lo=0.36, tarn_hi=0.54, verdigris=0.75, dust=0.4)


def m_iron(g):
    worn(g, (0.075, 0.07, 0.066), 1.0, 0.46, tarnish=(0.15, 0.055, 0.02), tarn=0.75, tarn_metal=0.85, bright=(0.36, 0.35, 0.34), scratch=0.25, aod=0.002, bump=0.6)


def m_castiron(g):
    """A big cast piece (the vent): rust in broad stains, not speckle."""
    worn(g, (0.060, 0.056, 0.052), 1.0, 0.55, tarnish=(0.13, 0.05, 0.02), tarn=0.8, tarn_metal=0.85, bright=(0.30, 0.29, 0.28), scratch=0.2, aod=0.008, er=0.002,
         bump=0.8, ns=110.0, tarn_lo=0.52, tarn_hi=0.70)


def m_steel(g):
    worn(g, (0.30, 0.30, 0.29), 1.0, 0.36, tarnish=(0.125, 0.052, 0.020), tarn=0.80, tarn_metal=0.85, bright=(0.60, 0.60, 0.59), edges=0.55, scratch=0.6, aod=0.002, bump=0.55,
         tarn_lo=0.47, tarn_hi=0.60, dust=0.4)


def m_gold(g):
    worn(g, (0.66, 0.45, 0.14), 1.0, 0.30, tarnish=(0.36, 0.23, 0.07), tarn=0.5, tarn_metal=0.0, bright=(0.90, 0.70, 0.28), scratch=0.85, dirty=0.8, aod=0.0015, ns=900.0, dust=0.25)


def m_wood(g):
    worn(g, (0.16, 0.085, 0.04), 0.0, 0.42, col=grain(g, (0.075, 0.036, 0.016), (0.20, 0.11, 0.05)), tarnish=(0.05, 0.03, 0.018), tarn=0.5,
         bright=(0.30, 0.20, 0.11), edges=0.8, scratch=0.25, aod=0.004, er=0.001, ns=300.0)


def m_wooddark(g):
    worn(g, (0.06, 0.03, 0.015), 0.0, 0.30, col=grain(g, (0.028, 0.013, 0.007), (0.085, 0.042, 0.018), 140.0), tarnish=(0.02, 0.012, 0.008), tarn=0.5,
         bright=(0.22, 0.14, 0.07), edges=0.85, scratch=0.35, aod=0.005, er=0.0012, ns=260.0)


def m_inlay(g):
    worn(g, (0.42, 0.33, 0.18), 0.0, 0.34, col=grain(g, (0.30, 0.22, 0.11), (0.50, 0.40, 0.22), 300.0, "Y"), tarnish=(0.16, 0.11, 0.05), tarn=0.5,
         bright=(0.55, 0.46, 0.28), edges=0.3, scratch=0.3, aod=0.003, ns=300.0)


def m_paintred(g):
    """Red enamel over wood, worn through where a hand has turned it for forty years."""
    wood = grain(g, (0.10, 0.05, 0.022), (0.24, 0.14, 0.065))
    fine = g.noise(900.0, 5.0)
    big = g.noise(140.0, 4.0, vec=g.mapping(loc=(0.2, 0.7, 0.4)))
    gone = g.math("MAXIMUM", g.math("MULTIPLY", g.edge(0.0012), 1.0), g.ramp(g.math("ADD", big, g.math("MULTIPLY", g.math("SUBTRACT", fine, 0.5), 0.5)), 0.56, 0.62))
    paint = g.mix((0.20, 0.018, 0.012), (0.10, 0.008, 0.006), g.ramp(g.noise(60.0, 3.0), 0.3, 0.7))
    c = g.mix(paint, wood, gone)
    worn(g, (0.2, 0.02, 0.015), 0.0, 0.34, col=c, tarnish=(0.03, 0.012, 0.01), tarn=0.45, bright=(0.30, 0.20, 0.11), edges=0.25, scratch=0.3, aod=0.004, ns=350.0)


def m_felt(g):
    c = g.mix((0.17, 0.012, 0.018), (0.07, 0.006, 0.01), g.ramp(g.noise(2600.0, 2.0), 0.35, 0.7))
    c = g.mix(c, (0.10, 0.03, 0.02), g.ramp(g.noise(60.0, 3.0), 0.55, 0.8, 0.0, 0.6))          # where it has faded
    c = g.mix(c, (0.03, 0.01, 0.01), g.ramp(g.ao(0.006), 0.9, 0.4, 0.0, 0.7))
    g.finish(c, 0.95, 0.0, g.noise(3000.0, 2.0), 0.5)


def m_card(g):
    worn(g, (0.15, 0.105, 0.058), 0.0, 0.85, tarnish=(0.07, 0.045, 0.025), tarn=0.6, bright=(0.26, 0.20, 0.12), edges=0.9, scratch=0.1, aod=0.004, er=0.0012, ns=250.0)


def m_label(g):
    worn(g, (0.20, 0.018, 0.015), 0.0, 0.7, tarnish=(0.09, 0.02, 0.012), tarn=0.5, bright=(0.30, 0.22, 0.15), edges=0.9, scratch=0.25, aod=0.003, er=0.001, ns=300.0)


def m_paper(g):
    worn(g, (0.34, 0.29, 0.19), 0.0, 0.9, tarnish=(0.16, 0.10, 0.045), tarn=0.8, bright=(0.40, 0.35, 0.25), edges=0.4, scratch=0.05, aod=0.002, ns=260.0, tarn_lo=0.42, tarn_hi=0.6)


def m_ink(g):
    worn(g, (0.016, 0.014, 0.013), 0.0, 0.6, tarnish=(0.05, 0.04, 0.03), tarn=0.3, bright=(0.08, 0.07, 0.06), edges=0.3, scratch=0.1, dirty=0.0, ns=500.0)


def m_cream(g):
    worn(g, (0.36, 0.31, 0.21), 0.0, 0.6, tarnish=(0.17, 0.12, 0.06), tarn=0.5, bright=(0.42, 0.37, 0.27), edges=0.2, scratch=0.1, dirty=0.3, ns=400.0)


def m_ribbon(g):
    weave = g.wave(5200.0, 0.0, 0.0, "X")
    c = g.mix((0.21, 0.014, 0.022), (0.11, 0.008, 0.014), g.ramp(weave, 0.3, 0.7))
    c = g.mix(c, (0.05, 0.012, 0.01), g.ramp(g.noise(90.0, 3.0), 0.5, 0.75, 0.0, 0.7))          # grubby where it was held
    g.finish(c, 0.8, 0.0, weave, 0.4)


def m_glass(g):
    c = g.mix((0.16, 0.20, 0.18), (0.05, 0.06, 0.05), g.ramp(g.noise(300.0, 3.0), 0.5, 0.8))
    g.finish(c, g.ramp(g.noise(700.0, 4.0), 0.3, 0.8, 0.05, 0.22), 0.0)


def m_mirror(g):
    gone = g.ramp(g.math("ADD", g.noise(70.0, 5.0), g.ramp(g.edge(0.004), 0.0, 1.0, 0.0, 0.12)), 0.63, 0.72)       # the silvering has gone in a few spots, mostly at the edges
    c = g.mix((0.50, 0.52, 0.51), (0.05, 0.045, 0.035), gone)
    g.finish(c, g.mix(0.05, 0.6, gone), g.mix(1.0, 0.0, gone))


def m_ceramic(g):
    crack = g.math("MULTIPLY", g.ramp(g.cells(1500.0), 0.0, 0.02, 1.0, 0.0), g.ramp(g.noise(240.0, 3.0), 0.45, 0.65))
    c = g.mix((0.50, 0.47, 0.40), (0.16, 0.12, 0.07), g.math("MULTIPLY", crack, 0.35))
    worn(g, (0.5, 0.47, 0.4), 0.0, 0.22, col=c, tarnish=(0.26, 0.20, 0.11), tarn=0.5, bright=(0.56, 0.53, 0.46), edges=0.2, scratch=0.15, aod=0.002, ns=500.0)


def m_polymer(g):
    worn(g, (0.014, 0.013, 0.013), 0.0, 0.36, tarnish=(0.04, 0.035, 0.03), tarn=0.4, bright=(0.10, 0.10, 0.10), edges=0.6, scratch=0.5, aod=0.002, ns=500.0)


def m_japan(g):
    """Black japanned handles (shears): the enamel is gone to bare steel where the fingers go."""
    fine = g.noise(900.0, 5.0)
    big = g.noise(110.0, 4.0, vec=g.mapping(loc=(0.6, 0.1, 0.3)))
    gone = g.math("MAXIMUM", g.edge(0.001), g.ramp(g.math("ADD", big, g.math("MULTIPLY", g.math("SUBTRACT", fine, 0.5), 0.5)), 0.55, 0.60))
    c = g.mix((0.012, 0.011, 0.011), (0.33, 0.32, 0.31), gone)
    m = g.math("MULTIPLY", gone, 1.0)
    r = g.mix(0.25, 0.42, gone)
    cav = g.ramp(g.ao(0.002), 0.9, 0.45, 0.0, 0.7)
    c = g.mix(c, (0.02, 0.015, 0.01), cav)
    g.finish(c, g.math("ADD", r, g.math("MULTIPLY", cav, 0.3)), g.math("MULTIPLY", m, g.math("SUBTRACT", 1.0, cav)), fine, 0.2)


def m_leather(g):
    pores = g.ramp(g.cells(1400.0, feature="F1"), 0.0, 0.5)
    c = g.mix((0.03, 0.014, 0.007), (0.10, 0.05, 0.022), pores)
    worn(g, (0.09, 0.045, 0.02), 0.0, 0.55, col=c, tarnish=(0.025, 0.012, 0.008), tarn=0.6, bright=(0.22, 0.13, 0.07), edges=0.9, scratch=0.3, aod=0.003, er=0.001, ns=300.0, bump=0.6)


def m_string(g):
    c = g.mix((0.26, 0.21, 0.12), (0.12, 0.09, 0.05), g.ramp(g.wave(3000.0, 2.0, 1.0, "X"), 0.3, 0.7))
    g.finish(c, 0.9, 0.0, g.noise(4000.0, 2.0), 0.5)


def m_black(g):
    g.finish((0.004, 0.004, 0.004), 0.9, 0.0)


EYE_R = 0.0125


def m_eye(g):
    """A hand-made glass eye: milk-white shell with fine red threads, a pale blue iris built up in radial strokes, the dark
    ring round it, the pupil.  The iris looks along +Z; the eye's centre is EYE_R above the underside."""
    p = g.mapping(loc=(0.0, 0.0, -EYE_R))
    sep = g.N.new("ShaderNodeSeparateXYZ")
    g.L.new(p, sep.inputs[0])
    x, y, z = sep.outputs[0], sep.outputs[1], sep.outputs[2]
    rxy = g.math("DIVIDE", g.math("SQRT", g.math("ADD", g.math("MULTIPLY", x, x), g.math("MULTIPLY", y, y))), EYE_R)
    up = g.ramp(z, 0.0, 0.0005)
    # radial strokes: noise sampled on the direction round the pupil (no seam), slowly changing outward
    inv = g.math("DIVIDE", 1.0, g.math("MAXIMUM", g.math("MULTIPLY", rxy, EYE_R), 1e-6))
    cmb = g.N.new("ShaderNodeCombineXYZ")
    g._in(cmb.inputs[0], g.math("MULTIPLY", g.math("MULTIPLY", x, inv), 9.0))
    g._in(cmb.inputs[1], g.math("MULTIPLY", g.math("MULTIPLY", y, inv), 9.0))
    g._in(cmb.inputs[2], g.math("MULTIPLY", rxy, 2.2))
    fib = g.noise(1.0, 7.0, 0.7, vec=cmb.outputs[0])
    fib2 = g.noise(2.6, 5.0, 0.6, vec=cmb.outputs[0])
    iris = g.mix((0.10, 0.20, 0.33), (0.42, 0.55, 0.62), g.ramp(fib, 0.32, 0.70))
    iris = g.mix(iris, (0.035, 0.07, 0.14), g.ramp(fib2, 0.55, 0.78, 0.0, 0.75))
    iris = g.mix(iris, (0.33, 0.27, 0.13), g.math("MULTIPLY", g.ramp(rxy, 0.30, 0.19), g.ramp(fib, 0.3, 0.7, 0.3, 0.9)))      # the paler ring by the pupil
    iris = g.mix(iris, (0.015, 0.03, 0.06), g.ramp(rxy, 0.385, 0.455))                                                       # the dark limbal ring
    iris = g.mix(iris, (0.004, 0.004, 0.005), g.ramp(rxy, 0.175, 0.150))                                                     # the pupil
    # the white
    wob = g.N.new("ShaderNodeVectorMath")
    wob.operation = "ADD"
    g.L.new(g.mapping(loc=(0.013, 0.007, 0.0)), wob.inputs[0])
    g._in(wob.inputs[1], g.mix((0.0, 0.0, 0.0), g.noise(420.0, 3.0, color=True), 0.0022))
    veins = g.ramp(g.cells(230.0, vec=wob.outputs[0]), 0.0, 0.011, 1.0, 0.0)
    veins = g.math("MULTIPLY", veins, g.ramp(g.noise(150.0, 3.0), 0.44, 0.60))
    veins = g.math("MULTIPLY", veins, g.ramp(rxy, 0.50, 0.95, 0.15, 1.0))
    white = g.mix((0.56, 0.53, 0.46), (0.50, 0.42, 0.26), g.ramp(g.noise(120.0, 3.0), 0.45, 0.8, 0.0, 0.7))
    white = g.mix(white, (0.30, 0.035, 0.025), g.math("MULTIPLY", veins, 0.8))
    white = g.mix(white, (0.33, 0.25, 0.14), g.ramp(z, 0.002, -0.012, 0.0, 0.6))                                             # yellowed toward the back
    isiris = g.math("MULTIPLY", g.ramp(rxy, 0.465, 0.445), up)
    c = g.mix(white, iris, isiris)
    scr = g.ramp(g.noise(1.0, 2.0, vec=g.mapping(scale=(500.0, 9000.0, 500.0), rot=(0.3, 0.2, 0.5))), 0.67, 0.71)
    r = g.math("ADD", 0.07, g.math("MULTIPLY", scr, 0.25))
    g.finish(c, r, 0.0, g.math("MULTIPLY", scr, -1.0), 0.15)


def m_cloth(g):
    """Unbleached muslin, grubby from years in a small pair of hands and then years in a duct."""
    weave = g.math("MULTIPLY", g.wave(4200.0, 0.0, 0.0, "X"), g.wave(4200.0, 0.0, 0.0, "Y"))
    c = g.mix((0.40, 0.34, 0.24), (0.27, 0.22, 0.15), g.ramp(weave, 0.1, 0.6))
    worn(g, (0.40, 0.34, 0.24), 0.0, 0.9, col=c, tarnish=(0.20, 0.155, 0.095), tarn=0.75, bright=(0.42, 0.37, 0.27), edges=0.1, scratch=0.0, aod=0.006, dirty=0.85,
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


MATS = {"CastIron": m_castiron, "Cloth": m_cloth, "Dress": m_dress, "Yarn": m_yarn, "Thread": m_thread, "Stuffing": m_stuffing, "Brass": m_brass, "Iron": m_iron, "Steel": m_steel, "Gold": m_gold, "Wood": m_wood, "WoodDark": m_wooddark, "Inlay": m_inlay, "PaintRed": m_paintred,
        "Felt": m_felt, "Card": m_card, "Label": m_label, "Paper": m_paper, "Ink": m_ink, "Cream": m_cream, "Ribbon": m_ribbon, "Glass": m_glass,
        "Mirror": m_mirror, "Ceramic": m_ceramic, "Polymer": m_polymer, "Japan": m_japan, "Leather": m_leather, "String": m_string, "Black": m_black, "Eye": m_eye}


def mat(name):
    m = bpy.data.materials.get(name)
    if not m:
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        MATS[name](Graph(m))
    return m


# ============================================================================================ geometry
def _fin(ob, m):
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    ob.data.materials.clear()
    ob.data.materials.append(mat(m))
    return ob


def _link(me, name="p"):
    ob = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(ob)
    return ob


def bev(ob, w, seg=2, angle=35.0):
    md = ob.modifiers.new("b", "BEVEL")
    md.width = w
    md.segments = seg
    md.limit_method = "ANGLE"
    md.angle_limit = math.radians(angle)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.modifier_apply(modifier="b")
    return ob


def box(sx, sy, sz, loc, rot=(0, 0, 0), m="Iron", bevel=0.0, seg=2):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    ob = bpy.context.object
    ob.scale = (sx, sy, sz)
    _fin(ob, m)
    if bevel > 0:
        bev(ob, bevel, seg)
    return ob


def cyl(r, h, loc, rot=(0, 0, 0), m="Iron", v=32, r2=None, bevel=0.0):
    if r2 is None:
        bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, vertices=v, location=loc, rotation=rot)
    else:
        bpy.ops.mesh.primitive_cone_add(radius1=r, radius2=r2, depth=h, vertices=v, location=loc, rotation=rot)
    ob = _fin(bpy.context.object, m)
    if bevel > 0:
        bev(ob, bevel, 2, 50.0)
    return ob


def sphere(r, loc, m="Steel", seg=24, rings=12, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, segments=seg, ring_count=rings, location=loc)
    bpy.context.object.scale = scale
    return _fin(bpy.context.object, m)


def torus(R, r, loc, rot=(0, 0, 0), m="Iron", seg=48, rseg=12, squash=1.0):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=r, major_segments=seg, minor_segments=rseg, location=loc, rotation=rot)
    bpy.context.object.scale = (1, 1, squash)
    return _fin(bpy.context.object, m)


def mesh(verts, faces, m):
    me = bpy.data.meshes.new("m")
    me.from_pydata(verts, [], faces)
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    return _fin(_link(me), m)


def lathe(profile, m, seg=40, flute=None, at=(0, 0, 0)):
    """Turned on a lathe round the X axis.  profile: (x, r) or (x, ry, rz), from one end to the other."""
    verts, faces = [], []
    n = len(profile)
    for p in profile:
        ry = p[1]
        rz = p[2] if len(p) > 2 else ry
        for k in range(seg):
            a = 2 * PI * k / seg
            f = flute(a, p[0]) if flute else 1.0
            verts.append((p[0] + at[0], ry * f * math.cos(a) + at[1], rz * f * math.sin(a) + at[2]))
    for i in range(n - 1):
        for k in range(seg):
            a0, a1 = i * seg + k, i * seg + (k + 1) % seg
            faces.append((a0, a1, a1 + seg, a0 + seg))
    faces.append(tuple(range(seg)))
    faces.append(tuple(range((n - 1) * seg, n * seg)))
    return mesh(verts, faces, m)


def tube(pts, r, m, closed=False, res=4):
    """A round rod along a path."""
    cu = bpy.data.curves.new("c", "CURVE")
    cu.dimensions = "3D"
    sp = cu.splines.new("POLY")
    sp.points.add(len(pts) - 1)
    for p, co in zip(sp.points, pts):
        p.co = (co[0], co[1], co[2] if len(co) > 2 else 0.0, 1.0)
    sp.use_cyclic_u = closed
    cu.bevel_depth = r
    cu.bevel_resolution = res
    cu.use_fill_caps = True
    ob = _link(cu, "c")
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    bpy.data.objects.remove(ob)
    for p in me.polygons:
        p.use_smooth = True
    return _fin(_link(me), m)


def plate(outline, t, m, bevel=0.0, z=0.0):
    """A flat piece cut to an outline (x, y), t thick, lying on z."""
    bm = bmesh.new()
    f = bm.faces.new([bm.verts.new((x, y, z)) for x, y in outline])
    ret = bmesh.ops.extrude_face_region(bm, geom=[f])
    bmesh.ops.translate(bm, verts=[e for e in ret["geom"] if isinstance(e, bmesh.types.BMVert)], vec=(0, 0, t))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("plate")
    bm.to_mesh(me)
    bm.free()
    ob = _fin(_link(me), m)
    if bevel > 0:
        bev(ob, bevel, 2, 50.0)
    return ob


def strip(pts, w, t, m):
    """A ribbon along a path (x, y, z), w wide (across, in the XY plane), t thick."""
    verts, faces = [], []
    n = len(pts)
    for i, p in enumerate(pts):
        a, b = Vector(pts[max(i - 1, 0)]), Vector(pts[min(i + 1, n - 1)])
        d = (b - a)
        side = Vector((-d.y, d.x, 0.0))
        side = side.normalized() * (w / 2) if side.length > 1e-9 else Vector((0, w / 2, 0))
        verts += [tuple(Vector(p) + side), tuple(Vector(p) - side)]
    for i in range(n - 1):
        faces.append((2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2))
    ob = mesh(verts, faces, m)
    md = ob.modifiers.new("s", "SOLIDIFY")
    md.thickness = t
    md.offset = 0.0
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.modifier_apply(modifier="s")
    for p in ob.data.polygons:
        p.use_smooth = True
    return ob


def text(s, size, depth, loc=(0, 0, 0), rot=(0, 0, 0), m="Ink", spacing=1.0):
    """Lettering lying in the XY plane (before rot), centred, depth thick."""
    cu = bpy.data.curves.new("t", "FONT")
    cu.body = s
    cu.size = size
    cu.extrude = depth / 2
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
    cu.space_character = spacing
    ob = _link(cu, "t")
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    bpy.data.objects.remove(ob)
    o2 = _link(me)
    o2.rotation_euler = rot
    o2.location = loc
    return _fin(o2, m)


def cut(a, b):
    md = a.modifiers.new("x", "BOOLEAN")
    md.operation = "DIFFERENCE"
    md.object = b
    try:
        md.solver = "EXACT"
    except Exception:
        pass
    bpy.context.view_layer.objects.active = a
    bpy.ops.object.modifier_apply(modifier="x")
    bpy.data.objects.remove(b)
    return a


def moved(parts, loc=(0, 0, 0), rot=(0, 0, 0)):
    for p in (parts if isinstance(parts, list) else [parts]):
        p.rotation_euler = rot
        p.location = loc
        bpy.ops.object.select_all(action="DESELECT")
        p.select_set(True)
        bpy.context.view_layer.objects.active = p
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return parts


def ring_pts(R, n=64, cx=0.0, cy=0.0, sx=1.0, sy=1.0, z=0.0, a0=0.0, a1=2 * PI):
    return [(cx + R * sx * math.cos(a0 + (a1 - a0) * k / n), cy + R * sy * math.sin(a0 + (a1 - a0) * k / n), z) for k in range(n + (0 if abs(a1 - a0 - 2 * PI) < 1e-6 else 1))]


# ============================================================================================ keys
def key_bit(x1, w, h, t, m, pattern="A", yy=0.0):
    """The bit: w along the shaft ending at x1, hanging h toward -Y, with ward cuts."""
    x0 = x1 - w
    if pattern == "A":
        o = [(x0, 0), (x1, 0), (x1, -h), (x0 + w * 0.72, -h), (x0 + w * 0.72, -h * 0.52), (x0 + w * 0.46, -h * 0.52), (x0 + w * 0.46, -h), (x0, -h),
             (x0, -h * 0.70), (x0 + w * 0.20, -h * 0.70), (x0 + w * 0.20, -h * 0.42), (x0, -h * 0.42)]
    elif pattern == "B":
        o = [(x0, 0), (x1, 0), (x1, -h * 0.38), (x1 - w * 0.25, -h * 0.38), (x1 - w * 0.25, -h * 0.62), (x1, -h * 0.62), (x1, -h), (x0 + w * 0.60, -h),
             (x0 + w * 0.60, -h * 0.68), (x0 + w * 0.34, -h * 0.68), (x0 + w * 0.34, -h), (x0, -h)]
    elif pattern == "C":
        o = [(x0, 0), (x1, 0), (x1, -h), (x0 + w * 0.80, -h), (x0 + w * 0.80, -h * 0.70), (x0 + w * 0.62, -h * 0.70), (x0 + w * 0.62, -h), (x0 + w * 0.40, -h),
             (x0 + w * 0.40, -h * 0.45), (x0 + w * 0.22, -h * 0.45), (x0 + w * 0.22, -h), (x0, -h)]
    else:
        o = [(x0, 0), (x1, 0), (x1, -h), (x0 + w * 0.55, -h), (x0 + w * 0.55, -h * 0.6), (x0, -h * 0.6)]
    return plate([(x, y + yy) for x, y in o], t, m, bevel=t * 0.12, z=-t / 2)


def key_shaft(x0, L, rs, m, barrel=False):
    pr = [(x0 - rs, rs * 0.9), (x0, rs * 1.15), (x0 + rs * 0.5, rs * 1.9), (x0 + rs * 1.3, rs * 1.9), (x0 + rs * 1.8, rs * 1.2), (x0 + rs * 2.5, rs * 1.2),
          (x0 + rs * 3.0, rs * 1.6), (x0 + rs * 3.6, rs * 1.6), (x0 + rs * 4.1, rs * 1.05), (x0 + rs * 9.0, rs * 1.0), (L - rs * 1.2, rs * 0.96)]
    pr += [(L, rs * 0.96)] if barrel else [(L - rs * 0.8, rs * 1.25), (L - rs * 0.3, rs * 1.25), (L, rs * 0.7)]
    sh = lathe(pr, m, 28)
    if barrel:
        sh = cut(sh, cyl(rs * 0.55, rs * 6, (L, 0, 0), (0, PI / 2, 0), m, 16))
    return sh


def bow_ring(R, r, m, squash=0.8):
    return [torus(R, r, (0, 0, 0), m=m, squash=squash), torus(R * 0.50, r * 0.72, (0, 0, 0), m=m, seg=32, rseg=10, squash=squash)] + \
           [box(R * 0.55, r * 1.3, r * 1.3, (sx * R * 0.74, 0, 0), m=m, bevel=r * 0.3) for sx in (-1, 1)] + \
           [box(r * 1.3, R * 0.55, r * 1.3, (0, sy * R * 0.74, 0), m=m, bevel=r * 0.3) for sy in (-1, 1)]


def bow_oval(a, b, r, m):
    P = [tube(ring_pts(1.0, 72, sx=a, sy=b), r, m, True)]
    for sy in (-1, 1):                                                   # two scrolls inside
        pts = []
        for k in range(50):
            u = k / 49.0
            ang = sy * (PI * 0.5 + u * PI * 2.6)
            rad = b * (0.80 - 0.62 * u)
            pts.append((a * 0.05 + rad * 0.9 * math.cos(ang) * 0.9, sy * b * 0.05 + rad * math.sin(ang) * 0.55 + sy * b * 0.36, 0.0))
        P.append(tube(pts, r * 0.62, m))
    P.append(sphere(r * 1.5, (-a, 0, 0), m, 16, 8))
    return P


def bow_heart(k, r, m):
    """A heart, its point toward +X at x = 0 ... the lobes behind it."""
    pts = []
    for i in range(96):
        t = 2 * PI * i / 96
        hx = 16 * math.sin(t) ** 3
        hy = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append(((-hy - 17.0) * k, hx * k, 0.0))
    P = [tube(pts, r, m, True)]
    P.append(sphere(r * 1.25, ((-5.0 - 17.0) * k, 0, 0), m, 16, 8))       # a bead in the cleft
    P.append(tube([((-17.0 + 5.0) * k, 0, 0), (-1.5 * k, 0, 0)], r * 0.7, m))
    return P


def bow_trefoil(R, r, m):
    P = []
    for a in (PI, PI / 3, -PI / 3):
        P.append(torus(R, r, (R * 1.28 * math.cos(a) - R * 1.28, R * 1.28 * math.sin(a), 0), m=m, seg=36, rseg=10, squash=0.85))
    P.append(cyl(R * 0.62, r * 1.5, (-R * 1.28, 0, 0), m=m, v=24, bevel=r * 0.3))
    return P


def key_heart():
    # the jewelry box key: small and fancy, a heart worked into the bow (brass)
    m, rs = "Brass", 0.0013
    P = bow_heart(0.00040, 0.00095, m)
    P.append(key_shaft(0.0, 0.026, rs, m, barrel=True))
    P.append(key_bit(0.0245, 0.0052, 0.0058, 0.0013, m, "D", -rs * 0.6))
    return P


def key_brass():
    # the sitting-room key: brass, an oval bow with two scrolls in it
    m, rs = "Brass", 0.0021
    P = moved(bow_oval(0.0125, 0.0092, 0.0017, m), (-0.0125, 0, 0))
    P.append(key_shaft(0.0, 0.050, rs, m))
    P.append(key_bit(0.0470, 0.0100, 0.0110, 0.0020, m, "A", -rs * 0.6))
    return P


def key_desk():
    # the desk key: a little steel barrel key with a plain ring
    m, rs = "Steel", 0.0016
    P = moved(bow_ring(0.0078, 0.0015, m), (-0.0078, 0, 0))
    P.append(key_shaft(0.0, 0.030, rs, m, barrel=True))
    P.append(key_bit(0.0285, 0.0062, 0.0066, 0.0014, m, "C", -rs * 0.6))
    return P


def key_long():
    # the attic key: long, iron, with a paper tag on a loop of string, too worn to read
    m, rs = "Iron", 0.0024
    P = moved(bow_ring(0.0125, 0.0023, m), (-0.0125, 0, 0))
    P.append(key_shaft(0.0, 0.074, rs, m))
    P.append(key_bit(0.0705, 0.0120, 0.0135, 0.0022, m, "B", -rs * 0.6))
    tag = plate([(-0.016, -0.008), (0.012, -0.008), (0.016, -0.004), (0.016, 0.004), (0.012, 0.008), (-0.016, 0.008)], 0.0005, "Paper", z=-0.00025)
    tag = cut(tag, cyl(0.0014, 0.004, (0.0125, 0, 0), m="Paper", v=16))
    P.append(moved(tag, (-0.047, 0.020, -0.0012), (0, 0, -0.5)))
    P.append(torus(0.0022, 0.0004, (-0.0360, 0.0140, -0.0010), m="Brass", seg=20, rseg=6))                  # the eyelet
    pts = [(-0.0355, 0.0138, -0.0008), (-0.031, 0.011, 0.0005), (-0.027, 0.006, 0.0018), (-0.0248, 0.0005, 0.0022), (-0.0235, -0.004, 0.0012),
           (-0.0250, -0.0085, -0.0015), (-0.029, -0.0045, -0.0022), (-0.031, 0.003, -0.0020), (-0.033, 0.009, -0.0016)]
    P.append(tube(pts, 0.00035, "String", True, 3))
    for i, y in enumerate((0.0035, 0.0005, -0.0030)):                                                        # what is left of the writing
        sc = moved(tube([(-0.010 + 0.0023 * k, y + 0.0007 * math.sin(k * 2.1 + i), 0.0) for k in range(9 - i * 2)], 0.00016, "Ink", False, 2),
                   (-0.047 - 0.004 * 0, 0.020, -0.0009), (0, 0, -0.5))
        P.append(sc)
    return P


def key_iron():
    # the prayer-room key: iron, a trefoil bow, on a length of red ribbon
    m, rs = "Iron", 0.0023
    P = bow_trefoil(0.0052, 0.0017, m)
    P.append(key_shaft(0.0, 0.058, rs, m))
    P.append(key_bit(0.0550, 0.0115, 0.0125, 0.0022, m, "A", -rs * 0.6))
    c = (-0.0052 * 1.28 * 2, 0.0)                                         # the far lobe: the ribbon goes through it
    for sgn, ln, sw in ((1, 0.058, 0.9), (-1, 0.047, 1.3)):
        pts = []
        for k in range(26):
            u = k / 25.0
            pts.append((c[0] - 0.002 - u * ln * 0.9, c[1] + sgn * (0.003 + u * ln * 0.45) + 0.0022 * math.sin(u * 7.0 * sw), 0.0002 + 0.0012 * math.sin(u * 9.0 + sgn) * (1 - u * 0.5) - 0.0010))
        P.append(strip(pts, 0.0080, 0.00035, "Ribbon"))
    P.append(strip([(c[0] + 0.0045, 0.0005, 0.0019), (c[0] + 0.001, 0.0, 0.0024), (c[0] - 0.003, -0.0003, 0.0016), (c[0] - 0.0055, 0.0, 0.0002)], 0.0058, 0.0004, "Ribbon"))
    P.append(sphere(0.0030, (c[0] - 0.0050, 0.0, 0.0003), "Ribbon", 16, 8, (1, 1.2, 0.6)))                   # the knot
    return P


def flat_key(m="Steel", L=0.030, head=0.0105, s=1.0, cuts=(0.35, 0.7, 0.2, 0.55, 0.85, 0.4), stamp="27"):
    """A flat padlock key: round head with a hole, a blade with saw cuts along one edge and a groove down it."""
    t = 0.0019 * s
    o = [(head * s * math.cos(a), head * s * math.sin(a)) for a in [PI * 0.28 + (2 * PI - PI * 0.56) * k / 40 for k in range(41)]]
    bw = 0.0040 * s
    x0 = head * s * 0.82
    o += [(x0 + 0.002 * s, -bw)]
    n = len(cuts)
    seg = (L * s - 0.006 * s) / n
    for i, c in enumerate(cuts):                                           # the cut edge (toward -Y)
        xa = x0 + 0.004 * s + i * seg
        o += [(xa, -bw), (xa + seg * 0.5, -bw + c * bw * 0.9), (xa + seg, -bw)]
    o += [(x0 + L * s, -bw * 0.2), (x0 + L * s + 0.002 * s, bw * 0.2), (x0 + L * s - 0.001 * s, bw), (x0 + 0.002 * s, bw)]
    k = plate(o, t, m, bevel=t * 0.14, z=-t / 2)
    k = cut(k, cyl(0.0030 * s, t * 4, (-head * s * 0.42, 0, 0), m=m, v=24))
    k = cut(k, box(L * s * 0.86, 0.0011 * s, t, (x0 + L * s * 0.50, bw * 0.30, t * 0.82), m=m))              # the groove
    P = [k]
    if stamp:
        P.append(text(stamp, 0.0050 * s, 0.0004, (head * s * 0.28, 0, t / 2), m=m))
    return P


def key_padlock():
    return flat_key("Brass", 0.031, 0.0112, 1.0, stamp="27")


def keyring():
    # Walter's keys: a steel split ring, a leather fob stamped W.H., and three keys that do not match
    P = []
    R = 0.0165
    pts = [(R * math.cos(a), R * math.sin(a), 0.0007 * (a / (2 * PI) - 1.0)) for a in [4 * PI * k / 150 for k in range(151)]]
    P.append(tube(pts, 0.00075, "Steel", False, 3))
    a = moved([key_shaft(0.0, 0.050, 0.0021, "Iron"), key_bit(0.047, 0.010, 0.011, 0.0020, "Iron", "B", -0.0013)] + moved(bow_ring(0.0100, 0.0019, "Iron"), (-0.0100, 0, 0)),
              (0.0165 + 0.0195, -0.0015, 0.0), (0, 0, -0.10))
    b = moved(flat_key("Brass", 0.029, 0.0105, 0.95, (0.5, 0.2, 0.8, 0.4, 0.65), "14"), (0.0115, -0.0235, 0.0021), (0, 0, -1.02))
    c = moved([key_shaft(0.0, 0.027, 0.0015, "Steel", True), key_bit(0.0258, 0.0056, 0.0060, 0.0013, "Steel", "C", -0.0009)] + moved(bow_ring(0.0070, 0.0013, "Steel"), (-0.0070, 0, 0)),
              (0.0235, 0.0200, -0.0018), (0, 0, 0.62))
    P += a + b + c
    fo = [(0.0, -0.0115), (0.030, -0.0135), (0.0385, -0.0085), (0.0405, 0.0), (0.0385, 0.0085), (0.030, 0.0135), (0.0, 0.0115), (-0.0050, 0.0050), (-0.0050, -0.0050)]
    fob = plate(fo, 0.0028, "Leather", bevel=0.0009, z=-0.0014)
    fob = cut(fob, cyl(0.0021, 0.01, (0.0008, 0, 0), m="Leather", v=20))
    fob = cut(fob, text("W.H.", 0.0105, 0.0012, (0.0215, 0, 0.0014), m="Leather"))
    stitch = [box(0.0018, 0.0005, 0.0004, (0.006 + 0.0034 * k, sy * (0.0098 + 0.0002 * k * (1 if k < 7 else 0)), 0.0014), m="String") for k in range(8) for sy in (-1, 1)]
    P += moved([fob, torus(0.0030, 0.0006, (0.0008, 0, 0.0014), m="Brass", seg=24, rseg=8)] + stitch, (-0.0180 - 0.0008, 0.0, -0.0022), (0, 0, PI + 0.22))
    return P


# ============================================================================================ tools and keepsakes
def screwdriver():
    # an old flat-head lying along X: a turned handle in chipped red enamel with flutes for the grip, a brass ferrule,
    # a steel shaft forged out flat at the tip
    def flute(a, x):
        k = max(0.0, min(1.0, (x + 0.086) / 0.012)) * max(0.0, min(1.0, (-0.012 - x) / 0.012))
        return 1.0 - 0.075 * k * (0.5 + 0.5 * math.cos(8 * a))
    hp = [(-0.097, 0.0040), (-0.0955, 0.0085), (-0.092, 0.0118), (-0.086, 0.0138), (-0.076, 0.0146), (-0.060, 0.0140), (-0.040, 0.0128), (-0.024, 0.0118),
          (-0.014, 0.0112), (-0.009, 0.0100), (-0.006, 0.0102)]
    P = [lathe(hp, "PaintRed", 48, flute)]
    P.append(lathe([(-0.0065, 0.0102), (-0.006, 0.0110), (-0.0045, 0.0112), (-0.004, 0.0106), (0.004, 0.0100), (0.0045, 0.0106), (0.006, 0.0106), (0.0065, 0.0092), (0.008, 0.0060)], "Brass", 40))
    P.append(lathe([(0.006, 0.0034), (0.090, 0.0033), (0.104, 0.0033, 0.0033), (0.116, 0.0046, 0.0019), (0.128, 0.0052, 0.0009), (0.1305, 0.0052, 0.00045)], "Steel", 24))
    P.append(cyl(0.0016, 0.0234, (-0.050, 0, 0), (PI / 2, 0, 0), "Brass", 12))                             # the pin through the handle
    return moved(P, (0, 0, 0), (0.35, 0, 0))


def fuse():
    # a screw-in plug fuse, the old kind: a brass threaded base, a porcelain body, a glass window with the rating under it
    def knurl(a, x):
        return 1.0 + 0.035 * (0.5 + 0.5 * math.cos(24 * a))
    P = [moved(lathe([(0.000, 0.0034), (0.0006, 0.0040), (0.0020, 0.0040), (0.0026, 0.0072), (0.0040, 0.0100), (0.0050, 0.0104)], "Ceramic", 40), rot=(0, -PI / 2, 0))]
    P.append(moved(lathe([(0.0048, 0.0108), (0.0052, 0.0113), (0.0205, 0.0113), (0.0210, 0.0120)], "Brass", 48), rot=(0, -PI / 2, 0)))
    pts = [(0.01135 * math.cos(a), 0.01135 * math.sin(a), 0.0060 + 0.0034 * a / (2 * PI)) for a in [2 * PI * 3.9 * k / 220 for k in range(221)]]
    P.append(tube(pts, 0.0010, "Brass", False, 3))                                                           # the thread
    P.append(moved(lathe([(0.0208, 0.0132), (0.0215, 0.0140), (0.0300, 0.0140), (0.0320, 0.0136), (0.0335, 0.0128), (0.0340, 0.0118)], "Ceramic", 48, knurl), rot=(0, -PI / 2, 0)))
    capr = moved(lathe([(0.0332, 0.0124), (0.0346, 0.0124), (0.0353, 0.0118), (0.0353, 0.0104)], "Brass", 48), rot=(0, -PI / 2, 0))
    P.append(cut(capr, cyl(0.0100, 0.01, (0, 0, 0.0345), m="Brass", v=48)))                                    # the cap ring
    P.append(cyl(0.0100, 0.0008, (0, 0, 0.0344), m="Cream", v=40))                                           # the card under the glass
    P.append(text("15", 0.0080, 0.0003, (0, 0.0002, 0.0349), m="Ink"))
    P.append(tube(ring_pts(0.0072, 40, z=0.0349), 0.00028, "Ink", True, 2))
    
    P.append(cyl(0.0017, 0.0010, (0, 0, -0.0003), m="Brass", v=16))                                          # the contact
    return P


def shears():
    # sewing shears: two long steel blades on a brass screw, bows in black japan worn through to the metal
    P = []
    for sgn in (1, -1):
        a = sgn * math.radians(8.5)
        t = 0.0021
        o = [(-0.012, -0.0050), (0.000, -0.0078), (0.020, -0.0076), (0.060, -0.0050), (0.092, -0.0020), (0.106, 0.0006), (0.100, 0.0030), (0.060, 0.0058),
             (0.020, 0.0072), (0.000, 0.0070), (-0.012, 0.0048)]
        b = plate([(x, sgn * y) for x, y in o], t, "Steel", bevel=t * 0.25, z=-t / 2)
        b = cut(b, box(0.085, 0.0030, t, (0.058, sgn * 0.0052, t * 0.86), (0, 0, sgn * -0.055), "Steel"))        # the hollow grind along the edge
        P.append(moved(b, (0, 0, sgn * t * 0.5), (0, 0, a)))
        ha = a + sgn * math.radians(13) + PI
        d = Vector((math.cos(ha), math.sin(ha), 0))
        nrm = Vector((-d.y, d.x, 0)) * sgn
        R = 0.0165 if sgn > 0 else 0.0128
        shank = [tuple(d * 0.010 + Vector((0, 0, sgn * t * 0.5))), tuple(d * 0.030 + nrm * 0.0015 + Vector((0, 0, sgn * t * 0.5))), tuple(d * 0.046 + nrm * 0.004 + Vector((0, 0, sgn * t * 0.4)))]
        P.append(tube(shank, 0.0030, "Japan", False, 4))
        c = d * (0.046 + R * 0.9) + nrm * (0.004 + R * 0.35)
        lp = ring_pts(R, 56, c.x, c.y, 1.0, 0.72 if sgn > 0 else 0.85, sgn * t * 0.4)
        ang = math.atan2(d.y, d.x)
        lp = [(c.x + (x - c.x) * math.cos(ang) - (y - c.y) * math.sin(ang), c.y + (x - c.x) * math.sin(ang) + (y - c.y) * math.cos(ang), z) for x, y, z in lp]
        P.append(tube(lp, 0.0029, "Japan", True, 4))
    scr = cut(cyl(0.0046, 0.0066, (0, 0, 0), m="Brass", v=28, bevel=0.0004), box(0.012, 0.0009, 0.002, (0, 0, 0.0033), (0, 0, 0.5), "Brass"))
    P.append(scr)
    return P


def ring():
    # Walter's wedding ring: a plain court band, a line of milgrain at each edge, worn soft
    P = [moved(lathe([(-0.0030, 0.0098, 0.0098), (-0.0027, 0.0106), (-0.0015, 0.0110), (0.0, 0.0111), (0.0015, 0.0110), (0.0027, 0.0106), (0.0030, 0.0098)], "Gold", 72), rot=(0, -PI / 2, 0))]
    P[0] = cut(P[0], cyl(0.0094, 0.02, (0, 0, 0), m="Gold", v=72))
    for z in (-0.0023, 0.0023):
        P.append(tube(ring_pts(0.01072, 96, z=z), 0.00012, "Gold", True, 2))
    return P


def tags():
    # Daniel's dog tags: two stamped steel tags with rolled rims on a ball chain
    P = []
    lines = ("HARROW", "DANIEL W", "37 204 118", "T44   O", "P")

    def one(z):
        w, h, r = 0.0250, 0.0140, 0.0058
        o = []
        for cx, cy, a0 in ((w - r, h - r, 0.0), (-w + r, h - r, PI / 2), (-w + r, -h + r, PI), (w - r, -h + r, 1.5 * PI)):
            o += [(cx + r * math.cos(a0 + PI / 2 * k / 8), cy + r * math.sin(a0 + PI / 2 * k / 8)) for k in range(9)]
        t = plate(o, 0.0009, "Steel", bevel=0.0002, z=-0.00045)
        t = cut(t, cyl(0.0019, 0.01, (-w + 0.0048, 0, 0), m="Steel", v=20))
        t = cut(t, box(0.004, 0.0030, 0.01, (w, -0.0035, 0), m="Steel"))                                       # the notch
        Q = [t, tube([(x, y, 0.00025) for x, y in o], 0.00055, "Steel", True, 3)]
        for i, s in enumerate(lines):
            Q.append(text(s, 0.0042, 0.0005, (0.0030, 0.0098 - i * 0.0049, 0.00045), m="Steel", spacing=1.08))
        return moved(Q, (0, 0, z))
    P += moved(one(0.0), (0.0, 0.0, 0.0), (0, 0, 0.22))
    P += moved(one(0.0), (0.0130, -0.0100, 0.0015), (0, 0, -0.33))
    n = 64
    for k in range(n):                                                     # the chain: a long loop lying in a curl
        a = 2 * PI * k / n
        P.append(sphere(0.0012, (-0.020 * 1.0 - 0.036 + 0.036 * math.cos(a) + 0.004 * math.sin(3 * a), 0.006 + 0.028 * math.sin(a) + 0.003 * math.cos(2 * a), 0.0006), "Steel", 10, 6))
    return P


def uv_ball(R, m, seg=64, rings=40, bulge=None):
    verts, faces = [(0.0, 0.0, R + (bulge(0.0) if bulge else 0.0))], []
    for i in range(1, rings):
        ph = PI * i / rings
        rr = R + (bulge(ph) if bulge else 0.0)
        for k in range(seg):
            a = 2 * PI * k / seg
            verts.append((rr * math.sin(ph) * math.cos(a), rr * math.sin(ph) * math.sin(a), rr * math.cos(ph)))
    verts.append((0.0, 0.0, -R))
    for k in range(seg):
        faces.append((0, 1 + k, 1 + (k + 1) % seg))
    for i in range(rings - 2):
        for k in range(seg):
            a0, a1 = 1 + i * seg + k, 1 + i * seg + (k + 1) % seg
            faces.append((a0, a0 + seg, a1 + seg, a1))
    last = len(verts) - 1
    for k in range(seg):
        faces.append((last, 1 + (rings - 2) * seg + (k + 1) % seg, 1 + (rings - 2) * seg + k))
    ob = mesh(verts, faces, m)
    for p in ob.data.polygons:
        p.use_smooth = True
    return ob


def glasseye():
    # her glass eye, lying iris-up: the clear dome over the iris stands a little proud of the white
    def bulge(ph):
        lim = 0.50
        return 0.0011 * (0.5 + 0.5 * math.cos(PI * ph / lim)) if ph < lim else 0.0
    return [moved(uv_ball(EYE_R, "Eye", 72, 48, bulge), (0, 0, EYE_R))]


def jewelbox(opened=False):
    # her jewelry box: dark walnut with a pale inlaid band and a lozenge in the lid, brass corners held with pins, a shield
    # escutcheon, two barrel hinges, four bun feet.  Open: the lid stands back on its hinges, a clouded mirror inside it, the
    # tray lined in faded red felt with a row of ring rolls.
    W, D = 0.170, 0.115
    P = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            P.append(sphere(0.0075, (sx * 0.074, sy * 0.047, 0.004), "Brass", 20, 10, (1, 1, 0.8)))
    P.append(box(W + 0.006, D + 0.006, 0.006, (0, 0, 0.011), m="WoodDark", bevel=0.0022, seg=3))             # the plinth
    wt = 0.007
    if not opened:
        P.append(box(W, D, 0.046, (0, 0, 0.037), m="WoodDark", bevel=0.0012))
    else:
        P.append(box(W, D, 0.012, (0, 0, 0.020), m="WoodDark", bevel=0.0012))                               # the bottom
        for sy in (-1, 1):
            P.append(box(W, wt, 0.046, (0, sy * (D - wt) / 2, 0.037), m="WoodDark", bevel=0.0010))
        for sx in (-1, 1):
            P.append(box(wt, D - 2 * wt + 0.001, 0.046, (sx * (W - wt) / 2, 0, 0.037), m="WoodDark", bevel=0.0010))
        P.append(box(W - 2 * wt, D - 2 * wt, 0.0016, (0, 0, 0.0268), m="Felt"))                             # the lining
        for sy in (-1, 1):
            P.append(box(W - 2 * wt, 0.0012, 0.031, (0, sy * ((D - 2 * wt) / 2 - 0.0006), 0.0425), m="Felt"))
        for sx in (-1, 1):
            P.append(box(0.0012, D - 2 * wt, 0.031, (sx * ((W - 2 * wt) / 2 - 0.0006), 0, 0.0425), m="Felt"))
        P.append(box(0.0030, D - 2 * wt, 0.024, (-0.036, 0, 0.039), m="Felt", bevel=0.0008))                 # the divider
        for k in range(5):                                                                                  # ring rolls
            P.append(cyl(0.0056, 0.036, (-0.0585, -0.036 + k * 0.018, 0.0322), (0, PI / 2, 0), "Felt", 20, bevel=0.001))
    P.append(box(W + 0.0008, D + 0.0008, 0.0050, (0, 0, 0.040), m="Inlay"))                                  # the inlaid band
    for z in (0.0370, 0.0430):
        P.append(box(W + 0.0010, D + 0.0010, 0.0007, (0, 0, z), m="Black"))
    for sx in (-1, 1):                                                                                      # brass corners with pins
        for sy in (-1, 1):
            P.append(box(0.016, 0.0010, 0.044, (sx * (W / 2 - 0.008), sy * (D / 2 + 0.0004), 0.037), m="Brass", bevel=0.0003))
            P.append(box(0.0010, 0.016, 0.044, (sx * (W / 2 + 0.0004), sy * (D / 2 - 0.008), 0.037), m="Brass", bevel=0.0003))
            for z in (0.020, 0.037, 0.054):
                P.append(sphere(0.0011, (sx * (W / 2 - 0.009), sy * (D / 2 + 0.0009), z), "Brass", 10, 6))
                P.append(sphere(0.0011, (sx * (W / 2 + 0.0009), sy * (D / 2 - 0.009), z), "Brass", 10, 6))
    # the escutcheon: a little shield on the front (-Y), with the keyhole
    es = plate([(-0.0085, 0.011), (0.0085, 0.011), (0.0085, 0.001), (0.0055, -0.007), (0.0, -0.012), (-0.0055, -0.007), (-0.0085, 0.001)], 0.0010, "Brass", bevel=0.0003)
    P.append(moved(es, (0, -D / 2 - 0.0011, 0.046), (PI / 2, 0, 0)))
    P.append(cyl(0.0020, 0.0006, (0, -D / 2 - 0.0013, 0.0485), (PI / 2, 0, 0), "Black", 16))
    P.append(box(0.0016, 0.0006, 0.0060, (0, -D / 2 - 0.0013, 0.0452), m="Black"))
    for sx in (-1, 1):
        P.append(sphere(0.0009, (sx * 0.0062, -D / 2 - 0.0012, 0.0545), "Brass", 10, 6))
    # the lid
    L = []
    L.append(box(W + 0.004, D + 0.004, 0.012, (0, 0, 0.006), m="WoodDark", bevel=0.0016, seg=3))
    L.append(box(W - 0.014, D - 0.014, 0.008, (0, 0, 0.014), m="WoodDark", bevel=0.0035, seg=3))            # the raised field
    L.append(box(W - 0.030, D - 0.030, 0.0006, (0, 0, 0.0181), m="Inlay"))
    L.append(box(W - 0.033, D - 0.033, 0.0007, (0, 0, 0.0182), m="WoodDark"))
    loz = plate([(-0.034, 0.0), (0.0, -0.019), (0.034, 0.0), (0.0, 0.019)], 0.0007, "Inlay", z=0.0182)
    L.append(loz)
    L.append(plate([(-0.027, 0.0), (0.0, -0.0145), (0.027, 0.0), (0.0, 0.0145)], 0.0008, "WoodDark", z=0.0183))
    L.append(plate([(-0.012, 0.0), (0.0, -0.0065), (0.012, 0.0), (0.0, 0.0065)], 0.0009, "Inlay", z=0.0184))
    L.append(box(0.022, 0.0010, 0.008, (0, -D / 2 - 0.0024, 0.005), m="Brass", bevel=0.0003))               # the hasp plate on the lid's front edge
    if opened:
        L.append(box(W - 0.020, D - 0.020, 0.0008, (0, 0, -0.0002), m="Mirror"))
        L.append(box(W - 0.014, D - 0.014, 0.0010, (0, 0, 0.0002), m="Felt"))
    for sx in (-1, 1):                                                                                      # barrel hinges on the back edge
        P.append(cyl(0.0022, 0.022, (sx * 0.050, D / 2 + 0.0016, 0.0605), (0, PI / 2, 0), "Brass", 16, bevel=0.0003))
        P.append(box(0.022, 0.0008, 0.010, (sx * 0.050, D / 2 + 0.0008, 0.0545), m="Brass", bevel=0.0002))
        L.append(box(0.022, 0.0008, 0.008, (sx * 0.050, D / 2 + 0.0026, 0.0045), m="Brass", bevel=0.0002))
    if not opened:
        P += moved(L, (0, 0, 0.0602))
    else:
        # swing the lid back about the hinge line (y = D/2 + 0.0016, z = 0.0605)
        a = math.radians(102)
        for ob in L:
            for v in ob.data.vertices:
                y, z = v.co.y - (D / 2 + 0.0016), v.co.z + 0.0602 - 0.0605
                v.co.y = (D / 2 + 0.0016) + y * math.cos(a) + z * math.sin(a)
                v.co.z = 0.0605 - y * math.sin(a) + z * math.cos(a)
        P += L
    return P


def ammobox():
    # a box of pistol cartridges with the flap torn off: a card tray in a printed sleeve, the brass heads of the rounds showing
    P = [box(0.110, 0.070, 0.044, (0, 0, 0.022), m="Card", bevel=0.0010)]
    P.append(box(0.1108, 0.0708, 0.024, (0, 0, 0.018), m="Label", bevel=0.0004))
    P.append(box(0.1110, 0.0710, 0.0030, (0, 0, 0.0285), m="Cream"))
    P.append(box(0.1110, 0.0710, 0.0016, (0, 0, 0.0080), m="Cream"))
    for sy in (-1, 1):
        P.append(text("50 CARTRIDGES", 0.0092, 0.0004, (0, sy * 0.0355, 0.0190), (PI / 2, 0, 0 if sy < 0 else PI), "Cream", 1.05))
        P.append(text("9 mm  -  115 GR.  -  CENTER FIRE", 0.0036, 0.0004, (0, sy * 0.0355, 0.0118), (PI / 2, 0, 0 if sy < 0 else PI), "Cream", 1.1))
    for sx in (-1, 1):
        P.append(text("9 mm", 0.0120, 0.0004, (sx * 0.0555, 0, 0.0185), (PI / 2, 0, PI / 2 * sx), "Cream"))
    P.append(box(0.100, 0.060, 0.002, (0, 0, 0.0432), m="Black"))                                            # the dark of the tray
    P.append(box(0.102, 0.062, 0.0012, (0, 0, 0.0444), m="Card"))
    tray = P[-1]
    for i in range(7):
        for j in range(4):
            x, y = -0.0405 + i * 0.0135, -0.0205 + j * 0.0137
            tray = cut(tray, cyl(0.0056, 0.01, (x, y, 0.0444), m="Card", v=16))
            if (i, j) in ((6, 3), (5, 3), (6, 2)):
                continue                                                                                    # a few already used
            P.append(cyl(0.0050, 0.0050, (x, y, 0.0440), m="Brass", v=20, bevel=0.0005))
            P.append(cyl(0.0021, 0.0052, (x, y, 0.04405), m="Steel", v=12))
            P.append(tube(ring_pts(0.0031, 20, x, y, z=0.0465), 0.00022, "Ink", True, 2))
    fl = box(0.108, 0.030, 0.0009, (0.004, 0.052, 0.0005), (0, 0, 0.12), "Card")
    P.append(fl)                                                                                            # the torn flap lying beside it
    return P


def vent_parts(frame=True, cover=True):
    # a cast-iron wall register, 36 x 26 cm.  Its back is on y = 0 and it faces -Y.
    W, H = 0.36, 0.26
    P = []
    if frame:
        P.append(box(W - 0.02, 0.004, H - 0.02, (0, -0.002, H / 2), m="Black"))
        for (sx, sz, cx, cz) in ((W, 0.03, 0, 0.015), (W, 0.03, 0, H - 0.015), (0.03, H, -W / 2 + 0.015, H / 2), (0.03, H, W / 2 - 0.015, H / 2)):
            P.append(box(sx, 0.028, sz, (cx, -0.014, cz), m="CastIron", bevel=0.003, seg=3))
        P.append(box(W - 0.06, 0.036, 0.004, (0, -0.018, 0.032), m="CastIron", bevel=0.0008))
    if cover:
        y = -0.0315
        P.append(box(W - 0.012, 0.005, 0.024, (0, y, 0.018), m="CastIron", bevel=0.0012))
        P.append(box(W - 0.012, 0.005, 0.024, (0, y, H - 0.018), m="CastIron", bevel=0.0012))
        P.append(box(0.024, 0.005, H - 0.012, (-W / 2 + 0.018, y, H / 2), m="CastIron", bevel=0.0012))
        P.append(box(0.024, 0.005, H - 0.012, (W / 2 - 0.018, y, H / 2), m="CastIron", bevel=0.0012))
        P.append(box(0.010, 0.005, H - 0.05, (0, y, H / 2), m="CastIron", bevel=0.0012))                         # the middle bar
        for i in range(8):
            P.append(box(W - 0.05, 0.016, 0.003, (0, y + 0.004, 0.046 + i * 0.024), (math.radians(40), 0, 0), "CastIron", 0.0006))
        for sx in (-1, 1):
            for z in (0.018, H - 0.018):
                sc = cut(cyl(0.0058, 0.004, (sx * (W / 2 - 0.018), y - 0.004, z), (PI / 2, 0, 0), "Steel", 20, bevel=0.0006),
                         box(0.0125, 0.003, 0.0012, (sx * (W / 2 - 0.018), y - 0.006, z), (0, 0.4 * sx + z * 9, 0), "Steel"))
                P.append(sc)
    if frame and cover:
        # what can be made out behind the slats: something pale, pushed in, with one black button
        P.append(sphere(0.019, (0.061, -0.0135, 0.079), "Cloth", 20, 10, (1.0, 0.55, 0.95)))
        P.append(sphere(0.020, (0.010, -0.0125, 0.079), "Cloth", 20, 10, (2.6, 0.5, 1.5)))
        P.append(cyl(0.0036, 0.0011, (0.066, -0.0245, 0.072), (PI / 2, 0, 0), "Polymer", 16))
    return P


def doll(empty=False):
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


def vent_cover_flat():
    return moved(vent_parts(frame=False, cover=True), (0, 0, 0), (-PI / 2, 0, 0))


# ============================================================================================ join, unwrap, bake, export
def join(name, parts):
    flat = []
    for p in parts:
        flat += p if isinstance(p, list) else [p]
    bpy.ops.object.select_all(action="DESELECT")
    for p in flat:
        p.select_set(True)
    bpy.context.view_layer.objects.active = flat[0]
    bpy.ops.object.join()
    ob = bpy.context.object
    ob.name = name
    ob.data.name = name
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    co = np.empty(len(ob.data.vertices) * 3, dtype=np.float32)
    ob.data.vertices.foreach_get("co", co)
    co = co.reshape(-1, 3)
    off = np.array([-(co[:, 0].min() + co[:, 0].max()) / 2, -(co[:, 1].min() + co[:, 1].max()) / 2, -co[:, 2].min()], dtype=np.float32)
    co += off
    ob.data.vertices.foreach_set("co", co.reshape(-1))
    ob.data.update()
    for fn in ("shade_auto_smooth", "shade_smooth_by_angle"):
        try:
            getattr(bpy.ops.object, fn)(angle=math.radians(38))
            break
        except Exception:
            continue
    else:
        bpy.ops.object.shade_smooth()
    return ob


def bake_item(name, ob, size):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.render.bake.margin = max(4, size // 128)
    sc.render.bake.use_clear = True
    sc.render.bake.use_selected_to_active = False
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.006)
    bpy.ops.object.mode_set(mode="OBJECT")
    mats = [m for m in ob.data.materials if m]
    em, tn = {}, {}
    for m in mats:
        nt = m.node_tree
        em[m.name] = nt.nodes.new("ShaderNodeEmission")
        tn[m.name] = nt.nodes.new("ShaderNodeTexImage")
        for n in nt.nodes:
            n.select = False
        tn[m.name].select = True
        nt.nodes.active = tn[m.name]

    def run(tag, kind, non_color, samples):
        img = bpy.data.images.new(f"bake_{tag}", size, size, alpha=False, float_buffer=False)
        if non_color:
            img.colorspace_settings.name = "Non-Color"
        for m in mats:
            g = SOCK[m.name]["g"]
            tn[m.name].image = img
            for l in list(g.out.inputs["Surface"].links):
                g.L.remove(l)
            if kind == "EMIT":
                for l in list(em[m.name].inputs["Color"].links):
                    g.L.remove(l)
                g.L.new(SOCK[m.name][tag], em[m.name].inputs["Color"])
                g.L.new(em[m.name].outputs[0], g.out.inputs["Surface"])
            else:
                g.L.new(g.bsdf.outputs[0], g.out.inputs["Surface"])
        sc.cycles.samples = samples
        bpy.ops.object.bake(type=kind)
        return img

    def pixels(img):
        a = np.empty(size * size * 4, dtype=np.float32)
        img.pixels.foreach_get(a)
        return a.reshape(size, size, 4)

    def save(img, fname):
        img.filepath_raw = os.path.join(TEX, fname)
        img.file_format = "PNG"
        img.save()

    c = run("col", "EMIT", False, 24)
    save(c, f"T_Item_{name}_C.png")
    r = pixels(run("rough", "EMIT", True, 16))
    mt = pixels(run("metal", "EMIT", True, 16))
    sc.render.bake.normal_space = "TANGENT"
    n = run("normal", "NORMAL", True, 4)
    save(n, f"T_Item_{name}_N.png")
    orm = bpy.data.images.new("orm", size, size, alpha=False)
    orm.colorspace_settings.name = "Non-Color"
    o = np.ones((size, size, 4), dtype=np.float32)
    o[:, :, 1] = r[:, :, 0]
    o[:, :, 2] = mt[:, :, 0]
    orm.pixels.foreach_set(o.reshape(-1))
    save(orm, f"T_Item_{name}_ORM.png")
    # one material, wearing the baked maps
    fm = bpy.data.materials.new("Item")
    fm.use_nodes = True
    nt = fm.node_tree
    b = next(x for x in nt.nodes if x.type == "BSDF_PRINCIPLED")
    tc = nt.nodes.new("ShaderNodeTexImage"); tc.image = c
    nt.links.new(tc.outputs[0], b.inputs["Base Color"])
    to = nt.nodes.new("ShaderNodeTexImage"); to.image = orm
    sp = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(to.outputs[0], sp.inputs[0])
    nt.links.new(sp.outputs[1], b.inputs["Roughness"])
    nt.links.new(sp.outputs[2], b.inputs["Metallic"])
    tnn = nt.nodes.new("ShaderNodeTexImage"); tnn.image = n
    nm = nt.nodes.new("ShaderNodeNormalMap")
    nt.links.new(tnn.outputs[0], nm.inputs["Color"])
    nt.links.new(nm.outputs[0], b.inputs["Normal"])
    ob.data.materials.clear()
    ob.data.materials.append(fm)
    ob.data.polygons.foreach_set("material_index", [0] * len(ob.data.polygons))
    ob.data.update()


def preview(name, ob):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.samples = 48
    try:
        sc.cycles.use_denoising = True
    except Exception:
        pass
    w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.012, 0.012, 0.014, 1)
    w.node_tree.nodes["Background"].inputs[1].default_value = 1.0
    d = ob.dimensions
    size = max(d.x, d.y, d.z * 1.5)
    tgt = Vector((0, 0, d.z / 2))

    def lamp(nm, loc, watts, col, sz):
        L = bpy.data.objects.new(nm, bpy.data.lights.new(nm, "AREA"))
        L.data.energy = watts * size * size / 0.0025
        L.data.color = col
        L.data.size = sz * size
        L.location = tgt + Vector(loc) * size
        L.rotation_euler = (tgt - L.location).to_track_quat("-Z", "Y").to_euler()
        sc.collection.objects.link(L)
    lamp("key", (1.2, -1.6, 2.2), 0.55, (1.0, 0.93, 0.82), 1.2)
    lamp("fill", (-2.0, -0.6, 1.0), 0.16, (0.7, 0.8, 1.0), 2.5)
    lamp("rim", (-0.4, 2.2, 1.4), 0.45, (1.0, 1.0, 1.0), 1.0)
    bpy.ops.mesh.primitive_plane_add(size=size * 30, location=(0, 0, -0.00005))
    fl = bpy.context.object
    fmat = bpy.data.materials.new("floor"); fmat.use_nodes = True
    fb = next(x for x in fmat.node_tree.nodes if x.type == "BSDF_PRINCIPLED")
    fb.inputs["Base Color"].default_value = (0.012, 0.010, 0.008, 1); fb.inputs["Roughness"].default_value = 0.6
    fl.data.materials.append(fmat)
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
    cam.data.lens = 85; cam.data.clip_start = 0.001; cam.data.clip_end = 50
    cam.location = tgt + Vector((0.35, -0.80, 0.85)).normalized() * size * 3.1
    cam.rotation_euler = (tgt - cam.location).to_track_quat("-Z", "Y").to_euler()
    sc.render.resolution_x = 800; sc.render.resolution_y = 600
    sc.view_settings.view_transform = "Standard"
    sc.render.filepath = os.path.join(PRE, name + ".png")
    bpy.ops.render.render(write_still=True)


def build(name, fn, size=None):
    if ONLY and name not in ONLY:
        return
    bpy.ops.wm.read_factory_settings(use_empty=True)
    SOCK.clear()
    random.seed(name)
    ob = join("SM_Item_" + name, fn())
    d = ob.dimensions
    print(f"FINE {name}: {len(ob.data.vertices)} verts, {d.x * 100:.1f} x {d.y * 100:.1f} x {d.z * 100:.1f} cm")
    bake_item(name, ob, size or SIZE)
    bpy.ops.object.select_all(action="DESELECT")
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.export_scene.fbx(filepath=os.path.join(OUT, f"SM_Item_{name}.fbx"), use_selection=True, object_types={"MESH"}, mesh_smooth_type="FACE",
                             add_leaf_bones=False, bake_anim=False, apply_scale_options="FBX_SCALE_NONE")
    if PREVIEW:
        preview(name, ob)
    print(f"FINE {name}: done")


build("Screwdriver", screwdriver)
build("Doll", doll)
build("DollEmpty", lambda: doll(True))
build("KeyHeart", key_heart)
build("Key", key_brass)
build("KeyDesk", key_desk)
build("KeyLong", key_long)
build("KeyIron", key_iron)
build("KeyPadlock", key_padlock)
build("Keyring", keyring)
build("GlassEye", glasseye)
build("JewelBox", jewelbox, 2048)
build("JewelBoxOpen", lambda: jewelbox(True), 2048)
build("Fuse", fuse)
build("Shears", shears)
build("Ring", ring)
build("Tags", tags)
build("AmmoBox", ammobox)
build("Vent", vent_parts)
build("VentOpen", lambda: vent_parts(True, False))
build("VentCoverFlat", vent_cover_flat)
print("FINE all done")
