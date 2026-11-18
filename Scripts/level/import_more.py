# Extra import steps, exec'd by import_assets.py (shares its helpers): generated props, grime decals, dead-body material.


# ============================================================================ generated props (cruiser, hands)
def build_prop_master():
    m = new_material("M_Prop")
    tb = mel.create_material_expression(m, unreal.MaterialExpressionTextureSampleParameter2D, -700, -200)
    tb.set_editor_property("parameter_name", "BaseColor")
    tb.set_editor_property("texture", eal.load_asset(G + "/Props/T_Cruiser_BaseColor"))
    tint = vparam(m, "Tint", (1, 1, 1, 1), -700, -420)
    mul = mel.create_material_expression(m, unreal.MaterialExpressionMultiply, -400, -260)
    mel.connect_material_expressions(tb, "RGB", mul, "A")
    mel.connect_material_expressions(tint, "", mul, "B")
    mel.connect_material_property(mul, "", unreal.MaterialProperty.MP_BASE_COLOR)
    tn = mel.create_material_expression(m, unreal.MaterialExpressionTextureSampleParameter2D, -700, 60)
    tn.set_editor_property("parameter_name", "Normal")
    tn.set_editor_property("texture", eal.load_asset(G + "/Props/T_Cruiser_Normal"))
    tn.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
    mel.connect_material_property(tn, "RGB", unreal.MaterialProperty.MP_NORMAL)
    tr = mel.create_material_expression(m, unreal.MaterialExpressionTextureSampleParameter2D, -700, 320)
    tr.set_editor_property("parameter_name", "MR")
    tr.set_editor_property("texture", eal.load_asset(G + "/Props/T_Cruiser_MR"))
    tr.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_MASKS)
    rs = sparam(m, "RoughScale", 1.0, -700, 560)
    rm = mel.create_material_expression(m, unreal.MaterialExpressionMultiply, -400, 380)
    mel.connect_material_expressions(tr, "G", rm, "A")
    mel.connect_material_expressions(rs, "", rm, "B")
    mel.connect_material_property(rm, "", unreal.MaterialProperty.MP_ROUGHNESS)
    ms = sparam(m, "MetalScale", 1.0, -700, 660)
    mm = mel.create_material_expression(m, unreal.MaterialExpressionMultiply, -400, 520)
    mel.connect_material_expressions(tr, "B", mm, "A")
    mel.connect_material_expressions(ms, "", mm, "B")
    mel.connect_material_property(mm, "", unreal.MaterialProperty.MP_METALLIC)
    mel.recompile_material(m)
    eal.save_loaded_asset(m, False)
    return m


