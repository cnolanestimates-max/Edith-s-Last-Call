"""Pass 100: the first scare is something the player sets off, not a clock (Cheyenne 2026-11-19 15:34 UTC).
"The first scare needs to be locked behind something that the player can do ... a locked box, maybe like a jewelry box, sitting
on a desk [upstairs, in her room] ... downstairs there's a key ... after you pick up the key, you hear the thump upstairs ...
I have to go upstairs because I have this key now ... and then bam, the scare happens."

  - a locked jewelry box on the table in the master bedroom ("Locked.")
  - a small key on the kitchen counter by the sink; taking it is what makes the heavy thump upstairs (the timers are gone)
  - going up to the box is the walk on which she is at the doorway (the peek, unchanged)
  - the key opens the box: a letter from Ruth, folded small
  - F9 (developer) makes the thump happen now"""
import json, sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit

R = "C:/GameDev/Unreal/WellnessCheck/"

# ---------------------------------------------------------------- the box, as a model (closed and open)
edit(R + "Scripts/art/build_items.py", [
    ('''build("AmmoBox", ammobox)''', '''def jewelbox(opened=False):
    # an old jewelry box: dark wood, brass corners and a little lock plate; the lid lifts on the back edge
    P = [box(0.170, 0.115, 0.060, (0, 0, 0.030), m="Wood", bevel=0.004)]
    for sx in (-1, 1):
        for sy in (-1, 1):
            P.append(box(0.016, 0.016, 0.062, (sx * 0.0785, sy * 0.051, 0.031), m="Brass", bevel=0.002))
    P.append(box(0.022, 0.003, 0.026, (0, -0.0585, 0.040), m="Brass", bevel=0.002))                 # the lock plate
    P.append(cyl(0.0022, 0.004, (0, -0.0600, 0.042), (math.pi / 2, 0, 0), "Iron", 10))              # the keyhole
    for sx in (-1, 1):
        for sy in (-1, 1):
            P.append(sphere(0.006, (sx * 0.074, sy * 0.047, 0.004), "Brass"))
    if not opened:
        P.append(box(0.174, 0.119, 0.024, (0, 0, 0.072), m="Wood", bevel=0.005))
        P.append(box(0.176, 0.004, 0.004, (0, -0.058, 0.062), m="Brass"))
        P.append(box(0.060, 0.030, 0.002, (0, 0, 0.0845), m="Brass", bevel=0.001))
    else:
        a = math.radians(-100)
        P.append(box(0.174, 0.119, 0.024, (0, 0.0575 + 0.060 * math.cos(a + math.pi / 2) * -1 + 0.012, 0.060 + 0.060), (a, 0, 0), "Wood", 0.005))
        P.append(box(0.156, 0.101, 0.002, (0, 0, 0.0585), m="Ribbon"))                               # faded red lining
    return P


build("JewelBox", jewelbox)
build("JewelBoxOpen", lambda: jewelbox(True))
build("AmmoBox", ammobox)'''),
])

