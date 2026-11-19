"""Unreal (headless): bring source assets into /Game/WC.  Re-runnable.  Steps chosen with env WC_STEPS (comma list) or all:
  kit      - give the Horror House Kit meshes collision (complex as simple)
  her      - skeletal mesh, animations, textures, material for Mabel
  mats     - small utility materials (dust mote, eye, glow, flat colours)
  audio    - every wav under SourceArt/Audio -> /Game/WC/Audio (VO in /Game/WC/Audio/VO)
  tex      - PBR texture sets under SourceArt/Textures/<Name>/ -> triplanar material instances MI_<Name>
"""
import json
import os

import unreal

G = "/Game/WC"
ROOT = "C:/GameDev/Unreal/WellnessCheck"
SRC = ROOT + "/SourceArt"
eal = unreal.EditorAssetLibrary
tools = unreal.AssetToolsHelpers.get_asset_tools()
mel = unreal.MaterialEditingLibrary
STEPS = [s.strip() for s in os.environ.get("WC_STEPS", "kit,her,mats,audio,tex,props,decals,extra,mega,variants,drawings").split(",")]


def log(msg):
    unreal.log_warning("WC_IMPORT: " + str(msg))


def import_files(files, dest, options=None):
    tasks = []
    for f in files:
        t = unreal.AssetImportTask()
        t.set_editor_property("filename", f)
        t.set_editor_property("destination_path", dest)
        t.set_editor_property("replace_existing", True)
        t.set_editor_property("automated", True)
        t.set_editor_property("save", True)
        if options is not None:
            t.set_editor_property("options", options)
        tasks.append(t)
    tools.import_asset_tasks(tasks)
    out = []
    for t in tasks:
        out += [str(p) for p in t.get_editor_property("imported_object_paths")]
    return out


def new_material(name, folder="Materials"):
    path = f"{G}/{folder}/{name}"
    if eal.does_asset_exist(path):
        eal.delete_asset(path)
    return tools.create_asset(name, f"{G}/{folder}", unreal.Material, unreal.MaterialFactoryNew())


def const3(m, rgb, x, y):
    e = mel.create_material_expression(m, unreal.MaterialExpressionConstant3Vector, x, y)
    e.set_editor_property("constant", unreal.LinearColor(rgb[0], rgb[1], rgb[2], 1))
    return e


def const1(m, v, x, y):
    e = mel.create_material_expression(m, unreal.MaterialExpressionConstant, x, y)
    e.set_editor_property("r", v)
    return e


def sparam(m, name, default, x, y):
    e = mel.create_material_expression(m, unreal.MaterialExpressionScalarParameter, x, y)
    e.set_editor_property("parameter_name", name)
    e.set_editor_property("default_value", default)
    return e


def vparam(m, name, default, x, y):
    e = mel.create_material_expression(m, unreal.MaterialExpressionVectorParameter, x, y)
    e.set_editor_property("parameter_name", name)
    e.set_editor_property("default_value", unreal.LinearColor(*default))
    return e


def tex_settings(path, srgb, normal=False):
    t = eal.load_asset(path)
    if not t:
        return None
    t.set_editor_property("srgb", srgb)
    if normal:
        t.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_NORMALMAP)
    elif not srgb:
        t.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_MASKS)
    eal.save_loaded_asset(t, False)
    return t


