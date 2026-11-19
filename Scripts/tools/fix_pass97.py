"""Pass 97: outside first (Cheyenne 2026-11-19 14:50 UTC).
"He shows up in his cop car and then immediately goes inside.  I would like an investigation prompt ... investigate the outside of
the house first ... more time and ambience.  An old shed out in the back, fill it with shovels and a rake on the wall, just
nasty, just old ... he turns around and there's nothing there, it's just the house from the back, dark ... a back door, maybe
the back door will be locked ... goes around in the front and then he goes into the house ... You'll have to create the tree
line for the backyard ... another 5 minutes or so."

  - the whole yard is open now, fenced, with a tree line behind and beside it
  - an old tool shed in the back corner, its door hanging open: bench, barrels, crates, shovels, a pitchfork, a rake on the wall
  - the first knock at the front door gets no answer (the one lit window goes dark); the objective sends him round the back;
    the back door is locked; once he has been in the shed and tried the back door, the front door opens to his knock as before
  - no figure in any window (she decided against it)"""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit

R = "C:/GameDev/Unreal/WellnessCheck/"

# ---------------------------------------------------------------- the level
edit(R + "Scripts/level/exterior.py", [
    ('''# invisible limits: the front yard only (the story keeps him at the house)
for name, (x0, x1, y0, y1) in {"LimFront": (-2460, -2440, -1100, 1100), "LimLeft": (-2460, 60, -1100, -1080), "LimRight": (-2460, 60, 1080, 1100),
                                "LimHouseL": (-60, -40, -1100, -640), "LimHouseR": (840, 860, 900, 1100), "LimHouseR2": (-60, 860, 1080, 1100)}.items():
    box(name, x0, x1, y0, y1, -40, 400, "WC:M_Collision", EX, hidden=True)''',
     '''# invisible limits: the whole yard, front and back (he looks round the outside before he goes in)
YARD_BACK = XB + 1460.0
for name, (x0, x1, y0, y1) in {"LimFront": (-2460, -2440, -1100, 1100), "LimLeft": (-2460, YARD_BACK + 20, -1100, -1080), "LimRight": (-2460, YARD_BACK + 20, 1080, 1100),
                                "LimBack": (YARD_BACK, YARD_BACK + 20, -1100, 1100)}.items():
    box(name, x0, x1, y0, y1, -40, 400, "WC:M_Collision", EX, hidden=True)'''),
    ('''for i in range(12):
    place("Fence_Wood_Old", -2340 + i * 200, -1080, -40, 0, EX + "/Yard")
    place("Fence_Wood_Broken_01" if i % 4 == 2 else "Fence_Wood_Old", -2340 + i * 200, 1080, -40, 0, EX + "/Yard")''',
     '''for i in range(34):
    if -2340 + i * 200 > YARD_BACK:
        break
    place("Fence_Wood_Broken_01" if i % 5 == 3 else "Fence_Wood_Old", -2340 + i * 200, -1080, -40, 0, EX + "/Yard")
    place("Fence_Wood_Broken_01" if i % 4 == 2 else "Fence_Wood_Old", -2340 + i * 200, 1080, -40, 0, EX + "/Yard")
for i in range(11):
    place("Fence_Wood_Broken_01" if i in (3, 7) else "Fence_Wood_Old", YARD_BACK, -1000 + i * 200, -40, 90, EX + "/Yard")'''),
    ('''log("exterior done")''', '''# ================================================================== THE BACK YARD: a tree line, and the tool shed
import random as _rnd
_tr = _rnd.Random(41)
_KT = ["Tree_Twisted_03", "Tree_Dead_Tall_Snag", "Tree_Twisted_05", "Tree_Hanging_Moss", "Tree_Twisted_01", "Tree_Twisted_06", "Tree_Graveyard_Dead", "Tree_Leaning_Swamp",
       "Tree_Graveyard_Gnarled_Willow"]
_n = 0
# two ragged ranks outside the fence down both sides (from the front corner back), three deep along the back
for _x in range(-200, int(YARD_BACK) + 700, 230):
    for _side in (-1, 1):
        for _rank, _off in ((0, 1190), (1, 1480), (2, 1800)):
            if _rank == 2 and _tr.random() < 0.4:
                continue
            place(_tr.choice(_KT), _x + _tr.uniform(-90, 90), _side * (_off + _tr.uniform(-70, 110)), -46, _tr.uniform(0, 360), EX + "/TreeLine",
                  scale=_tr.uniform(1.7, 2.6), collide=False)
            _n += 1
for _y in range(-1900, 1901, 220):
    for _rank, _off in ((0, 150), (1, 430), (2, 760)):
        place(_tr.choice(_KT), YARD_BACK + _off + _tr.uniform(-80, 110), _y + _tr.uniform(-90, 90), -46, _tr.uniform(0, 360), EX + "/TreeLine",
              scale=_tr.uniform(1.8, 2.8), collide=False)
        _n += 1
log(f"tree line: {_n} trees")
for _i in range(26):                                                     # brambles and rocks along the fences and in the long grass
    _x, _y = _tr.uniform(200, YARD_BACK - 80), _tr.choice((-1, 1)) * _tr.uniform(760, 1040)
    place(("Bramble_Bush_Dead", "Bush_Thorny_Dead", "Rock_Fog_Small")[_i % 3], _x, _y, -41, _tr.uniform(0, 360), EX + "/BackYard", scale=_tr.uniform(0.9, 1.5), collide=False)
for _i in range(10):
    place(("Bramble_Bush_Dead", "Rock_Cluster_Mossy")[_i % 2], _tr.uniform(XB + 500, YARD_BACK - 100), _tr.uniform(-900, 900), -41, _tr.uniform(0, 360), EX + "/BackYard",
          scale=_tr.uniform(0.9, 1.4), collide=False)
place("Wheelbarrow_Old", XB + 610, -330, -40, 70, EX + "/BackYard")
place("Stump_Axe", XB + 520, 520, -40, 30, EX + "/BackYard")
place("Woodpile_Rotten", XB + 380, 760, -40, 0, EX + "/BackYard")
place("Barrel_Tipped_Spilled", XB + 300, -520, -40, 20, EX + "/BackYard")
place("Tree_Graveyard_Dead", XB + 900, 420, -45, 200, EX + "/BackYard", scale=1.8, collide=False)

# ---- the shed: back left corner, door toward the house.  Boards, a rusted roof, forty years of tools.
SH = EX + "/Shed"
SX0, SX1, SY0, SY1 = XB + 760.0, XB + 1140.0, -900.0, -580.0
box("ShedFloor", SX0, SX1, SY0, SY1, -40, -33, M_PFLOOR, SH, tags=["Floor_Wood"])
box("ShedWallS", SX0, SX1, SY0, SY0 + 8, -40, 200, M_ROT, SH)
box("ShedWallN", SX0, SX1, SY1 - 8, SY1, -40, 200, M_ROT, SH)
box("ShedWallE", SX1 - 8, SX1, SY0, SY1, -40, 200, M_ROT, SH)
_DY0, _DY1 = -790.0, -700.0                                              # the doorway, in the wall that faces the house
box("ShedWallW_a", SX0, SX0 + 8, SY0, _DY0, -40, 200, M_ROT, SH)
box("ShedWallW_b", SX0, SX0 + 8, _DY1, SY1, -40, 200, M_ROT, SH)
box("ShedLintel", SX0, SX0 + 8, _DY0, _DY1, 158, 200, M_ROT, SH)
box("ShedDoor", SX0 - 84, SX0, _DY1 - 2, _DY1 + 5, -34, 156, M_SHUT, SH, yaw=-14)        # hanging open on one hinge
for _k, _y in enumerate((-880, -850, -660, -612)):                       # boards gone: black gaps you can see the yard through
    box(f"ShedGap_{_k}", SX0 - 1, SX0 + 9, _y, _y + 9, 20 + 30 * (_k % 2), 190, "WC:M_Void" if False else M_SHUT, SH, collide=False, shadow=False)
_ridge = (SY0 + SY1) / 2
beam("ShedRoofS", ((SX0 + SX1) / 2, _ridge, 292), ((SX0 + SX1) / 2, SY0 - 30, 192), SX1 - SX0 + 50, 6, M_ROOF, wdir=(1, 0, 0))
beam("ShedRoofN", ((SX0 + SX1) / 2, _ridge, 292), ((SX0 + SX1) / 2, SY1 + 30, 192), SX1 - SX0 + 50, 6, M_ROOF, wdir=(1, 0, 0))
gable_tri("ShedGableW", "y", SX0 + 4, SY0, SY1, 200, 92, M_ROT, thick=8.0, step=32.0)
gable_tri("ShedGableE", "y", SX1 - 4, SY0, SY1, 200, 92, M_ROT, thick=8.0, step=32.0)
# inside: a bench under the back wall, barrels and crates, what is left on the shelves
box("ShedBenchTop", SX1 - 78, SX1 - 10, SY0 + 40, SY1 - 40, 44, 50, M_ROT, SH)
for _k, (_x, _y) in enumerate(((SX1 - 74, SY0 + 44), (SX1 - 16, SY0 + 44), (SX1 - 74, SY1 - 44), (SX1 - 16, SY1 - 44))):
    box(f"ShedBenchLeg_{_k}", _x - 4, _x + 4, _y - 4, _y + 4, -33, 44, M_ROT, SH, collide=False)
box("ShedShelf", SX0 + 60, SX1 - 110, SY1 - 30, SY1 - 8, 118, 122, M_ROT, SH, collide=False)
place("Tin_Cans_Rusty", SX0 + 150, SY1 - 20, 122, 30, SH, collide=False)
place("Paint_Can_Spilled", SX0 + 230, SY1 - 20, 122, 200, SH, collide=False)
place("Flashlight_Camping_Lantern", SX1 - 44, SY0 + 90, 50, 40, SH, collide=False)
place("Tin_Cans_Rusty", SX1 - 40, SY1 - 90, 50, 110, SH, collide=False)
place("Bucket_Rusty", SX1 - 46, _ridge + 10, 50, 0, SH, collide=False)
place("Barrel_Old", SX0 + 60, SY1 - 60, -33, 0, SH)
place("Crate_Wood_Small", SX0 + 150, SY1 - 62, -33, 20, SH)
place("Crate_Wood_Open", SX0 + 250, SY1 - 70, -33, 80, SH)
place("Planks_Pile", SX1 - 150, SY0 + 46, -33, 0, SH, collide=False)
place("Box_Cardboard_Stack", SX1 - 60, SY1 - 30, -33, 10, SH, collide=False)
place("Cobweb_Corner", SX1 - 12, SY1 - 12, 150, 180, SH, collide=False)
place("Cobweb_Corner", SX0 + 14, SY0 + 14, 150, 0, SH, collide=False)
# the tools on the south wall: two shovels, a pitchfork, a pickaxe, and a rake hung on nails
for _k, (_m, _x, _pitch) in enumerate((("Shovel", SX0 + 90, 0), ("Shovel", SX0 + 130, 0), ("Pitchfork_Rusty", SX0 + 180, 0), ("Pickaxe", SX0 + 235, 0))):
    place(_m, _x, SY0 + 18, -33, 90 + 12 * (_k % 2), SH, collide=False, roll=6)
beam("RakeHandle", (SX0 + 300, SY0 + 12, 8), (SX0 + 296, SY0 + 12, 178), 3.2, 3.2, M_ROT, wdir=(1, 0, 0), collide=False)
box("RakeHead", SX0 + 276, SX0 + 316, SY0 + 10, SY0 + 13, 176, 180, "Rust", SH, collide=False)
for _k in range(9):
    box(f"RakeTine_{_k}", SX0 + 277.5 + _k * 4.5, SX0 + 278.7 + _k * 4.5, SY0 + 10, SY0 + 12, 168, 177, "Rust", SH, collide=False)
for _k in range(3):
    box(f"WallNail_{_k}", SX0 + 110 + _k * 60, SX0 + 111 + _k * 60, SY0 + 8, SY0 + 13, 150, 151, "Rust", SH, collide=False, shadow=False)
point("A_Shed", SX0 - 140, (_DY0 + _DY1) / 2, GZ, 0, folder="Auto")
point("A_ShedIn", SX0 + 110, (_DY0 + _DY1) / 2, -33, 0, folder="Auto")
point("A_BackStoop", XB + 190, 0, 0, 180, folder="Auto")
point("A_BackYard", XB + 620, 60, GZ, 180, folder="Auto")
trigger("t_shed", SX0 + 30, SX1 - 10, SY0 + 10, SY1 - 10, -40, 190)
log("exterior done")'''),
])
edit(R + "Scripts/level/looks.py", [
    ('''    ("bulkhead", 1000, 715, 10,''', '''    ("shed_bench", 3896, -740, 62, "Seed packets gone to pulp, twine, a coffee can of nails rusted into one lump. Walter's bench. Nobody has stood at it in years.", (40, 110, 26)),
    ("shed_tools", 2800 + 760 + 190, -884, 90, "Shovels, a pitchfork, a rake. One nail has nothing hanging on it, and the dust under it is not as thick.", (130, 14, 80)),
    ("bulkhead", 1000, 715, 10,'''),
])

