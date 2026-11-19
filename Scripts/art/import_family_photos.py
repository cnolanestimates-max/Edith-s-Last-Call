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


def build_print_material(first_photo):
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
    # Use the actual opening of the frame, even when the photograph inside has been cropped.
    # Local coordinates keep the damage attached to loose prints and to the falling clue.
    shape = node(ue.MaterialExpressionVectorParameter, -670, 590)
    shape.set_editor_property("parameter_name", "PaperShape")
    shape.set_editor_property("default_value", ue.LinearColor(1, 1, 0, 0))
    weather = node(ue.MaterialExpressionVectorParameter, -670, 780)
    weather.set_editor_property("parameter_name", "PaperWeather")
    weather.set_editor_property("default_value", ue.LinearColor(.5, .5, .5, 0))
    wear = node(ue.MaterialExpressionCustom, 180, 0)
    wear.set_editor_property("description", "Faded silver print with moisture damage at the mount")
    wear.set_editor_property("output_type", ue.CustomMaterialOutputType.CMOT_FLOAT3)
    sources = [("Print", photo, "RGB"), ("UV", uv, ""), ("Shape", shape, ""), ("Weather", weather, "")]
    for i, (pin, surface) in enumerate((("PaperTex", "PaperOld"), ("DirtTex", "Grime"))):
        texture = node(ue.MaterialExpressionTextureObject, -130, 640 + i * 160)
        tex = assets.load_asset(f"/Game/WC/Textures/{surface}/BaseColor")
        if not tex:
            raise RuntimeError("Missing house texture " + surface)
        texture.set_editor_property("texture", tex)
        sources.append((pin, texture, ""))
    inputs = []
    for pin, _, _ in sources:
        entry = ue.CustomInput()
        entry.set_editor_property("input_name", pin)
        inputs.append(entry)
    wear.set_editor_property("inputs", inputs)
    wear.set_editor_property("code", """
float2 p = (UV - Weather.xy) * Shape.xy + 0.5;
float2 inset = 0.5 - abs(p - 0.5);
float edge = lerp(min(inset.x, inset.y), 0.5 - length(p - 0.5), Shape.z);
float2 offset = frac(Weather.z * float2(3.13, 7.61));
float3 stock = Texture2DSample(PaperTex, PaperTexSampler, p * 0.89 + offset).rgb;
float3 dirt = Texture2DSample(DirtTex, DirtTexSampler, p * float2(0.87,0.69) + offset.yx).rgb;
float3 speckle = Texture2DSample(DirtTex, DirtTexSampler, p * 2.4 + offset).rgb;
const float3 luma = float3(0.213, 0.715, 0.072);
float moisture = 1.0 - smoothstep(0.14, 0.52, dot(dirt,luma));
float flecks = 1.0 - smoothstep(0.14, 0.32, dot(speckle,luma));
// Emulsion dulls over the whole print. Water creeps further in from the lower edge,
// leaving a narrow dark tideline and little islands of exposed paper underneath.
float boundary = 0.018 + 0.095 * moisture + 0.055 * smoothstep(0.61, 1.0, p.y);
float distanceToTide = edge - boundary;
float damp = 1.0 - smoothstep(-0.026, 0.022, distanceToTide);
float tide = 1.0 - smoothstep(0.001, 0.011, abs(distanceToTide));
float3 faded = lerp(Print, dot(Print,luma).xxx, 0.28) * float3(0.78,0.75,0.70) + float3(0.016,0.014,0.012);
faded *= lerp(float3(1,1,1), float3(0.64,0.53,0.39), moisture * 0.38 + damp * 0.54);
faded *= 1.0 - tide * (0.12 + 0.32 * moisture);
float loss = damp * (0.13 + 0.70 * flecks) + flecks * moisture * 0.10;
return lerp(faded, stock * float3(0.64,0.51,0.37), saturate(loss));
""")
    for pin, source, output in sources:
        wire(source, output, wear, pin)
    property_input(wear, "", mp.MP_BASE_COLOR)
    scalar(m, .86, mp.MP_ROUGHNESS, 290)
    scalar(m, .12, mp.MP_SPECULAR, 390)
    finish(m)


def build_frame_finishes():
    # Inherit the house's colour/normal/roughness maps. Use finer grain and patches of
    # oxidation on these narrow mouldings than on full-size doors or architectural trim.
    for name, parent, tile, grime, metal, tint, dirt in (
        ("MI_FrameWood", "WoodRotten", 38., .58, 0., (1.15, .99, .82), (.18, .14, .10)),
        ("MI_FrameBrass", "Brass", 20., .94, .35, (.66, .56, .42), (.07, .16, .12)),
    ):
        mi = assets.load_asset(DEST + "/" + name) if assets.does_asset_exist(DEST + "/" + name) else tools.create_asset(
            name, DEST, ue.MaterialInstanceConstant, ue.MaterialInstanceConstantFactoryNew())
        base = assets.load_asset("/Game/WC/Materials/MI_" + parent)
        if not mi or not base:
            raise RuntimeError("Missing frame finish or parent for " + name)
        edit.set_material_instance_parent(mi, base)
        for key, value in (("Tile", tile), ("GrimeTile", 37.), ("Grime", grime), ("Metal", metal),
                           ("RoughScale", 1.25), ("Skirt", 0.0)):
            if not edit.set_material_instance_scalar_parameter_value(mi, key, value):
                raise RuntimeError("Missing frame finish parameter " + key)
        for key, color in (("Tint", tint), ("GrimeTint", dirt)):
            if not edit.set_material_instance_vector_parameter_value(mi, key, ue.LinearColor(*color, 1)):
                raise RuntimeError("Missing frame finish parameter " + key)
        edit.update_material_instance(mi)
        if not assets.save_loaded_asset(mi, False):
            raise RuntimeError("Could not save " + name)


def build_materials(first_photo):
    build_print_material(first_photo)
    build_frame_finishes()
    mp = ue.MaterialProperty
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
    ue.log(f"HARROW_PHOTOS imported {len(PRINTS)} prints and built their paper, frame and glass materials")


if __name__ == "__main__":
    build()
