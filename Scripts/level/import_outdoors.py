"""Unreal (headless): bring in the outdoor polish assets (Cheyenne, 2026-11-28).  Re-runnable.

  Scripts/tools/uepy.ps1 Scripts/level/import_outdoors.py

  /Game/WC/Props/SM_Item_Wheelbarrow, _Stump, _StumpRot, _StumpAxe, _Woodpile, _RockA/B/C
        the baked models of Scripts/art/outdoor_models.py (through the "items" step), walked into as they are shaped
        (collision = the mesh itself, as the kit pieces have)
  /Game/WC/Outdoors/SM_Grass_<T1..F2>   fifteen grass clumps (Scripts/art/outdoor_grass.py), colour on the vertices
  /Game/WC/Outdoors/M_GrassBlades       their material: two-sided foliage, a little light through the blade, a slow wind
  /Game/WC/Mock/SM_MockYard_nn          the yard's leaves, needles and stones again, now without their flat grass blades
Set WC_OUTDOORS_SKIP=items,grass,mock to leave a part out."""
import json, os

ROOT = "C:/GameDev/Unreal/WellnessCheck"
SKIP = [s for s in os.environ.get("WC_OUTDOORS_SKIP", "").split(",") if s]
ITEMS = ["Wheelbarrow", "Stump", "StumpRot", "StumpAxe", "Woodpile", "RockA", "RockB", "RockC"]
os.environ["WC_STEPS"] = "none" if "items" in SKIP else "items"
os.environ["WC_ITEMS_ONLY"] = ",".join(ITEMS)
exec(open(ROOT + "/Scripts/level/import_assets.py", encoding="utf-8").read())      # gives unreal, eal, tools, mel, G, SRC, new_material, log ...
u = unreal
D = G + "/Outdoors"
eal.make_directory(D)


def olog(m):
    u.log_warning("WC_OUTDOORS " + str(m))


