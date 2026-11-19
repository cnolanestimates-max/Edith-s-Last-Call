"""Pass 110: a photo test of the new fetch spots from where a person stands (-WCHerLook -WCSpotOnly): the vent shut and open
with the doll, the jewelry box and screwdriver, the box open with the eye, the drawer key upstairs, the fuse, the desk open
with the keys and cartridges, and the settlers book coming out with her eye behind it at eye level."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
R = "C:/GameDev/Unreal/WellnessCheck/"
edit(R + "Source/WellnessCheck/WCAuto.cpp", [
    ('''		else if (FParse::Param(FCommandLine::Get(), TEXT("WCPeekOnly")))''', '''		else if (FParse::Param(FCommandLine::Get(), TEXT("WCSpotOnly")))
		{
			Set(TEXT("inside")); Set(TEXT("locked_in")); Set(TEXT("tv_first"));
			auto At = [this](const TCHAR* S) { AutoSteps.Add({ A_Do, S, 0.f }); };
			At(TEXT("at:1400,335,92,-90,-4")); Wait(1.2f); Shot(TEXT("spot_1_vent_shut"));
			At(TEXT("at:1400,300,92,-90,-8")); Wait(0.8f); Shot(TEXT("spot_1b_vent_shut_close"));
			At(TEXT("flag:vent_open")); Wait(0.8f); Shot(TEXT("spot_2_vent_open_doll"));
			At(TEXT("at:1400,335,92,-90,-14")); Wait(0.8f); Shot(TEXT("spot_2b_vent_open_from_further"));
			At(TEXT("at:625,330,442,-20,-28")); Wait(1.2f); Shot(TEXT("spot_3_jewelry_box_and_screwdriver"));
			At(TEXT("flag:box_open")); Wait(0.8f); Shot(TEXT("spot_4_box_open_letter_eye"));
			At(TEXT("flag:phone_done")); At(TEXT("at:1380,-372,442,90,-24")); Wait(1.2f); Shot(TEXT("spot_5_drawer_key_upstairs_bath"));
			At(TEXT("at:1130,-312,92,143,-26")); Wait(1.2f); Shot(TEXT("spot_6_fuse_in_sitting_room"));
			At(TEXT("flag:desk_open")); At(TEXT("at:2222,-300,92,-31,-24")); Wait(1.2f); Shot(TEXT("spot_7_desk_open_keys_cartridges"));
			At(TEXT("at:2215,-352,92,0,-22")); Wait(0.8f); Shot(TEXT("spot_7b_desk_from_the_front"));
			At(TEXT("at:640,-330,92,128,2")); Wait(1.2f); Shot(TEXT("spot_8_bookcase"));
			At(TEXT("at:592,-296,92,124,0")); Wait(1.0f); Shot(TEXT("spot_8b_at_the_book"));
			At(TEXT("book")); Wait(0.75f); Shot(TEXT("spot_9_book_coming_out")); Wait(0.3f); Shot(TEXT("spot_9b_her_eye")); Wait(0.5f); Shot(TEXT("spot_9c")); Wait(2.5f); Shot(TEXT("spot_9d_after"));
			Wait(2.f);
		}
		else if (FParse::Param(FCommandLine::Get(), TEXT("WCPeekOnly")))'''),
    ('''else if (S.Arg == TEXT("inspectdoll")) Event(TEXT("inspect:doll"));''', '''else if (S.Arg == TEXT("inspectdoll")) Event(TEXT("inspect:doll"));
		else if (S.Arg.ToString().StartsWith(TEXT("flag:"))) { Set(FName(*S.Arg.ToString().Mid(5))); ApplyWorldState(); }
		else if (S.Arg == TEXT("book")) { bBusy = false; ScareBook(); }'''),
])
print("pass 110 applied")