def step_props():
    d = SRC + "/Props/export"
    P = G + "/Props"
    if not os.path.isdir(d):
        log("no props export yet")
        return
    # textures first (the master material takes its defaults from the cruiser's)
    alltex = [f"{d}/{f}" for f in sorted(os.listdir(d)) if f.lower().endswith(".png")]
    import_files(alltex, P)
    for f in alltex:
        nm_ = os.path.basename(f)[:-4]
        tex_settings(f"{P}/{nm_}", nm_.endswith("_BaseColor"), normal=nm_.endswith("_Normal"))
    master = build_prop_master()
    for f in sorted(os.listdir(d)):
        if not f.lower().endswith(".fbx"):
            continue
        name = f[:-4]                       # SM_Cruiser
        short = name[3:]
        if eal.does_asset_exist(f"{P}/{name}"):
            eal.delete_asset(f"{P}/{name}")
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
        sd.set_editor_property("normal_import_method", unreal.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS_AND_TANGENTS)
        sd.set_editor_property("auto_generate_collision", False)
        t.set_editor_property("options", ui)
        tools.import_asset_tasks([t])
        sm = eal.load_asset(f"{P}/{name}")
        if not sm:
            log(f"prop {name} FAILED")
            continue
        texs = [f"{d}/T_{short}_{k}.png" for k in ("BaseColor", "Normal", "MR") if os.path.exists(f"{d}/T_{short}_{k}.png")]
        import_files(texs, P)
        mi_path = f"{P}/MI_{short}"
        if eal.does_asset_exist(mi_path):
            eal.delete_asset(mi_path)
        mi = tools.create_asset("MI_" + short, P, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
        mel.set_material_instance_parent(mi, master)
        bc = tex_settings(f"{P}/T_{short}_BaseColor", True)
        if bc:
            mel.set_material_instance_texture_parameter_value(mi, "BaseColor", bc)
        nm = tex_settings(f"{P}/T_{short}_Normal", False, normal=True)
        if nm:
            mel.set_material_instance_texture_parameter_value(mi, "Normal", nm)
        mr = tex_settings(f"{P}/T_{short}_MR", False)
        if mr:
            mel.set_material_instance_texture_parameter_value(mi, "MR", mr)
        if short.startswith("Hand"):
            # the deputy's sleeve and glove: the generated texture is too orange under a flashlight
            mel.set_material_instance_vector_parameter_value(mi, "Tint", unreal.LinearColor(0.26, 0.23, 0.22, 1))
        eal.save_loaded_asset(mi, False)
        sm.set_material(0, mi)
        bs = sm.get_editor_property("body_setup")
        if bs and short == "Cruiser":
            bs.set_editor_property("collision_trace_flag", unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
        eal.save_loaded_asset(sm, False)
        b = sm.get_bounding_box()
        log(f"prop {name}: min {b.min} max {b.max}")


# ============================================================================ grime decals
def build_decal_master():
    m = new_material("M_Decal", "Decals")
    m.set_editor_property("material_domain", unreal.MaterialDomain.MD_DEFERRED_DECAL)
    m.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
    t = mel.create_material_expression(m, unreal.MaterialExpressionTextureSampleParameter2D, -700, 0)
    t.set_editor_property("parameter_name", "Tex")
    tint = vparam(m, "Tint", (0.5, 0.42, 0.3, 1), -700, -220)
    mul = mel.create_material_expression(m, unreal.MaterialExpressionMultiply, -400, -80)
    mel.connect_material_expressions(t, "RGB", mul, "A")
    mel.connect_material_expressions(tint, "", mul, "B")
    mel.connect_material_property(mul, "", unreal.MaterialProperty.MP_BASE_COLOR)
    amt = sparam(m, "Amount", 0.9, -700, 300)
    om = mel.create_material_expression(m, unreal.MaterialExpressionMultiply, -400, 200)
    mel.connect_material_expressions(t, "A", om, "A")
    mel.connect_material_expressions(amt, "", om, "B")
    mel.connect_material_property(om, "", unreal.MaterialProperty.MP_OPACITY)
    r = sparam(m, "Rough", 0.85, -400, 400)
    mel.connect_material_property(r, "", unreal.MaterialProperty.MP_ROUGHNESS)
    mel.recompile_material(m)
    eal.save_loaded_asset(m, False)
    return m


def step_decals():
    d = SRC + "/Decals"
    if not os.path.isdir(d):
        log("no decals yet")
        return
    eal.make_directory(G + "/Decals")
    master = build_decal_master()
    files = [f"{d}/{f}" for f in sorted(os.listdir(d)) if f.lower().endswith(".png")]
    import_files(files, G + "/Decals")
    tints = {"mold": (0.42, 0.46, 0.34), "water": (0.34, 0.27, 0.19), "filth": (0.5, 0.36, 0.22), "rust": (0.7, 0.42, 0.24), "dirt": (0.4, 0.34, 0.27),
             "crack": (0.25, 0.23, 0.2), "blood": (0.36, 0.14, 0.1), "scratches": (0.2, 0.17, 0.14), "puddle": (0.05, 0.05, 0.05)}
    for f in files:
        name = os.path.basename(f)[:-4]
        tex = eal.load_asset(f"{G}/Decals/{name}")
        if not tex:
            continue
        mi_path = f"{G}/Decals/MD_{name}"
        if eal.does_asset_exist(mi_path):
            eal.delete_asset(mi_path)
        mi = tools.create_asset("MD_" + name, G + "/Decals", unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
        mel.set_material_instance_parent(mi, master)
        mel.set_material_instance_texture_parameter_value(mi, "Tex", tex)
        key = name.split("_")[0]
        tint = tints.get(key, (0.5, 0.42, 0.3))
        mel.set_material_instance_vector_parameter_value(mi, "Tint", unreal.LinearColor(tint[0], tint[1], tint[2], 1))
        if key == "puddle":
            mel.set_material_instance_scalar_parameter_value(mi, "Rough", 0.04)
            mel.set_material_instance_scalar_parameter_value(mi, "Amount", 0.96)
        eal.save_loaded_asset(mi, False)
    log(f"decals: {len(files)}")


def step_extra_mats():
    flat_material("M_Fly", (0.004, 0.004, 0.004), 0.5)
    her = eal.load_asset(G + "/Her/M_Her")
    if her:
        p = G + "/Her/MI_HerDead"
        if eal.does_asset_exist(p):
            eal.delete_asset(p)
        mi = tools.create_asset("MI_HerDead", G + "/Her", unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
        mel.set_material_instance_parent(mi, her)
        mel.set_material_instance_vector_parameter_value(mi, "Tint", unreal.LinearColor(0.2, 0.17, 0.13, 1))
        mel.set_material_instance_scalar_parameter_value(mi, "RoughScale", 1.25)
        eal.save_loaded_asset(mi, False)
    log("extra mats done")


# ============================================================================ Megascans (Fab) surfaces through our world-aligned master, collision on Fab props
MEGA = {"MegaPlaster": "Damaged_Wall_Plaster", "MegaMuddyPlaster": "Old_Muddy_Plaster", "MegaPlasterCracked": "Urban_Ruin_Wall_Plaster_Cracked",
        "MegaRottenWood": "Old_Rotten_Wood", "MegaTilesStained": "Stained_Ceramic_Tiles", "MegaTilesOld": "Old_Floor_Tiles", "MegaTilesDusty": "Dusty_Floor_Tiles"}


def step_mega():
    ar = unreal.AssetRegistryHelpers.get_asset_registry()
    master = eal.load_asset(G + "/Materials/M_Surface")
    if not master:
        log("mega: no M_Surface yet (run tex first)")
        return
    grime_tex = eal.load_asset(G + "/Textures/Grime/BaseColor")
    for name, folder in MEGA.items():
        tex = {}
        for a in ar.get_assets_by_path("/Game/Fab/" + folder, recursive=True):
            if str(a.asset_class_path.asset_name) != "Texture2D":
                continue
            n = str(a.asset_name)
            for suffix, key in (("_B", "BaseColor"), ("_N", "Normal"), ("_ORM", "ORM")):
                if n.endswith(suffix):
                    tex[key] = a.get_asset()
        if "BaseColor" not in tex:
            log(f"mega: {folder} not installed")
            continue
        p = f"{G}/Materials/MI_{name}"
        if eal.does_asset_exist(p):
            eal.delete_asset(p)
        mi = tools.create_asset("MI_" + name, G + "/Materials", unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
        mel.set_material_instance_parent(mi, master)
        for key, t in tex.items():
            mel.set_material_instance_texture_parameter_value(mi, key, t)
        if grime_tex:
            mel.set_material_instance_texture_parameter_value(mi, "GrimeTex", grime_tex)
        mel.set_material_instance_scalar_parameter_value(mi, "Tile", 200.0)
        mel.set_material_instance_scalar_parameter_value(mi, "Grime", 0.8)
        mel.set_material_instance_scalar_parameter_value(mi, "Skirt", 0.5)
        mel.set_material_instance_vector_parameter_value(mi, "Tint", unreal.LinearColor(0.8, 0.78, 0.74, 1))
        eal.save_loaded_asset(mi, False)
        log(f"mega surface MI_{name}")
    n = 0
    for a in list(ar.get_assets_by_path("/Game/Fab", recursive=True)) + list(ar.get_assets_by_path("/Game/OldWest", recursive=True)):
        if str(a.asset_class_path.asset_name) != "StaticMesh":
            continue
        m = a.get_asset()
        bs = m.get_editor_property("body_setup")
        if bs and bs.get_editor_property("collision_trace_flag") != unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE:
            bs.set_editor_property("collision_trace_flag", unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
            eal.save_loaded_asset(m, False)
            n += 1
    log(f"mega: collision on {n} Fab meshes")


# ============================================================================ Edith's drawings (Scripts/art/gen_drawings.py)
def step_drawings():
    d = SRC + "/Drawings"
    if not os.path.isdir(d):
        log("no drawings yet")
        return
    D = G + "/Drawings"
    eal.make_directory(D)
    files = [f"{d}/{f}" for f in sorted(os.listdir(d)) if f.lower().endswith(".png")]
    import_files(files, D)
    m = new_material("M_Drawing", "Drawings")
    t = mel.create_material_expression(m, unreal.MaterialExpressionTextureSampleParameter2D, -500, 0)
    t.set_editor_property("parameter_name", "Tex")
    t.set_editor_property("texture", eal.load_asset(f"{D}/draw_1"))
    dim = const1(m, 0.8, -500, -160)
    mul = mel.create_material_expression(m, unreal.MaterialExpressionMultiply, -250, -40)
    mel.connect_material_expressions(t, "RGB", mul, "A")
    mel.connect_material_expressions(dim, "", mul, "B")
    mel.connect_material_property(mul, "", unreal.MaterialProperty.MP_BASE_COLOR)
    r = const1(m, 0.95, -250, 200)
    mel.connect_material_property(r, "", unreal.MaterialProperty.MP_ROUGHNESS)
    mel.recompile_material(m)
    eal.save_loaded_asset(m, False)
    for f in files:
        name = os.path.basename(f)[:-4]
        tex = tex_settings(f"{D}/{name}", True)
        mi_path = f"{D}/MI_Draw_{name.split('_')[-1]}"
        if eal.does_asset_exist(mi_path):
            eal.delete_asset(mi_path)
        mi = tools.create_asset(mi_path.split("/")[-1], D, unreal.MaterialInstanceConstant, unreal.MaterialInstanceConstantFactoryNew())
        mel.set_material_instance_parent(mi, m)
        mel.set_material_instance_texture_parameter_value(mi, "Tex", tex)
        eal.save_loaded_asset(mi, False)
    log(f"drawings: {len(files)}")
