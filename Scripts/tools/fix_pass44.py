"""Hunt catch: what follows the grab is timed from the end of the grab (and of any memory), not from the catch.
Memories a little less blown out."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
R = "C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/"
L = "C:/GameDev/Unreal/WellnessCheck/Scripts/level/"
edit(R + "WCHouse.cpp", [
    ('''			Grab(1.35f, [this]() { if (AWCCharacter* Pl = Player()) Pl->Knockdown(3.4f); FadeTo(1.f, 0.3f); After(0.7f, [this]() { if (AWCEntity* E = Her()) E->Vanish(); }); });
			if (Catches >= 3)
			{
				After(3.0f, [this]() { BigText = TEXT("You stayed."); BigSub = TEXT(""); BigTarget = 1.f; });
				After(7.4f, [this]() { RestartFromCheckpoint(); });
			}
			else
			{
				After(4.6f, [this]() { FadeTo(0.f, 1.8f); Think(Catches <= 1 ? TEXT("She had me. She let go.") : TEXT("Not again. Next time she keeps me.")); });
			}''', '''Grab(1.35f, [this]()
			{
				if (AWCCharacter* Pl = Player()) Pl->Knockdown(Catches >= 3 ? 9.f : 3.4f);
				FadeTo(1.f, 0.3f);
				After(0.7f, [this]() { if (AWCEntity* E = Her()) E->Vanish(); });
				if (Catches >= 3)
				{
					After(1.6f, [this]() { BigText = TEXT("You stayed."); BigSub = TEXT(""); BigTarget = 1.f; });
					After(6.0f, [this]() { RestartFromCheckpoint(); });
				}
				else
				{
					After(3.2f, [this]() { FadeTo(0.f, 1.8f); Think(Catches <= 1 ? TEXT("She had me. She let go.") : TEXT("Not again. Next time she keeps me.")); });
				}
			});'''),
])
edit(L + "memory.py", [
    ('''mem_light("Mem1_Sun", 60, 0, GZ + 190, 26000, "Mem1", (1.0, 0.86, 0.66), 1300)''', '''mem_light("Mem1_Sun", 60, 0, GZ + 190, 11000, "Mem1", (1.0, 0.86, 0.66), 1300)'''),
    ('''grade("Grade_Memory", NIGHT_EV + 3.2, [''', '''grade("Grade_Memory", NIGHT_EV + 2.5, ['''),
    ('''("vignette_intensity", 0.9), ("film_grain_intensity", 0.5), ("bloom_intensity", 2.4),''', '''("vignette_intensity", 0.9), ("film_grain_intensity", 0.5), ("bloom_intensity", 1.6),'''),
])
print("ok")
