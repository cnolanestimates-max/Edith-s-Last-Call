"""Import the round-two mock-ups (Cheyenne, 2026-11-22: before and after pictures, she keeps or trashes each):
  /Game/WC/Mock/T_MockKitchenPaper_*, T_MockLinoleum_*        Scripts/art/mock_surfaces.py
  /Game/WC/Mock/MI_MockKitchenPaper, MI_MockLinoleum          children of the house's surface material (world-mapped)
  /Game/WC/Mock/SM_MockYard_nn                                Scripts/art/mock_yard.py (vertex colour grass, stones, bark)
  /Game/WC/Road/M_RoadWater                                   the puddles made glassier (WC_MOCK_PUDDLE=1; trashed)
UnrealEditor-Cmd WellnessCheck.uproject -run=pythonscript -script=<this> -AllowCommandletRendering -unattended -nosplash"""
import json, os
import unreal as u

SRC = "C:/GameDev/Unreal/WellnessCheck/SourceArt/Mock"
D = "/Game/WC/Mock"
eal = u.EditorAssetLibrary
mel = u.MaterialEditingLibrary
tools = u.AssetToolsHelpers.get_asset_tools()
eal.make_directory(D)


def log(m):
    u.log_warning("WC_MOCK " + m)


def tex(name, srgb, kind=None):
    t = u.AssetImportTask()
    t.set_editor_property("filename", f"{SRC}/{name}.png")
    t.set_editor_property("destination_path", D)
    t.set_editor_property("replace_existing", True)
    t.set_editor_property("automated", True)
    t.set_editor_property("save", True)
    tools.import_asset_tasks([t])
    tx = eal.load_asset(f"{D}/{name}")
    tx.set_editor_property("srgb", srgb)
    if kind == "normal":
        tx.set_editor_property("compression_settings", u.TextureCompressionSettings.TC_NORMALMAP)
    elif kind == "mask":
        tx.set_editor_property("compression_settings", u.TextureCompressionSettings.TC_MASKS)
    eal.save_loaded_asset(tx, False)
    return tx


def surface_mi(name, template, stem, tile, grime=None):
    path = f"{D}/{name}"
    if eal.does_asset_exist(path):
        eal.delete_asset(path)
    mi = eal.duplicate_asset(template, path)
    mel.set_material_instance_texture_parameter_value(mi, "BaseColor", tex(stem + "_C", True))
    mel.set_material_instance_texture_parameter_value(mi, "ORM", tex(stem + "_ORM", False, "mask"))
    mel.set_material_instance_texture_parameter_value(mi, "Normal", tex(stem + "_N", False, "normal"))
    mel.set_material_instance_scalar_parameter_value(mi, "Tile", tile)
    if grime is not None:
        mel.set_material_instance_scalar_parameter_value(mi, "Grime", grime)
    eal.save_loaded_asset(mi, False)
    log(f"{name} made")


surface_mi("MI_MockKitchenPaper", "/Game/WC/Materials/MI_WallpaperRed", "T_MockKitchenPaper", 64.0, 0.7)
surface_mi("MI_MockLinoleum", "/Game/WC/Materials/MI_MegaTilesOld", "T_MockLinoleum", 60.0, 0.6)

# the yard scatter
u.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 0")
MATS = {"RoadGrass": "/Game/WC/Road/M_RoadGrass", "RoadStone": "/Game/WC/Road/M_RoadStone", "Bark": "/Game/WC/Materials/MI_Bark"}
meta = json.load(open(f"{SRC}/mock_yard.json"))
for name in sorted(meta):
    if eal.does_asset_exist(f"{D}/{name}"):
        eal.delete_asset(f"{D}/{name}")
    t = u.AssetImportTask()
    t.set_editor_property("filename", f"{SRC}/{name}.fbx")
    t.set_editor_property("destination_path", D)
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
    sm = eal.load_asset(f"{D}/{name}")
    if not sm:
        log(f"{name} FAILED")
        continue
    for i, sl in enumerate(sm.static_materials):
        key = next((k for k in MATS if str(sl.material_slot_name).startswith(k)), None)
        if key:
            sm.set_material(i, eal.load_asset(MATS[key]))
    eal.save_loaded_asset(sm, False)
log(f"{len(meta)} yard chunks imported")

# the puddles: glassier, so they mirror the sky and the flashlight instead of reading as holes
if os.environ.get("WC_MOCK_PUDDLE", "0") == "1":                 # (trashed by Cheyenne, 2026-11-22: off unless asked)
    m = eal.load_asset("/Game/WC/Road/M_RoadWater")
    mel.delete_all_material_expressions(m)

    def ex(cls, x, y):
        return mel.create_material_expression(m, cls, x, y)
    base = ex(u.MaterialExpressionConstant3Vector, -400, 0)
    base.set_editor_property("constant", u.LinearColor(0.018, 0.017, 0.014, 1))
    mel.connect_material_property(base, "", u.MaterialProperty.MP_BASE_COLOR)
    r = ex(u.MaterialExpressionConstant, -400, 120)
    r.set_editor_property("r", 0.012)
    mel.connect_material_property(r, "", u.MaterialProperty.MP_ROUGHNESS)
    sp = ex(u.MaterialExpressionConstant, -400, 200)
    sp.set_editor_property("r", 1.0)
    mel.connect_material_property(sp, "", u.MaterialProperty.MP_SPECULAR)
    tn = ex(u.MaterialExpressionTextureSample, -900, 300)
    tn.set_editor_property("texture", eal.load_asset("/Game/WC/Road/T_RoadGravel_N"))
    tn.set_editor_property("sampler_type", u.MaterialSamplerType.SAMPLERTYPE_NORMAL)
    up = ex(u.MaterialExpressionConstant3Vector, -900, 500)
    up.set_editor_property("constant", u.LinearColor(0, 0, 1, 1))
    k = ex(u.MaterialExpressionConstant, -900, 600)
    k.set_editor_property("r", 0.97)
    lp = ex(u.MaterialExpressionLinearInterpolate, -600, 350)
    mel.connect_material_expressions(tn, "RGB", lp, "A")
    mel.connect_material_expressions(up, "", lp, "B")
    mel.connect_material_expressions(k, "", lp, "Alpha")
    mel.connect_material_property(lp, "", u.MaterialProperty.MP_NORMAL)
    mel.recompile_material(m)
    log(f"M_RoadWater glassier, saved {eal.save_loaded_asset(m, False)}")