# ============================================================================ kit collision
def step_kit():
    ar = unreal.AssetRegistryHelpers.get_asset_registry()
    n = 0
    for a in ar.get_assets_by_path("/Game/HorrorHouseKit/Meshes", recursive=True):
        m = a.get_asset()
        if not isinstance(m, unreal.StaticMesh):
            continue
        bs = m.get_editor_property("body_setup")
        if bs and bs.get_editor_property("collision_trace_flag") != unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE:
            bs.set_editor_property("collision_trace_flag", unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
            eal.save_loaded_asset(m, False)
            n += 1
    log(f"kit: collision set on {n} meshes")


# ============================================================================ her
def fbx_task(path, dest, name, skeleton=None):
    t = unreal.AssetImportTask()
    t.set_editor_property("filename", path)
    t.set_editor_property("destination_path", dest)
    t.set_editor_property("destination_name", name)
    t.set_editor_property("replace_existing", True)
    t.set_editor_property("automated", True)
    t.set_editor_property("save", True)
    ui = unreal.FbxImportUI()
    ui.set_editor_property("automated_import_should_detect_type", False)
    if skeleton is None:
        ui.set_editor_property("import_mesh", True)
        ui.set_editor_property("import_as_skeletal", True)
        ui.set_editor_property("import_animations", False)
        ui.set_editor_property("import_materials", False)
        ui.set_editor_property("import_textures", False)
        ui.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_SKELETAL_MESH)
        sd = ui.get_editor_property("skeletal_mesh_import_data")
        sd.set_editor_property("normal_import_method", unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS)
        try:
            sd.set_editor_property("normal_generation_method", unreal.FBXNormalGenerationMethod.MIKK_T_SPACE)
        except Exception as exc:
            log(f"mikk: {exc}")
        sd.set_editor_property("import_morph_targets", True)
    else:
        ui.set_editor_property("import_mesh", False)
        ui.set_editor_property("import_animations", True)
        ui.set_editor_property("skeleton", skeleton)
        ui.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_ANIMATION)
        ad = ui.get_editor_property("anim_sequence_import_data")
        ad.set_editor_property("animation_length", unreal.FBXAnimationLengthImportType.FBXALIT_EXPORTED_TIME)
        ad.set_editor_property("import_bone_tracks", True)
    t.set_editor_property("options", ui)
    tools.import_asset_tasks([t])
    return [str(p) for p in t.get_editor_property("imported_object_paths")]


def usage(m, what):
    try:
        mel.set_material_usage(m, getattr(unreal.MaterialUsage, "MATUSAGE_" + what))
    except Exception as exc:
        log(f"usage {what}: {exc}")


def step_her_skin():
    # Both the full character import and material-only updates use the approved
    # maps. Keep the texture object paths stable for the mesh and corpse instance.
    folder = G + "/Her"
    maps = ("BaseColor", "Normal", "Roughness")
    # look_d = skin D, crusted scabs (Cheyenne's pick, 2026-11-19), baked by Scripts/her/her_tex.py over Codex's look C:
    # the portrait stays on the upper face.  Remove the look_d folder to go back to look C alone.
    look = "look_d" if all(os.path.isfile(f"{SRC}/Her/look_d/T_Her_{name}.png") for name in maps) else "look_c"
    paths = [f"{SRC}/Her/{look}/T_Her_{name}.png" for name in maps]
    for path in paths:
        if not os.path.isfile(path):
            raise FileNotFoundError(path)
    imported = import_files(paths, folder)
    textures = [tex_settings(f"{folder}/T_Her_{name}", name == "BaseColor", normal=name == "Normal") for name in maps]
    if len(imported) != len(maps) or not all(textures):
        raise RuntimeError(f"Edith C texture import incomplete: {imported}")
    for texture in textures:
        if texture.blueprint_get_size_x() != 4096 or texture.blueprint_get_size_y() != 4096:
            raise RuntimeError(f"Unexpected texture dimensions for {texture.get_name()}")
    log(f"Edith skin imported from {look}: {imported}")
    return textures


