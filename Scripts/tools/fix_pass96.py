"""Pass 96: everything he takes is a thing lying in the world (Cheyenne 2026-11-19 14:45 UTC: "it's not just text ... appearing in
your inventory ... I actually want there to be a thing that we're picking up").
The three gaps:
  - Walter's keys: opening his desk used to put them straight in the inventory.  Now the desk shows the key ring and a box of
    cartridges lying in it, and he takes them.
  - Daniel's dog tags and the padlock key: opening the footlocker used to hand over both.  Now they lie on it; taking the tags
    is what sets the attic scare going.
  - the cartridge boxes were plain cardboard blocks: a modelled box with the rounds showing (Blender, build_items.py)."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit

R = "C:/GameDev/Unreal/WellnessCheck/"

# ---------------------------------------------------------------- the model
edit(R + "Scripts/art/build_items.py", [
    ('"Wood": (0.2, 0.11, 0.06, 1), "Screen": (0.03, 0.04, 0.04, 1)}',
     '"Wood": (0.2, 0.11, 0.06, 1), "Screen": (0.03, 0.04, 0.04, 1),\n       "Card": (0.30, 0.22, 0.13, 1), "Label": (0.30, 0.05, 0.04, 1)}'),
    ('b.inputs["Metallic"].default_value = 0.0 if name in ("Glass", "Ceramic", "Ribbon", "Polymer", "Wood", "Screen") else 1.0',
     'b.inputs["Metallic"].default_value = 0.0 if name in ("Glass", "Ceramic", "Ribbon", "Polymer", "Wood", "Screen", "Card", "Label") else 1.0'),
    ('build("TV", tv)', '''def ammobox():
    # a box of pistol cartridges with the flap torn off: card tray, a printed band round it, the brass heads of the rounds showing
    P = [box(0.110, 0.070, 0.044, (0, 0, 0.022), m="Card", bevel=0.0012)]
    P.append(box(0.1106, 0.0706, 0.020, (0, 0, 0.018), m="Label"))
    P.append(box(0.100, 0.060, 0.002, (0, 0, 0.0435), m="Polymer"))                       # the dark of the tray between the rounds
    for i in range(7):
        for j in range(4):
            if (i, j) in ((6, 3), (5, 3), (6, 2)):
                continue                                                               # a few already used
            x, y = -0.0405 + i * 0.0135, -0.0205 + j * 0.0137
            P.append(cyl(0.0052, 0.006, (x, y, 0.0455), m="Brass", v=14))
            P.append(cyl(0.0019, 0.0064, (x, y, 0.0457), m="Steel", v=8))
    P.append(box(0.108, 0.030, 0.0009, (0.004, 0.052, 0.0005), (0, 0, 0.12), "Card"))    # the torn flap lying beside it
    return P


build("AmmoBox", ammobox)
build("TV", tv)'''),
])
edit(R + "Scripts/level/import_items.py", [
    ('''"Screen": tv_material(),''', '''"Screen": tv_material(),
        "Card": item_material("M_ItemCard", (0.085, 0.062, 0.036), 0.9, 0.0),
        "Label": item_material("M_ItemLabel", (0.070, 0.012, 0.010), 0.75, 0.0),'''),
])

# ---------------------------------------------------------------- the level
edit(R + "Scripts/level/ell.py", [
    ('''a = put_pickup("pick_" + wid, wid, "Box of cartridges", CUBE, x, y, zhint + 3.0, yaw, (0.11, 0.07, 0.055), grab=(12, 12, 9), mats={0: surf("Cardboard", "MI_Cardboard")})
    return a''', '''real = ITEM("AmmoBox")
    a = put_pickup("pick_" + wid, wid, "Box of cartridges", ("AmmoBox", CUBE, (0.11, 0.07, 0.055), {0: surf("Cardboard", "MI_Cardboard")}), x, y,
                   zhint + (0.0 if real else 3.0), yaw, grab=(12, 12, 9), **kw)
    return a'''),
    ('def ammo(wid, x, y, zhint, yaw=0.0):', 'def ammo(wid, x, y, zhint, yaw=0.0, **kw):'),
    ('''place("Chair_Dining_HighBack", 2255, -330, GZ, 90, DN)''', '''place("Chair_Dining_HighBack", 2255, -330, GZ, 90, DN)
# what is in the desk, seen once it is open: Walter's key ring and a box of his cartridges (they used to go straight into the inventory)
put_pickup("pick_key_ell", "key_ell", "Walter's keys", ("Keyring", CUBE, (0.06, 0.05, 0.006), {0: "Iron"}), 2312, -352, GZ + 78, 25, grab=(11, 11, 7), tags=["Show_desk"])
ammo("ammo_desk", 2314, -306, GZ + 78, 70, tags=["Show_deskammo"])'''),
])
edit(R + "Scripts/level/build_house.py", [
    ('''interact("WCUsable", "trunk", "Chest_Trunk", 760, -430, AZ, 90, "Open the footlocker", (50, 30, 36), (0, 0, 36))''',
     '''interact("WCUsable", "trunk", "Chest_Trunk", 760, -430, AZ, 90, "Open the footlocker", (50, 30, 36), (0, 0, 36))
# what was in it, laid out on the lid once it has been opened (they used to go straight into the inventory)
_tb = kit("Chest_Trunk").get_bounds()
_ttop = AZ + _tb.origin.z + _tb.box_extent.z
log(f"footlocker lid at z {_ttop:.0f}")
pickup("pick_keep_daniel", "keep_daniel", "Daniel's dog tags", ("Tags", CUBE, (0.05, 0.03, 0.004), {0: "Iron"}), 752, -444, _ttop + 0.8, 20, grab=(11, 11, 7), tags=["Show_trunktags"])
pickup("pick_key_cellar", "key_cellar", "Padlock key", ("KeyIron", CUBE, (0.08, 0.024, 0.006), {0: "Iron"}), 770, -416, _ttop + 0.8, 110, grab=(11, 11, 7), tags=["Show_trunkkey"])'''),
])

# ---------------------------------------------------------------- the game
edit(R + "Source/WellnessCheck/WCHouse.cpp", [
    ('''After(0.9f, [this]()
		{
			GiveItem(TEXT("key_ell"), TEXT("Walter's keys"));
			if (AWCCharacter* Pl = Player()) Pl->Reserve += 8;
			Think(TEXT("Walter's key ring. Upstairs, the back rooms. And a box of his cartridges."));
			if (!Has(TEXT("placed"))) SetObjective(TEXT("Upstairs: the locked back rooms"));
			Checkpoint(TEXT("desk"));
		});
		return true;''', '''// the roll-top is open: his key ring and a box of cartridges are lying in it, for him to take
		After(0.5f, [this]() { ApplyWorldState(); });
		return true;'''),
    ('''if (S.StartsWith(TEXT("take:ammo")))
	{''', '''if (Id == TEXT("take:key_ell"))
	{
		if (!Has(TEXT("placed"))) SetObjective(TEXT("Upstairs: the locked back rooms"));
		Checkpoint(TEXT("desk"));
		return true;
	}
	if (S.StartsWith(TEXT("take:ammo")))
	{
		if (Id == TEXT("take:ammo_desk")) Set(TEXT("desk_ammo"));'''),
])
edit(R + "Source/WellnessCheck/WCStory.cpp", [
    ('''ShowTagged(TEXT("Show_bookkey"), Has(TEXT("book_done")) && !HasItem(TEXT("key_desk")) && !Has(TEXT("desk_open")));''',
     '''ShowTagged(TEXT("Show_bookkey"), Has(TEXT("book_done")) && !HasItem(TEXT("key_desk")) && !Has(TEXT("desk_open")));
	ShowTagged(TEXT("Show_desk"), Has(TEXT("desk_open")) && !HasItem(TEXT("key_ell")));
	ShowTagged(TEXT("Show_deskammo"), Has(TEXT("desk_open")) && !Has(TEXT("desk_ammo")));
	ShowTagged(TEXT("Show_trunktags"), Has(TEXT("attic_started")) && !HasItem(TEXT("keep_daniel")));
	ShowTagged(TEXT("Show_trunkkey"), Has(TEXT("attic_started")) && !HasItem(TEXT("key_cellar")));'''),
    ('''Play2D(TEXT("trunk_open"), 0.9f);
	GiveItem(TEXT("keep_daniel"), TEXT("Daniel's dog tags"));
	float T = Say(TEXT("d_attic"), 0.6f);
	T = Say(TEXT("d_tags"), T + 0.4f);
	After(T, [this]() { GiveItem(TEXT("key_cellar"), TEXT("Padlock key")); });
	After(T + 1.4f, [this]()
	{''', '''Play2D(TEXT("trunk_open"), 0.9f);
	// the tags and the padlock key are lying on it now, for him to take; taking the tags is what she cannot bear
	After(0.5f, [this]() { ApplyWorldState(); });
}

void AWCDirector::AtticTagsTaken()
{
	if (Has(TEXT("attic_tags"))) return;
	Set(TEXT("attic_tags"));
	After(1.4f, [this]()
	{'''),
    ('''if (Is(Id, TEXT("take:key_sitting"))) { SetObjective(TEXT("Find what the key opens")); return; }''',
     '''if (Is(Id, TEXT("take:key_sitting"))) { SetObjective(TEXT("Find what the key opens")); return; }
	if (Is(Id, TEXT("take:keep_daniel"))) { AtticTagsTaken(); return; }'''),
])
edit(R + "Source/WellnessCheck/WCDirector.h", [
    ('void TickTV(float Dt);', 'void TickTV(float Dt);\n\tvoid AtticTagsTaken();'),
])
edit(R + "Source/WellnessCheck/WCAuto.cpp", [
    ('Use(TEXT("pick_key_desk")); Use(TEXT("desk")); Flag(TEXT("desk_open"), 6.f); Wait(2.f);',
     'Use(TEXT("pick_key_desk")); Use(TEXT("desk")); Flag(TEXT("desk_open"), 6.f); Wait(2.f); Shot(TEXT("16b_desk_open_keys")); Use(TEXT("pick_key_ell")); Use(TEXT("pick_ammo_desk")); Wait(1.f);'),
    ('Use(TEXT("trunk")); Flag(TEXT("attic_started"), 5.f);',
     'Use(TEXT("trunk")); Flag(TEXT("attic_started"), 5.f); Wait(1.2f); Shot(TEXT("22b_footlocker_tags_key")); Use(TEXT("pick_key_cellar")); Use(TEXT("pick_keep_daniel"));'),
])
print("pass 96 applied")
