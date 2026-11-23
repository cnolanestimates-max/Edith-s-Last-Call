"""Import the transparent notebook artwork from SourceArt/RuthMap."""
from pathlib import Path
import unreal as u

source = Path(__file__).resolve().parents[2] / "SourceArt" / "RuthMap"
destination = "/Game/WC/RuthMap"
editor_assets = u.EditorAssetLibrary
asset_tools = u.AssetToolsHelpers.get_asset_tools()
for plate in ("Header", *(f"Scrap{i}" for i in range(1, 8))):
    name = f"T_RuthMap_{plate}"
    task = u.AssetImportTask()
    task.filename = str(source / f"{name}.png")
    task.destination_path = destination
    task.destination_name = name
    task.automated = True
    task.replace_existing = True
    task.save = False
    asset_tools.import_asset_tasks([task])
    texture = editor_assets.load_asset(f"{destination}/{name}")
    assert isinstance(texture, u.Texture2D), name
    texture.set_editor_property("compression_settings", u.TextureCompressionSettings.TC_EDITOR_ICON)
    texture.set_editor_property("mip_gen_settings", u.TextureMipGenSettings.TMGS_NO_MIPMAPS)
    texture.set_editor_property("lod_group", u.TextureGroup.TEXTUREGROUP_UI)
    assert editor_assets.save_loaded_asset(texture), name
u.log_warning("RUTH MAP eight notebook textures imported")
