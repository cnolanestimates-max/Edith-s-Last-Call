"""Pass 90: darkness.  The moonlight through the boarded windows drops to under a third (Cheyenne: "everything else needs to be
dark"), and the upstairs hall window, which showed her outline from the stairs, all but goes out while she is at the doorway."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit

R = "C:/GameDev/Unreal/WellnessCheck/"
edit(R + "Scripts/level/lighting.py", [
    ('''m_ = light_spot(name + "_moon", x, y, z, yaw, pitch, 9000, (0.5, 0.63, 1.0), 900, 36, 62, "Lights/Windows", tags=["Hide_dawn"], shadows=True, vol=2.0)''',
     '''m_ = light_spot(name + "_moon", x, y, z, yaw, pitch, 2600, (0.5, 0.63, 1.0), 900, 36, 62, "Lights/Windows", tags=["Hide_dawn", name], shadows=True, vol=1.5)'''),
])
edit(R + "Source/WellnessCheck/WCStory.cpp", [
    ('''H->SetFarGlow(0.f);                 // barely there: only his own light, close to, finds her''',
     '''H->SetFarGlow(0.f);                 // barely there: only his own light, close to, finds her
	SetLightsTagged(TEXT("W_U_hall"), 0.04f);      // and no moonlit window behind her to give her outline away from the stairs'''),
    ('''if (AWCEntity* E = Her()) E->Vanish();
				if (AWCDoor* D = Door(TEXT("up_master"))) D->SetOpen(false, 2.8f);
				Set(TEXT("peek_done"));''', '''if (AWCEntity* E = Her()) E->Vanish();
				if (AWCDoor* D = Door(TEXT("up_master"))) D->SetOpen(false, 2.8f);
				SetLightsTagged(TEXT("W_U_hall"), 1.f);
				Set(TEXT("peek_done"));'''),
])
edit(R + "Source/WellnessCheck/WCAuto.cpp", [
    ('Set(TEXT("locked_in")); Set(TEXT("heard_upstairs")); Set(TEXT("tv_first"));', 'Set(TEXT("inside")); Set(TEXT("locked_in")); Set(TEXT("heard_upstairs")); Set(TEXT("tv_first"));'),
])
print("pass 90 applied")
