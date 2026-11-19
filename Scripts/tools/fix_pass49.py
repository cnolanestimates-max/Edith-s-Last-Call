"""Look test also shows: the Company silhouette, her drawings, the hand under the bed, and the three memories."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
R = "C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/"
edit(R + "WCAuto.cpp", [
    ('''enum { A_Go, A_Use, A_Wait, A_WaitFlag, A_Shot, A_Fire, A_Look, A_Light, A_LookHer, A_WaitHer, A_Crouch, A_Tele, A_Her, A_FaceItem, A_Aim };''',
     '''enum { A_Go, A_Use, A_Wait, A_WaitFlag, A_Shot, A_Fire, A_Look, A_Light, A_LookHer, A_WaitHer, A_Crouch, A_Tele, A_Her, A_FaceItem, A_Aim, A_Do };'''),
    ('''			AutoSteps.Add({ A_Tele, TEXT("Tour_00_yard"), 0.f }); Wait(1.5f); AutoSteps.Add({ A_Look, TEXT("A_Cruiser"), 0.f }); Wait(1.f); Shot(TEXT("cruiser"));''',
     '''			AutoSteps.Add({ A_Tele, TEXT("Tour_00_yard"), 0.f }); Wait(1.5f); AutoSteps.Add({ A_Look, TEXT("A_Cruiser"), 0.f }); Wait(1.f); Shot(TEXT("cruiser"));
			// the Company, her drawings, the hand under the bed, the three memories
			AutoSteps.Add({ A_Her, TEXT("Idle"), 3000.f });
			AutoSteps.Add({ A_Tele, TEXT("A_UpEll"), 0.f }); Wait(0.8f); AutoSteps.Add({ A_Look, TEXT("W_company_uprear"), -1.f }); Wait(0.2f); Shot(TEXT("company_uprear"));
			AutoSteps.Add({ A_Tele, TEXT("A_Sitting"), 0.f }); Wait(0.8f); AutoSteps.Add({ A_Do, TEXT("drawings"), 0.f }); Wait(0.8f); Shot(TEXT("drawings_wall"));
			AutoSteps.Add({ A_Tele, TEXT("A_Kids"), 0.f }); Wait(1.0f); AutoSteps.Add({ A_Do, TEXT("s7"), 0.f });
			Wait(3.6f); Shot(TEXT("hand_1_coming")); Wait(1.7f); Shot(TEXT("hand_2_on_box")); Wait(1.6f); Shot(TEXT("hand_3_taking")); Wait(3.6f);
			AutoSteps.Add({ A_Crouch, NAME_None, 1.f }); AutoSteps.Add({ A_Look, TEXT("pick_keep_ruth"), -1.f }); Wait(0.3f); Shot(TEXT("hand_4_box_under_bed")); AutoSteps.Add({ A_Crouch, NAME_None, 0.f });
			AutoSteps.Add({ A_Do, TEXT("mem1"), 0.f }); Wait(10.5f);
			AutoSteps.Add({ A_Do, TEXT("mem2"), 0.f }); Wait(10.5f);
			AutoSteps.Add({ A_Do, TEXT("mem3"), 0.f }); Wait(10.5f);'''),
    ('''	case A_Aim: P->SetAiming(S.F > 0.5f); Next(); return;''', '''	case A_Aim: P->SetAiming(S.F > 0.5f); Next(); return;
	case A_Do:
		if (S.Arg == TEXT("drawings"))
		{
			if (AController* C = P->GetController()) C->SetControlRotation((FVector(818.f, -430.f, P->GetActorLocation().Z + 72.f) - P->EyeLocation()).Rotation());
		}
		else if (S.Arg == TEXT("s7")) { bBusy = false; ScareUnderBed(); }
		else if (S.Arg == TEXT("mem1")) PlayMemory(1, [this]() { bBusy = true; });
		else if (S.Arg == TEXT("mem2")) PlayMemory(2, [this]() { bBusy = true; });
		else if (S.Arg == TEXT("mem3")) PlayMemory(3, [this]() { bBusy = true; });
		Next(); return;'''),
])
print("ok")