def step_her():
    d = SRC + "/Her/export"
    H = G + "/Her"
    info = json.load(open(d + "/her_info.json"))
    for nm in [f"A_Her_{c}" for c in info["clips"]] + ["SK_Her", "SK_Her_Skeleton", "SK_Her_PhysicsAsset"]:
        if eal.does_asset_exist(f"{H}/{nm}"):
            eal.delete_asset(f"{H}/{nm}")
    log("her mesh: " + str(fbx_task(d + "/SK_Her.fbx", H, "SK_Her")))
    sk = eal.load_asset(H + "/SK_Her")
    if not sk:
        raise RuntimeError("SK_Her did not import")
    skel = sk.skeleton
    for c in info["clips"]:
        p = fbx_task(f"{d}/A_Her_{c}.fbx", H, f"A_Her_{c}", skel)
        a = eal.load_asset(f"{H}/A_Her_{c}")
        log(f"her clip {c}: {p} -> {a.get_play_length() if a else 'FAILED'} s")
    # textures + material
    bc, nm, rg = step_her_skin()
    if eal.does_asset_exist(H + "/M_Her"):
        eal.delete_asset(H + "/M_Her")
    m = tools.create_asset("M_Her", H, unreal.Material, unreal.MaterialFactoryNew())
    m.set_editor_property("two_sided", True)
    usage(m, "SKELETAL_MESH")
    usage(m, "MORPH_TARGETS")
    tb = mel.create_material_expression(m, unreal.MaterialExpressionTextureSample, -700, -200)
    tb.set_editor_property("texture", bc)
    tint = vparam(m, "Tint", (0.21, 0.19, 0.17, 1), -700, -420)        # Cheyenne: "way darker"; was (0.50, 0.46, 0.41)
    mul = mel.create_material_expression(m, unreal.MaterialExpressionMultiply, -400, -260)
    mel.connect_material_expressions(tb, "RGB", mul, "A")
    mel.connect_material_expressions(tint, "", mul, "B")
    # filth: darker and browner from the knees down, as if she has been walking a wet cellar for months
    wp_ = mel.create_material_expression(m, unreal.MaterialExpressionWorldPosition, -1000, -700)
    op_ = mel.create_material_expression(m, unreal.MaterialExpressionObjectPositionWS, -1000, -600)
    dirt = _custom(m, "float h = saturate((WP.z - OP.z) / 135.0); float k = h * h * (3.0 - 2.0 * h); return lerp(float3(0.30, 0.24, 0.17), float3(1.0, 1.0, 1.0), k);",
                   ["WP", "OP"], unreal.CustomMaterialOutputType.CMOT_FLOAT3, -700, -650)
    mel.connect_material_expressions(wp_, "", dirt, "WP")
    mel.connect_material_expressions(op_, "", dirt, "OP")
    mul2 = mel.create_material_expression(m, unreal.MaterialExpressionMultiply, -200, -300)
    mel.connect_material_expressions(mul, "", mul2, "A")
    mel.connect_material_expressions(dirt, "", mul2, "B")
    mel.connect_material_property(mul2, "", unreal.MaterialProperty.MP_BASE_COLOR)
    tn = mel.create_material_expression(m, unreal.MaterialExpressionTextureSample, -700, 60)
    tn.set_editor_property("texture", nm)
    tn.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
    mel.connect_material_property(tn, "RGB", unreal.MaterialProperty.MP_NORMAL)
    tr = mel.create_material_expression(m, unreal.MaterialExpressionTextureSample, -700, 320)
    tr.set_editor_property("texture", rg)
    tr.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_MASKS)
    rs = sparam(m, "RoughScale", 0.9, -700, 560)
    rm = mel.create_material_expression(m, unreal.MaterialExpressionMultiply, -400, 380)
    mel.connect_material_expressions(tr, "G", rm, "A")
    mel.connect_material_expressions(rs, "", rm, "B")
    mel.connect_material_property(rm, "", unreal.MaterialProperty.MP_ROUGHNESS)
    sp = const1(m, 0.22, -400, 180)
    mel.connect_material_property(sp, "", unreal.MaterialProperty.MP_SPECULAR)
    mel.recompile_material(m)
    eal.save_loaded_asset(m, False)
    mats = sk.get_editor_property("materials")
    new = []
    for sm in mats:
        sm.set_editor_property("material_interface", m)
        new.append(sm)
    sk.set_editor_property("materials", new)
    eal.save_loaded_asset(sk, False)
    # reference pose, to check axes
    log("her bones: " + str(len(skel.get_reference_pose().get_bone_names()) if hasattr(skel, "get_reference_pose") else "?"))
    b = sk.get_bounds()
    log(f"her bounds origin {b.origin} extent {b.box_extent}")


