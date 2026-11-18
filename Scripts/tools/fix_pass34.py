"""Level side of the watchers and the book: class, module hook, the hint note in her sitting room (replaces the loose desk key), hair material."""
import json, sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
L = "C:/GameDev/Unreal/WellnessCheck/Scripts/level/"
R = "C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/"
edit(L + "build_house.py", [
    ('''"WCTrigger", "WCEntity", "WCLook"):''', '''"WCTrigger", "WCEntity", "WCLook", "WCWatcher"):'''),
    ('''pickup("pick_key_desk", "key_desk", "Small desk key", CUBE, 1488, -372, GZ + 102, 20, (0.045, 0.016, 0.005), mats={0: "BrassOld"})''',
     '''note("note_deskkey", "Letters_Scattered", 1488, -372, GZ + 101.5, 20, scale=0.55)'''),
    ('''exec(open(os.path.join(HERE, "settle.py"), encoding="utf-8").read())''', '''exec(open(os.path.join(HERE, "watchers.py"), encoding="utf-8").read())
exec(open(os.path.join(HERE, "settle.py"), encoding="utf-8").read())'''),
])
edit(L + "import_assets.py", [
    ('''    flat_material("M_EyeBlack", (0.002, 0.002, 0.002), 0.05)''', '''flat_material("M_Hair", (0.36, 0.33, 0.27), 0.55)
    flat_material("M_EyeBlack", (0.002, 0.002, 0.002), 0.05)'''),
])
P = L + "notes.json"
n = json.load(open(P, encoding="utf-8"))
n["note_deskkey"] = {"title": "A scrap in her hand, folded small", "style": 1, "body":
                     "W. keeps the key to his desk in the settlers book.\n\nThe one on the shelf in his den. He cut the middle out of it with his razor.\n\n"
                     "He thinks I do not know.\n\nI know where everything in this house is. I am in all of it now."}
json.dump(n, open(P, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
# bot: read the scrap, pull the book (S10), take the key
edit(R + "WCAuto.cpp", [
    ('''	Use(TEXT("pick_key_prayer")); Use(TEXT("pick_key_desk"));
	Use(TEXT("desk")); Flag(TEXT("desk_open"), 6.f); Wait(2.f);''', '''Use(TEXT("pick_key_prayer")); Use(TEXT("note_deskkey")); Wait(1.f); Close();
	Go(TEXT("A_Den")); Use(TEXT("book_settlers")); Flag(TEXT("book_done"), 6.f); Wait(0.9f); Shot(TEXT("16b_S10_book_eye")); Wait(3.f); Shot(TEXT("16c_S10_after"));
	Use(TEXT("pick_key_desk")); Use(TEXT("desk")); Flag(TEXT("desk_open"), 6.f); Wait(2.f);'''),
])
print("ok")
