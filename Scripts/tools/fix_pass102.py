"""Pass 102: fetches that send him across the house (Cheyenne 2026-11-19 15:44 to 15:48 UTC).
"The thing to unlock the thing needs to be far enough away that the player is forced to have to go and get it ... a little bit
of a fetch here, fetch here" and "don't make it so easy as 1, 2, 3 ... one of the cool things in Resident Evil is a room where
you need something ... and you might not find that thing for [a long while] ... finding the item before the door ... or an item
they need behind a locked door that requires a different key."

The opening chain (hers):
  - a wall vent in the kitchen, screwed shut, something small caught behind the slats
  - the screwdriver is upstairs, on the table beside the locked jewelry box
  - back down: the screwdriver opens the vent, the small key is on the ledge inside; taking it brings the thump
  - up again (the walk with her at the doorway), the key opens the box: Ruth's letter and the glass eye (used at the very end)

Keys moved away from their locks:
  - the sitting-room key: was in a kitchen drawer across the hall from its door; now a drawer slides open in the upstairs bath
  - the settlers book (desk key): was on a shelf in the den two steps from the desk; now in the front room, the other end of the house
  - the fuse: was in the den beside the pantry; now in the locked sitting room (the lights stay dead until he gets in there)
Objectives no longer say which door a key is for."""
import json, sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit

R = "C:/GameDev/Unreal/WellnessCheck/"

# ---------------------------------------------------------------- models
edit(R + "Scripts/art/build_items.py", [
    ('''build("GlassEye", glasseye)''', '''def screwdriver():
    # an old flat-head lying along X: turned wooden handle, brass ferrule, steel shaft
    P = [cyl(0.0125, 0.085, (-0.0425, 0, 0.0125), (0, math.pi / 2, 0), "Wood", 16)]
    P.append(cyl(0.0105, 0.010, (-0.088, 0, 0.0125), (0, math.pi / 2, 0), "Wood", 16))
    P.append(cyl(0.0135, 0.012, (0.004, 0, 0.0125), (0, math.pi / 2, 0), "Brass", 16))
    P.append(cyl(0.0032, 0.120, (0.068, 0, 0.0125), (0, math.pi / 2, 0), "Steel", 10))
    P.append(box(0.016, 0.0075, 0.0016, (0.134, 0, 0.0125), m="Steel"))
    return P


def vent_parts(frame=True, cover=True):
    # a cast-iron wall register, 36 x 26 cm.  Its back is on y = 0 and it faces -Y.
    W, H = 0.36, 0.26
    P = []
    if frame:
        P.append(box(W - 0.02, 0.004, H - 0.02, (0, -0.002, H / 2), m="Polymer"))                 # the dark of the duct
        P.append(box(W, 0.028, 0.03, (0, -0.014, 0.015), m="Iron", bevel=0.002))
        P.append(box(W, 0.028, 0.03, (0, -0.014, H - 0.015), m="Iron", bevel=0.002))
        P.append(box(0.03, 0.028, H, (-W / 2 + 0.015, -0.014, H / 2), m="Iron", bevel=0.002))
        P.append(box(0.03, 0.028, H, (W / 2 - 0.015, -0.014, H / 2), m="Iron", bevel=0.002))
        P.append(box(W - 0.06, 0.036, 0.004, (0, -0.018, 0.032), m="Iron"))                       # the ledge the key lies on
    if cover:
        y = -0.0315
        P.append(box(W - 0.012, 0.005, 0.024, (0, y, 0.018), m="Iron", bevel=0.001))
        P.append(box(W - 0.012, 0.005, 0.024, (0, y, H - 0.018), m="Iron", bevel=0.001))
        P.append(box(0.024, 0.005, H - 0.012, (-W / 2 + 0.018, y, H / 2), m="Iron", bevel=0.001))
        P.append(box(0.024, 0.005, H - 0.012, (W / 2 - 0.018, y, H / 2), m="Iron", bevel=0.001))
        for i in range(8):
            P.append(box(W - 0.05, 0.016, 0.003, (0, y + 0.004, 0.046 + i * 0.024), (math.radians(40), 0, 0), "Iron"))
        for sx in (-1, 1):
            for z in (0.018, H - 0.018):
                P.append(cyl(0.0055, 0.004, (sx * (W / 2 - 0.018), y - 0.004, z), (math.pi / 2, 0, 0), "Steel", 10))
    if frame and cover:
        P.append(box(0.034, 0.006, 0.004, (0.03, -0.016, 0.037), m="Brass"))                      # what glints behind the slats
    return P


def vent_cover_flat():
    # the cover taken off and laid on the floor, face up
    P = vent_parts(frame=False, cover=True)
    for p in P:
        p.rotation_euler = (-math.pi / 2, 0, 0)
        bpy.ops.object.select_all(action="DESELECT")
        p.select_set(True)
        bpy.context.view_layer.objects.active = p
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    return P


build("Screwdriver", screwdriver)
build("Vent", vent_parts)
build("VentOpen", lambda: vent_parts(True, False))
build("VentCoverFlat", vent_cover_flat)
build("GlassEye", glasseye)'''),
])

