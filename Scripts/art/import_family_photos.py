"""Import Harrow album prints and build their shared Unreal materials. Run in the Unreal Python interpreter."""
from pathlib import Path
import unreal as ue

DEST = "/Game/WC/FamilyPhotos"
SOURCE = Path(ue.Paths.convert_relative_path_to_full(ue.Paths.project_dir())) / "SourceArt" / "FamilyPhotos"
PRINTS = ("Porch", "Baking", "Anniversary", "Christmas", "Siblings", "Walter", "Daniel", "Scratched", "Attic",
          "VowsDefaced", "EdithGarden")
assets = ue.EditorAssetLibrary
tools = ue.AssetToolsHelpers.get_asset_tools()
edit = ue.MaterialEditingLibrary


def material(name):
    path = DEST + "/" + name
    mat = assets.load_asset(path) if assets.does_asset_exist(path) else tools.create_asset(name, DEST, ue.Material, ue.MaterialFactoryNew())
    if not mat:
        raise RuntimeError("Could not create " + path)
    edit.delete_all_material_expressions(mat)
    return mat


def wire(source, output, target, input_name):
    if not edit.connect_material_expressions(source, output, target, input_name):
        raise RuntimeError(f"Cannot connect {source.get_name()}.{output} to {target.get_name()}.{input_name}")


def property_input(source, output, prop):
    if not edit.connect_material_property(source, output, prop):
        raise RuntimeError(f"Cannot connect {source.get_name()} to {prop}")


def scalar(mat, value, prop, y):
    node = edit.create_material_expression(mat, ue.MaterialExpressionConstant, -240, y)
    node.set_editor_property("r", value)
    property_input(node, "", prop)


def finish(mat):
    edit.recompile_material(mat)
    if not assets.save_loaded_asset(mat, False):
        raise RuntimeError("Could not save " + mat.get_name())


def build_materials(first_photo):
    mp = ue.MaterialProperty
    m = material("M_FamilyPrint")
    node = lambda cls, x, y: edit.create_material_expression(m, cls, x, y)
    # Project onto the existing print surface in mesh space, including the tilted floor frames.
    local = node(ue.MaterialExpressionPreSkinnedPosition, -1200, 0)
    interp = node(ue.MaterialExpressionVertexInterpolator, -1000, 0)
    wire(local, "", interp, "")
    uv = node(ue.MaterialExpressionAppendVector, -370, 0)
    for i, pname in enumerate(("PhotoU", "PhotoV")):
        axis = node(ue.MaterialExpressionVectorParameter, -1000, 180 + i * 280)
        axis.set_editor_property("parameter_name", pname)
        axis.set_editor_property("default_value", ue.LinearColor(.01, 0, 0, .5) if not i else ue.LinearColor(0, 0, -.01, .5))
        dot = node(ue.MaterialExpressionDotProduct, -760, i * 290)
        wire(interp, "", dot, "A")
        wire(axis, "", dot, "B")
        add = node(ue.MaterialExpressionAdd, -560, i * 290)
        wire(dot, "", add, "A")
        wire(axis, "A", add, "B")
        wire(add, "", uv, "B" if i else "A")
    photo = node(ue.MaterialExpressionTextureSampleParameter2D, -200, 0)
    photo.set_editor_property("parameter_name", "Photograph")
    photo.set_editor_property("texture", first_photo)
    wire(uv, "", photo, "UVs")
    property_input(photo, "RGB", mp.MP_BASE_COLOR)
    scalar(m, .72, mp.MP_ROUGHNESS, 290)
    scalar(m, .18, mp.MP_SPECULAR, 390)
    finish(m)

    hidden = material("M_HidePortraitRelief")
    hidden.set_editor_property("blend_mode", ue.BlendMode.BLEND_MASKED)
    scalar(hidden, 0, mp.MP_OPACITY_MASK, 0)
    finish(hidden)

    glass = material("M_PhotoGlass")
    glass.set_editor_property("blend_mode", ue.BlendMode.BLEND_TRANSLUCENT)
    scalar(glass, .27, mp.MP_BASE_COLOR, 0)
    scalar(glass, .09, mp.MP_OPACITY, 150)
    finish(glass)


def build():
    files = [SOURCE / (name + ".png") for name in PRINTS]
    if not all(path.is_file() for path in files):
        raise RuntimeError("Missing photos: " + str([p.name for p in files if not p.is_file()]))
    assets.make_directory(DEST)
    jobs = []
    for path in files:
        task = ue.AssetImportTask()
        task.filename = str(path)
        task.destination_path = DEST
        task.automated = True
        task.replace_existing = True
        task.save = True
        jobs.append(task)
    tools.import_asset_tasks(jobs)
    for name in PRINTS:
        tex = assets.load_asset(DEST + "/" + name)
        if not isinstance(tex, ue.Texture2D):
            raise RuntimeError(f"Missing imported photo {name}")
        tex.set_editor_property("max_texture_size", 1024)
        tex.set_editor_property("address_x", ue.TextureAddress.TA_CLAMP)
        tex.set_editor_property("address_y", ue.TextureAddress.TA_CLAMP)
        tex.set_editor_property("power_of_two_mode", ue.TexturePowerOfTwoSetting.STRETCH_TO_POWER_OF_TWO)
        if not assets.save_loaded_asset(tex, False):
            raise RuntimeError(f"Could not save photo {name}")
    build_materials(assets.load_asset(DEST + "/Porch"))
    ue.log(f"HARROW_PHOTOS imported {len(PRINTS)} prints and three materials")


build()
