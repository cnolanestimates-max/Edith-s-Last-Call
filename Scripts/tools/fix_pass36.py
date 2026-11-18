"""Look test also photographs the watchers and the bookshelf scare."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
R = "C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/"
L = "C:/GameDev/Unreal/WellnessCheck/Scripts/level/"
edit(L + "watchers.py", [
    ('''    a.set_editor_property("scripted", scripted)''', '''a.set_editor_property("scripted", scripted)
    tag(a, ["W_" + wid])'''),
])
edit(R + "WCAuto.cpp", [
    ('''		Set(TEXT("inside")); Set(TEXT("heard_upstairs")); Set(TEXT("peek_started")); Set(TEXT("peek_done")); Set(TEXT("briefed"));
		bBusy = true;                      // no story triggers during the test''', '''Set(TEXT("heard_upstairs")); Set(TEXT("peek_started")); Set(TEXT("peek_done")); Set(TEXT("briefed"));
		NotesRead.AddUnique(TEXT("note_deskkey"));
		bBusy = true;                      // no story triggers during the test'''),
    ('''			AutoSteps.Add({ A_Aim, NAME_None, 0.f }); Wait(0.8f); Shot(TEXT("gun_down_hand"));''', '''AutoSteps.Add({ A_Aim, NAME_None, 0.f }); Wait(0.8f); Shot(TEXT("gun_down_hand"));
			// she was there the whole time
			AutoSteps.Add({ A_Tele, TEXT("A_Foyer"), 0.f }); Wait(0.6f); AutoSteps.Add({ A_Look, TEXT("W_hall_stair"), 0.f }); Wait(0.3f); Shot(TEXT("watch_hall_eye"));
			AutoSteps.Add({ A_Tele, TEXT("A_Kitchen"), 0.f }); Wait(0.6f); AutoSteps.Add({ A_Look, TEXT("W_kitchen_fridge"), 0.f }); Wait(0.3f); Shot(TEXT("watch_kitchen_eye"));
			AutoSteps.Add({ A_Tele, TEXT("A_Living"), 0.f }); Wait(0.6f); AutoSteps.Add({ A_Look, TEXT("W_fireplace"), 0.f }); Wait(0.3f); Shot(TEXT("watch_fireplace_eye"));
			AutoSteps.Add({ A_Tele, TEXT("A_Sitting"), 0.f }); Wait(0.6f); AutoSteps.Add({ A_Look, TEXT("W_hair_sitting"), 0.f }); Wait(0.3f); Shot(TEXT("watch_hair_sitting"));
			AutoSteps.Add({ A_Tele, TEXT("N_hallF"), 0.f }); Wait(0.6f); AutoSteps.Add({ A_Look, TEXT("W_hair_backhall"), 0.f }); Wait(0.3f); Shot(TEXT("watch_hair_hall"));
			AutoSteps.Add({ A_Tele, TEXT("N_den_shelf"), 0.f }); Wait(0.6f); AutoSteps.Add({ A_Look, TEXT("SettlersBook"), 0.f }); Wait(0.3f); Shot(TEXT("book_before"));
			AutoSteps.Add({ A_Use, TEXT("book_settlers"), 0.f }); Wait(0.75f); Shot(TEXT("book_eye")); Wait(2.6f); Shot(TEXT("book_after"));'''),
])
print("ok")
