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


def step_items():
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
    }
    # the television's own cabinet: dark old wood and black fittings (plain item colours go cream under the flashlight)
    tvm = dict(mats)
    wood = G + "/Materials/MI_WoodDark"
    tvm["Wood"] = eal.load_asset(wood) if eal.does_asset_exist(wood) else item_material("M_TVWood", (0.02, 0.011, 0.006), 0.5, 0.0)
    tvm["Polymer"] = item_material("M_TVBezel", (0.004, 0.004, 0.0045), 0.35, 0.0)
    tvm["Gunmetal"] = item_material("M_TVPanel", (0.007, 0.0065, 0.006), 0.5, 0.0)
    tvm["Brass"] = item_material("M_TVKnob", (0.16, 0.11, 0.04), 0.4, 1.0)
    for f in sorted(os.listdir(d)):
        if not f.lower().endswith(".fbx"):
            continue
        name = f[:-4]
        t = unreal.AssetImportTask()
        t.set_editor_property("filename", f"{d}/{f}")
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
        for i, sm_mat in enumerate(sm.static_materials):
            slot = str(sm_mat.material_slot_name)
            key = next((k for k in mats if slot.lower().startswith(k.lower())), None)
            if key:
                sm.set_material(i, (tvm if name == "SM_Item_TV" else mats)[key])
            slots.append(f"{slot}->{key}")
        eal.save_loaded_asset(sm, False)
        b = sm.get_bounds().box_extent
        log(f"item {name}: {', '.join(slots)}; half size {b.x:.1f} x {b.y:.1f} x {b.z:.1f} cm")
