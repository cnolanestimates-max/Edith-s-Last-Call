"""Pass 114: Cheyenne's play-test of 2026-11-19 19:33 to 19:44 UTC.

  1. The opening: the front door stays shut until he has been round the back and taken the VHS tape from the shed bench.
     Taking it brings the trash can by the back of the house over (a real can, lying on its side with its trash spilled when
     he turns), and he calls "Mrs. Harrow? ...Is that you?".  Then the front door opens.
  2. The television is off when he comes in.  Three tapes are found (shed, the aide's room upstairs, the attic) and played in
     the recorder on top of the set.  Switching the set off after his second tape is the reflection scare.
  3. The kitchen vent calls attention to itself the first time he walks in (something moves behind it).
  4. The settlers book pulls out without waiting for the note.
  5. A picture frame comes off the hall wall behind him (big sound); picking it up brings back "Every face scratched out.
     Every one but hers."  The smell line at the door is back too.  (The photographs themselves are Codex's.)
  6. Floating props: a sweep at the end of the level build that drops what hangs in the air and reports the rest.
  7. Sound: the music bed is a steady drone (the old one had a boom in it about every ten seconds); crickets are back."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit

R = "C:/GameDev/Unreal/WellnessCheck/"

# ================================================================ story
edit(R + "Source/WellnessCheck/WCStory.cpp", [
    ('''{ TEXT("d_call3"), TEXT("Deputy Brandt"), TEXT("Mrs. Harrow, it's the sheriff's office. Can you hear me?"), 0 },''',
     '''{ TEXT("d_call3"), TEXT("Deputy Brandt"), TEXT("Mrs. Harrow, it's the sheriff's office. Can you hear me?"), 0 },
	{ TEXT("d_shedcall"), TEXT("Deputy Brandt"), TEXT("Mrs. Harrow? ...Is that you?"), 0 },'''),
    # two of his lines come back (she asked for them by name)
    ('''TEXT("d_table"), TEXT("d_photos"),
		TEXT("d_foyer"), TEXT("d_wayout"),''', '''TEXT("d_table"),
		TEXT("d_wayout"),'''),
    ('''if (Is(Id, TEXT("trig:t_living")) && !Has(TEXT("seen_living"))) { Set(TEXT("seen_living")); Say(TEXT("d_photos"), 2.5f); return; }''',
     '''if (Is(Id, TEXT("trig:t_living")) && !Has(TEXT("seen_living"))) { Set(TEXT("seen_living")); return; }       // (his line about the photographs is said over the fallen frame now)'''),
    # the outside: the tape in the shed is what opens the house
    ('''	const bool bShed = Has(TEXT("shed_seen")), bBack = Has(TEXT("back_tried"));
	if (bShed && bBack) SetObjective(TEXT("Go back round to the front door"));
	else if (Has(TEXT("knocked_first")) && !bShed && !bBack) SetObjective(TEXT("No answer. Look round the back of the house."));
	else if (bShed) SetObjective(TEXT("Try the back door"));
	else if (bBack) SetObjective(TEXT("Look in the shed"));''',
     '''	const bool bShed = Has(TEXT("shed_seen")), bBack = Has(TEXT("back_tried"));
	if (Has(TEXT("tape1_taken"))) SetObjective(TEXT("Go back round to the front door"));
	else if (bShed) SetObjective(TEXT("Search the shed"));
	else if (Has(TEXT("knocked_first"))) SetObjective(bBack ? TEXT("Look in the shed") : TEXT("No answer. Look round the back of the house."));'''),
    ('''	if (Is(Id, TEXT("trig:t_shed")) && !Has(TEXT("shed_seen")))''', '''	// the tape on the shed bench: taking it is what brings the trash can over behind him, and what opens the house
	if (Is(Id, TEXT("take:tape1")) && !Has(TEXT("tape1_taken")))
	{
		Set(TEXT("tape1_taken"));
		Set(TEXT("shed_seen"));
		UE_LOG(LogWCStory, Display, TEXT("WCTAPE t=%.1f the shed tape is taken"), PlaySeconds);
		After(1.2f, [this]()
		{
			ApplyWorldState();                                   // the can is on its side now, its trash across the ground
			PlayAt(TEXT("trash_crash"), Pos(TEXT("TrashPoint")), 1.f, 1.f, 8000.f);
			if (AWCCharacter* Pl = Player()) Pl->AddShake(0.35f);
			Tension = FMath::Max(Tension, 0.5f);
			const float T = Say(TEXT("d_shedcall"), 2.6f);
			After(T + 1.2f, [this]() { OutsideProgress(); });
		});
		return;
	}
	if (Is(Id, TEXT("use:frame")))
	{
		if (!Has(TEXT("frame_seen")))
		{
			Set(TEXT("frame_seen"));
			Play2D(TEXT("pickup"), 0.5f, EWCSnd::SFX, 0.8f);
			Say(TEXT("d_photos"), 0.7f);
			ApplyWorldState();
		}
		return;
	}
	if (Is(Id, TEXT("trig:t_shed")) && !Has(TEXT("shed_seen")))'''),
    ('''if (Is(Id, TEXT("locked:front")) && !Has(TEXT("inside")) && !(Has(TEXT("shed_seen")) && Has(TEXT("back_tried"))))''',
     '''if (Is(Id, TEXT("locked:front")) && !Has(TEXT("inside")) && !Has(TEXT("tape1_taken")))'''),
    ('''Set(TEXT("shed_seen")); Set(TEXT("back_tried")); Set(TEXT("knocked_first"));''', '''Set(TEXT("shed_seen")); Set(TEXT("back_tried")); Set(TEXT("knocked_first")); Set(TEXT("tape1_taken"));'''),
    ('''	ShowTagged(TEXT("Show_vent"), Has(TEXT("vent_open")));''', '''	ShowTagged(TEXT("Show_vent"), Has(TEXT("vent_open")));
	ShowTagged(TEXT("Show_trash"), Has(TEXT("tape1_taken")));
	ShowTagged(TEXT("Hide_trash"), !Has(TEXT("tape1_taken")));
	ShowTagged(TEXT("Show_framefall"), Has(TEXT("frame_fell")));
	ShowTagged(TEXT("Hide_framefall"), !Has(TEXT("frame_fell")));
	if (AWCInteractable* Fr = Thing(TEXT("frame"))) Fr->bEnabled = Has(TEXT("frame_fell")) && !Has(TEXT("frame_seen"));'''),
])
edit(R + "Scripts/audio/gen_vo.py", [
    ('''    "d_call3": "Calling through the house, official but strained, listening for any answer.",''',
     '''    "d_call3": "Calling through the house, official but strained, listening for any answer.",
    "d_shedcall": "Badly startled by a crash behind him outdoors at night: the name sharp and loud as he spins round, then after a held breath, quieter and unsure, 'Is that you?'",'''),
])

# ================================================================ the book pulls out on its own
edit(R + "Source/WellnessCheck/WCHouse.cpp", [
    ('''		if (!NotesRead.Contains(TEXT("note_deskkey")))
		{
			if (Clock > SpeechFreeAt) { SpeechFreeAt = Clock + 5.0; Feedback(TEXT("County histories. One spine is cleaner than the rest: 'Customs of the First Settlers'.")); }
			return true;
		}
		ScareBook();''', '''		// (it used to wait until he had read her scrap about the hollow book.  Cheyenne: "I don't think it's necessary
		// for that to wait ... that scare is such a small scare that it could just add to the scares in general.")
		ScareBook();'''),
])

# ================================================================ the television: tapes and a recorder
edit(R + "Source/WellnessCheck/WCDirector.h", [
    ('''	int32 DoorEvents = 0, CallStep = 0;''', '''	int32 DoorEvents = 0, CallStep = 0;
	int32 TVWant = 0;                                          // the tape he has just put in (0 = none)
	TWeakObjectPtr<class UStaticMeshComponent> VCRMesh;        // the recorder on top of the set'''),
])
p = R + "Source/WellnessCheck/WCEvents.cpp"
s = open(p, encoding="utf-8").read()
a = s.index("		// already on when he first comes in (")
b = s.index("	if (TVPhase == 1)", a)
s = s[:a] + '''		// The set is off until he puts a tape in (it used to be playing when he came in, and came on by itself later).
		static bool bVCRTried = false;
		if (!VCRMesh.IsValid() && !bVCRTried && Tv->Mesh)
		{
			bVCRTried = true;
			// the video recorder sits on top of the set, and goes wherever the set goes
			if (UStaticMesh* M = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/WC/Props/SM_Item_VCR.SM_Item_VCR"), nullptr, LOAD_NoWarn | LOAD_Quiet))
			{
				UStaticMeshComponent* C = NewObject<UStaticMeshComponent>(Tv);
				C->SetupAttachment(Tv->Mesh);
				C->SetStaticMesh(M);
				C->SetRelativeLocation(FVector(-21.f, 0.f, 82.4f));
				C->SetCollisionEnabled(ECollisionEnabled::NoCollision);
				C->SetLightingChannels(Tv->Mesh->LightingChannels.bChannel0, Tv->Mesh->LightingChannels.bChannel1, Tv->Mesh->LightingChannels.bChannel2);
				C->RegisterComponent();
				VCRMesh = C;
			}
		}
		Tv->Prompt = (HasItem(TEXT("tape1")) || HasItem(TEXT("tape2")) || HasItem(TEXT("tape3"))) ? TEXT("Put the tape in the recorder") : TEXT("Look at the television");
		return;
	}
''' + s[b:]
open(p, "w", encoding="utf-8", newline="\n").write(s)
edit(p, [
    ('''	const int32 N = 1 + (TVTape % Tapes);''', '''	const int32 N = TVWant > 0 ? FMath::Clamp(TVWant, 1, Tapes) : 1 + (TVTape % Tapes);
	TVWant = 0;'''),
    ('''		// the first showing (it is on when he comes in) plays until he switches it off; later ones for 75 s
		if (TVTape > 1 && T > 75.f) TVOff(false);''', '''		// (every tape plays until he switches the set off)'''),
    ('''		else if (TVPhase == 0) Feedback(TEXT("An old console set. The screen is grey with dust, except where a hand has wiped it."));''',
     '''		else if (TVPhase == 0)
		{
			static const TCHAR* TapeId[3] = { TEXT("tape1"), TEXT("tape2"), TEXT("tape3") };
			int32 Have = 0;
			for (int32 i = 0; i < 3 && Have == 0; ++i) if (HasItem(TapeId[i])) Have = i + 1;
			if (Have == 0)
			{
				Feedback(Has(TEXT("tape_played")) ? TEXT("The recorder is empty. There were more tapes than this.") : TEXT("An old console set, and a video recorder on top of it. No tape in it."));
				return true;
			}
			Items.Remove(TapeId[Have - 1]);
			Set(TEXT("tape_played"));
			Set(FName(*FString::Printf(TEXT("tape%d_played"), Have)));
			UE_LOG(LogWCEvents, Display, TEXT("WCTAPE t=%.1f tape %d goes into the recorder"), PlaySeconds, Have);
			if (AWCInteractable* Tv0 = Thing(TEXT("tv"))) PlayAt(TEXT("door_unlock"), Tv0->GetActorLocation() + FVector(0, 0, 90), 0.8f, 0.6f, 1200.f);       // the tape going home
			TVWant = Have;
			After(1.5f, [this]() { if (TVPhase == 0) TVOn(); });
		}'''),
    # the cues: the vent calls attention to itself; a frame comes off the wall
    ('''		{ TEXT("enter:t_kitchen"), 1, TEXT("thump_far"), 1, 200.f, 400.f, 0.9f, 0.95f, nullptr, 0 },''',
     '''		{ TEXT("enter:t_kitchen"), 1, TEXT(""), 0, 0.f, 0.f, 1.f, 1.f, nullptr, 5 },                    // something moves behind the wall vent'''),
    ('''		{ TEXT("enter:t_hall_mid"), 2, TEXT("steps_above"), 1, 100.f, 300.f, 0.9f, 1.f, nullptr, 0 },''',
     '''		{ TEXT("enter:t_hall_mid"), 2, TEXT(""), 0, 0.f, 0.f, 1.f, 1.f, TEXT("locked_in"), 6 },          // a picture comes off the wall behind him
		{ TEXT("enter:t_hall_mid"), 3, TEXT("steps_above"), 1, 100.f, 300.f, 0.9f, 1.f, nullptr, 0 },
		{ TEXT("enter:t_dining"), 2, TEXT("thump_far"), 1, 200.f, 400.f, 0.9f, 0.95f, nullptr, 0 },'''),
    ('''			else if (Act == 4)
			{''', '''			else if (Act == 5)
			{
				const FVector Vp = Pos(TEXT("VentPoint"));
				PlayAt(TEXT("skitter"), Vp, 1.f, 0.9f, 1600.f);
				After(1.5f, [this, Vp]() { PlayAt(TEXT("scratch_wall"), Vp, 0.8f, 1.1f, 1600.f); });
				After(2.3f, [this]() { if (!Has(TEXT("vent_seen")) && !bBusy) Feedback(TEXT("Something moved behind the wall vent.")); });
			}
			else if (Act == 6)
			{
				Set(TEXT("frame_fell"));
				ApplyWorldState();
				PlayAt(TEXT("frame_fall"), Pos(TEXT("FramePoint")), 1.f, 1.f, 5000.f);
				Play2D(TEXT("sting_hit"), 0.75f, EWCSnd::Music);
				Pl->AddShake(0.4f);
				Tension = FMath::Max(Tension, 0.6f);
				Rest(60.f);
				UE_LOG(LogWCEvents, Display, TEXT("WCSCARE t=%.1f frame off the wall"), PlaySeconds);
			}
			else if (Act == 4)
			{'''),
    ('''// 3 behind him.  Need: a story flag that has to be set first (nullptr = none).  Act: 1 the rocking chair rocks, 2 a light he
// left on goes out, 3 Walter's radio tunes itself, 4 bare feet run across the other floor.''',
     '''// 3 behind him.  Need: a story flag that has to be set first (nullptr = none).  Act: 1 the rocking chair rocks, 2 a light he
// left on goes out, 3 Walter's radio tunes itself, 4 bare feet run across the other floor, 5 something moves behind the kitchen
// vent, 6 a picture frame comes off the hall wall.'''),
])

# ================================================================ inventory
edit(R + "Source/WellnessCheck/WCGame.cpp", [
    ('''		{ TEXT("doll"), TEXT("Rag doll"),''', '''		{ TEXT("tape1"), TEXT("VHS tape"), TEXT("A home video cassette. The label says 'Ruthie - bedtime, Oct. 1991' in ballpoint."), TEXT("/Game/WC/Props/SM_Item_Tape1.SM_Item_Tape1") },
		{ TEXT("tape2"), TEXT("VHS tape"), TEXT("Another cassette. 'Living room, Thanksgiving 1991.'"), TEXT("/Game/WC/Props/SM_Item_Tape2.SM_Item_Tape2") },
		{ TEXT("tape3"), TEXT("VHS tape"), TEXT("'Mother - porch, Nov. 1991.' The handwriting is not Edith's."), TEXT("/Game/WC/Props/SM_Item_Tape3.SM_Item_Tape3") },
		{ TEXT("doll"), TEXT("Rag doll"),'''),
    ('''	if (Id == TEXT("doll")) {''', '''	if (S.StartsWith(TEXT("tape"))) { if (F && F->WCId == TEXT("tv")) OnWhatHeFaces(); else InvSay(TEXT("It needs a video recorder.")); return; }
	if (Id == TEXT("doll")) {'''),
])

# ================================================================ the level
edit(R + "Scripts/level/exterior.py", [
    ('''point("A_Shed", SX0 - 140, (_DY0 + _DY1) / 2, GZ, 0, folder="Auto")''', '''# the first tape: on the bench, among the junk.  Taking it is what lets him into the house.
pickup("pick_tape1", "tape1", "VHS tape", ("Tape1", CUBE, (0.187, 0.103, 0.025), {0: "BrassOld"}), SX1 - 46, _ridge - 52, 50.4, 25, grab=(13, 10, 6))
# the trash can by the back of the house: standing until he takes the tape, then on its side with everything out of it
_TX, _TY = XB + 105.0, -340.0
if ITEM("TrashCan"):
    place(ITEM("TrashCan"), _TX, _TY, -40, 0, EX + "/BackYard", name="TrashCanUp", tags=["Hide_trash"])
if ITEM("TrashCanDown"):
    place(ITEM("TrashCanDown"), _TX + 70, _TY - 30, -40, 250, EX + "/BackYard", name="TrashCanDown", tags=["Show_trash"], collide=False)
for _k, (_m, _dx, _dy, _yw) in enumerate((("Tin_Cans_Rusty", 150, -70, 30), ("Bottles_Empty_Group", 205, -20, 110), ("Newspaper_Pile", 120, 25, 60), ("Paint_Can_Spilled", 250, -95, 200),
                                          ("Tin_Cans_Rusty", 285, 10, 250), ("Newspaper_Pile", 215, -130, 10))):
    place(_m, _TX + _dx, _TY + _dy, -40, _yw, EX + "/BackYard", name=f"Trash_{_k}", tags=["Show_trash"], collide=False)
point("TrashPoint", _TX + 70, _TY - 30, 0)
point("A_Shed", SX0 - 140, (_DY0 + _DY1) / 2, GZ, 0, folder="Auto")'''),
])
edit(R + "Scripts/level/ell.py", [
    ('''put_note("note_aide2", "Book_Open_Pages", 2035, 525, UZ + 98, 20)''', '''put_note("note_aide2", "Book_Open_Pages", 2035, 525, UZ + 98, 20)
# the second tape: on the aide's stripped bed (behind Walter's keys, so about the middle of the night)
put_pickup("pick_tape2", "tape2", "VHS tape", ("Tape2", CUBE, (0.187, 0.103, 0.025), {0: "BrassOld"}), 2185, 430, UZ + 55, 70, grab=(13, 10, 6))'''),
])
edit(R + "Scripts/level/build_house.py", [
    ('''place("Portrait_Oval", 600, 181, GZ + 150, 180, D + "Hall", collide=False)''',
     '''place("Portrait_Oval", 600, 181, GZ + 150, 180, D + "Hall", collide=False, name="FrameUp", tags=["Hide_framefall"])
# ...which comes off the wall behind him (WCEvents.cpp, cue 6): the same frame on the floor, glass out, and a spot to pick it up
place("Picture_Frame_Fallen", 600, 148, GZ, 70, D + "Hall", collide=False, name="FrameDown", tags=["Show_framefall"])
interact("WCUsable", "frame", None, 600, 148, GZ + 6, 0, "Pick up the frame", (30, 30, 12), (0, 0, 4), enabled=False)
point("FramePoint", 600, 165, GZ + 60)
point("VentPoint", 1400, 224, GZ + 125)'''),
    ('''interact("WCUsable", "trunk", "Chest_Trunk", 760, -430, AZ, 90, "Open the footlocker", (50, 30, 36), (0, 0, 36))''',
     '''interact("WCUsable", "trunk", "Chest_Trunk", 760, -430, AZ, 90, "Open the footlocker", (50, 30, 36), (0, 0, 36))
# the third tape: on the attic floor beside the footlocker
pickup("pick_tape3", "tape3", "VHS tape", ("Tape3", CUBE, (0.187, 0.103, 0.025), {0: "BrassOld"}), 850, -395, AZ + 1.0, 140, grab=(13, 10, 6))'''),
])
p = R + "Scripts/level/build_house.py"
s = open(p, encoding="utf-8").read()
if "float_sweep.py" not in s:
    s = s.rstrip("\n") + '''
# last of all (after everything has been placed and moved): nothing is left hanging in the air
exec(open(os.path.join(HERE, "float_sweep.py"), encoding="utf-8").read())
'''
    open(p, "w", encoding="utf-8", newline="\n").write(s)
open(R + "Scripts/level/float_sweep.py", "w", encoding="utf-8", newline="\n").write('''# Float sweep (Cheyenne 2026-11-19: "a lot of props are literally in midair still ... bottles in the kitchen that are just
# hanging in the air by the sink").  Runs last in the level build.  Every small loose thing is checked against what is really
# under it, at five points of its footprint; anything hanging more than 3 cm above its support is dropped onto it.  Things that
# are meant to hang (pictures, cobwebs, lamps on walls and so on) are left alone, and whatever else is found in the air but is
# not on the list of loose things is reported, not moved.
import math as _m
_fw = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
_HANG = ("Portrait", "Mirror", "Cobweb", "Curtain", "Medicine_Cabinet", "Cross", "Chain", "Ceiling", "Bunting", "Jar_Herbs", "Hook", "Bulb", "Cord", "Socket", "Switch",
         "Fuse", "Knot", "Window", "Lantern", "Decal", "Wall", "Stairs", "Rail", "Shutter", "Gutter", "Pane", "Trim", "Beam", "Roof", "Gable", "Post", "Brace", "Sconce",
         "Rack", "Wreath", "Voodoo", "Hanging", "Blanket", "Dress", "Rag", "Chandelier", "Vent", "Shelf", "Drawing_", "Frame", "Clock_Wall", "Antler", "Eye", "Hole", "Rake",
         "Nail", "Gap", "Door", "Lintel", "Board", "Skull_Goat", "Shed", "BookCase", "Book_", "DenBook", "ShelfBook", "Settlers", "Curtains", "Plank")
_LOOSE = ("Bottle", "Tin_Cans", "Jar", "Candle", "Plates", "Teapot", "Bucket", "Crate", "Box_", "Newspaper", "Doll", "Toy", "Pill", "Lamp", "Radio", "Typewriter",
          "Telephone", "Cup", "Suitcase", "Hatbox", "Barrel", "Basket", "Paint_Can", "Letters", "Clipboard", "Music_Box", "Flashlight", "Tome", "Pickup_", "Note_",
          "Mantel_Clock", "Trash", "Stack", "Pile", "Bust", "Vase", "Bowl", "Pot", "Pan", "Kettle", "Glass", "Mug", "Ink", "Quill", "Photo")
_dropped, _left, _seen = 0, [], 0
for _a in actors.get_all_level_actors():
    _folder = str(_a.get_folder_path())
    if not _folder.startswith("House/") or _folder.startswith(("House/Shell", "House/Nav", "House/Points", "House/Auto", "House/Environment", "House/Exterior/Forest")):
        continue
    _label = _a.get_actor_label()
    if any(_w in _label for _w in _HANG):
        continue
    if any(str(_t).startswith(("Show_", "Hide_")) for _t in _a.tags):
        continue
    _rot = _a.get_actor_rotation()
    if abs(_rot.roll) > 45 or abs(_rot.pitch) > 45:
        continue
    _comps = [_c for _c in _a.get_components_by_class(unreal.StaticMeshComponent) if _c.static_mesh]
    if not _comps:
        continue
    _o, _e, _r = unreal.SystemLibrary.get_component_bounds(_comps[0])
    if max(_e.x, _e.y) > 70 or _e.z > 60 or (_e.x + _e.y + _e.z) < 0.5:
        continue
    _seen += 1
    _bottom = _o.z - _e.z
    _best = None
    for _dx, _dy in ((0, 0), (0.5, 0), (-0.5, 0), (0, 0.5), (0, -0.5)):
        try:
            _h = unreal.SystemLibrary.line_trace_single(_fw, V(_o.x + _dx * _e.x, _o.y + _dy * _e.y, _bottom + 6.0), V(_o.x + _dx * _e.x, _o.y + _dy * _e.y, _bottom - 400.0),
                                                        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [_a], unreal.DrawDebugTrace.NONE, True)
        except Exception:
            _h = None
        if _h and _h.to_tuple()[0]:
            _z = _h.to_tuple()[5].z
            _best = _z if _best is None else max(_best, _z)
    if _best is None:
        continue
    _gap = _bottom - _best
    if _gap <= 3.0:
        continue
    if any(_w in _label for _w in _LOOSE):
        _l = _a.get_actor_location()
        _a.set_actor_location(V(_l.x, _l.y, _l.z - _gap + 0.3), False, False)
        _dropped += 1
        log(f"float: {_label} at ({_l.x:.0f},{_l.y:.0f},{_l.z:.0f}) hung {_gap:.0f} cm in the air: dropped")
    else:
        _left.append(f"{_label} ({_o.x:.0f},{_o.y:.0f},{_bottom:.0f}) {_gap:.0f} cm")
log(f"float sweep: {_seen} small things checked, {_dropped} dropped onto what is under them, {len(_left)} others are off their support and were left: " + "; ".join(_left[:60]))
''')
import py_compile
py_compile.compile(R + "Scripts/level/float_sweep.py", doraise=True)
py_compile.compile(R + "Scripts/level/build_house.py", doraise=True)

# ================================================================ the photo test sees the new things
edit(R + "Source/WellnessCheck/WCAuto.cpp", [
    ('''			At(TEXT("book")); Wait(0.75f); Shot(TEXT("spot_9_book_coming_out"));''', '''			At(TEXT("at:3790,-745,59,-22,-28")); Wait(1.2f); Shot(TEXT("spot_10_shed_tape_on_bench"));
			At(TEXT("at:3580,-745,59,149,-4")); Wait(1.0f); Shot(TEXT("spot_11_trash_can_standing"));
			At(TEXT("flag:tape1_taken")); Wait(0.8f); Shot(TEXT("spot_11b_trash_can_over"));
			At(TEXT("at:3140,-470,59,140,-18")); Wait(1.0f); Shot(TEXT("spot_11c_trash_close"));
			At(TEXT("at:366,-560,92,-90,-6")); Wait(1.2f); Shot(TEXT("spot_12_television_and_recorder"));
			At(TEXT("at:820,60,92,151,-4")); Wait(1.0f); Shot(TEXT("spot_13_frame_on_the_wall"));
			At(TEXT("flag:frame_fell")); Wait(0.8f); Shot(TEXT("spot_13b_frame_fallen"));
			At(TEXT("at:1320,470,92,-70,-6")); Wait(1.0f); Shot(TEXT("spot_14_kitchen_sink_side"));
			At(TEXT("at:592,-296,92,124,0")); Wait(1.0f);
			At(TEXT("book")); Wait(0.75f); Shot(TEXT("spot_9_book_coming_out"));'''),
])
print("pass 114 applied")