# ---------------------------------------------------------------- the story
edit(R + "Source/WellnessCheck/WCStory.cpp", [
    ('''After(bAuto ? 0.5f : T, [this]() { SetObjective(TEXT("Check on Edith Harrow")); Set(TEXT("briefed")); });''',
     '''After(bAuto ? 0.5f : T, [this]()
	{
		// the test bot goes straight in; a person looks round the outside first
		if (bAuto && !FParse::Param(FCommandLine::Get(), TEXT("WCOutside"))) { Set(TEXT("shed_seen")); Set(TEXT("back_tried")); Set(TEXT("knocked_first")); SetObjective(TEXT("Check on Edith Harrow")); }
		else SetObjective(TEXT("Check on Edith Harrow. Take a look round the outside first."));
		Set(TEXT("briefed"));
	});'''),
    ('''if (Is(Id, TEXT("locked:front")))
	{
		if (!Has(TEXT("knocked")))
		{''', '''if (Is(Id, TEXT("trig:t_shed")) && !Has(TEXT("shed_seen")))
	{
		Set(TEXT("shed_seen"));
		OutsideProgress();
		return;
	}
	if (Is(Id, TEXT("locked:back")) && !Has(TEXT("inside")))
	{
		if (Clock > SpeechFreeAt) { SpeechFreeAt = Clock + 4.0; Feedback(TEXT("Locked.")); }
		if (!Has(TEXT("back_tried")))
		{
			Set(TEXT("back_tried"));
			// the house is not empty: one slow board, somewhere inside, after he lets go of the handle
			After(2.6f, [this]() { PlayAt(TEXT("creak"), Pos(TEXT("FrontDoorPoint")) + FVector(1900, 0, 120), 0.8f, 0.8f, 2600.f); });
			OutsideProgress();
		}
		return;
	}
	if (Is(Id, TEXT("locked:front")) && !Has(TEXT("inside")) && !(Has(TEXT("shed_seen")) && Has(TEXT("back_tried"))))
	{
		// the first knock: nobody comes.  The one lit window goes dark.
		if (!Has(TEXT("knocked_first")))
		{
			Set(TEXT("knocked_first"));
			PlayAt(TEXT("knock"), Pos(TEXT("FrontDoorPoint")), 1.f);
			After(2.4f, [this]() { ShowTagged(TEXT("L_Welcome"), false); });
			const float T = Say(TEXT("d_knock"), 0.9f);
			After(T + 2.5f, [this]() { OutsideProgress(); });
		}
		else if (Clock > SpeechFreeAt) { SpeechFreeAt = Clock + 5.0; PlayAt(TEXT("knock"), Pos(TEXT("FrontDoorPoint")), 0.9f); Feedback(TEXT("No answer.")); }
		return;
	}
	if (Is(Id, TEXT("locked:front")))
	{
		if (!Has(TEXT("knocked")))
		{'''),
    ('''// ---------------------------------------------------------------------------------------------- events
static bool Is(FName Id, const TCHAR* S) { return Id == S; }''',
     '''// ---------------------------------------------------------------------------------------------- events
static bool Is(FName Id, const TCHAR* S) { return Id == S; }

/** Outside, before he goes in: what is left to look at (the shed, the back door), then round to the front. */
void AWCDirector::OutsideProgress()
{
	if (Has(TEXT("inside"))) return;
	const bool bShed = Has(TEXT("shed_seen")), bBack = Has(TEXT("back_tried"));
	if (bShed && bBack) SetObjective(TEXT("Go back round to the front door"));
	else if (Has(TEXT("knocked_first")) && !bShed && !bBack) SetObjective(TEXT("No answer. Look round the back of the house."));
	else if (bShed) SetObjective(TEXT("Try the back door"));
	else if (bBack) SetObjective(TEXT("Look in the shed"));
	UE_LOG(LogWCStory, Display, TEXT("WCOUTSIDE t=%.1f shed %d back door %d"), PlaySeconds, bShed ? 1 : 0, bBack ? 1 : 0);
}'''),
])
edit(R + "Source/WellnessCheck/WCDirector.h", [
    ('void AtticTagsTaken();', 'void AtticTagsTaken();\n\tvoid OutsideProgress();'),
])

