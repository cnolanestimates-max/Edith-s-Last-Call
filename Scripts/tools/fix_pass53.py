"""The small carried things become real little models (keys, key ring, wedding ring, fuse, shears) in the world too,
and the import script learns the "items" step."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
L = "C:/GameDev/Unreal/WellnessCheck/Scripts/level/"
edit(L + "import_assets.py", [
    ('''exec(open(ROOT + "/Scripts/level/import_variants.py", encoding="utf-8").read())''',
     '''exec(open(ROOT + "/Scripts/level/import_variants.py", encoding="utf-8").read())
exec(open(ROOT + "/Scripts/level/import_items.py", encoding="utf-8").read())'''),
    ('''("variants", step_variants), ("drawings", step_drawings)):''', '''("variants", step_variants), ("drawings", step_drawings), ("items", step_items)):'''),
])
edit(L + "build_house.py", [
    ('''def pickup(wid, item, display, mesh, x, y, z, yaw=0.0, scale=1.0, grab=(12, 12, 8), tags=(), mats=None):''',
     '''def ITEM(name, fallback=None):
    """One of the small carried models (Scripts/art/build_items.py), or the plain shape it replaces if it is not imported yet."""
    p = f"{G}/Props/SM_Item_{name}"
    return asset(p) if eal.does_asset_exist(p) else fallback


def pickup(wid, item, display, mesh, x, y, z, yaw=0.0, scale=1.0, grab=(12, 12, 8), tags=(), mats=None):
    if isinstance(mesh, tuple):          # (item model name, plain fallback mesh, fallback scale, fallback mats)
        real = ITEM(mesh[0])
        mesh, scale, mats = (real, 1.0, None) if real else (mesh[1], mesh[2], mesh[3])'''),
    ('''pickup("pick_key_sitting", "key_sitting", "Small brass key", CUBE, 1530, 300, GZ + 97, 20, (0.07, 0.022, 0.006), tags=["Show_drawer"], mats={0: "BrassOld"})''',
     '''pickup("pick_key_sitting", "key_sitting", "Small brass key", ("Key", CUBE, (0.07, 0.022, 0.006), {0: "BrassOld"}), 1530, 300, GZ + 97, 20, tags=["Show_drawer"])'''),
    ('''pickup("pick_key_prayer", "key_prayer", "Iron key on a ribbon", CUBE, 1510, -450, GZ + 102, 70, (0.08, 0.024, 0.006), mats={0: "Iron"})''',
     '''pickup("pick_key_prayer", "key_prayer", "Iron key on a ribbon", ("KeyIron", CUBE, (0.08, 0.024, 0.006), {0: "Iron"}), 1510, -450, GZ + 102, 70)'''),
    ('''pickup("pick_keep_walter", "keep_walter", "Walter's wedding ring", CYL, 1180, 535, UZ + 102, 0, (0.022, 0.022, 0.006), mats={0: "Gold"})''',
     '''pickup("pick_keep_walter", "keep_walter", "Walter's wedding ring", ("Ring", CYL, (0.022, 0.022, 0.006), {0: "Gold"}), 1180, 535, UZ + 102, 0)'''),
])
edit(L + "ell.py", [
    ('''put_pickup("pick_fuse", "fuse", "Spare fuse", CYL, 2352, -250, GZ + 132, 0, (0.03, 0.03, 0.075), grab=(10, 10, 10), mats={0: "Glass"})''',
     '''put_pickup("pick_fuse", "fuse", "Spare fuse", ("Fuse", CYL, (0.03, 0.03, 0.075), {0: "Glass"}), 2352, -250, GZ + 132, 0, grab=(10, 10, 10))'''),
    ('''put_pickup("pick_key_attic", "key_attic", "Attic key", CUBE, 1686, -372, UZ + 78, 110, (0.075, 0.022, 0.006), mats={0: "BrassOld"})''',
     '''put_pickup("pick_key_attic", "key_attic", "Attic key", ("Key", CUBE, (0.075, 0.022, 0.006), {0: "BrassOld"}), 1686, -372, UZ + 78, 110)'''),
    ('''put_pickup("pick_shears", "shears", "Sewing shears", CUBE, 2456, -492, UZ + 74, 35, (0.21, 0.035, 0.008), grab=(14, 14, 9), mats={0: "Iron"})''',
     '''put_pickup("pick_shears", "shears", "Sewing shears", ("Shears", CUBE, (0.21, 0.035, 0.008), {0: "Iron"}), 2456, -492, UZ + 74, 35, grab=(14, 14, 9))'''),
])
edit(L + "watchers.py", [
    ('''pickup("pick_key_desk", "key_desk", "Small desk key", CUBE, SETTLERS_X + 8, BKY - 52, GZ + 2.0, 35, (0.05, 0.018, 0.005), tags=["Show_bookkey"], mats={0: "BrassOld"})''',
     '''pickup("pick_key_desk", "key_desk", "Small desk key", ("Key", CUBE, (0.05, 0.018, 0.005), {0: "BrassOld"}), SETTLERS_X + 8, BKY - 52, GZ + 2.0, 35, tags=["Show_bookkey"])'''),
])
print("ok")
