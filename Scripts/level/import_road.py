"""Import the gravel footpath round the house (Scripts/art/road_textures.py + road_build.py) and make its four materials.
UnrealEditor-Cmd WellnessCheck.uproject -run=pythonscript -script=<this> -unattended -nosplash
  /Game/WC/Road/T_RoadGravel_C, _N, _R            the rendered gravel (1.2 m tile)
  /Game/WC/Road/M_RoadGravel                      the bed: loose gravel, packed to dirt where feet go (vertex R), earth and
                                                  moss at the verges (G), darker and glossier where damp (B)
  /Game/WC/Road/M_RoadStone, M_RoadGrass, M_RoadWater
  /Game/WC/Road/SM_Road_<L|R>_<nn>                one per five metres of path"""
import json, os
import unreal as u

SRC = "C:/GameDev/Unreal/WellnessCheck/SourceArt/Road"
D = "/Game/WC/Road"
eal = u.EditorAssetLibrary
mel = u.MaterialEditingLibrary
tools = u.AssetToolsHelpers.get_asset_tools()
eal.make_directory(D)


def log(m):
    u.log_warning("WC_ROAD " + m)


def import_tex(name, srgb, normal=False):
    t = u.AssetImportTask()
    t.set_editor_property("filename", f"{SRC}/{name}.png")
    t.set_editor_property("destination_path", D)
    t.set_editor_property("replace_existing", True)
    t.set_editor_property("automated", True)
    t.set_editor_property("save", True)
    tools.import_asset_tasks([t])
    tx = eal.load_asset(f"{D}/{name}")
    tx.set_editor_property("srgb", srgb)
    if normal:
        tx.set_editor_property("compression_settings", u.TextureCompressionSettings.TC_NORMALMAP)
        tx.set_editor_property("flip_green_channel", True)
    elif not srgb:
        tx.set_editor_property("compression_settings", u.TextureCompressionSettings.TC_MASKS)
    eal.save_loaded_asset(tx, False)
    return tx


def new_mat(name):
    """The material, emptied (rebuilt in place, so the meshes that use it keep pointing at it)."""
    p = f"{D}/{name}"
    if eal.does_asset_exist(p):
        m = eal.load_asset(p)
        mel.delete_all_material_expressions(m)
        return m
    return tools.create_asset(name, D, u.Material, u.MaterialFactoryNew())


def ex(m, cls, x, y):
    return mel.create_material_expression(m, cls, x, y)


def c3(m, rgb, x, y):
    e = ex(m, u.MaterialExpressionConstant3Vector, x, y)
    e.set_editor_property("constant", u.LinearColor(rgb[0], rgb[1], rgb[2], 1))
    return e


def c1(m, v, x, y):
    e = ex(m, u.MaterialExpressionConstant, x, y)
    e.set_editor_property("r", v)
    return e


def lerp(m, a, b, alpha, x, y, pa="", pb="", pal=""):
    e = ex(m, u.MaterialExpressionLinearInterpolate, x, y)
    r = [mel.connect_material_expressions(a, pa, e, "A"), mel.connect_material_expressions(b, pb, e, "B"), mel.connect_material_expressions(alpha, pal, e, "Alpha")]
    if not all(r):
        log(f"lerp at {x},{y}: connected {r}")
    return e


def mul(m, a, b, x, y, pa="", pb=""):
    e = ex(m, u.MaterialExpressionMultiply, x, y)
    r = [mel.connect_material_expressions(a, pa, e, "A"), mel.connect_material_expressions(b, pb, e, "B")]
    if not all(r):
        log(f"mul at {x},{y}: connected {r}")
    return e