# ---------------------------------------------------------------- the level
edit(R + "Scripts/level/build_house.py", [
    ('''note("note_diary1", "Book_Open_Pages", 690, 310, UZ + 99, 30)''',
     '''note("note_diary1", "Book_Open_Pages", 690, 310, UZ + 99, 30)
# her jewelry box, locked, on the same table: what he has to come back up the stairs for
interact("WCUsable", "jewelbox", ITEM("JewelBox") or "Music_Box_Closed", 716, 284, UZ + 98, 205, "Open the jewelry box", (14, 12, 9), (0, 0, 5))
if ITEM("JewelBoxOpen"):
    place(ITEM("JewelBoxOpen"), 716, 284, UZ + 98, 205, MB, name="JewelBoxOpen", tags=["Show_jewel"], collide=False)
note("note_box", "Letters_Scattered", 690, 268, UZ + 98.6, 60, scale=0.32, grab=(9, 9, 5), tags=["Show_jewel"])'''),
    ('''place("Tin_Cans_Rusty", 920, 560, GZ + 95, 0, K, collide=False)''',
     '''place("Tin_Cans_Rusty", 920, 560, GZ + 95, 0, K, collide=False)
# the small key: on the counter by the sink.  Taking it is what brings the thump upstairs.
pickup("pick_key_box", "key_box", "Small key", ("Key", CUBE, (0.05, 0.018, 0.005), {0: "BrassOld"}), 872, 556, GZ + 96, 35, grab=(11, 11, 7))'''),
])
edit(R + "Scripts/level/settle.py", [
    ('''    if any(str(t).startswith(("Show_", "Hide_")) for t in a.tags):
        continue''', '''    if any(str(t).startswith(("Show_", "Hide_")) for t in a.tags) and not any(str(t) == "Show_jewel" for t in a.tags):
        continue'''),
])
p = R + "Scripts/level/notes.json"
d = json.load(open(p, encoding="utf-8"))
d["note_box"] = {"style": 0, "title": "A letter, folded small, in the jewelry box",
                 "body": "November 14\n\nMother,\n\nWe are not coming for Thanksgiving. I am sorry. The children are frightened of the house and, if I am honest, so am I. You stand in doorways and you do not answer when we speak to you. You still set a place for Daddy.\n\nThe doctor says there are good homes in Ashby, where somebody would always be with you. Please think about it.\n\nI will telephone on Sunday.\n\nRuth\n\n\n(Under the fold, in pencil, in a hand that shakes:)\n\nshe did not telephone"}
json.dump(d, open(p, "w", encoding="utf-8", newline="\n"), indent=1, ensure_ascii=False)