# ---------------------------------------------------------------- the level
VX, VY, VZ = 1400, 217.9, "GZ + 112"
edit(R + "Scripts/level/build_house.py", [
    # the kitchen dresser is only a dresser now
    ('''place("Dresser_Drawers", 1560, 300, GZ, 270, K, tags=["Hide_drawer"])
place("Dresser_Drawers_Open", 1548, 300, GZ, 270, K, tags=["Show_drawer"])''',
     '''place("Dresser_Drawers", 1560, 300, GZ, 270, K)'''),
    # the small key: no longer lying on the counter, but behind a wall vent that is screwed shut
    ('''# the small key: on the counter by the sink.  Taking it is what brings the thump upstairs.
pickup("pick_key_box", "key_box", "Small key", ("Key", CUBE, (0.05, 0.018, 0.005), {0: "BrassOld"}), 872, 556, GZ + 96, 35, grab=(11, 11, 7))''',
     f'''# the wall vent on the hall side of the kitchen: screwed shut, and something small is caught behind the slats.
# The screwdriver is upstairs beside the jewelry box; the small key is on the ledge inside.  Taking the key brings the thump.
interact("WCUsable", "vent", ITEM("Vent"), {VX}, {VY}, {VZ}, 0, "Wall vent", (22, 9, 15), (0, 0, 13))
if ITEM("VentOpen"):
    place(ITEM("VentOpen"), {VX}, {VY}, {VZ}, 0, K, name="VentOpen", tags=["Show_vent"], collide=False)
if ITEM("VentCoverFlat"):
    place(ITEM("VentCoverFlat"), {VX} - 22, 262, GZ + 0.4, 24, K, name="VentCoverOff", tags=["Show_vent"], collide=False)
pickup("pick_key_box", "key_box", "Small key", ("Key", CUBE, (0.05, 0.018, 0.005), {{0: "BrassOld"}}), {VX} - 2, {VY}, {VZ} + 3.7, 0, grab=(11, 9, 6), tags=["Show_ventkey"])'''),
    ('''pickup("pick_key_sitting", "key_sitting", "Small brass key", ("Key", CUBE, (0.07, 0.022, 0.006), {0: "BrassOld"}), 1530, 300, GZ + 97, 20, tags=["Show_drawer"])
''', ''''''),
    # the fuse: in her sitting room, behind its lock
    ('''note("note_deskkey", "Letters_Scattered", 1492, -377, GZ + 101.5, 20, scale=0.45, grab=(10, 10, 5))''',
     '''note("note_deskkey", "Letters_Scattered", 1492, -377, GZ + 101.5, 20, scale=0.45, grab=(10, 10, 5))
# the spare fuse is in here (it used to lie in the den, next door to the fuse box): the lights stay dead until he gets in
place(TABLE, 1010, -545, GZ, 0, S)
pickup("pick_fuse", "fuse", "Spare fuse", ("Fuse", CYL, (0.03, 0.03, 0.075), {0: "Glass"}), 1010, -545, GZ + 98.6, 0, grab=(10, 10, 10))'''),
    # the screwdriver, beside the jewelry box
    ('''pickup("pick_keep_eye", "keep_eye", "Glass eye",''',
     '''pickup("pick_screwdriver", "screwdriver", "Screwdriver", ("Screwdriver", CUBE, (0.2, 0.02, 0.02), {0: "Iron"}), 724, 311, UZ + 98.4, 100, grab=(13, 13, 7))
pickup("pick_keep_eye", "keep_eye", "Glass eye",'''),
    # the drawer that slides open after the telephone: upstairs, in the bathroom
    ('''place("Privacy_Screen_Torn", 880, -330, UZ, 70, B)''',
     '''place("Privacy_Screen_Torn", 880, -330, UZ, 70, B)
# the drawer that is found open after the telephone (it was in the kitchen, across the hall from the door its key opens)
place("Dresser_Drawers", 1380, -256, UZ, 0, B, tags=["Hide_drawer"])
place("Dresser_Drawers_Open", 1380, -268, UZ, 0, B, tags=["Show_drawer"])
pickup("pick_key_sitting", "key_sitting", "Small brass key", ("Key", CUBE, (0.07, 0.022, 0.006), {0: "BrassOld"}), 1380, -286, UZ + 97, 110, tags=["Show_drawer"])
point("DrawerPoint", 1380, -268, UZ + 60)'''),
    # the front room: the armchair makes way for the bookshelf
    ('''place("Armchair_Wingback_Torn", 545, -265, GZ, 205, L)''', '''place("Armchair_Wingback_Torn", 105, -535, GZ, 45, L)            # in the corner by the piano: the bookshelf wall is kept clear'''),
    ('''place("Armchair_Tipped", 615, -415, GZ, 120, L)''', '''place("Armchair_Tipped", 715, -390, GZ, 120, L)'''),
    ('''("A_Prayer", 1150, 330, UZ, 60),''', '''("A_Prayer", 1150, 330, UZ, 60), ("A_UpBath", 1300, -400, UZ, 250), ("A_Book", 610, -292, GZ, 100), ("A_HallSit", 1390, -90, GZ, 250),'''),
])
edit(R + "Scripts/level/ell.py", [
    ('''put_pickup("pick_fuse", "fuse", "Spare fuse", ("Fuse", CYL, (0.03, 0.03, 0.075), {0: "Glass"}), 2352, -250, GZ + 132, 0, grab=(10, 10, 10))
''', '''# (the spare fuse is in her sitting room now: build_house.py)
'''),
    ('''"key_attic", "Attic key",''', '''"key_attic", "Long key",'''),
])
edit(R + "Scripts/level/watchers.py", [
    ('''BKX0, BKX1, BKY, BKZ = 2168.0, 2322.0, -216.0, GZ + 104.0           # a shelf on the hall-side wall of the den''',
     '''BKX0, BKX1, BKY, BKZ = 470.0, 624.0, -216.0, GZ + 104.0             # a shelf on the hall-side wall of the front room (it was in the den, beside the desk its key opens)'''),
])
p = R + "Scripts/level/notes.json"
d = json.load(open(p, encoding="utf-8"))
d["note_deskkey"]["body"] = ("W. keeps the key to his desk in the settlers book.\n\nThe one on the shelf in the front room, with the county histories. "
                             "He cut the middle out of it with his razor.\n\nHe thinks I do not know.\n\nI know where everything in this house is. I am in all of it now.")
