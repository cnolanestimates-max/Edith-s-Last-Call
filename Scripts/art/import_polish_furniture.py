"""Import the polish-pass furniture sets (Scripts/art/polish_furniture.py) into /Game/WC/Props/Polish, with the house's own
materials by slot name.  UnrealEditor-Cmd WellnessCheck.uproject -run=pythonscript -script=<this> -unattended -nosplash
(WC_POLISH_ONLY=SM_PolishChinaSet,... to import only some)."""
import os
from pathlib import Path
import unreal as u

ROOT = Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir()))
SRC = ROOT / "SourceArt/Props/Polish"
DEST = "/Game/WC/Props/Polish"
eal = u.EditorAssetLibrary
tools = u.AssetToolsHelpers.get_asset_tools()
only = [s for s in os.environ.get("WC_POLISH_ONLY", "").split(",") if s]
u.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 0")     # the legacy importer keeps slot names
for fbx in sorted(SRC.glob("SM_*.fbx")):
    name = fbx.stem
    if only and name not in only:
        continue
    if eal.does_asset_exist(f"{DEST}/{name}"):
        eal.delete_asset(f"{DEST}/{name}")
    t = u.AssetImportTask()
    t.set_editor_property("filename", str(fbx))
    t.set_editor_property("destination_path", DEST)
    t.set_editor_property("replace_existing", True)
    t.set_editor_property("automated", True)
    t.set_editor_property("save", True)
    ui = u.FbxImportUI()
    ui.set_editor_property("import_materials", False)
    ui.set_editor_property("import_textures", False)
    ui.set_editor_property("import_as_skeletal", False)
    ui.set_editor_property("automated_import_should_detect_type", False)
    ui.set_editor_property("mesh_type_to_import", u.FBXImportType.FBXIT_STATIC_MESH)
    sd = ui.get_editor_property("static_mesh_import_data")
    sd.set_editor_property("combine_meshes", True)
    sd.set_editor_property("auto_generate_collision", "Wardrobe" in name or "Cupboard" in name)      # furniture blocks; the sets sit in cabinets
    t.set_editor_property("options", ui)
    tools.import_asset_tasks([t])
    sm = eal.load_asset(f"{DEST}/{name}")
    if not sm:
        u.log_error(f"WC_POLISHFURN {name} failed")
        continue
    missing = []
    for i, sl in enumerate(sm.static_materials):
        slot = str(sl.material_slot_name)
        m = eal.load_asset("/Game/WC/Materials/" + slot)
        if m:
            sm.set_material(i, m)
        else:
            missing.append(slot)
    eal.save_loaded_asset(sm, False)
    u.log_warning(f"WC_POLISHFURN {name}: {len(sm.static_materials)} materials, missing {missing}")