def chan(m, src, ch, x, y):
    """One channel of a vertex colour, as a dot product with a unit axis (a ComponentMask on the vertex colour did nothing
    in the game, 2026-11-22: the ruts and verges never darkened)."""
    e = ex(m, u.MaterialExpressionDotProduct, x, y)
    axis = c3(m, tuple(1.0 if c == ch else 0.0 for c in "RGB"), x - 150, y + 40)
    ok = mel.connect_material_expressions(src, "", e, "A") and mel.connect_material_expressions(axis, "", e, "B")
    if not ok:
        log(f"channel {ch}: not connected")
    return e


def tex(m, t, x, y, kind=None):
    e = ex(m, u.MaterialExpressionTextureSample, x, y)
    e.set_editor_property("texture", t)
    if kind == "normal":
        e.set_editor_property("sampler_type", u.MaterialSamplerType.SAMPLERTYPE_NORMAL)
    elif kind == "mask":
        e.set_editor_property("sampler_type", u.MaterialSamplerType.SAMPLERTYPE_MASKS)
    return e


TC = import_tex("T_RoadGravel_C", True)
TN = import_tex("T_RoadGravel_N", False, normal=True)
TR = import_tex("T_RoadGravel_R", False)

# ---- the bed
m = new_mat("M_RoadGravel")
vc = ex(m, u.MaterialExpressionVertexColor, -1500, 300)
cs = tex(m, TC, -1500, -300)
ns = tex(m, TN, -1500, 700, "normal")
rs = tex(m, TR, -1500, 1100, "mask")
# the footpath: loose limestone gravel greyed with dust; where feet go (R) it is packed down into brown dirt with only fine
# grit showing; the verges and patches (G) are dark earth and moss; damp ground (B) is darker and catches the light
gravel = lerp(m, mul(m, cs, c1(m, 0.30, -1300, -200), -1250, -280, "RGB"), c3(m, (0.055, 0.048, 0.038), -1200, -150), c1(m, 0.30, -1200, -60), -1000, -250)
packed = lerp(m, mul(m, cs, c3(m, (0.16, 0.13, 0.10), -1100, -20), -1000, -20, "RGB"), c3(m, (0.042, 0.033, 0.024), -1050, 40), c1(m, 0.5, -1050, 90), -900, 0)
trod = lerp(m, gravel, packed, mul(m, chan(m, vc, "R", -1200, 140), c1(m, 1.0, -1100, 160), -950, 140), -800, -200)
earth = lerp(m, mul(m, cs, c3(m, (0.075, 0.072, 0.045), -900, 220), -800, 220, "RGB"), c3(m, (0.030, 0.034, 0.018), -850, 280), c1(m, 0.5, -850, 320), -700, 240)
verge = lerp(m, trod, earth, mul(m, chan(m, vc, "G", -1000, 360), c1(m, 1.0, -900, 380), -750, 360), -600, -150)
mud = lerp(m, verge, mul(m, verge, c1(m, 0.5, -500, 300), -450, 300), chan(m, vc, "B", -600, 420), -400, -120)
mel.connect_material_property(mud, "", u.MaterialProperty.MP_BASE_COLOR)
r1 = lerp(m, rs, c1(m, 0.86, -900, 1200), mul(m, chan(m, vc, "R", -1000, 1300), c1(m, 0.6, -950, 1340), -850, 1300), -700, 1150, "R")
rough = lerp(m, r1, c1(m, 0.30, -600, 1250), mul(m, chan(m, vc, "B", -800, 1400), c1(m, 0.85, -750, 1440), -650, 1400), -500, 1150)
mel.connect_material_property(rough, "", u.MaterialProperty.MP_ROUGHNESS)
flat = lerp(m, ns, c3(m, (0, 0, 1), -900, 820), mul(m, chan(m, vc, "R", -1100, 950), c1(m, 0.55, -1000, 900), -800, 900), -600, 760, "RGB")
mel.connect_material_property(flat, "", u.MaterialProperty.MP_NORMAL)
mel.recompile_material(m)
log(f"M_RoadGravel saved {eal.save_loaded_asset(m, False)}")

