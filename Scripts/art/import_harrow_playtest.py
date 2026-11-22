"""Import the Harrow door plaques and the remixed wheelchair impacts."""
from pathlib import Path
import runpy
import unreal as u

ROOT = Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir()))
PROPS = "/Game/WC/Props/HouseDetails"
SOURCE = ROOT / "SourceArt/Props/HarrowFurniture"
edit = u.MaterialEditingLibrary
imported = runpy.run_path(str(ROOT / 'Scripts/art/import_arrival_assets.py'))['imported']
options = u.FbxImportUI()
options.import_materials = options.import_textures = options.import_as_skeletal = False
options.static_mesh_import_data.auto_generate_collision = False
options.static_mesh_import_data.combine_meshes = True
imported(SOURCE / "SM_HarrowDoorPlaque.fbx", PROPS, options)
for name in ("Ruth", "Danny"):
    texture = imported(SOURCE / f"T_HarrowPlaque{name}.png", PROPS)
    material_name = "M_HarrowPlaque" + name
    mat = u.load_asset(PROPS + "/" + material_name)
    if not mat:
        mat = u.AssetToolsHelpers.get_asset_tools().create_asset(material_name, PROPS, u.Material, u.MaterialFactoryNew())
    edit.delete_all_material_expressions(mat)
    tex = edit.create_material_expression(mat, u.MaterialExpressionTextureSample, -260, -40)
    tex.set_editor_property("texture", texture)
    assert edit.connect_material_property(tex, "RGB", u.MaterialProperty.MP_BASE_COLOR)
    for index, (prop, amount) in enumerate(((u.MaterialProperty.MP_ROUGHNESS, .77), (u.MaterialProperty.MP_SPECULAR, .27))):
        dial = edit.create_material_expression(mat, u.MaterialExpressionConstant, -260, 220 + index * 100)
        dial.set_editor_property("r", amount)
        assert edit.connect_material_property(dial, "", prop)
    edit.recompile_material(mat)
    assert u.EditorAssetLibrary.save_loaded_asset(mat, False)

for sound in ("wheel_sidefall", "wheel_baseboard"):
    wave = imported(ROOT / "SourceArt/Audio" / (sound + ".wav"), "/Game/WC/Audio")
    assert u.EditorAssetLibrary.save_loaded_asset(wave, False)

level = u.get_editor_subsystem(u.LevelEditorSubsystem)
assert level.load_level("/Game/WC/Maps/House")
runpy.run_path(str(ROOT / "Scripts/level/harrow_playtest.py"))["dress"]()
assert level.save_current_level()
print("WCHARRPLAYTEST_SAVED")
