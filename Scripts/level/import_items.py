# The small carried things (Scripts/art/build_items.py): static meshes + plain metal / glass materials.
# exec'd by import_assets.py; step name "items".
def item_material(name, rgb, rough, metallic):
    m = new_material(name)
    mel.connect_material_property(const3(m, rgb, -400, 0), "", unreal.MaterialProperty.MP_BASE_COLOR)
    mel.connect_material_property(const1(m, rough, -400, 200), "", unreal.MaterialProperty.MP_ROUGHNESS)
    mel.connect_material_property(const1(m, metallic, -400, 320), "", unreal.MaterialProperty.MP_METALLIC)
    mel.recompile_material(m)
    eal.save_loaded_asset(m, False)
    return m


def tv_material():
    """The television picture: one frame out of a sheet of 240, or the dead glass showing a mirror of the room."""
    D = G + "/TV"
    eal.make_directory(D)
    tdir = SRC + "/TV"
    files = [f"{tdir}/{f}" for f in sorted(os.listdir(tdir))] if os.path.isdir(tdir) else []
    files = [f for f in files if os.path.basename(f).startswith("T_Tape_") and f.endswith(".png")]
    if files:
        import_files(files, D)
    first = None
    for f in files:
        t = eal.load_asset(f"{D}/{os.path.basename(f)[:-4]}")
        if not t:
            continue
        first = first or t
        for prop, val in (("mip_gen_settings", unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS), ("never_stream", True), ("srgb", True),
                          ("filter", unreal.TextureFilter.TF_BILINEAR)):
            try:
                t.set_editor_property(prop, val)
            except Exception as exc:
                log(f"tape texture {prop}: {exc}")
        eal.save_loaded_asset(t, False)
    for n in range(len(files) + 1, 9):                    # tapes that were retired must not stay playable
        for stale in (f"{D}/T_Tape_{n}", f"{G}/Audio/tv_tape_{n}"):
            if eal.does_asset_exist(stale):
                eal.delete_asset(stale)
                log(f"retired {stale}")
    first = first or eal.load_asset(G + "/Drawings/draw_1")
    F1, F2, F3 = unreal.CustomMaterialOutputType.CMOT_FLOAT1, unreal.CustomMaterialOutputType.CMOT_FLOAT2, unreal.CustomMaterialOutputType.CMOT_FLOAT3
    m = new_material("M_TV")
    tc = mel.create_material_expression(m, unreal.MaterialExpressionTextureCoordinate, -1700, 0)
    prm = {n: sparam(m, n, d, -1700, 160 + 110 * i) for i, (n, d) in enumerate((("Frame", 0.0), ("Cols", 16.0), ("Rows", 15.0), ("Flip", 0.0), ("Mode", 0.0), ("Gain", 420.0), ("RGain", 30.0)))}
    uv = _custom(m, "float2 uv = UV; uv.x = lerp(uv.x, 1.0 - uv.x, Flip); float f = floor(Frame + 0.5); float c = fmod(f, Cols); float r = floor(f / Cols); "
                    "return (float2(c, r) + clamp(uv, 0.004, 0.996)) / float2(Cols, Rows);", ["UV", "Frame", "Cols", "Rows", "Flip"], F2, -1300, 0)
    mel.connect_material_expressions(tc, "", uv, "UV")
    for n in ("Frame", "Cols", "Rows", "Flip"):
        mel.connect_material_expressions(prm[n], "", uv, n)
    ruv = _custom(m, "float2 uv = UV; uv.x = lerp(1.0 - uv.x, uv.x, Flip); return uv;", ["UV", "Flip"], F2, -1300, 320)
    mel.connect_material_expressions(tc, "", ruv, "UV")
    mel.connect_material_expressions(prm["Flip"], "", ruv, "Flip")
    atlas = mel.create_material_expression(m, unreal.MaterialExpressionTextureSampleParameter2D, -1000, 0)
    atlas.set_editor_property("parameter_name", "Atlas")
    atlas.set_editor_property("texture", first)
    mel.connect_material_expressions(uv, "", atlas, "UVs")
    refl = mel.create_material_expression(m, unreal.MaterialExpressionTextureSampleParameter2D, -1000, 320)
    refl.set_editor_property("parameter_name", "Reflect")
    refl.set_editor_property("texture", first)
    mel.connect_material_expressions(ruv, "", refl, "UVs")
    out = _custom(m, "float w1 = saturate(1.0 - abs(Mode - 1.0)); float w2 = saturate(Mode - 1.0); float sl = 0.84 + 0.16 * sin(UV.y * 1500.0); "
                     "float3 c = V * Gain * w1 * sl + Rf * RGain * w2; float2 d = UV - 0.5; return c * saturate(1.12 - dot(d, d) * 1.5);",
                  ["V", "Rf", "UV", "Mode", "Gain", "RGain"], F3, -600, 100)
    mel.connect_material_expressions(atlas, "RGB", out, "V")
    mel.connect_material_expressions(refl, "RGB", out, "Rf")
    mel.connect_material_expressions(tc, "", out, "UV")
    for n in ("Mode", "Gain", "RGain"):
        mel.connect_material_expressions(prm[n], "", out, n)
    mel.connect_material_property(out, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    mel.connect_material_property(const3(m, (0.002, 0.0025, 0.0025), -600, -200), "", unreal.MaterialProperty.MP_BASE_COLOR)
    mel.connect_material_property(const1(m, 0.07, -600, -80), "", unreal.MaterialProperty.MP_ROUGHNESS)
    mel.connect_material_property(const1(m, 0.35, -600, -140), "", unreal.MaterialProperty.MP_SPECULAR)
    mel.recompile_material(m)
    eal.save_loaded_asset(m, False)
    log(f"M_TV made, {len(files)} tapes")
    return m



FILTER_CODE = """
#define WCH(p) frac(sin(dot((p), float2(12.9898, 78.233))) * 43758.5453)
#define WCS(u) SceneTextureLookup(ViewportUVToSceneTextureUV(saturate(u), 14), 14, false).rgb
float2 uv = GetViewportUV(Parameters);
float2 vs = View.ViewSizeAndInvSize.xy;
float aspect = vs.x / max(vs.y, 1.0);
const float3 lum = float3(0.30, 0.59, 0.11);
int look = (int)(Look + 0.5);
float t = T;
float3 c = WCS(uv) + Dummy.rgb * 0.0;
if (look == 1)
{
    // VHS camcorder: lines that jitter, colours that slip sideways, a tracking band crawling up, snow, washed blacks
    float ln = floor(uv.y * 240.0);
    float jit = (WCH(float2(ln, floor(t * 30.0))) - 0.5) * 0.0016;
    float bar = frac(uv.y + t * 0.11);
    float band = smoothstep(0.0, 0.015, bar) * (1.0 - smoothstep(0.02, 0.07, bar));
    float2 u = uv + float2(jit + band * 0.010 * (WCH(float2(ln, floor(t * 24.0))) - 0.3), 0.0);
    u.x += step(0.972, uv.y) * (WCH(float2(ln, floor(t * 60.0))) - 0.5) * 0.06;
    float3 a = WCS(u + float2(0.0035, 0.0));
    float3 b = WCS(u);
    float3 d = WCS(u - float2(0.0035, 0.0));
    c = float3(a.r, (b.g * 2.0 + a.g + d.g) * 0.25, d.b);
    c = lerp(c, (a + b + d) / 3.0, 0.35);
    c = lerp(dot(c, lum), c, 0.72);
    c = c * 0.92 + 0.030;
    c *= 0.93 + 0.07 * sin(uv.y * 480.0 * 3.14159);
    c += (WCH(uv * vs * 0.5 + frac(t) * 91.7) - 0.5) * 0.10;
    c += band * 0.05;
    float2 dv = uv - 0.5;
    c *= saturate(1.10 - dot(dv, dv) * 0.9);
}
else if (look == 2)
{
    // old film: weave in the gate, flicker, sepia, scratches, dust, heavy grain, dark corners
    float fr = floor(t * 18.0);
    float2 u = uv + (float2(WCH(float2(fr, 1.3)), WCH(float2(fr, 7.1))) - 0.5) * 0.004;
    c = WCS(u);
    float l = pow(saturate(dot(c, lum) * 1.25), 0.9);
    c = l * float3(1.05, 0.93, 0.74);
    c *= 0.84 + 0.16 * WCH(float2(fr, 3.7));
    for (int k = 0; k < 3; ++k)
    {
        float sx = WCH(float2(floor(t * 2.0) + k * 3.1, k * 17.3));
        float on = step(0.45, WCH(float2(floor(t * 3.0) + k, 5.5)));
        c += on * (1.0 - smoothstep(0.0, 0.0011, abs(uv.x - sx - 0.002 * sin(uv.y * 9.0 + fr)))) * 0.30 * (0.4 + 0.6 * WCH(float2(floor(uv.y * 30.0), fr)));
    }
    float2 g = floor(uv * float2(70.0, 40.0));
    c *= 1.0 - step(0.9988, WCH(g + fr * 0.37)) * 0.85;
    c += (WCH(uv * vs * 0.6 + fr * 13.1) - 0.5) * 0.15;
    float2 dv = uv - 0.5;
    c *= saturate(1.16 - dot(dv, dv) * 2.0);
}
else if (look == 3)
{
    // cold and drained: most of the colour gone, blue in the shadows, harder contrast, a little grain
    float l = dot(c, lum);
    c = lerp(l, c, 0.30);
    c = pow(saturate(c), 1.14) * 1.10;
    c *= lerp(float3(0.74, 0.94, 1.22), float3(1.0, 1.0, 1.0), smoothstep(0.0, 0.55, l));
    c += (WCH(uv * vs * 0.5 + frac(t) * 37.0) - 0.5) * 0.035;
}
else if (look == 4)
{
    // bodycam: a fisheye lens with black corners, colour fringes toward the edge, a hard digital look
    float2 d = uv - 0.5;
    d.x *= aspect;
    float r2 = dot(d, d);
    float2 w = d * (1.0 + 0.62 * r2 + 0.50 * r2 * r2) * 0.74;
    w.x /= aspect;
    float2 u = w + 0.5;
    float ca = 0.012 * r2;
    c = float3(WCS(u + (u - 0.5) * ca).r, WCS(u).g, WCS(u - (u - 0.5) * ca).b);
    float inside = smoothstep(0.0, 0.012, min(min(u.x, 1.0 - u.x), min(u.y, 1.0 - u.y)));
    c *= inside;
    c *= saturate(1.30 - r2 * 2.3);
    c = lerp(dot(c, lum), c, 0.78) * float3(0.96, 1.0, 0.97);
    c = pow(saturate(c), 0.94);
    c += (WCH(floor(uv * vs * 0.5) + floor(t * 30.0) * 7.3) - 0.5) * 0.045;
}
else if (look == 5)
{
    // night vision in black and white: the dark lifted a long way, snow, lines, a round falloff like a scope
    float l = dot(c, lum);
    l = pow(saturate(l * 3.4), 0.60);
    l += (WCH(uv * vs * 0.5 + frac(t) * 53.0) - 0.5) * 0.20;
    l *= 0.90 + 0.10 * sin(uv.y * vs.y * 1.5708);
    float2 d = uv - 0.5;
    d.x *= aspect;
    l *= saturate(1.40 - dot(d, d) * 3.1);
    c = saturate(l) * float3(0.86, 0.95, 1.0);
}
return c;
"""


def filter_material():
    """The whole-game picture filter (see FILTER_CODE): a post-process material applied after tone mapping."""
    m = new_material("M_Filter")
    m.set_editor_property("material_domain", unreal.MaterialDomain.MD_POST_PROCESS)
    for nm in ("BL_SCENE_COLOR_AFTER_TONEMAPPING", "BL_AFTER_TONEMAPPING"):
        loc = getattr(unreal.BlendableLocation, nm, None)
        if loc is not None:
            m.set_editor_property("blendable_location", loc)
            log("filter blend location " + nm)
            break
    st = mel.create_material_expression(m, unreal.MaterialExpressionSceneTexture, -900, 0)
    for nm in ("PPI_POST_PROCESS_INPUT0", "PPI_POSTPROCESS_INPUT0"):
        sid = getattr(unreal.SceneTextureId, nm, None)
        if sid is not None:
            st.set_editor_property("scene_texture_id", sid)
            break
    look = sparam(m, "Look", 0.0, -900, 260)
    tm = mel.create_material_expression(m, unreal.MaterialExpressionTime, -900, 380)
    out = _custom(m, FILTER_CODE, ["Dummy", "Look", "T"], unreal.CustomMaterialOutputType.CMOT_FLOAT3, -500, 100)
    mel.connect_material_expressions(st, "Color", out, "Dummy")
    mel.connect_material_expressions(look, "", out, "Look")
    mel.connect_material_expressions(tm, "", out, "T")
    mel.connect_material_property(out, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    mel.recompile_material(m)
    eal.save_loaded_asset(m, False)
    log("M_Filter made")


def fine_material(name, tdir):
    """One baked item (build_items_fine.py): base colour, normal, and occlusion / roughness / metal in one map."""
    files = [f"{tdir}/T_Item_{name}_{k}.png" for k in ("C", "N", "ORM")]
    if not all(os.path.isfile(f) for f in files):
        return None
    D = G + "/Props/Tex"
    eal.make_directory(D)
    import_files(files, D)
    c = tex_settings(f"{D}/T_Item_{name}_C", True)
    n = tex_settings(f"{D}/T_Item_{name}_N", False, normal=True)
    o = tex_settings(f"{D}/T_Item_{name}_ORM", False)
    if not (c and n and o):
        return None
    n.set_editor_property("flip_green_channel", True)            # Blender bakes +Y normals
    eal.save_loaded_asset(n, False)
    m = new_material("M_Item_" + name)
    tb = mel.create_material_expression(m, unreal.MaterialExpressionTextureSample, -700, -200)
    tb.set_editor_property("texture", c)
    mel.connect_material_property(tb, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
    tn = mel.create_material_expression(m, unreal.MaterialExpressionTextureSample, -700, 60)
    tn.set_editor_property("texture", n)
    tn.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
    mel.connect_material_property(tn, "RGB", unreal.MaterialProperty.MP_NORMAL)
    to = mel.create_material_expression(m, unreal.MaterialExpressionTextureSample, -700, 320)
    to.set_editor_property("texture", o)
    to.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_MASKS)
    mel.connect_material_property(to, "G", unreal.MaterialProperty.MP_ROUGHNESS)
    mel.connect_material_property(to, "B", unreal.MaterialProperty.MP_METALLIC)
    mel.recompile_material(m)
    eal.save_loaded_asset(m, False)
    return m


def step_items():
    filter_material()
    d = SRC + "/Props/items"
    if not os.path.isdir(d):
        log("no item models yet (run Scripts/art/build_items.py)")
        return
    P = G + "/Props"
    mats = {
        "Brass": item_material("M_ItemBrass", (0.50, 0.34, 0.11), 0.42, 1.0),
        "Iron": item_material("M_ItemIron", (0.10, 0.09, 0.085), 0.55, 1.0),
        "Gold": item_material("M_ItemGold", (0.86, 0.62, 0.22), 0.28, 1.0),
        "Steel": item_material("M_ItemSteel", (0.48, 0.48, 0.47), 0.38, 1.0),
        "Glass": item_material("M_ItemGlass", (0.50, 0.62, 0.60), 0.08, 0.0),
        "Ceramic": item_material("M_ItemCeramic", (0.74, 0.70, 0.62), 0.5, 0.0),
        "Ribbon": item_material("M_ItemRibbon", (0.26, 0.03, 0.04), 0.9, 0.0),
        "Polymer": item_material("M_ItemPolymer", (0.025, 0.025, 0.028), 0.55, 0.0),
        "Gunmetal": item_material("M_ItemGunmetal", (0.075, 0.075, 0.08), 0.36, 1.0),
        "Wood": item_material("M_ItemWood", (0.13, 0.07, 0.04), 0.55, 0.0),
        "Screen": tv_material(),
        "Card": item_material("M_ItemCard", (0.085, 0.062, 0.036), 0.9, 0.0),
        "Label": item_material("M_ItemLabel", (0.070, 0.012, 0.010), 0.75, 0.0),
    }
    # the television's own cabinet: dark old wood and black fittings (plain item colours go cream under the flashlight)
    tvm = dict(mats)
    wood = G + "/Materials/MI_WoodDark"
    tvm["Wood"] = eal.load_asset(wood) if eal.does_asset_exist(wood) else item_material("M_TVWood", (0.02, 0.011, 0.006), 0.5, 0.0)
    tvm["Polymer"] = item_material("M_TVBezel", (0.004, 0.004, 0.0045), 0.35, 0.0)
    tvm["Gunmetal"] = item_material("M_TVPanel", (0.007, 0.0065, 0.006), 0.5, 0.0)
    tvm["Brass"] = item_material("M_TVKnob", (0.16, 0.11, 0.04), 0.4, 1.0)
    # the fine versions (real detail, baked wear) replace the plain ones of the same name
    fbx = {}
    for dd in (d, SRC + "/Props/items_fine"):
        if os.path.isdir(dd):
            for f in sorted(os.listdir(dd)):
                if f.lower().endswith(".fbx"):
                    fbx[f[:-4]] = dd
    for name, dd in sorted(fbx.items()):
        fine = dd.endswith("items_fine")
        t = unreal.AssetImportTask()
        t.set_editor_property("filename", f"{dd}/{name}.fbx")
        t.set_editor_property("destination_path", P)
        t.set_editor_property("destination_name", name)
        t.set_editor_property("replace_existing", True)
        t.set_editor_property("automated", True)
        t.set_editor_property("save", True)
        ui = unreal.FbxImportUI()
        ui.set_editor_property("automated_import_should_detect_type", False)
        ui.set_editor_property("import_mesh", True)
        ui.set_editor_property("import_as_skeletal", False)
        ui.set_editor_property("import_animations", False)
        ui.set_editor_property("import_materials", False)
        ui.set_editor_property("import_textures", False)
        ui.set_editor_property("mesh_type_to_import", unreal.FBXImportType.FBXIT_STATIC_MESH)
        sd = ui.get_editor_property("static_mesh_import_data")
        sd.set_editor_property("combine_meshes", True)
        sd.set_editor_property("auto_generate_collision", True)
        sd.set_editor_property("normal_import_method", unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS)
        t.set_editor_property("options", ui)
        tools.import_asset_tasks([t])
        sm = eal.load_asset(f"{P}/{name}")
        if not sm:
            log(f"item {name}: FAILED to import")
            continue
        slots = []
        fm = fine_material(name[len("SM_Item_"):], dd + "/tex") if fine else None
        if fm:
            for i in range(len(sm.static_materials)):
                sm.set_material(i, fm)
            slots.append("fine, textured")
        for i, sm_mat in enumerate([] if fm else sm.static_materials):
            slot = str(sm_mat.material_slot_name)
            key = next((k for k in mats if slot.lower().startswith(k.lower())), None)
            if key:
                sm.set_material(i, (tvm if name == "SM_Item_TV" else mats)[key])
            slots.append(f"{slot}->{key}")
        eal.save_loaded_asset(sm, False)
        b = sm.get_bounds().box_extent
        log(f"item {name}: {', '.join(slots)}; half size {b.x:.1f} x {b.y:.1f} x {b.z:.1f} cm")