# ---- loose stones: their own grey from vertex colour, with the gravel's grain
m = new_mat("M_RoadStone")
vc = ex(m, u.MaterialExpressionVertexColor, -900, 0)
cs = tex(m, TC, -900, -300)
base = lerp(m, vc, mul(m, cs, vc, -700, -250, "RGB", ""), c1(m, 0.55, -700, -100), -500, -150)
mel.connect_material_property(base, "", u.MaterialProperty.MP_BASE_COLOR)
mel.connect_material_property(c1(m, 0.72, -500, 100), "", u.MaterialProperty.MP_ROUGHNESS)
mel.connect_material_property(tex(m, TN, -900, 300, "normal"), "RGB", u.MaterialProperty.MP_NORMAL)
mel.recompile_material(m)
eal.save_loaded_asset(m, False)

# ---- dead grass, weeds and needles: vertex colour, both sides
m = new_mat("M_RoadGrass")
m.set_editor_property("two_sided", True)
vc = ex(m, u.MaterialExpressionVertexColor, -600, 0)
mel.connect_material_property(vc, "", u.MaterialProperty.MP_BASE_COLOR)
mel.connect_material_property(c1(m, 0.86, -400, 160), "", u.MaterialProperty.MP_ROUGHNESS)
mel.recompile_material(m)
eal.save_loaded_asset(m, False)

# ---- standing rain: dark, murky and glassy, the faintest ripple
m = new_mat("M_RoadWater")
mel.connect_material_property(c3(m, (0.030, 0.025, 0.017), -400, 0), "", u.MaterialProperty.MP_BASE_COLOR)     # murky, silt in it
mel.connect_material_property(c1(m, 0.045, -400, 120), "", u.MaterialProperty.MP_ROUGHNESS)
mel.connect_material_property(c1(m, 1.0, -400, 200), "", u.MaterialProperty.MP_SPECULAR)
ripple = lerp(m, tex(m, TN, -900, 300, "normal"), c3(m, (0, 0, 1), -900, 500), c1(m, 0.92, -900, 600), -600, 350, "RGB")
mel.connect_material_property(ripple, "", u.MaterialProperty.MP_NORMAL)
mel.recompile_material(m)
eal.save_loaded_asset(m, False)

# the legacy FBX importer, so the FbxImportUI options below (vertex colours above all) are honoured; Interchange ignores them
u.SystemLibrary.execute_console_command(None, "Interchange.FeatureFlags.Import.FBX 0")
MATS = {"Road": f"{D}/M_RoadGravel", "RoadStone": f"{D}/M_RoadStone", "RoadGrass": f"{D}/M_RoadGrass", "RoadWater": f"{D}/M_RoadWater"}
meta = {} if os.environ.get("WC_ROAD_MATS_ONLY") else json.load(open(f"{SRC}/road_chunks.json"))
n = 0
for name in sorted(meta):
    # a re-import of an existing mesh goes through its saved (Interchange) import settings and drops the vertex colours,
    # so the old chunk is deleted first and imported fresh (the level's actors find the new one by path)
    if eal.does_asset_exist(f"{D}/{name}"):
        eal.delete_asset(f"{D}/{name}")
    t = u.AssetImportTask()
    t.set_editor_property("filename", f"{SRC}/{name}.fbx")
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
        log(f"{name} FAILED")
        continue
    for i, sl in enumerate(sm.static_materials):
        slot = str(sl.material_slot_name)
        key = next((k for k in MATS if slot == k or slot.startswith(k + "_") or slot.endswith(k)), None)
        if slot.startswith("RoadStone"):
            key = "RoadStone"
        elif slot.startswith("RoadGrass"):
            key = "RoadGrass"
        elif slot.startswith("RoadWater"):
            key = "RoadWater"
        elif slot.startswith("Road"):
            key = "Road"
        if key:
            sm.set_material(i, eal.load_asset(MATS[key]))
    eal.save_loaded_asset(sm, False)
    n += 1
log(f"imported {n} chunks and 4 materials")
