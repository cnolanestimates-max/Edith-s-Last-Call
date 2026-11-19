"""Blender: Edith's skin, made to look like skin (Cheyenne 2026-11-19: "less gamey looking and more real ... wrinkly, but the skin
is still skin ... especially her face").  Procedural in object space on the existing model: creases and folds, pores, mottling,
veins, age spots, wet patches, light going a little way into the flesh.  No paid generation.

  blender -b --factory-startup -P her_look.py -- <SK_Her.fbx> <tex dir> <out dir> preview [names...]   close-up renders to choose from
  blender -b --factory-startup -P her_look.py -- <SK_Her.fbx> <tex dir> <out dir> bake <name>          4k maps of one look for Unreal

Looks: now (what is in the game), leather, darkwet, corpse.
"""
import bpy, math, os, sys
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
FBX, TEX, OUT, MODE = argv[0], argv[1], argv[2], argv[3]
NAMES = argv[4:]
os.makedirs(OUT, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.fbx(filepath=FBX)
sc = bpy.context.scene
mesh = max((o for o in sc.objects if o.type == "MESH"), key=lambda o: len(o.data.vertices))
bb = [mesh.matrix_world @ Vector(c) for c in mesh.bound_box]
zmin, zmax = min(v.z for v in bb), max(v.z for v in bb)
K = (zmax - zmin) / 270.0                      # WORLD units per centimetre (she is 270 cm tall): cameras, lights, distances
KO = (max(c[2] for c in mesh.bound_box) - min(c[2] for c in mesh.bound_box)) / 270.0     # the mesh's own units per centimetre: textures
print("HERLOOK mesh", mesh.name, len(mesh.data.vertices), "verts, height", round(zmax - zmin, 3), "units; k =", round(K, 5),
      "; materials", [m.name for m in mesh.data.materials], "; keys", [k.name for k in (mesh.data.shape_keys.key_blocks if mesh.data.shape_keys else [])])


def cm(x, y, z):
    return Vector((x * K, y * K, zmin + z * K))


LOOKS = {
    #            skin A (dark)          skin B (light)         crease red  wet   sss   bump
    "leather": ((0.040, 0.029, 0.022), (0.150, 0.112, 0.086), 0.40, 0.30, 0.30, 1.0),
    "darkwet": ((0.012, 0.010, 0.009), (0.050, 0.038, 0.031), 0.50, 0.75, 0.25, 1.0),
    "corpse":  ((0.060, 0.058, 0.056), (0.210, 0.200, 0.186), 0.60, 0.40, 0.40, 1.1),
    # look C taken further (a seventh number: how much of the extra layers)
    "darkwet2": ((0.012, 0.010, 0.009), (0.056, 0.042, 0.033), 0.55, 0.80, 0.25, 1.40, 0.6),
    "darkwet3": ((0.012, 0.010, 0.009), (0.060, 0.044, 0.034), 0.65, 0.90, 0.25, 1.70, 1.0),
    # an eighth number: the middle-scale layers (deeper folds, traceable veins, scabs, wet streaks), with no fine grain added
    "darkwet4": ((0.012, 0.010, 0.009), (0.062, 0.046, 0.037), 0.60, 0.80, 0.25, 1.30, 0.0, 1.0),
    "darkwet5": ((0.012, 0.010, 0.009), (0.066, 0.049, 0.039), 0.70, 0.85, 0.25, 1.55, 0.0, 1.6),
}


def tex_image(nt, fname, non_color):
    n = nt.nodes.new("ShaderNodeTexImage")
    n.image = bpy.data.images.load(os.path.join(TEX, fname))
    if non_color:
        n.image.colorspace_settings.name = "Non-Color"
    return n


def material_now():
    """What the game shows today: the generated texture, tinted dark, plain."""
    m = bpy.data.materials.new("her_now"); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    t = tex_image(nt, "T_Her_BaseColor.png", False)
    mul = nt.nodes.new("ShaderNodeMixRGB"); mul.blend_type = "MULTIPLY"; mul.inputs[0].default_value = 1.0
    mul.inputs[2].default_value = (0.21 * 2.2, 0.19 * 2.2, 0.17 * 2.2, 1)
    nt.links.new(t.outputs["Color"], mul.inputs[1]); nt.links.new(mul.outputs[0], b.inputs["Base Color"])
    nm = nt.nodes.new("ShaderNodeNormalMap"); n = tex_image(nt, "T_Her_Normal.png", True)
    nt.links.new(n.outputs["Color"], nm.inputs["Color"]); nt.links.new(nm.outputs[0], b.inputs["Normal"])
    b.inputs["Roughness"].default_value = 0.55
    return m


def material_look(name):
    ca, cb, red, wet, sss, bump = LOOKS[name][:6]
    extra = LOOKS[name][6] if len(LOOKS[name]) > 6 else 0.0
    mid = LOOKS[name][7] if len(LOOKS[name]) > 7 else 0.0
    m = bpy.data.materials.new("her_" + name); m.use_nodes = True
    nt = m.node_tree; N = nt.nodes; L = nt.links
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

    def ramp(v, lo, hi):
        n = N.new("ShaderNodeMapRange"); n.inputs["From Min"].default_value = lo; n.inputs["From Max"].default_value = hi
        n.interpolation_type = "SMOOTHSTEP"; L.new(v, n.inputs["Value"]); return n.outputs[0]

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

    def mapped(scale):
        n = N.new("ShaderNodeMapping"); n.inputs["Scale"].default_value = scale; L.new(P, n.inputs["Vector"]); return n.outputs[0]

    def noise(vec, scale, detail=3.0, rough=0.55):
        n = N.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = scale; n.inputs["Detail"].default_value = detail
        n.inputs["Roughness"].default_value = rough; L.new(vec, n.inputs["Vector"]); return n

    def edges(vec, scale, rand=1.0):
        n = N.new("ShaderNodeTexVoronoi"); n.feature = "DISTANCE_TO_EDGE"; n.inputs["Scale"].default_value = scale
        n.inputs["Randomness"].default_value = rand; L.new(vec, n.inputs["Vector"]); return n.outputs["Distance"]

    # a slow warp so nothing runs in straight lines
    warp = noise(P, 0.22, 2.0)
    wv = N.new("ShaderNodeVectorMath"); wv.operation = "SCALE"; wv.inputs["Scale"].default_value = 3.2
    L.new(warp.outputs["Color"], wv.inputs[0])
    add = N.new("ShaderNodeVectorMath"); add.operation = "ADD"; L.new(P, add.inputs[0]); L.new(wv.outputs[0], add.inputs[1])
    Pw = add.outputs[0]

    def mapped_w(scale):
        n = N.new("ShaderNodeMapping"); n.inputs["Scale"].default_value = scale; L.new(Pw, n.inputs["Vector"]); return n.outputs[0]

    def waves(vec, scale, distortion, direction="Z"):
        n = N.new("ShaderNodeTexWave"); n.wave_type = "BANDS"; n.bands_direction = direction; n.wave_profile = "SIN"
        n.inputs["Scale"].default_value = scale; n.inputs["Distortion"].default_value = distortion
        n.inputs["Detail"].default_value = 3.0; n.inputs["Detail Scale"].default_value = 1.6; n.inputs["Detail Roughness"].default_value = 0.6
        L.new(vec, n.inputs["Vector"]); return n.outputs["Fac"]
    # old skin: long wandering wrinkles lying across the body, a second fainter set crossing them, and a tiny polygon grain
    w1 = waves(Pw, 0.55, 5.5)
    w2 = waves(Pw, 1.25, 7.0)
    w3 = waves(Pw, 0.9, 6.0, "X")
    fold = math_("MULTIPLY", w1, ramp(noise(P, 0.3, 2.0).outputs["Fac"], 0.25, 0.7))      # wrinkles come and go
    fold = math_("MAXIMUM", fold, math_("MULTIPLY", w2, 0.55))
    fold = math_("SUBTRACT", 1.0, math_("POWER", fold, 3.0))                                  # 0 down in the crease, 1 on the flat
    fine = edges(mapped((1.0, 1.0, 1.0)), 5.5)                                              # the polygon grain, about 2 mm
    fine2 = math_("ADD", math_("MULTIPLY", math_("SUBTRACT", 1.0, math_("POWER", w3, 4.0)), 0.5), 0.5)
    pore = noise(P, 34.0, 2.0, 0.6).outputs["Fac"]
    mott = noise(P, 0.085, 5.0, 0.62).outputs["Fac"]
    spot = ramp(noise(P, 0.75, 2.0).outputs["Fac"], 0.66, 0.74)
    vein = math_("SUBTRACT", 1.0, ramp(edges(mapped_w((1, 1, 1)), 0.14), 0.0, 0.035))
    veinsoft = math_("MULTIPLY", vein, ramp(noise(P, 0.05, 2.0).outputs["Fac"], 0.45, 0.6))
    # ---- the extra layers (0 = none of them)
    w4 = waves(Pw, 2.7, 8.0)
    w5 = waves(Pw, 3.6, 9.0, "X")
    micro = math_("SUBTRACT", 1.0, math_("POWER", math_("MAXIMUM", w4, math_("MULTIPLY", w5, 0.75)), 2.5))          # fine wrinkles between the big ones
    vor = N.new("ShaderNodeTexVoronoi"); vor.feature = "F1"; vor.inputs["Scale"].default_value = 15.0; L.new(P, vor.inputs["Vector"])
    pit = ramp(vor.outputs["Distance"], 0.0, 0.30)                                                              # 0 in the pore, 1 on the skin
    bruise = ramp(noise(P, 0.06, 3.0).outputs["Fac"], 0.54, 0.70)
    scabn = noise(Pw, 0.85, 5.0, 0.65).outputs["Fac"]
    scab = math_("MULTIPLY", ramp(scabn, 0.675, 0.715), ramp(noise(P, 0.12, 2.0).outputs["Fac"], 0.40, 0.60))  # crusted patches, in a few regions only
    peel = math_("SUBTRACT", ramp(scabn, 0.635, 0.655), ramp(scabn, 0.670, 0.690))                              # the skin lifting round them
    drip = math_("MULTIPLY", ramp(noise(mapped((7.0, 7.0, 0.22)), 1.0, 2.0).outputs["Fac"], 0.60, 0.70), ramp(noise(P, 0.07, 2.0).outputs["Fac"], 0.42, 0.62))
    veinw = math_("MULTIPLY", math_("SUBTRACT", 1.0, ramp(edges(mapped_w((1, 1, 1)), 0.11), 0.0, 0.06)), ramp(noise(P, 0.045, 2.0).outputs["Fac"], 0.40, 0.58))
    scabn2 = noise(Pw, 0.42, 4.0, 0.6).outputs["Fac"]
    scabm = math_("MULTIPLY", ramp(scabn2, 0.66, 0.70), ramp(noise(P, 0.09, 2.0).outputs["Fac"], 0.45, 0.62))
    peelm = math_("SUBTRACT", ramp(scabn2, 0.615, 0.635), ramp(scabn2, 0.655, 0.675))
    streak = math_("MULTIPLY", ramp(noise(mapped((3.0, 3.0, 0.10)), 1.0, 2.0).outputs["Fac"], 0.55, 0.68), ramp(noise(P, 0.05, 2.0).outputs["Fac"], 0.40, 0.60))
    c_fold = math_("SUBTRACT", 1.0, ramp(fold, 0.15, 0.75))
    c_fine = math_("SUBTRACT", 1.0, ramp(fine, 0.0, 0.07))
    crease = math_("MAXIMUM", c_fold, math_("MULTIPLY", c_fine, 0.35))

    # ---- what the model's own texture says each bit is: hair (warm), dress (pale), inside the mouth (black), skin (the rest)
    old = tex_image(nt, "T_Her_BaseColor.png", False)
    gam = N.new("ShaderNodeGamma"); gam.inputs["Gamma"].default_value = 1 / 2.2; L.new(old.outputs["Color"], gam.inputs["Color"])
    sep = N.new("ShaderNodeSeparateColor"); L.new(gam.outputs[0], sep.inputs[0])
    val = math_("MAXIMUM", sep.outputs[0], math_("MAXIMUM", sep.outputs[1], sep.outputs[2]))
    # hair is warmer for its brightness than skin is ((r - b) / r about 0.12 against 0.06)
    m_hair = ramp(math_("DIVIDE", math_("SUBTRACT", sep.outputs[0], sep.outputs[2]), math_("MAXIMUM", sep.outputs[0], 0.05)), 0.078, 0.102)
    # the dress cannot be told from skin by colour: it is the trunk between the thighs and the collar
    sp = N.new("ShaderNodeSeparateXYZ"); L.new(P, sp.inputs[0])
    ax = math_("ABSOLUTE", sp.outputs[0])
    m_dress = math_("MULTIPLY", math_("MULTIPLY", ramp(sp.outputs[2], 97.0, 103.0), math_("SUBTRACT", 1.0, ramp(sp.outputs[2], 201.0, 207.0))),
                    math_("SUBTRACT", 1.0, ramp(ax, 25.0, 30.0)))
    m_dress = math_("MULTIPLY", m_dress, math_("SUBTRACT", 1.0, m_hair))
    m_dark = math_("SUBTRACT", 1.0, ramp(val, 0.10, 0.26))
    m_skin = math_("SUBTRACT", 1.0, math_("MAXIMUM", m_hair, m_dress), clamp=True)

    # ---- shape: folds, hatch, pores, on top of the model's own normal map
    h = math_("ADD", math_("MULTIPLY", fold, 1.0), math_("MULTIPLY", ramp(fine, 0.0, 0.09), 0.10))
    h = math_("ADD", h, math_("MULTIPLY", fine2, 0.30))
    h = math_("ADD", h, math_("MULTIPLY", pore, 0.05))
    if extra > 0.0:
        h = math_("ADD", h, math_("MULTIPLY", micro, 0.42 * extra))
        h = math_("ADD", h, math_("MULTIPLY", ramp(fine, 0.0, 0.09), 0.22 * extra))
        h = math_("ADD", h, math_("MULTIPLY", pit, 0.16 * extra))
        h = math_("ADD", h, math_("MULTIPLY", veinsoft, 0.22 * extra))
        h = math_("ADD", h, math_("MULTIPLY", scab, 0.38 * extra))
        h = math_("ADD", h, math_("MULTIPLY", peel, 0.50 * extra))
    if mid > 0.0:
        h = math_("ADD", h, math_("MULTIPLY", fold, 0.6 * mid))                    # the big folds cut deeper
        h = math_("ADD", h, math_("MULTIPLY", fine2, 0.35 * mid))
        h = math_("ADD", h, math_("MULTIPLY", veinw, 0.30 * mid))                  # veins stand up under the skin
        h = math_("ADD", h, math_("MULTIPLY", scabm, 0.45 * mid))
        h = math_("ADD", h, math_("MULTIPLY", peelm, 0.40 * mid))
    nm = N.new("ShaderNodeNormalMap"); nm.inputs["Strength"].default_value = 0.8
    nimg = tex_image(nt, "T_Her_Normal.png", True); L.new(nimg.outputs["Color"], nm.inputs["Color"])
    bp = N.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = 0.75 * bump; bp.inputs["Distance"].default_value = (0.30 + 0.16 * extra) * K
    strand = noise(mapped((9.0, 9.0, 0.12)), 1.0, 2.0).outputs["Fac"]                 # long streaks down the hair
    h = math_("ADD", math_("MULTIPLY", h, m_skin), math_("MULTIPLY", math_("MULTIPLY", strand, m_hair), 0.5))
    L.new(h, bp.inputs["Height"]); L.new(nm.outputs[0], bp.inputs["Normal"])
    L.new(bp.outputs[0], b.inputs["Normal"])

    # ---- colour: two tones mottled, dark and red in the creases, veins, liver spots, grime where it is shut in
    ao = N.new("ShaderNodeAmbientOcclusion"); ao.inputs["Distance"].default_value = 7.0 * K; ao.samples = 4
    col = mix(ca, cb, ramp(mott, 0.34, 0.66))
    
    col = mix(col, (ca[0] * 0.35, ca[1] * 0.3, ca[2] * 0.28), math_("MULTIPLY", crease, 0.9))
    col = mix(col, (0.30 * red + ca[0], 0.045, 0.035), math_("MULTIPLY", c_fold, red * 0.55))
    col = mix(col, (cb[0] * 0.35, cb[1] * 0.42, cb[2] * 0.62), math_("MULTIPLY", veinsoft, 0.30))
    col = mix(col, (ca[0] * 1.3, ca[1] * 0.9, ca[2] * 0.6), math_("MULTIPLY", spot, 0.55))
    if extra > 0.0:
        col = mix(col, (0.030, 0.011, 0.028), math_("MULTIPLY", bruise, 0.22 * extra))                             # bruising under the skin
        col = mix(col, (cb[0] * 0.30, cb[1] * 0.40, cb[2] * 0.75), math_("MULTIPLY", veinsoft, 0.35 * extra))         # the veins stand out more
        col = mix(col, (ca[0] * 0.30, ca[1] * 0.26, ca[2] * 0.24), math_("MULTIPLY", math_("SUBTRACT", 1.0, micro), 0.30 * extra))
        col = mix(col, (0.004, 0.003, 0.003), math_("MULTIPLY", math_("SUBTRACT", 1.0, pit), 0.50 * extra))           # dark in the pores
        col = mix(col, (0.050, 0.008, 0.006), math_("MULTIPLY", scab, 0.85 * extra))                                  # old scabs
        col = mix(col, (cb[0] * 1.9, cb[1] * 1.8, cb[2] * 1.7), math_("MULTIPLY", peel, 0.75 * extra))                # dead skin lifting, paler
        col = mix(col, (ca[0] * 0.5, ca[1] * 0.5, ca[2] * 0.5), math_("MULTIPLY", drip, 0.45 * extra))                # wet runs darker
    if mid > 0.0:
        col = mix(col, (cb[0] * 0.28, cb[1] * 0.40, cb[2] * 0.85), math_("MULTIPLY", veinw, min(1.0, 0.55 * mid)))
        col = mix(col, (0.035, 0.012, 0.030), math_("MULTIPLY", bruise, min(1.0, 0.22 * mid)))
        col = mix(col, (0.045, 0.007, 0.005), math_("MULTIPLY", scabm, min(1.0, 0.9 * mid)))
        col = mix(col, (cb[0] * 2.2, cb[1] * 2.0, cb[2] * 1.8), math_("MULTIPLY", peelm, min(1.0, 0.8 * mid)))
    col = mix(col, (0, 0, 0), math_("MULTIPLY", math_("SUBTRACT", 1.0, ao.outputs["AO"]), 0.75))
    hairc = mix(mix(old.outputs["Color"], (0.30, 0.26, 0.19), 1.0, "MULTIPLY"), (0.012, 0.010, 0.008), ramp(strand, 0.30, 0.70))
    dressc = mix(old.outputs["Color"], (0.42, 0.39, 0.34), 1.0, "MULTIPLY")
    dressc = mix(dressc, (0.02, 0.016, 0.012), math_("MULTIPLY", ramp(noise(P, 0.12, 4.0).outputs["Fac"], 0.45, 0.7), 0.55))
    dressc = mix(dressc, (0, 0, 0), math_("MULTIPLY", math_("SUBTRACT", 1.0, ao.outputs["AO"]), 0.6))
    col = mix(mix(col, dressc, m_dress), hairc, m_hair)
    col = mix(col, (0.012, 0.002, 0.002), m_dark)
    L.new(col, b.inputs["Base Color"])

    # ---- wet: patches where it is slick, drier and rougher down in the creases
    wetmask = ramp(noise(P, 0.11, 3.0).outputs["Fac"], 0.62 - 0.35 * wet, 0.80 - 0.35 * wet)
    rough = math_("SUBTRACT", 0.62, math_("MULTIPLY", wetmask, 0.42))
    rough = math_("ADD", rough, math_("MULTIPLY", crease, 0.12), clamp=True)
    if extra > 0.0:
        rough = math_("ADD", rough, math_("MULTIPLY", math_("MAXIMUM", scab, peel), 0.45 * extra), clamp=True)       # crust and dead skin are dry
        rough = math_("SUBTRACT", rough, math_("MULTIPLY", drip, 0.40 * extra))                                      # the runs are slick
        rough = math_("MAXIMUM", rough, 0.06)
    if mid > 0.0:
        rough = math_("ADD", rough, math_("MULTIPLY", math_("MAXIMUM", scabm, peelm), min(1.0, 0.4 * mid)), clamp=True)
        rough = math_("MAXIMUM", math_("SUBTRACT", rough, math_("MULTIPLY", streak, min(1.0, 0.38 * mid))), 0.07)
    rough = mix(mix(rough, 0.9, m_dress), 0.42, m_hair)
    rough = mix(rough, 0.12, m_dark)
    L.new(rough, b.inputs["Roughness"])
    for key, val in (("Subsurface Scale", 0.6 * K), ("Specular IOR Level", 0.62), ("Coat Roughness", 0.12)):
        if key in b.inputs:
            b.inputs[key].default_value = val
    if "Subsurface Weight" in b.inputs:
        L.new(math_("MULTIPLY", m_skin, sss), b.inputs["Subsurface Weight"])
    if "Subsurface Radius" in b.inputs:
        b.inputs["Subsurface Radius"].default_value = (1.0, 0.35, 0.22)
    if "Coat Weight" in b.inputs:
        L.new(math_("MAXIMUM", math_("MULTIPLY", wetmask, 0.55 * wet), math_("MULTIPLY", streak, min(1.0, 0.8 * mid))) if mid > 0.0 else math_("MULTIPLY", wetmask, 0.55 * wet), b.inputs["Coat Weight"])
    m["_out"] = name
    return m, {"color": col, "rough": rough, "normal": bp.outputs[0]}


def use(mat):
    mesh.data.materials.clear()
    mesh.data.materials.append(mat)


def key(name, v):
    kb = mesh.data.shape_keys.key_blocks if mesh.data.shape_keys else {}
    if name in kb:
        kb[name].value = v


sc.render.engine = "CYCLES"
sc.cycles.device = "CPU"
sc.render.threads_mode = "FIXED"; sc.render.threads = 4            # the game may be running: leave it most of the machine
sc.cycles.use_denoising = True
try:
    sc.view_settings.view_transform = "Standard"; sc.view_settings.look = "Medium High Contrast"
except Exception as exc:
    print("HERLOOK view", exc)

if MODE == "preview":
    SHARP = any(len(LOOKS.get(n_, ())) > 6 for n_ in NAMES)          # the detailed looks: nothing may smear the detail
    sc.cycles.samples = 72 if SHARP else 28
    sc.cycles.use_denoising = not SHARP
    sc.render.threads = 6 if SHARP else 4
    sc.render.resolution_x = 800 if SHARP else 640; sc.render.resolution_y = 900 if SHARP else 720
    w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
    w.node_tree.nodes["Background"].inputs[0].default_value = (0.010, 0.012, 0.016, 1)
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); sc.collection.objects.link(cam); sc.camera = cam
    cam.data.lens = 62; cam.data.clip_start = 0.5 * K; cam.data.clip_end = 5000 * K
    cam.data.dof.use_dof = True; cam.data.dof.aperture_fstop = 2.2

    def light(name, kind, loc, target, watts, color, size):
        d = bpy.data.lights.new(name, kind); d.energy = watts; d.color = color
        if kind == "SPOT":
            d.spot_size = math.radians(48); d.spot_blend = 0.6; d.shadow_soft_size = size * K
        else:
            d.shadow_soft_size = size * K
        o = bpy.data.objects.new(name, d); sc.collection.objects.link(o)
        o.location = loc; o.rotation_euler = (target - loc).to_track_quat("-Z", "Y").to_euler()
        return o

    face = cm(1.0, -22.0, 236.0)
    # his flashlight, a little below and to one side; a cold rim from behind so the hair and the cheek separate from the dark
    light("flash", "SPOT", cm(-22, -115, 205), face, 150.0, (1.0, 0.90, 0.76), 1.5)
    light("rim", "POINT", cm(60, 55, 262), face, 25.0, (0.55, 0.70, 1.0), 6.0)
    # her eye as the game draws it: a glossy black ball with a small pale iris and a pupil
    def ball(r, loc, colr, rough_, emit=0.0):
        bpy.ops.mesh.primitive_uv_sphere_add(radius=r * K, segments=40, ring_count=20, location=loc)
        o = bpy.context.object; bpy.ops.object.shade_smooth()
        mm = bpy.data.materials.new("eye"); mm.use_nodes = True
        bb_ = mm.node_tree.nodes["Principled BSDF"]; bb_.inputs["Base Color"].default_value = (colr[0], colr[1], colr[2], 1); bb_.inputs["Roughness"].default_value = rough_
        o.data.materials.append(mm)
        return o
    ball(4.3, cm(6.0, -21.9, 246.6), (0.002, 0.002, 0.002), 0.04)
    ir = ball(1.0, cm(6.0, -21.9 - 4.3 * 0.80, 246.6), (0.30, 0.36, 0.40), 0.3); ir.scale = (1.46, 1.3, 1.46)
    pu = ball(1.0, cm(6.0, -21.9 - 4.3 * 0.985, 246.6), (0.001, 0.001, 0.001), 0.05); pu.scale = (0.69, 0.6, 0.69)
    views = {"close": (cm(7, -62, 240), cm(2.5, -22, 240), 85), "arm": (cm(-70, -120, 150), cm(-38, -8, 150), 70), "face": (cm(10, -92, 233), cm(1.5, -22, 237), 62), "mouth": (cm(-8, -70, 222), cm(1.0, -22, 228), 80), "bust": (cm(26, -165, 228), cm(0, -10, 222), 50)}
    mats = {"now": material_now()}
    for n in LOOKS:
        mats[n] = material_look(n)[0]
    for look in (NAMES or ["now", "leather", "darkwet", "corpse"]):
        use(mats[look])
        for pose, sv in ((("rest", 0.0),) if SHARP else (("rest", 0.0), ("scream", 1.0))):
            key("Scream", sv)
            for vname in (("face", "close") if pose == "rest" else ("face",)):
                loc, tgt, lens = views[vname]
                cam.location = loc; cam.rotation_euler = (tgt - loc).to_track_quat("-Z", "Y").to_euler(); cam.data.lens = lens
                cam.data.dof.focus_distance = (tgt - loc).length
                cam.data.dof.use_dof = not SHARP
                sc.render.filepath = os.path.join(OUT, f"{look}_{pose}_{vname}.png")
                bpy.ops.render.render(write_still=True)
                print("HERLOOK rendered", look, pose, vname)

