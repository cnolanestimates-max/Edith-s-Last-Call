"""Pass 103: the rag doll and Inspect; the detailed item models; a black screen after her memories.

Cheyenne 2026-11-19 15:54 and 15:59 UTC:
  "whatever items you add now with this new fetch stuff please give them good assets, model them in blender ... the items you
   actually get to pick up are usually very detailed and intricate, even the little keys"
  "the inspect feature needs to come into play for a few items ... you inspect them and turn them over ... and bam a different
   item is inside them ... on the back of the toy there could be a slit and inside will be a key the player needs"

  - behind the kitchen vent is a rag doll, not a bare key.  Turned over in Inspect, the seam down her back shows; E works the
    small key out of the stuffing (the doll stays, emptied).  That is what brings the thump.
  - every key has its own model (heart bow, scrolled brass, barrel desk key, long tagged key, ribboned iron key, flat padlock key)
  - the fine models and their baked textures (Scripts/art/build_items_fine.py) are imported over the plain ones
  - item descriptions no longer say which door a key is for
  - FOUND IN THE BOT RUN: after one of her memories the picture stayed black until something else faded it in (minutes, after
    the telephone).  The memory now fades back in itself."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit

R = "C:/GameDev/Unreal/WellnessCheck/"

# ---------------------------------------------------------------- import: fine models over plain ones, with their textures
edit(R + "Scripts/level/import_items.py", [
    ('''def step_items():''', '''def fine_material(name, tdir):
    """One baked item (build_items_fine.py): base colour, normal, and occlusion / roughness / metal in one map."""
    files = [f"{tdir}/T_Item_{name}_{k}.png" for k in ("C", "N", "ORM")]
    if not all(os.path.isfile(f) for f in files):
        return None
    D = G + "/Props/Tex"
    eal.make_directory(D)
    import_files(files, D)
    c = tex_settings(f"{D}/T_Item_{name}_C", True)
    n = tex_settings(f"{D}/T_Item_{name}_N", False, normal=True)
    o = tex_settings(f"{D}/T_Item_{name}_ORM", False)
    if not (c and n and o):
        return None
    n.set_editor_property("flip_green_channel", True)            # Blender bakes +Y normals
    eal.save_loaded_asset(n, False)
    m = new_material("M_Item_" + name)
    tb = mel.create_material_expression(m, unreal.MaterialExpressionTextureSample, -700, -200)
    tb.set_editor_property("texture", c)
    mel.connect_material_property(tb, "RGB", unreal.MaterialProperty.MP_BASE_COLOR)
    tn = mel.create_material_expression(m, unreal.MaterialExpressionTextureSample, -700, 60)
    tn.set_editor_property("texture", n)
    tn.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_NORMAL)
    mel.connect_material_property(tn, "RGB", unreal.MaterialProperty.MP_NORMAL)
    to = mel.create_material_expression(m, unreal.MaterialExpressionTextureSample, -700, 320)
    to.set_editor_property("texture", o)
    to.set_editor_property("sampler_type", unreal.MaterialSamplerType.SAMPLERTYPE_MASKS)
    mel.connect_material_property(to, "G", unreal.MaterialProperty.MP_ROUGHNESS)
    mel.connect_material_property(to, "B", unreal.MaterialProperty.MP_METALLIC)
    mel.recompile_material(m)
    eal.save_loaded_asset(m, False)
    return m


def step_items():'''),
    ('''    for f in sorted(os.listdir(d)):
        if not f.lower().endswith(".fbx"):
            continue
        name = f[:-4]
        t = unreal.AssetImportTask()
        t.set_editor_property("filename", f"{d}/{f}")''', '''    # the fine versions (real detail, baked wear) replace the plain ones of the same name
    fbx = {}
    for dd in (d, SRC + "/Props/items_fine"):
        if os.path.isdir(dd):
            for f in sorted(os.listdir(dd)):
                if f.lower().endswith(".fbx"):
                    fbx[f[:-4]] = dd
    for name, dd in sorted(fbx.items()):
        fine = dd.endswith("items_fine")
        t = unreal.AssetImportTask()
        t.set_editor_property("filename", f"{dd}/{name}.fbx")'''),
    ('''        slots = []
        for i, sm_mat in enumerate(sm.static_materials):''', '''        slots = []
        fm = fine_material(name[len("SM_Item_"):], dd + "/tex") if fine else None
        if fm:
            for i in range(len(sm.static_materials)):
                sm.set_material(i, fm)
            slots.append("fine, textured")
        for i, sm_mat in enumerate([] if fm else sm.static_materials):'''),
])

# ---------------------------------------------------------------- the level
edit(R + "Scripts/level/build_house.py", [
    ('''def pickup(wid, item, display, mesh, x, y, z, yaw=0.0, scale=1.0, grab=(12, 12, 8), tags=(), mats=None):''',
     '''def pickup(wid, item, display, mesh, x, y, z, yaw=0.0, scale=1.0, grab=(12, 12, 8), tags=(), mats=None, pitch=0.0, roll=0.0):'''),
    ('''    a = interact("WCPickup", wid, mesh, x, y, z, yaw, "Take", grab, (0, 0, 4), scale, tags, mats=mats)''',
     '''    a = interact("WCPickup", wid, mesh, x, y, z, yaw, "Take", grab, (0, 0, 4), scale, tags, mats=mats, pitch=pitch, roll=roll)'''),
    ('''pickup("pick_key_box", "key_box", "Small key", ("Key", CUBE, (0.05, 0.018, 0.005), {0: "BrassOld"}), 1400 - 2, 217.9, GZ + 112 + 3.7, 0, grab=(11, 9, 6), tags=["Show_ventkey"])''',
     '''# what is behind the cover: a rag doll, pushed into the duct, lying along the ledge with her face to the room.
# The small key is sewn inside her; it is found by turning her over in Inspect.
pickup("pick_doll", "doll", "Rag doll", ("Doll", CUBE, (0.15, 0.09, 0.025), {0: "BrassOld"}), 1400, 216.7, GZ + 112 + 3.5 + 5.0, 0, grab=(10, 6, 4), tags=["Show_ventkey"], roll=90)'''),
    ('''pickup("pick_key_cellar", "key_cellar", "Padlock key", ("KeyIron", CUBE,''', '''pickup("pick_key_cellar", "key_cellar", "Padlock key", ("KeyPadlock", CUBE,'''),
])
edit(R + "Scripts/level/watchers.py", [
    ('''pickup("pick_key_desk", "key_desk", "Small desk key", ("Key", CUBE,''', '''pickup("pick_key_desk", "key_desk", "Small desk key", ("KeyDesk", CUBE,'''),
])
edit(R + "Scripts/level/ell.py", [
    ('''put_pickup("pick_key_attic", "key_attic", "Long key", ("Key", CUBE,''', '''put_pickup("pick_key_attic", "key_attic", "Long key", ("KeyLong", CUBE,'''),
])
p = R + "Scripts/level/settle.py"
s = open(p, encoding="utf-8").read()
assert s.count("_l.z + 6.1") == 2
s = s.replace("_l.z + 6.1", "_l.z + 3.0")          # the fine box has a real tray: the eye lies on the felt at the bottom of it
open(p, "w", encoding="utf-8", newline="\n").write(s)

# ---------------------------------------------------------------- the game
edit(R + "Source/WellnessCheck/WCGame.cpp", [
    ('''{ TEXT("key_box"), TEXT("Small key"), TEXT("Small and fancy, with a heart worked into the bow. Too small for any door in this house."), TEXT("/Game/WC/Props/SM_Item_Key.SM_Item_Key") },''',
     '''{ TEXT("doll"), TEXT("Rag doll"), TEXT("A child's rag doll, pushed deep into the duct. One button eye is gone. There is something hard inside her."), TEXT("/Game/WC/Props/SM_Item_Doll.SM_Item_Doll") },
		{ TEXT("doll_empty"), TEXT("Rag doll"), TEXT("Ruth's, I would guess. The seam down her back has been cut and sewn up again more than once."), TEXT("/Game/WC/Props/SM_Item_DollEmpty.SM_Item_DollEmpty") },
		{ TEXT("key_box"), TEXT("Small key"), TEXT("Small and fancy, with a heart worked into the bow. Too small for any door in this house."), TEXT("/Game/WC/Props/SM_Item_KeyHeart.SM_Item_KeyHeart") },'''),
    ('''TEXT("From the kitchen drawer that was shut a minute before. Worn smooth. Her sitting room is the only door downstairs that is locked.")''',
     '''TEXT("Worn smooth, two little scrolls in the bow. It was lying in a drawer that had been shut.")'''),
    ('''TEXT("Heavy and old, on a faded red ribbon. For the locked room upstairs, the one she prayed in.")''', '''TEXT("Heavy and old, on a faded red ribbon gone grey where it was held.")'''),
    ('''TEXT("It was inside a hollow book. Walter's desk, in the den."), TEXT("/Game/WC/Props/SM_Item_Key.SM_Item_Key")''',
     '''TEXT("It was inside a hollow book. A barrel key, too small for a door."), TEXT("/Game/WC/Props/SM_Item_KeyDesk.SM_Item_KeyDesk")'''),
    ('''TEXT("Three on a ring, from his desk. The door across the upstairs hall, and the rooms behind it.")''', '''TEXT("Three that do not match, on a split ring with a leather fob. W.H. From his desk.")'''),
    ('''TEXT("It was in Daniel's room, kept where a boy keeps things. Long, with a paper tag too worn to read."), TEXT("/Game/WC/Props/SM_Item_Key.SM_Item_Key")''',
     '''TEXT("It was in Daniel's room, kept where a boy keeps things. Long, with a paper tag too worn to read."), TEXT("/Game/WC/Props/SM_Item_KeyLong.SM_Item_KeyLong")'''),
    ('''TEXT("From the bottom of Daniel's footlocker. The padlock on the cellar door."), TEXT("/Game/WC/Props/SM_Item_KeyIron.SM_Item_KeyIron")''',
     '''TEXT("Flat brass, stamped 27. From the bottom of Daniel's footlocker."), TEXT("/Game/WC/Props/SM_Item_KeyPadlock.SM_Item_KeyPadlock")'''),
    ('''TEXT("A screw-in plug fuse, the old kind. The fuse box is in the pantry.")''', '''TEXT("A screw-in plug fuse, the old kind. Fifteen amperes.")'''),
    # a thing with something hidden on it
    ('''	const FWCItemInfo* FindWCItemInfo(FName Id)''', '''	// Some things have something hidden on them: turn that side toward him in Inspect and it can be taken.
	struct FWCHidden { const TCHAR* Item; FVector Side; const TCHAR* Hint; const TCHAR* Prompt; const TCHAR* Found; const TCHAR* Event; };
	const FWCHidden GWCHidden[] = {
		{ TEXT("doll"), FVector(0.f, 0.f, -1.f), TEXT("Something hard is sewn inside her. Turn her over."), TEXT("[E]  Work it out through the seam"), TEXT("A small key, sewn into the stuffing."), TEXT("inspect:doll") },
	};
	const FWCItemInfo* FindWCItemInfo(FName Id)'''),
    ('''		Text(TEXT("Drag, or W A S D: turn it      Wheel, or Q / Z: closer, further      Esc: back"), W * 0.5f, H - Px(64.f), Px(19.f), Dim, 1);''',
     '''		Text(TEXT("Drag, or W A S D: turn it      Wheel, or Q / Z: closer, further      Esc: back"), W * 0.5f, H - Px(64.f), Px(19.f), Dim, 1);
		for (const FWCHidden& Hd : GWCHidden)
		{
			if (Cur->Id != Hd.Item) continue;
			const FQuat Qv = FQuat(FRotator(InvPitch, 0.f, 0.f)) * FQuat(FRotator(0.f, InvYaw, 0.f)) * P->InspectBase();
			const bool bSide = Qv.RotateVector(Hd.Side).X < -0.62f;                 // that side is toward him
			if (bSide) InvTouchedAt = RealNow;                                        // hold still while he looks at it
			Text(bSide ? Hd.Prompt : Hd.Hint, W * 0.5f, H - Px(262.f), Px(25.f), bSide ? Hot : Dim, 1);
			if (bSide && bGo)
			{
				const float Y0 = InvYaw, P0 = InvPitch, Z0 = InvZoom;
				D->Event(Hd.Event);
				TArray<FInvItem> Now;
				BuildInventory(D, Now);
				if (Now.IsValidIndex(InvSel)) { ShowInvItem(D, Now[InvSel].Id); InvYaw = Y0; InvPitch = P0; InvZoom = Z0; }
				InvSay(Hd.Found);
				return;
			}
		}
		if (RealNow < InvMsgUntil) Text(InvMsg, W * 0.5f, H - Px(262.f), Px(25.f), Hot, 1);'''),
    ('''	if (Id == TEXT("screwdriver")) {''', '''	if (Id == TEXT("doll")) { InvSay(TEXT("There is something hard inside her. Inspect her.")); return; }
	if (Id == TEXT("screwdriver")) {'''),
])
edit(R + "Source/WellnessCheck/WCStory.cpp", [
    ('''	if (Is(Id, TEXT("take:screwdriver")))''', '''	// the doll from the vent: the small key is sewn inside her, and comes out in Inspect (WCGame.cpp, GWCHidden)
	if (Is(Id, TEXT("take:doll")))
	{
		Feedback(TEXT("Something hard is sewn inside her."));
		if (!Has(TEXT("heard_upstairs"))) SetObjective(TEXT("Look the doll over (Tab, Inspect)"));
		return;
	}
	if (Is(Id, TEXT("inspect:doll")))
	{
		const int32 At = Items.IndexOfByKey(FName(TEXT("doll")));
		if (At == INDEX_NONE) return;
		Items[At] = FName(TEXT("doll_empty"));
		Set(TEXT("doll_opened"));
		if (!HasItem(TEXT("key_box")) && !Has(TEXT("box_open"))) Items.Insert(FName(TEXT("key_box")), At + 1);
		Play2D(TEXT("pickup"), 0.6f, EWCSnd::SFX, 1.15f);
		UE_LOG(LogWCStory, Display, TEXT("WCDOLL t=%.1f the small key comes out of the doll"), PlaySeconds);
		UpstairsThump();
		return;
	}
	if (Is(Id, TEXT("take:screwdriver")))'''),
    ('''ShowTagged(TEXT("Show_ventkey"), Has(TEXT("vent_open")) && !Has(TEXT("heard_upstairs")));''',
     '''ShowTagged(TEXT("Show_ventkey"), Has(TEXT("vent_open")) && !HasItem(TEXT("doll")) && !HasItem(TEXT("doll_empty")) && !Has(TEXT("doll_opened")));'''),
    ('''Feedback(TEXT("Screwed shut. Something small is caught behind the slats."));''', '''Feedback(TEXT("Screwed shut. Something has been pushed in behind the slats."));'''),
])
edit(R + "Source/WellnessCheck/WCHouse.cpp", [
    ('''		Play2D(TEXT("her_scream_short"), 1.f);
		if (P) P->SetInputLocked(false);
		if (Then) Then();
	});
}''', '''		Play2D(TEXT("her_scream_short"), 1.f);
		if (P) P->SetInputLocked(false);
		FadeTo(0.f, 1.4f);                      // back to the house (whatever comes next may fade again; it used to stay black)
		if (Then) Then();
	});
}'''),
    ('''if (!HasItem(TEXT("key_box")) && !Has(TEXT("box_open"))) GiveItem(TEXT("key_box"), TEXT("Small key"));
				UpstairsThump();''', '''if (!HasItem(TEXT("key_box")) && !Has(TEXT("box_open"))) GiveItem(TEXT("key_box"), TEXT("Small key"));
				Set(TEXT("doll_opened"));
				UpstairsThump();'''),
])
edit(R + "Source/WellnessCheck/WCAuto.cpp", [
    ('''Shot(TEXT("08g_vent_open_key"));
	Use(TEXT("pick_key_box")); Flag(TEXT("heard_upstairs"), 10.f); Wait(14.f);''',
     '''Shot(TEXT("08g_vent_open_doll"));
	Use(TEXT("pick_doll")); Wait(0.6f); AutoSteps.Add({ A_Do, TEXT("inspectdoll"), 0.f }); Flag(TEXT("heard_upstairs"), 10.f); Wait(14.f);'''),
    ('''else if (S.Arg == TEXT("tvon")) { bBusy = false; TVOn(); }''', '''else if (S.Arg == TEXT("inspectdoll")) Event(TEXT("inspect:doll"));
		else if (S.Arg == TEXT("tvon")) { bBusy = false; TVOn(); }'''),
])
print("pass 103 applied")
