"""Old West furniture (Fab) replaces the weakest kit pieces: beds, desks, the gun cabinet, dressers, washstands."""
import io
L = "C:/GameDev/Unreal/WellnessCheck/Scripts/level/"


def edit(f, pairs):
    s = io.open(L + f, encoding="utf-8").read()
    for old, new in pairs:
        assert old in s, (f, old[:80])
        s = s.replace(old, new, 1)
    io.open(L + f, "w", encoding="utf-8", newline="\n").write(s)


edit("build_house.py", [
    ('''NOTES = json.load(open(os.path.join(HERE, "notes.json"), encoding="utf-8"))''',
     '''NOTES = json.load(open(os.path.join(HERE, "notes.json"), encoding="utf-8"))


def ow(name, fallback):
    """Old West furniture (Fab) by short name, e.g. 'Bed_01f'; the kit piece `fallback` if that pack is not installed."""
    p = f"/Game/OldWest/VOL1/Meshes/SM_{name}"
    return asset(p) if eal.does_asset_exist(p) else fallback


OW_YAW = float(os.environ.get("WC_OW_YAW", "0"))          # added to every Old West piece if the pack faces another way'''),
    ('place("Bed_FourPoster_Broken", 560, 440, UZ, 90, MB)', 'place(ow("Bed_01f", "Bed_FourPoster_Broken"), 560, 455, UZ, 0 + OW_YAW, MB, name="MasterBed")'),
    ('place("Bed_Hospital_Sheet", 620, -500, UZ, 0, KD, tags=["RuthBed"])', 'place(ow("Bed_02g", "Bed_Hospital_Sheet"), 640, -470, UZ, 180 + OW_YAW, KD, tags=["RuthBed"], name="RuthBed")'),
    ('place("Bed_Hospital_Rusty", 250, -520, UZ, 0, KD)', 'place(ow("Bed_02c", "Bed_Hospital_Rusty"), 250, -470, UZ, 180 + OW_YAW, KD, name="DannyOldBed")'),
    ('place("Desk_Writing", 1500, -420, GZ, 270, S)', 'place(ow("Desk_01a", "Desk_Writing"), 1535, -420, GZ, 270 + OW_YAW, S, name="EdithDesk")'),
    ('place("Dresser_Drawers", 420, 560, GZ, 180, DI)', 'place(ow("Cabinet_02a", "Dresser_Drawers"), 420, 556, GZ, 180 + OW_YAW, DI, name="ChinaCabinet")'),
])
edit("ell.py", [
    ('interact("WCUsable", "desk", "Desk_Writing", 2330, -330, GZ, 270, "Open the desk", (40, 62, 52), (0, 0, 56))',
     'interact("WCUsable", "desk", ow("Desk_01a", "Desk_Writing"), 2340, -330, GZ, 270 + OW_YAW, "Open the desk", (44, 86, 66), (0, 0, 66))'),
    ('put("Typewriter_Old", 2330, -310, GZ + 101, 250, DN)', 'put("Typewriter_Old", 2318, -310, GZ + 78, 250, DN)'),
    ('put("Desk_Lamp_Green", 2340, -385, GZ + 101, 200, DN)', 'put("Desk_Lamp_Green", 2318, -385, GZ + 78, 200, DN)'),
    ('put("Book_Stack_Old", 2325, -270, GZ + 101, 30, DN)', 'put("Book_Stack_Old", 2318, -262, GZ + 78, 30, DN)'),
    ('place("Cabinet_Instruments_Glass", 2352, -530, GZ, 270, DN, name="GunCabinet")', 'place(ow("Cabinet_02a", "Cabinet_Instruments_Glass"), 2356, -520, GZ, 270 + OW_YAW, DN, name="GunCabinet")'),
    ('ammo("ammo_den", 2340, -520, GZ + 98, 20)', 'ammo("ammo_den", 2300, -545, GZ + 0, 20)'),
    ('place("Bed_FourPoster", 2230, -450, UZ, 270, DR, name="DanielBed")', 'place(ow("Bed_02g", "Bed_FourPoster"), 2240, -470, UZ, 180 + OW_YAW, DR, name="DanielBed")'),
    ('place("Desk_Writing", 1650, -400, UZ, 90, DR, name="DanielDesk")', 'place(ow("Desk_01a", "Desk_Writing"), 1660, -400, UZ, 90 + OW_YAW, DR, name="DanielDesk")'),
    ('put("Portrait_Small", 1640, -350, UZ + 101, 90, DR, name="DanielPhoto", pitch=-70)', 'put("Portrait_Small", 1682, -350, UZ + 78, 90, DR, name="DanielPhoto", pitch=-70)'),
    ('put("Toy_Train_Wind_Up", 1650, -450, UZ + 101, 60, DR)', 'put("Toy_Train_Wind_Up", 1682, -455, UZ + 78, 60, DR)'),
    ('put("Book_Closed_Leather", 1655, -395, UZ + 101, 20, DR)', 'put("Book_Closed_Leather", 1684, -395, UZ + 78, 20, DR)'),
    ('put_note("note_daniel", "Letters_Scattered", 1660, -430, UZ + 101, 100, scale=0.7)', 'put_note("note_daniel", "Letters_Scattered", 1686, -425, UZ + 78, 100, scale=0.7)'),
    ('put_pickup("pick_key_attic", "key_attic", "Attic key", CUBE, 1648, -370, UZ + 102, 110, (0.075, 0.022, 0.006), mats={0: "BrassOld"})',
     'put_pickup("pick_key_attic", "key_attic", "Attic key", CUBE, 1686, -372, UZ + 78, 110, (0.075, 0.022, 0.006), mats={0: "BrassOld"})'),
    ('place("Bed_Hospital_Bare_Springs", 2200, 505, UZ, 180, AD)', 'place(ow("Bed_02c", "Bed_Hospital_Bare_Springs"), 2200, 470, UZ, 0 + OW_YAW, AD, name="AideBed")'),
    ('place("Dresser_Drawers_Open", 1640, 380, UZ, 90, AD)', 'place(ow("Dresser_01a", "Dresser_Drawers_Open"), 1646, 380, UZ, 90 + OW_YAW, AD, name="AideDresser")'),
    ('put_note("note_aide3", "Letters_Scattered", 1640, 380, UZ + 97, 60, scale=0.6)', 'put_note("note_aide3", "Letters_Scattered", 1650, 380, UZ + 119, 60, scale=0.6)'),
    ('place("Desk_Writing", 2450, -470, UZ, 90, SW, name="SewingTable")', 'place(ow("Work_Table_01a", "Desk_Writing"), 2446, -470, UZ, 90 + OW_YAW, SW, name="SewingTable")'),
    ('put("Hatbox_Round", 2445, -520, UZ + 101, 0, SW)', 'put("Hatbox_Round", 2445, -525, UZ + 74, 0, SW)'),
    ('put(m, 2445, -445 + i * 22, UZ + 101, 90, SW, name=f"FamilyDoll_{i}", scale=s)', 'put(m, 2440, -450 + i * 22, UZ + 74, 90, SW, name=f"FamilyDoll_{i}", scale=s)'),
    ('put_pickup("pick_shears", "shears", "Sewing shears", CUBE, 2462, -500, UZ + 102, 35,', 'put_pickup("pick_shears", "shears", "Sewing shears", CUBE, 2456, -492, UZ + 74, 35,'),
    ('put(CUBE, 2462, -500, UZ + 102.6, 62, SW, name="ShearsBlade2",', 'put(CUBE, 2456, -492, UZ + 74.6, 62, SW, name="ShearsBlade2",'),
    ('place("Dresser_Drawers", 2752, 300, GZ, 270, SK_)', 'place(ow("Sink_01a", "Dresser_Drawers"), 2748, 300, GZ, 270 + OW_YAW, SK_, name="Washstand")'),
    ('put("Porcelain_Doll_Cracked", 2752, 300, GZ + 97, 250, SK_)', 'put("Porcelain_Doll_Cracked", 2752, 250, GZ + 92, 250, SK_)'),
])
edit("import_more.py", [
    ('''    for a in ar.get_assets_by_path("/Game/Fab", recursive=True):
        if str(a.asset_class_path.asset_name) != "StaticMesh":
            continue''', '''    for a in list(ar.get_assets_by_path("/Game/Fab", recursive=True)) + list(ar.get_assets_by_path("/Game/OldWest", recursive=True)):
        if str(a.asset_class_path.asset_name) != "StaticMesh":
            continue'''),
])
print("ok")