# ---------------------------------------------------------------- photographs of the back yard and the shed
edit(R + "Source/WellnessCheck/WCAuto.cpp", [
    ('''else if (FParse::Param(FCommandLine::Get(), TEXT("WCFilterShots")))''',
     '''else if (FParse::Param(FCommandLine::Get(), TEXT("WCOutsideOnly")))
		{
			AutoSteps.Add({ A_Do, TEXT("filter:0"), 0.f });
			AutoSteps.Add({ A_Do, TEXT("at:2950,-800,52,3,2"), 0.f }); Wait(1.5f); Shot(TEXT("out_1_side_of_house_to_shed"));
			AutoSteps.Add({ A_Tele, TEXT("A_Shed"), 0.f }); Wait(1.0f); AutoSteps.Add({ A_Look, TEXT("A_ShedIn"), 0.f }); Wait(0.6f); Shot(TEXT("out_2_shed_door"));
			AutoSteps.Add({ A_Do, TEXT("at:3760,-720,59,-90,-6"), 0.f }); Wait(1.0f); Shot(TEXT("out_3_shed_tools_wall"));
			AutoSteps.Add({ A_Do, TEXT("at:3700,-740,59,0,-10"), 0.f }); Wait(0.8f); Shot(TEXT("out_4_shed_bench"));
			AutoSteps.Add({ A_Do, TEXT("at:3740,-770,59,90,2"), 0.f }); Wait(0.8f); Shot(TEXT("out_5_shed_shelf"));
			AutoSteps.Add({ A_Do, TEXT("at:3470,-745,52,168,7"), 0.f }); Wait(1.0f); Shot(TEXT("out_6_turn_round_house_from_the_back"));
			AutoSteps.Add({ A_Do, TEXT("at:3180,0,60,180,2"), 0.f }); Wait(1.0f); Shot(TEXT("out_7_back_door"));
			AutoSteps.Add({ A_Do, TEXT("at:3900,300,52,20,4"), 0.f }); Wait(1.0f); Shot(TEXT("out_8_back_fence_and_trees"));
			AutoSteps.Add({ A_Do, TEXT("at:1400,-900,52,0,3"), 0.f }); Wait(1.0f); Shot(TEXT("out_9_left_side_yard"));
			AutoSteps.Add({ A_Do, TEXT("filter:1"), 0.f }); AutoSteps.Add({ A_Do, TEXT("at:3470,-745,52,168,7"), 0.f }); Wait(1.0f); Shot(TEXT("out_10_house_from_the_back_vhs"));
			Wait(1.f);
		}
		else if (FParse::Param(FCommandLine::Get(), TEXT("WCFilterShots")))'''),
])
print("pass 97 applied")