elif MODE == "bake":
    name = NAMES[0]
    key("Scream", 0.0)
    mat, outs = material_look(name)
    use(mat)
    nt = mat.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    out = next(n for n in nt.nodes if n.type == "OUTPUT_MATERIAL")
    bpy.context.view_layer.objects.active = mesh
    mesh.select_set(True)
    SIZE = 4096
    sc.render.bake.margin = 8

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
        print("HERLOOK baked", fname)

    # colour and roughness go out through an emission shader (no lighting in the bake); the AO node needs a few samples
    em = nt.nodes.new("ShaderNodeEmission")
    sc.cycles.samples = 12
    nt.links.new(outs["color"], em.inputs["Color"]); nt.links.new(em.outputs[0], out.inputs["Surface"])
    img = target("color", False); bpy.ops.object.bake(type="EMIT"); save(img, f"T_Her_{name}_BaseColor.png")
    sc.cycles.samples = 2
    nt.links.new(outs["rough"], em.inputs["Color"])
    img = target("rough", True); bpy.ops.object.bake(type="EMIT"); save(img, f"T_Her_{name}_Roughness.png")
    nt.links.new(bsdf.outputs[0], out.inputs["Surface"])
    img = target("normal", True); bpy.ops.object.bake(type="NORMAL"); save(img, f"T_Her_{name}_Normal.png")
print("HERLOOK done")