# ---------------------------------------------------------------------------------------------- the props: solid as shaped
if "items" not in SKIP:
    for n in ITEMS:
        sm = eal.load_asset(f"{G}/Props/SM_Item_{n}")
        if not sm:
            olog(f"{n}: MISSING")
            continue
        bs = sm.get_editor_property("body_setup")
        if bs:
            bs.set_editor_property("collision_trace_flag", u.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
        eal.save_loaded_asset(sm, False)
        bb = sm.get_bounding_box()
        olog(f"{n}: {sm.get_num_triangles(0)} triangles, {bb.max.x - bb.min.x:.0f} x {bb.max.y - bb.min.y:.0f} x {bb.max.z - bb.min.z:.0f} cm")

# ---------------------------------------------------------------------------------------------- grass
if "grass" not in SKIP:
    m = new_material("M_GrassBlades", "Outdoors")
    m.set_editor_property("two_sided", True)
    m.set_editor_property("shading_model", u.MaterialShadingModel.MSM_TWO_SIDED_FOLIAGE)
    vc = mel.create_material_expression(m, u.MaterialExpressionVertexColor, -900, -100)
    tint = mel.create_material_expression(m, u.MaterialExpressionVectorParameter, -900, -320)
    tint.set_editor_property("parameter_name", "Tint")
    tint.set_editor_property("default_value", u.LinearColor(0.80, 0.80, 0.77, 1.0))
    col = mel.create_material_expression(m, u.MaterialExpressionMultiply, -600, -200)
    mel.connect_material_expressions(vc, "", col, "A")
    mel.connect_material_expressions(tint, "", col, "B")
    mel.connect_material_property(col, "", u.MaterialProperty.MP_BASE_COLOR)
    thru = mel.create_material_expression(m, u.MaterialExpressionMultiply, -350, 0)       # light through the blade, when the torch is behind it
    k = mel.create_material_expression(m, u.MaterialExpressionConstant, -600, 60)
    k.set_editor_property("r", 0.45)
    mel.connect_material_expressions(col, "", thru, "A")
    mel.connect_material_expressions(k, "", thru, "B")
    mel.connect_material_property(thru, "", u.MaterialProperty.MP_SUBSURFACE_COLOR)
    for val, prop, y in ((0.78, u.MaterialProperty.MP_ROUGHNESS, 200), (0.12, u.MaterialProperty.MP_SPECULAR, 300)):
        c = mel.create_material_expression(m, u.MaterialExpressionConstant, -350, y)
        c.set_editor_property("r", val)
        mel.connect_material_property(c, "", prop)
    # wind: the tips move a couple of centimetres, slowly, in waves that cross the yard; the crown stays put
    wp = mel.create_material_expression(m, u.MaterialExpressionWorldPosition, -1200, 500)
    op = mel.create_material_expression(m, u.MaterialExpressionObjectPositionWS, -1200, 620)
    tm = mel.create_material_expression(m, u.MaterialExpressionTime, -1200, 740)
    cu = mel.create_material_expression(m, u.MaterialExpressionCustom, -800, 560)
    cu.set_editor_property("code", "float w1 = sin(T * 1.1 + WP.x * 0.011 + WP.y * 0.007);"
                                   "float w2 = sin(T * 2.7 + WP.x * 0.041 - WP.y * 0.033);"
                                   "float gust = 0.55 + 0.45 * sin(T * 0.23 + WP.x * 0.002);"
                                   "float k = A * saturate((WP.z - OP.z) / 45.0);"
                                   "return float3((w1 * 1.6 + w2 * 0.5) * gust, (w1 * 0.9 - w2 * 0.6) * gust, 0.0) * k;")
    cu.set_editor_property("output_type", u.CustomMaterialOutputType.CMOT_FLOAT3)
    ins = []
    for nm in ("WP", "OP", "T", "A"):
        ci = u.CustomInput()
        ci.set_editor_property("input_name", nm)
        ins.append(ci)
    cu.set_editor_property("inputs", ins)
    mel.connect_material_expressions(wp, "", cu, "WP")
    mel.connect_material_expressions(op, "", cu, "OP")
    mel.connect_material_expressions(tm, "", cu, "T")
    mel.connect_material_expressions(vc, "A", cu, "A")
    mel.connect_material_property(cu, "", u.MaterialProperty.MP_WORLD_POSITION_OFFSET)
    usage(m, "INSTANCED_STATIC_MESHES")
    mel.recompile_material(m)
    eal.save_loaded_asset(m, False)
    olog("M_GrassBlades made")

    u.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 0")      # the legacy importer honours the vertex colours
    src = SRC + "/Outdoors"
    names = sorted(f[:-4] for f in os.listdir(src) if f.startswith("SM_Grass_") and f.endswith(".fbx"))
    for name in names:
        if eal.does_asset_exist(f"{D}/{name}"):
            eal.delete_asset(f"{D}/{name}")
        t = u.AssetImportTask()
        t.set_editor_property("filename", f"{src}/{name}.fbx")
        t.set_editor_property("destination_path", D)
        t.set_editor_property("destination_name", name)
        t.set_editor_property("replace_existing", True)
        t.set_editor_property("automated", True)
        t.set_editor_property("save", True)
        ui = u.FbxImportUI()
        ui.set_editor_property("automated_import_should_detect_type", False)
        ui.set_editor_property("import_mesh", True)
        ui.set_editor_property("import_as_skeletal", False)
        ui.set_editor_property("import_materials", False)
        ui.set_editor_property("import_textures", False)
        ui.set_editor_property("mesh_type_to_import", u.FBXImportType.FBXIT_STATIC_MESH)
        sd = ui.get_editor_property("static_mesh_import_data")
        sd.set_editor_property("combine_meshes", True)
        sd.set_editor_property("auto_generate_collision", False)
        sd.set_editor_property("vertex_color_import_option", u.VertexColorImportOption.REPLACE)
        sd.set_editor_property("normal_import_method", u.FBXNormalImportMethod.FBXNIM_IMPORT_NORMALS)
        t.set_editor_property("options", ui)
        tools.import_asset_tasks([t])
        sm = eal.load_asset(f"{D}/{name}")
        if not sm:
            olog(f"{name}: FAILED")
            continue
        for i in range(len(sm.static_materials)):
            sm.set_material(i, m)
        eal.save_loaded_asset(sm, False)
        bb = sm.get_bounding_box()
        olog(f"{name}: {sm.get_num_triangles(0)} triangles, {bb.max.z - bb.min.z:.0f} cm tall")

# ---------------------------------------------------------------------------------------------- the yard scatter, without its old grass
if "mock" not in SKIP:
    u.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 0")
    MD = G + "/Mock"
    src = SRC + "/Mock"
    MATS = {"RoadGrass": "/Game/WC/Road/M_RoadGrass", "RoadStone": "/Game/WC/Road/M_RoadStone", "Bark": "/Game/WC/Materials/MI_Bark"}
    meta = json.load(open(f"{src}/mock_yard.json"))
    n = 0
    for name in sorted(meta):
        if eal.does_asset_exist(f"{MD}/{name}"):
            eal.delete_asset(f"{MD}/{name}")
        t = u.AssetImportTask()
        t.set_editor_property("filename", f"{src}/{name}.fbx")
        t.set_editor_property("destination_path", MD)
        t.set_editor_property("replace_existing", True)
        t.set_editor_property("automated", True)
        t.set_editor_property("save", True)
        ui = u.FbxImportUI()
        ui.set_editor_property("import_materials", False)
        ui.set_editor_property("import_textures", False)
        ui.set_editor_property("automated_import_should_detect_type", False)
        ui.set_editor_property("mesh_type_to_import", u.FBXImportType.FBXIT_STATIC_MESH)
        sd = ui.get_editor_property("static_mesh_import_data")
        sd.set_editor_property("combine_meshes", True)
        sd.set_editor_property("auto_generate_collision", False)
        sd.set_editor_property("vertex_color_import_option", u.VertexColorImportOption.REPLACE)
        t.set_editor_property("options", ui)
        tools.import_asset_tasks([t])
        sm = eal.load_asset(f"{MD}/{name}")
        if not sm:
            olog(f"{name}: FAILED")
            continue
        for i, sl in enumerate(sm.static_materials):
            key = next((kk for kk in MATS if str(sl.material_slot_name).startswith(kk)), None)
            if key:
                sm.set_material(i, eal.load_asset(MATS[key]))
        eal.save_loaded_asset(sm, False)
        n += 1
    olog(f"{n} yard scatter chunks re-imported without grass blades")
olog("DONE")
