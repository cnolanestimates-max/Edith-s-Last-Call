"""Stair test also stands on every flight and photographs what is above and below (Cheyenne: floors still cover the attic
and basement stairs).  New bot step: A_Do "at:x,y,z,yaw,pitch" puts him there, looking that way."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
R = "C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/"
edit(R + "WCAuto.cpp", [
    ('''		else if (S.Arg == TEXT("s7")) { bBusy = false; ScareUnderBed(); }''', '''		else if (S.Arg.ToString().StartsWith(TEXT("at:")))
		{
			TArray<FString> V;
			S.Arg.ToString().Mid(3).ParseIntoArray(V, TEXT(","));
			if (V.Num() >= 5)
			{
				P->TeleportToCheckpoint(FVector(FCString::Atof(*V[0]), FCString::Atof(*V[1]), FCString::Atof(*V[2])), FCString::Atof(*V[3]));
				if (AController* C = P->GetController()) C->SetControlRotation(FRotator(FCString::Atof(*V[4]), FCString::Atof(*V[3]), 0.f));
				P->SetFlashlight(true, false);
			}
		}
		else if (S.Arg == TEXT("s7")) { bBusy = false; ScareUnderBed(); }'''),
    ('''			AutoSteps.Add({ A_Tele, TEXT("A_Foyer"), 0.f }); Wait(1.5f);
			AutoSteps.Add({ A_Go, TEXT("N_up_land"), 0.f }); Shot(TEXT("stairs_1_up_landing"));''',
     '''			static const TCHAR* Views[][2] = {
				{ TEXT("at:150,-88,-258,0,8"), TEXT("view_01_cellar_hall_to_stairs") }, { TEXT("at:440,-88,-225,0,30"), TEXT("view_02_cellar_flight_foot_up") },
				{ TEXT("at:600,-88,-83,0,22"), TEXT("view_03_cellar_flight_mid_up") }, { TEXT("at:770,-88,62,180,-34"), TEXT("view_04_cellar_flight_top_down") },
				{ TEXT("at:930,70,92,-133,-4"), TEXT("view_05_hall_to_cellar_door") }, { TEXT("at:330,-88,92,0,24"), TEXT("view_06_main_flight_foot_up") },
				{ TEXT("at:600,-88,267,0,22"), TEXT("view_07_main_flight_mid_up") }, { TEXT("at:770,-88,412,180,-34"), TEXT("view_08_main_flight_top_down") },
				{ TEXT("at:330,-88,442,0,24"), TEXT("view_09_attic_flight_foot_up") }, { TEXT("at:600,-88,617,0,22"), TEXT("view_10_attic_flight_mid_up") },
				{ TEXT("at:770,-88,762,180,-34"), TEXT("view_11_attic_flight_top_down") }, { TEXT("at:1040,120,792,-140,-22"), TEXT("view_12_attic_to_stair_opening") },
				{ TEXT("at:600,-88,442,0,60"), TEXT("view_13_upstairs_in_well_look_up") }, { TEXT("at:600,-88,-258,0,60"), TEXT("view_14_cellar_in_well_look_up") } };
			for (const auto& Vw : Views) { AutoSteps.Add({ A_Do, Vw[0], 0.f }); Wait(0.9f); Shot(Vw[1]); }
			AutoSteps.Add({ A_Tele, TEXT("A_Foyer"), 0.f }); Wait(1.5f);
			AutoSteps.Add({ A_Go, TEXT("N_up_land"), 0.f }); Shot(TEXT("stairs_1_up_landing"));'''),
])
print("ok")