json.dump(d, open(p, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)

# ---------------------------------------------------------------- the game
edit(R + "Source/WellnessCheck/WCGame.cpp", [
    ('''{ TEXT("key_box"), TEXT("Small key"),''', '''{ TEXT("screwdriver"), TEXT("Screwdriver"), TEXT("A flat-head with a turned wooden handle. The tip is bright: somebody has used it not long ago."), TEXT("/Game/WC/Props/SM_Item_Screwdriver.SM_Item_Screwdriver") },
		{ TEXT("key_box"), TEXT("Small key"),'''),
    ('''{ TEXT("key_attic"), TEXT("Attic key"), TEXT("It was in Daniel's room, kept where a boy keeps things. The attic door."),''',
     '''{ TEXT("key_attic"), TEXT("Long key"), TEXT("It was in Daniel's room, kept where a boy keeps things. Long, with a paper tag too worn to read."),'''),
    ('''{ TEXT("key_attic"), TEXT("Attic key") }''', '''{ TEXT("key_attic"), TEXT("Long key") }'''),
    ('''if (Id == TEXT("fuse")) { if (F && F->WCId == TEXT("fusebox")) OnWhatHeFaces();''',
     '''if (Id == TEXT("screwdriver")) { if (F && F->WCId == TEXT("vent")) OnWhatHeFaces(); else InvSay(TEXT("Nothing here to unscrew.")); return; }
	if (Id == TEXT("fuse")) { if (F && F->WCId == TEXT("fusebox")) OnWhatHeFaces();'''),
])
edit(R + "Source/WellnessCheck/WCStory.cpp", [
    ('''if (Is(Id, TEXT("take:key_box"))) { UpstairsThump(); return; }''',
     '''if (Is(Id, TEXT("take:key_box"))) { UpstairsThump(); return; }
	// the kitchen wall vent: screwed shut until he brings the screwdriver down from her bedroom
	if (Is(Id, TEXT("use:vent")))
	{
		if (Has(TEXT("vent_open"))) return;
		if (!HasItem(TEXT("screwdriver")))
		{
			if (Clock > SpeechFreeAt) { SpeechFreeAt = Clock + 3.0; Feedback(TEXT("Screwed shut. Something small is caught behind the slats.")); PlayAt(TEXT("door_locked"), P->GetActorLocation(), 0.4f, 1.7f, 600.f); }
			if (!Has(TEXT("vent_seen"))) { Set(TEXT("vent_seen")); if (!Has(TEXT("heard_upstairs"))) SetObjective(TEXT("Search the house. Something is behind the kitchen vent.")); }
			return;
		}
		Items.Remove(TEXT("screwdriver"));
		Set(TEXT("vent_seen"));
		Set(TEXT("vent_open"));
		UE_LOG(LogWCStory, Display, TEXT("WCVENT t=%.1f opened (%.0f s after coming in)"), PlaySeconds, PlaySeconds - InsideAt);
		for (int32 i = 0; i < 4; ++i) After(0.1f + i * 0.38f, [this, i]() { Play2D(TEXT("switch_click"), 0.45f, EWCSnd::SFX, 0.62f + 0.05f * i); });
		After(1.75f, [this]() { Play2D(TEXT("door_unlock"), 0.5f, EWCSnd::SFX, 0.75f); ApplyWorldState(); });
		return;
	}
	if (Is(Id, TEXT("take:screwdriver")))
	{
		if (Has(TEXT("vent_seen")) && !Has(TEXT("vent_open")) && !Has(TEXT("heard_upstairs"))) SetObjective(TEXT("Search the house. The kitchen vent."));
		return;
	}'''),
    ('''ShowTagged(TEXT("Show_jewel"), Has(TEXT("box_open")));''', '''ShowTagged(TEXT("Show_jewel"), Has(TEXT("box_open")));
	ShowTagged(TEXT("Show_vent"), Has(TEXT("vent_open")));
	ShowTagged(TEXT("Show_ventkey"), Has(TEXT("vent_open")) && !Has(TEXT("heard_upstairs")));
	if (AWCInteractable* Vt = Thing(TEXT("vent"))) { Vt->SetActorHiddenInGame(Has(TEXT("vent_open"))); Vt->SetActorEnableCollision(!Has(TEXT("vent_open"))); Vt->bEnabled = !Has(TEXT("vent_open")); }'''),
    ('''After(T2, [this]() { SetObjective(TEXT("Search the kitchen")); Checkpoint(TEXT("phone_done")); });''',
     '''After(T2, [this]()
								{
									// somewhere above him a drawer is pulled open (its key is no longer in the kitchen)
									PlayAt(TEXT("drag_floor"), Pos(TEXT("DrawerPoint")), 1.f, 1.5f, 4500.f);
									SetObjective(TEXT("Something slid open upstairs"));
									Checkpoint(TEXT("phone_done"));
								});'''),
    ('''SetObjective(TEXT("Upstairs: the locked room"));''', '''SetObjective(TEXT("Find what the iron key opens"));'''),
])
edit(R + "Source/WellnessCheck/WCHouse.cpp", [
    ('''SetObjective(TEXT("Upstairs: the locked back rooms"));''', '''SetObjective(TEXT("Find what Walter's keys open"));'''),
    ('''SetObjective(TEXT("The attic"));''', '''SetObjective(TEXT("Find what the long key opens"));'''),
    ('''UpstairsThump();                                     // as if he had just taken the small key''',
     '''if (!HasItem(TEXT("key_box")) && !Has(TEXT("box_open"))) GiveItem(TEXT("key_box"), TEXT("Small key"));
				UpstairsThump();                                     // as if he had just taken the small key'''),
])

# ---------------------------------------------------------------- the test bot plays it the new way
edit(R + "Source/WellnessCheck/WCAuto.cpp", [
    ('''Shot(TEXT("08_kitchen")); Use(TEXT("phone")); Wait(3.f);''',
     '''Shot(TEXT("08_kitchen")); Use(TEXT("phone")); Wait(3.f); Use(TEXT("vent")); Flag(TEXT("vent_seen"), 4.f); Shot(TEXT("08a_vent_screwed_shut"));'''),
    ('''Shot(TEXT("08c_den")); Use(TEXT("pick_fuse")); Use(TEXT("desk"));''', '''Shot(TEXT("08c_den")); Use(TEXT("desk"));'''),
    ('''Go(TEXT("A_Kitchen")); Use(TEXT("pick_key_box")); Flag(TEXT("heard_upstairs"), 10.f); Wait(14.f);''',
     '''Go(TEXT("A_StairsTop")); Go(TEXT("A_Master")); Use(TEXT("jewelbox")); Wait(1.f); Shot(TEXT("08f_box_locked_screwdriver")); Use(TEXT("pick_screwdriver")); Wait(0.5f);
	Go(TEXT("A_StairsTop")); Go(TEXT("A_Kitchen")); Use(TEXT("vent")); Flag(TEXT("vent_open"), 6.f); Wait(2.4f); Shot(TEXT("08g_vent_open_key"));
	Use(TEXT("pick_key_box")); Flag(TEXT("heard_upstairs"), 10.f); Wait(14.f);'''),
    ('''Use(TEXT("pick_key_sitting")); Use(TEXT("sitting")); Wait(3.f);''',
     '''Go(TEXT("A_StairsTop")); Go(TEXT("A_UpBath")); Wait(1.f); Shot(TEXT("15b_drawer_open_upstairs")); Use(TEXT("pick_key_sitting"));
	Go(TEXT("A_StairsTop")); Go(TEXT("A_HallSit")); Use(TEXT("sitting")); Wait(3.f);'''),
    ('''Use(TEXT("pick_key_prayer")); Use(TEXT("note_deskkey")); Wait(1.f); Close();
	Go(TEXT("A_Den")); Use(TEXT("book_settlers"));''',
     '''Use(TEXT("pick_key_prayer")); Use(TEXT("note_deskkey")); Wait(1.f); Close(); Use(TEXT("pick_fuse"));
	Go(TEXT("A_Pantry")); Use(TEXT("fusebox")); Flag(TEXT("fuse_done"), 4.f); Wait(2.f); Shot(TEXT("16a_fuse_in"));
	Go(TEXT("A_Book")); Use(TEXT("book_settlers"));'''),
    ('''Use(TEXT("pick_key_desk")); Use(TEXT("desk")); Flag(TEXT("desk_open"), 6.f);''',
     '''Use(TEXT("pick_key_desk")); Go(TEXT("A_Den")); Use(TEXT("desk")); Flag(TEXT("desk_open"), 6.f);'''),
])
print("pass 102 applied")
