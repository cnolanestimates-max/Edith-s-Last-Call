"""Look test also photographs a grab (her face in his, lit)."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
R = "C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/"
edit(R + "WCAuto.cpp", [
    ('''			AutoSteps.Add({ A_Do, TEXT("mem1"), 0.f }); Wait(10.5f);''', '''			AutoSteps.Add({ A_Tele, TEXT("A_Foyer"), 0.f }); Wait(1.0f); AutoSteps.Add({ A_Her, TEXT("Idle"), 400.f }); Wait(0.5f);
			AutoSteps.Add({ A_Do, TEXT("grab"), 0.f }); Wait(0.75f); Shot(TEXT("grab_face_1")); Wait(0.45f); Shot(TEXT("grab_face_2")); Wait(3.f);
			AutoSteps.Add({ A_Do, TEXT("mem1"), 0.f }); Wait(10.5f);'''),
    ('''		else if (S.Arg == TEXT("s7")) { bBusy = false; ScareUnderBed(); }''', '''		else if (S.Arg == TEXT("s7")) { bBusy = false; ScareUnderBed(); }
		else if (S.Arg == TEXT("grab"))
		{
			Set(TEXT("mem1")); Set(TEXT("mem2")); Set(TEXT("mem3"));
			Grab(1.35f, [this]() { if (AWCEntity* E = Her()) E->Vanish(); Flags.Remove(TEXT("mem1")); Flags.Remove(TEXT("mem2")); Flags.Remove(TEXT("mem3")); bBusy = true; });
		}'''),
])
print("ok")
