"""CRITICAL (found by walking the cellar stairs for the first time): the house's foundation slab (z -40..0) and the forest
ground (z -70..-41) both ran straight across the stairwell, so nobody could climb out of the cellar: his head hit them a
quarter of the way up.  In every run so far he was thrown down the stairs by the script and teleported out by the bot, so
it was never walked.  The game ends with him walking out at dawn; this would have stopped a player at the very end.
Both slabs are now cut away over the stair tower (and over the rotted hole in the ground floor)."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
P = "C:/GameDev/Unreal/WellnessCheck/"
edit(P + "Scripts/level/exterior.py", [
    ('''box("Foundation", -60, XB + 60, -660, 660, -40, 0, M_STONE, EX)''',
     '''_open = [(SX0, SX1, SY0, SY1 + 16)] + list(HOLES.get(GZ, []))          # where the house is open to the cellar below
_rects = [(-60, XB + 60, -660, 660)]
for _h in _open:
    _rects = cut(_rects, _h)
for _i, (_a, _b, _c, _d) in enumerate(_rects):
    box(f"Foundation_{_i}", _a, _b, _c, _d, -40, 0, M_STONE, EX)'''),
    ('''box("ForestGround", -40000, 9000, -9000, 9000, -70, -41, M_FOREST, EX, tags=["Floor_Gravel"])''',
     '''_rects = [(-40000, 9000, -9000, 9000)]
for _h in _open:
    _rects = cut(_rects, _h)
for _i, (_a, _b, _c, _d) in enumerate(_rects):
    box(f"ForestGround_{_i}", _a, _b, _c, _d, -70, -41, M_FOREST, EX, tags=["Floor_Gravel"])'''),
])
edit(P + "Source/WellnessCheck/WCAuto.cpp", [
    ('''			AutoSteps.Add({ A_Tele, TEXT("N_c_bot"), 0.f }); Wait(1.5f); Shot(TEXT("stairs_cellar_foot"));
			AutoSteps.Add({ A_Go, TEXT("A_Foyer"), 0.f }); Shot(TEXT("stairs_after"));
			AutoSteps.Add({ A_Tele, TEXT("N_stairs_g"), 0.f }); Wait(1.f); AutoSteps.Add({ A_Go, TEXT("N_up_land"), 0.f }); Shot(TEXT("stairs_up_land"));
			AutoSteps.Add({ A_Go, TEXT("N_c_bot"), 0.f }); Shot(TEXT("stairs_down_to_cellar")); Wait(1.f);''',
     '''			if (AWCDoor* Ad = Door(TEXT("up_attic"))) { Ad->SetLocked(false); Ad->SetOpen(true, 0.1f, true); }
			AutoSteps.Add({ A_Tele, TEXT("A_Foyer"), 0.f }); Wait(1.5f);
			AutoSteps.Add({ A_Go, TEXT("N_up_land"), 0.f }); Shot(TEXT("stairs_1_up_landing"));
			AutoSteps.Add({ A_Go, TEXT("N_attic_top"), 0.f }); Shot(TEXT("stairs_2_attic_top"));
			AutoSteps.Add({ A_Go, TEXT("N_c_bot"), 0.f }); Shot(TEXT("stairs_3_cellar_foot"));
			AutoSteps.Add({ A_Go, TEXT("A_Foyer"), 0.f }); Shot(TEXT("stairs_4_back_in_foyer")); Wait(1.f);'''),
])
print("ok")