# ---------------------------------------------------------------- the game
edit(R + "Source/WellnessCheck/WCGame.cpp", [
    ('''{ TEXT("key_sitting"), TEXT("Small brass key"),''', '''{ TEXT("key_box"), TEXT("Small key"), TEXT("Small and fancy, with a heart worked into the bow. Too small for any door in this house."), TEXT("/Game/WC/Props/SM_Item_Key.SM_Item_Key") },
		{ TEXT("key_sitting"), TEXT("Small brass key"),'''),
])
edit(R + "Source/WellnessCheck/WCDirector.h", [
    ('bool DoorOpensByItself();', 'bool DoorOpensByItself();\n\tvoid UpstairsThump();'),
])
edit(R + "Source/WellnessCheck/WCStory.cpp", [
    ('''		if (Id.ToString().StartsWith(TEXT("trig:t_")) && P->GetActorLocation().Z < 250.f && P->GetActorLocation().Z > -50.f
				&& !Has(TEXT("heard_upstairs")) && Has(TEXT("inside")) && !bBusy
		&& ((BuildStep >= 7 && PlaySeconds - InsideAt > 450.f * TestPace && NotesRead.Num() + LooksSeen.Num() >= 6) || PlaySeconds - InsideAt > 570.f * TestPace))
	{
		Set(TEXT("heard_upstairs"));
		After(6.f, [this]()
		{
			const FVector Up = Pos(TEXT("Snd_UpstairsThump"));
			PlayAt(TEXT("thump_heavy"), Up, 1.f, 1.f);
			if (AWCCharacter* Pl = Player()) Pl->AddShake(0.25f);
			After(1.6f, [this, Up]() { PlayAt(TEXT("drag_floor"), Up, 1.f); });
			float T = Say(TEXT("d_thump"), 4.2f);
			After(T, [this]() { SetObjective(TEXT("Check upstairs")); });
			Tension = 0.3f;
		});
		return;
	}''', '''	// the first scare is set off by the player: taking the small key is what brings the thump (no clock)
	if (Is(Id, TEXT("take:key_box"))) { UpstairsThump(); return; }
	if (Is(Id, TEXT("use:jewelbox")))
	{
		if (Has(TEXT("box_open"))) return;
		if (!HasItem(TEXT("key_box"))) { if (Clock > SpeechFreeAt) { SpeechFreeAt = Clock + 3.0; Feedback(TEXT("Locked.")); PlayAt(TEXT("door_locked"), P->GetActorLocation(), 0.5f, 1.4f, 600.f); } return; }
		Items.Remove(TEXT("key_box"));
		Set(TEXT("box_open"));
		Play2D(TEXT("door_unlock"), 0.6f, EWCSnd::SFX, 1.3f);
		ApplyWorldState();
		return;
	}'''),
    ('''// ---------------------------------------------------------------------------------------------- events
static bool Is(FName Id, const TCHAR* S) { return Id == S; }''',
     '''// ---------------------------------------------------------------------------------------------- events
static bool Is(FName Id, const TCHAR* S) { return Id == S; }

/** Something heavy goes over upstairs, a few seconds after he pockets the key. */
void AWCDirector::UpstairsThump()
{
	if (Has(TEXT("heard_upstairs"))) return;
	Set(TEXT("heard_upstairs"));
	UE_LOG(LogWCStory, Display, TEXT("WCTHUMP t=%.1f (%.0f s after coming in)"), PlaySeconds, PlaySeconds - InsideAt);
	After(6.f, [this]()
	{
		const FVector Up = Pos(TEXT("Snd_UpstairsThump"));
		PlayAt(TEXT("thump_heavy"), Up, 1.f, 1.f);
		if (AWCCharacter* Pl = Player()) Pl->AddShake(0.25f);
		After(1.6f, [this, Up]() { PlayAt(TEXT("drag_floor"), Up, 1.f); });
		float T = Say(TEXT("d_thump"), 4.2f);
		After(T, [this]() { SetObjective(TEXT("Check upstairs")); });
		Tension = 0.3f;
	});
}'''),
    ('''ShowTagged(TEXT("Show_desk"), Has(TEXT("desk_open")) && !HasItem(TEXT("key_ell")));''',
     '''ShowTagged(TEXT("Show_desk"), Has(TEXT("desk_open")) && !HasItem(TEXT("key_ell")));
	ShowTagged(TEXT("Show_jewel"), Has(TEXT("box_open")));
	if (AWCInteractable* Jb = Thing(TEXT("jewelbox"))) { Jb->SetActorHiddenInGame(Has(TEXT("box_open"))); Jb->SetActorEnableCollision(!Has(TEXT("box_open"))); Jb->bEnabled = !Has(TEXT("box_open")); }'''),
])
edit(R + "Source/WellnessCheck/WCHouse.cpp", [
    ('''if (!Has(TEXT("heard_upstairs")) && T > 640.f && L.Z > 300.f && L.Z < 650.f)
	{
		Set(TEXT("heard_upstairs"));
		UpstairsAt = Clock;
		PlayAt(TEXT("thump_heavy"), Pos(TEXT("Snd_UpstairsThump")), 1.f);
		P->AddShake(0.25f);
		After(1.6f, [this]() { PlayAt(TEXT("drag_floor"), Pos(TEXT("Snd_UpstairsThump")), 1.f); });
		SetObjective(TEXT("Find her upstairs"));
		Tension = 0.35f;
	}''', '''// (the thump used to come on a clock here; it is now set off by taking the small key: AWCDirector::UpstairsThump)'''),
    ('''InsideAt = PlaySeconds - 700.f;                      // as if he had been in the house long enough
				BuildStep = FMath::Max(BuildStep, 7);
				ShowToast(TEXT("DEV: the upstairs thump is due. Walk through a doorway downstairs."));''',
     '''UpstairsThump();                                     // as if he had just taken the small key
				ShowToast(TEXT("DEV: the upstairs thump is coming. Go up the stairs."));'''),
])
edit(R + "Source/WellnessCheck/WCAuto.cpp", [
    ('''Flag(TEXT("heard_upstairs"), 55.f * Slow); Wait(14.f);''',
     '''Go(TEXT("A_Kitchen")); Use(TEXT("pick_key_box")); Flag(TEXT("heard_upstairs"), 10.f); Wait(14.f);'''),
])
print("pass 100 applied")
