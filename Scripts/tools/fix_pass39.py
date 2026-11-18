"""Level + import side of: drawings, the Company, memories, the attic book; proper small tables instead of the odd
pedestal; scattered-letter notes at half size; settle pass also handles the phone and lets unsupported things fall."""
import io, json, sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
L = "C:/GameDev/Unreal/WellnessCheck/Scripts/level/"

# ---------------------------------------------------------------- import: drawings step, void material
p = L + "import_more.py"
s = io.open(p, encoding="utf-8").read()
assert "step_drawings" not in s
s = s.rstrip() + '''


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
'''
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
compile(s, p, "exec")
edit(L + "import_assets.py", [
    ('''("mega", step_mega), ("variants", step_variants)):''', '''("mega", step_mega), ("variants", step_variants), ("drawings", step_drawings)):'''),
    ('''"kit,her,mats,audio,tex,props,decals,extra,mega,variants"''', '''"kit,her,mats,audio,tex,props,decals,extra,mega,variants,drawings"'''),
    ('''    flat_material("M_Hair", (0.36, 0.33, 0.27), 0.55)''', '''mv_ = flat_material("M_Void", (0.0, 0.0, 0.0), 1.0, unlit=True)
    usage(mv_, "SKELETAL_MESH")
    mel.recompile_material(mv_)
    eal.save_loaded_asset(mv_, False)
    flat_material("M_Hair", (0.36, 0.33, 0.27), 0.55)'''),
])

# ---------------------------------------------------------------- level
edit(L + "build_house.py", [
    ('''OW_YAW = float(os.environ.get("WC_OW_YAW", "0"))''', '''OW_YAW = float(os.environ.get("WC_OW_YAW", "0"))
TABLE = ow("Table_Small_01a", "Table_Side_Round")     # a plain small table (the kit's pedestal stand read as "not a table")'''),
    ('''    n = NOTES[wid]
    a = interact("WCNote", wid, mesh, x, y, z, yaw, "Read", grab, (0, 0, 4), scale, tags, pitch=pitch, roll=roll)''', '''n = NOTES[wid]
    if mesh == "Letters_Scattered" and scale == 1.0:
        scale = 0.5                      # a fan of loose sheets wider than the table they are on looks like it is floating
    a = interact("WCNote", wid, mesh, x, y, z, yaw, "Read", grab, (0, 0, 4), scale, tags, pitch=pitch, roll=roll)'''),
    ('''for i, (x, z) in enumerate(((900, 150), (960, 190), (1020, 150), (1080, 195), (1140, 150), (930, 100), (1050, 105), (1110, 245), (990, 245))):
    place("Portrait_Small", 816, -560 + i * 38, GZ + z, 270, S, collide=False, name=f"Drawing_{i}")''', '''# (her drawings on this wall are real drawings now: memory.py)'''),
    ('''exec(open(os.path.join(HERE, "watchers.py"), encoding="utf-8").read())''', '''exec(open(os.path.join(HERE, "watchers.py"), encoding="utf-8").read())
exec(open(os.path.join(HERE, "memory.py"), encoding="utf-8").read())'''),
])
for f in ("build_house.py", "ell.py"):
    p = L + f
    s = io.open(p, encoding="utf-8").read()
    n = s.count('place("Table_Side_Round",')
    s = s.replace('place("Table_Side_Round",', 'place(TABLE,')
    io.open(p, "w", encoding="utf-8", newline="\n").write(s)
    compile(s, p, "exec")
    print(f, "tables", n)
# memory.py uses grade() from lighting.py, which is exec'd later: move the hook after lighting
p = L + "build_house.py"
s = io.open(p, encoding="utf-8").read()
s = s.replace('exec(open(os.path.join(HERE, "memory.py"), encoding="utf-8").read())\n', '', 1)
a = 'exec(open(os.path.join(HERE, "lighting.py"), encoding="utf-8").read())'
assert a in s
s = s.replace(a, a + '\nexec(open(os.path.join(HERE, "memory.py"), encoding="utf-8").read())', 1)
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
compile(s, p, "exec")

edit(L + "settle.py", [
    ('''"Tour", "Nav", "A_", "Light", "Usable_", "note_rem", "note_calendar",
              "Picture", "Clock", "Sconce",''', '''"Tour", "Nav", "A_", "Light", "note_rem", "note_calendar", "Drawing_", "Mem",
              "Picture", "Sconce",'''),
    ('''    if not hit:
        continue
    t = hit.to_tuple()
    if not t[0]:
        continue''', '''if not hit or not hit.to_tuple()[0]:
        # nothing under it within reach: it was hanging in the air beside the furniture.  Let it fall to whatever is below.
        try:
            hit = unreal.SystemLibrary.line_trace_single(_w, V(origin.x, origin.y, bottom + 4.0), V(origin.x, origin.y, bottom - 340.0), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
                                                         True, [a], unreal.DrawDebugTrace.NONE, True)
        except Exception:
            hit = None
        if not hit or not hit.to_tuple()[0]:
            continue
        fell += 1
    t = hit.to_tuple()'''),
    ('''moved, checked = 0, 0''', '''moved, checked, fell = 0, 0, 0'''),
    ('''log(f"settle: {moved} of {checked} resting props moved onto the surface under them")''', '''log(f"settle: {moved} of {checked} resting props moved onto the surface under them ({fell} had nothing under them and fell)")'''),
])
edit(L + "looks.py", [
    ('''"She drew the same thing over and over. A woman in a nightgown. Each one is taller than the last. In the last one her head is bent to fit the paper."''',
     '''"Crayon, like a child's. A small woman and a tall black shape, holding hands. MY FREND. She was eighty-six."'''),
])
P = L + "notes.json"
n = json.load(open(P, encoding="utf-8"))
n["note_wrenbook"] = {"title": "Grandmother Wren's book, open where she left it", "style": 1, "body":
                      "CUSTOMS FOR THE LONG WINTER\n\nThere is One that keeps company with the lonely. It wants only to be with you.\n\n"
                      "Tie a knot of your own hair for each who left you. Set a place. Ask it in by lamplight, and ask politely.\n\n"
                      "It will sit with you. It will grant what your heart most desires. It will never, ever go.\n\n\n"
                      "The rest of the page is torn away. In the margin, in an older hand than hers:\n\nIt does not grant. It keeps."}
json.dump(n, open(P, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("ok")