# ============================================================================ utility materials
def flat_material(name, rgb, rough=0.8, emissive=0.0, unlit=False, two_sided=False):
    m = new_material(name)
    c = const3(m, rgb, -400, 0)
    if unlit:
        m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
        mel.connect_material_property(c, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    else:
        mel.connect_material_property(c, "", unreal.MaterialProperty.MP_BASE_COLOR)
        r = const1(m, rough, -400, 200)
        mel.connect_material_property(r, "", unreal.MaterialProperty.MP_ROUGHNESS)
        if emissive > 0:
            e = const3(m, [v * emissive for v in rgb], -400, 400)
            mel.connect_material_property(e, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    m.set_editor_property("two_sided", two_sided)
    usage(m, "INSTANCED_STATIC_MESHES")
    mel.recompile_material(m)
    eal.save_loaded_asset(m, False)
    return m


def smoke_material():
    """Black smoke: unlit, see-through at the edge of every blob, with noise drifting up through it and the whole shape swaying."""
    src = SRC + "/Textures/misc/T_SmokeNoise.png"
    if not os.path.exists(src):
        log("no smoke noise texture (run Scripts/art/gen_noise.py)")
        return None
    import_files([src], G + "/Materials")
    nt = eal.load_asset(G + "/Materials/T_SmokeNoise")
    try:
        nt.set_editor_property("srgb", False)
        nt.set_editor_property("compression_settings", unreal.TextureCompressionSettings.TC_GRAYSCALE)
        eal.save_loaded_asset(nt, False)
    except Exception as exc:
        log(f"smoke noise settings: {exc}")
    m = new_material("M_Smoke")
    m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
    m.set_editor_property("shading_model", unreal.MaterialShadingModel.MSM_UNLIT)
    m.set_editor_property("two_sided", False)
    usage(m, "INSTANCED_STATIC_MESHES")
    mel.connect_material_property(const3(m, (0.0, 0.0, 0.0), -300, -200), "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    wp = mel.create_material_expression(m, unreal.MaterialExpressionWorldPosition, -1300, 0)
    tm = mel.create_material_expression(m, unreal.MaterialExpressionTime, -1300, 200)
    uv1 = _custom(m, "return WP.yz * 0.0052 + WP.x * 0.0021 + float2(0.0, T * 0.09);", ["WP", "T"], unreal.CustomMaterialOutputType.CMOT_FLOAT2, -1000, 0)
    uv2 = _custom(m, "return WP.xz * 0.0125 + float2(T * 0.04, T * 0.21);", ["WP", "T"], unreal.CustomMaterialOutputType.CMOT_FLOAT2, -1000, 200)
    for u_ in (uv1, uv2):
        mel.connect_material_expressions(wp, "", u_, "WP")
        mel.connect_material_expressions(tm, "", u_, "T")
    n1 = mel.create_material_expression(m, unreal.MaterialExpressionTextureSample, -700, 0)
    n2 = mel.create_material_expression(m, unreal.MaterialExpressionTextureSample, -700, 200)
    for n_, u_ in ((n1, uv1), (n2, uv2)):
        n_.set_editor_property("texture", nt)
        n_.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_LINEAR_GRAYSCALE)
        mel.connect_material_expressions(u_, "", n_, "UVs")
    fr = mel.create_material_expression(m, unreal.MaterialExpressionFresnel, -700, 420)
    fr.set_editor_property("exponent", 1.0)
    fr.set_editor_property("base_reflect_fraction", 0.0)
    op = _custom(m, "float edge = saturate(1.0 - F); float n = saturate(N1 * 1.25 + N2 * 0.55 - 0.3); return saturate(edge * (0.95 + 0.6 * n) + n * 0.12) * 0.98;",
                 ["F", "N1", "N2"], unreal.CustomMaterialOutputType.CMOT_FLOAT1, -350, 200)
    mel.connect_material_expressions(fr, "", op, "F")
    mel.connect_material_expressions(n1, "R", op, "N1")
    mel.connect_material_expressions(n2, "R", op, "N2")
    mel.connect_material_property(op, "", unreal.MaterialProperty.MP_OPACITY)
    wo = _custom(m, "float a = T * 1.25 + WP.z * 0.021; return float3(sin(a) * 4.5 + sin(T * 0.7 + WP.z * 0.05) * 2.5, cos(a * 0.83) * 4.5, sin(T * 0.9 + WP.x * 0.03) * 2.0);",
                 ["WP", "T"], unreal.CustomMaterialOutputType.CMOT_FLOAT3, -350, 500)
    mel.connect_material_expressions(wp, "", wo, "WP")
    mel.connect_material_expressions(tm, "", wo, "T")
    mel.connect_material_property(wo, "", unreal.MaterialProperty.MP_WORLD_POSITION_OFFSET)
    mel.recompile_material(m)
    eal.save_loaded_asset(m, False)
    log("M_Smoke made")
    return m


def step_mats():
    eal.make_directory(G + "/Materials")
    flat_material("M_Dust", (0.9, 0.86, 0.78), 1.0)
    flat_material("M_Black", (0.005, 0.005, 0.005), 0.9)
    flat_material("M_Collision", (0.3, 0.3, 0.3), 0.9)
    flat_material("M_GlowRed", (1.0, 0.03, 0.02), 0.5, emissive=40.0)
    flat_material("M_GlowBlue", (0.03, 0.12, 1.0), 0.5, emissive=40.0)
    flat_material("M_GlowWarm", (1.0, 0.75, 0.45), 0.5, emissive=25.0)
    flat_material("M_Paper", (0.62, 0.58, 0.48), 0.9)
    flat_material("M_WindowWarm", (1.0, 0.6, 0.26), 0.6, emissive=float(os.environ.get("WC_WINDOW_GLOW", "2.6")))
    mv_ = flat_material("M_Void", (0.0, 0.0, 0.0), 1.0, unlit=True)
    usage(mv_, "SKELETAL_MESH")
    mel.recompile_material(mv_)
    eal.save_loaded_asset(mv_, False)
    flat_material("M_Hair", (0.36, 0.33, 0.27), 0.55)
    smoke_material()
    flat_material("M_EyeBlack", (0.002, 0.002, 0.002), 0.05)
    flat_material("M_EyeIris", (0.30, 0.36, 0.40), 0.3, emissive=0.06)
    # the same iris with its glow on a dial (the eye in the dark, S14)
    mg = new_material("M_EyeIrisGlow")
    cg = const3(mg, (0.30, 0.36, 0.40), -600, 0)
    mel.connect_material_property(cg, "", unreal.MaterialProperty.MP_BASE_COLOR)
    mel.connect_material_property(const1(mg, 0.3, -600, 200), "", unreal.MaterialProperty.MP_ROUGHNESS)
    gg = sparam(mg, "Glow", 0.06, -600, 400)
    mu = mel.create_material_expression(mg, unreal.MaterialExpressionMultiply, -300, 400)
    mel.connect_material_expressions(cg, "", mu, "A")
    mel.connect_material_expressions(gg, "", mu, "B")
    mel.connect_material_property(mu, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    mel.recompile_material(mg)
    eal.save_loaded_asset(mg, False)
    flat_material("M_GlowBulb", (1.0, 0.62, 0.22), 0.5, emissive=14.0)
    flat_material("M_BulbOff", (0.09, 0.08, 0.06), 0.3)
    flat_material("M_Dash", (0.012, 0.012, 0.013), 0.55)
    flat_material("M_DashGlow", (0.25, 0.85, 0.55), 0.5, emissive=0.9)
    log("mats done")


# ============================================================================ audio
def step_audio():
    base = SRC + "/Audio"
    if not os.path.isdir(base):
        log("no audio folder yet")
        return
    for sub, dest in (("", G + "/Audio"), ("VO", G + "/Audio/VO")):
        d = base + ("/" + sub if sub else "")
        if not os.path.isdir(d):
            continue
        files = [d + "/" + f for f in sorted(os.listdir(d)) if f.lower().endswith(".wav")]
        if not files:
            continue
        paths = import_files(files, dest)
        n = 0
        for p in paths:
            w = eal.load_asset(p.split(".")[0])
            if not isinstance(w, unreal.SoundWave):
                continue
            nm = w.get_name()
            loop = nm.startswith(("amb_", "music_")) or nm in ("phone_ring", "musicbox", "radio_static_loop", "her_breath_loop", "flies_buzz")      # (the flies were silent after six seconds: their buzz did not loop)
            w.set_editor_property("looping", loop)
            eal.save_loaded_asset(w, False)
            n += 1
        log(f"audio: {n} waves -> {dest}")


# ============================================================================ textured surfaces (world-aligned, so any box or kit piece takes them)
def build_surface_master():
    m = new_material("M_Surface")
    wp = mel.create_material_expression(m, unreal.MaterialExpressionWorldPosition, -1700, -100)
    tile = sparam(m, "Tile", 200.0, -1700, 60)
    div = mel.create_material_expression(m, unreal.MaterialExpressionDivide, -1500, -60)
    mel.connect_material_expressions(wp, "", div, "A")
    mel.connect_material_expressions(tile, "", div, "B")
    vn = mel.create_material_expression(m, unreal.MaterialExpressionVertexNormalWS, -1700, 220)
    code_w = "float3 w = pow(abs(N), 6.0); return w / (w.x + w.y + w.z);"

    def custom(code, inputs, out, x, y):
        c = mel.create_material_expression(m, unreal.MaterialExpressionCustom, x, y)
        c.set_editor_property("code", code)
        c.set_editor_property("output_type", out)
        ins = []
        for name in inputs:
            ci = unreal.CustomInput()
            ci.set_editor_property("input_name", name)
            ins.append(ci)
        c.set_editor_property("inputs", ins)
        return c
    wts = custom(code_w, ["N"], unreal.CustomMaterialOutputType.CMOT_FLOAT3, -1450, 220)
    mel.connect_material_expressions(vn, "", wts, "N")

    def tri(param, default_tex, sampler, x, y, normal=False):
        tp = mel.create_material_expression(m, unreal.MaterialExpressionTextureObjectParameter, x - 300, y)
        tp.set_editor_property("parameter_name", param)
        tp.set_editor_property("sampler_type", sampler)
        if default_tex:
            tp.set_editor_property("texture", default_tex)
        if normal:
            code = ("float3 tx = UnpackNormalMap(Texture2DSample(T, TSampler, P.yz)).xyz;"
                    "float3 ty = UnpackNormalMap(Texture2DSample(T, TSampler, P.xz)).xyz;"
                    "float3 tz = UnpackNormalMap(Texture2DSample(T, TSampler, P.xy)).xyz;"
                    "float3 s = sign(N);"
                    "float3 nx = float3(tx.z * s.x, tx.x, tx.y);"
                    "float3 ny = float3(ty.x, ty.z * s.y, ty.y);"
                    "float3 nz = float3(tz.x, tz.y, tz.z * s.z);"
                    "return normalize(nx * W.x + ny * W.y + nz * W.z);")
            c = custom(code, ["T", "P", "W", "N"], unreal.CustomMaterialOutputType.CMOT_FLOAT3, x, y)
            mel.connect_material_expressions(vn, "", c, "N")
        else:
            code = ("return Texture2DSample(T, TSampler, P.yz) * W.x + Texture2DSample(T, TSampler, P.xz) * W.y + Texture2DSample(T, TSampler, P.xy) * W.z;")
            c = custom(code, ["T", "P", "W"], unreal.CustomMaterialOutputType.CMOT_FLOAT4, x, y)
        mel.connect_material_expressions(tp, "", c, "T")
        mel.connect_material_expressions(div, "", c, "P")
        mel.connect_material_expressions(wts, "", c, "W")
        return c
    white = unreal.load_object(None, "/Engine/EngineResources/WhiteSquareTexture.WhiteSquareTexture")
    flatn = unreal.load_object(None, "/Engine/EngineMaterials/DefaultNormal.DefaultNormal")
    bc = tri("BaseColor", white, unreal.MaterialSamplerType.SAMPLERTYPE_COLOR, -1000, -300)
    orm = tri("ORM", white, unreal.MaterialSamplerType.SAMPLERTYPE_MASKS, -1000, 0)
    nrm = tri("Normal", flatn, unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL, -1000, 300, normal=True)
    tint = vparam(m, "Tint", (1, 1, 1, 1), -1000, -520)
    bcm = mel.create_material_expression(m, unreal.MaterialExpressionComponentMask, -750, -300)
    for ch, v in (("r", True), ("g", True), ("b", True), ("a", False)):
        bcm.set_editor_property(ch, v)
    mel.connect_material_expressions(bc, "", bcm, "")
    mul = mel.create_material_expression(m, unreal.MaterialExpressionMultiply, -520, -360)
    mel.connect_material_expressions(bcm, "", mul, "A")
    mel.connect_material_expressions(tint, "", mul, "B")
    # large-scale grime so tiling never reads as tiling
    grime = custom("float n = sin(P.x * 0.011 + sin(P.y * 0.007) * 2.1) * sin(P.y * 0.013 + sin(P.z * 0.009) * 1.7) * sin(P.z * 0.008 + 1.3);"
                   "return lerp(1.0 - A, 1.0, saturate(0.55 + 0.45 * n));", ["P", "A"], unreal.CustomMaterialOutputType.CMOT_FLOAT1, -750, -560)
    ga = sparam(m, "Grime", 0.35, -1000, -640)
    mel.connect_material_expressions(wp, "", grime, "P")
    mel.connect_material_expressions(ga, "", grime, "A")
    mul2 = mel.create_material_expression(m, unreal.MaterialExpressionMultiply, -300, -420)
    mel.connect_material_expressions(mul, "", mul2, "A")
    mel.connect_material_expressions(grime, "", mul2, "B")
    mel.connect_material_property(mul2, "", unreal.MaterialProperty.MP_BASE_COLOR)

    def chan(src, ch, x, y):
        k = mel.create_material_expression(m, unreal.MaterialExpressionComponentMask, x, y)
        for c2 in "rgba":
            k.set_editor_property(c2, c2 == ch)
        mel.connect_material_expressions(src, "", k, "")
        return k
    ao = chan(orm, "r", -750, -60)
    ro = chan(orm, "g", -750, 40)
    me = chan(orm, "b", -750, 140)
    rsc = sparam(m, "RoughScale", 1.0, -750, 240)
    rmul = mel.create_material_expression(m, unreal.MaterialExpressionMultiply, -520, 60)
    mel.connect_material_expressions(ro, "", rmul, "A")
    mel.connect_material_expressions(rsc, "", rmul, "B")
    mel.connect_material_property(rmul, "", unreal.MaterialProperty.MP_ROUGHNESS)
    mel.connect_material_property(ao, "", unreal.MaterialProperty.MP_AMBIENT_OCCLUSION)
    msc = sparam(m, "Metal", 0.0, -750, 340)
    mmul = mel.create_material_expression(m, unreal.MaterialExpressionMultiply, -520, 180)
    mel.connect_material_expressions(me, "", mmul, "A")
    mel.connect_material_expressions(msc, "", mmul, "B")
    mel.connect_material_property(mmul, "", unreal.MaterialProperty.MP_METALLIC)
    mel.connect_material_property(nrm, "", unreal.MaterialProperty.MP_NORMAL)
    m.set_editor_property("tangent_space_normal", False)
    mel.recompile_material(m)
    eal.save_loaded_asset(m, False)
    return m


def step_tex():
    base = SRC + "/Textures"
    if not os.path.isdir(base):
        log("no textures folder yet")
        return
    master = build_surface_master()
    spec = json.load(open(base + "/surfaces.json")) if os.path.exists(base + "/surfaces.json") else {}
    eal.make_directory(G + "/Textures")
    for name in sorted(os.listdir(base)):
        d = base + "/" + name
        if not os.path.isdir(d):
            continue
        files = {k: f"{d}/{k}.png" for k in ("BaseColor", "ORM", "Normal") if os.path.exists(f"{d}/{k}.png")}
        if "BaseColor" not in files:
            continue
        dest = f"{G}/Textures/{name}"
        import_files(list(files.values()), dest)
        mi_path = f"{G}/Materials/MI_{name}"
        if eal.does_asset_exist(mi_path):
            eal.delete_asset(mi_path)
        mi = tools.create_asset("MI_" + name, G + "/Materials", unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
        mel.set_material_instance_parent(mi, master)
        t = tex_settings(dest + "/BaseColor", True)
        mel.set_material_instance_texture_parameter_value(mi, "BaseColor", t)
        if "ORM" in files:
            mel.set_material_instance_texture_parameter_value(mi, "ORM", tex_settings(dest + "/ORM", False))
        if "Normal" in files:
            mel.set_material_instance_texture_parameter_value(mi, "Normal", tex_settings(dest + "/Normal", False, normal=True))
        s = spec.get(name, {})
        mel.set_material_instance_scalar_parameter_value(mi, "Tile", float(s.get("tile", 200.0)))
        mel.set_material_instance_scalar_parameter_value(mi, "Grime", float(s.get("grime", 0.35)))
        mel.set_material_instance_scalar_parameter_value(mi, "RoughScale", float(s.get("rough", 1.0)))
        mel.set_material_instance_scalar_parameter_value(mi, "Metal", float(s.get("metal", 0.0)))
        tint = s.get("tint", [1, 1, 1])
        mel.set_material_instance_vector_parameter_value(mi, "Tint", unreal.LinearColor(tint[0], tint[1], tint[2], 1))
        eal.save_loaded_asset(mi, False)
        log(f"surface MI_{name}")


exec(open(ROOT + "/Scripts/level/import_more.py", encoding="utf-8").read())
exec(open(ROOT + "/Scripts/level/import_surfaces.py", encoding="utf-8").read())
exec(open(ROOT + "/Scripts/level/import_variants.py", encoding="utf-8").read())
exec(open(ROOT + "/Scripts/level/import_items.py", encoding="utf-8").read())

for name, fn in (("kit", step_kit), ("her", step_her), ("her_skin", step_her_skin), ("mats", step_mats), ("audio", step_audio), ("tex", step_tex), ("props", step_props), ("decals", step_decals), ("extra", step_extra_mats), ("mega", step_mega), ("variants", step_variants), ("drawings", step_drawings), ("items", step_items)):
    if name in STEPS:
        try:
            fn()
        except Exception as exc:
            import traceback
            log(f"STEP {name} FAILED: {exc}\n{traceback.format_exc()}")
log("DONE " + ",".join(STEPS))
