"""Look test: hold the pistol up for a picture, hall light on, and a close-up of her scream."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
R = "C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/"
edit(R + "WCAuto.cpp", [
    ('''A_Tele, A_Her, A_FaceItem };''', '''A_Tele, A_Her, A_FaceItem, A_Aim };'''),
    ('''			AutoSteps.Add({ A_Fire, NAME_None, 0.f }); Wait(1.2f); Shot(TEXT("gun_up"));''',
     '''AutoSteps.Add({ A_Her, TEXT("Run"), 135.f });
			Wait(0.9f); AutoSteps.Add({ A_LookHer, NAME_None, 0.5f }); Shot(TEXT("her_scream_close"));
			AutoSteps.Add({ A_Her, TEXT("Lunge"), 240.f });
			Wait(0.5f); AutoSteps.Add({ A_LookHer, NAME_None, 0.2f }); Shot(TEXT("her_scream_mid"));
			AutoSteps.Add({ A_Her, TEXT("Idle"), 420.f });
			AutoSteps.Add({ A_Aim, NAME_None, 1.f }); Wait(1.4f); Shot(TEXT("gun_up"));
			AutoSteps.Add({ A_Look, TEXT("A_Living"), 0.f }); Wait(0.4f); Shot(TEXT("gun_up_turn"));
			AutoSteps.Add({ A_Aim, NAME_None, 0.f }); Wait(0.8f); Shot(TEXT("gun_down_hand"));'''),
    ('''	case A_Tele:
		if (AActor* T = AutoTarget(this, S.Arg))''', '''case A_Aim: P->SetAiming(S.F > 0.5f); Next(); return;
	case A_Tele:
		if (AActor* T = AutoTarget(this, S.Arg))'''),
    ('''		if (AWCCharacter* Pl = Player()) { Pl->SetInputLocked(false); Pl->SetFlashlight(true, false); }
		Fade = 0.f; FadeTarget = 0.f;
		Wait(4.f);
		if (FParse::Param(FCommandLine::Get(), TEXT("WCHerLook")))''', '''if (AWCCharacter* Pl = Player()) { Pl->SetInputLocked(false); Pl->SetFlashlight(true, false); }
		Fade = 0.f; FadeTarget = 0.f;
		SwitchRoom(TEXT("hall"), true, false);
		Wait(4.f);
		if (FParse::Param(FCommandLine::Get(), TEXT("WCHerLook")))'''),
])
print("ok")
