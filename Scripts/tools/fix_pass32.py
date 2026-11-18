"""The single warm window (visible from the yard, goes dark at the knock); a tour option that switches every room light on."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
R = "C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/"
L = "C:/GameDev/Unreal/WellnessCheck/Scripts/level/"
edit(L + "import_assets.py", [
    ('''    flat_material("M_EyeBlack", (0.002, 0.002, 0.002), 0.05)''', '''flat_material("M_WindowWarm", (1.0, 0.6, 0.26), 0.6, emissive=float(os.environ.get("WC_WINDOW_GLOW", "2.6")))
    flat_material("M_EyeBlack", (0.002, 0.002, 0.002), 0.05)'''),
])
edit(L + "exterior.py", [
    ('''    if not (face == "-x" and y == 400 and z == UZ):
        # dark glass: nothing behind a window shows from the yard (the one exception is the lamp she leaves burning)
        piece("WinGlass_" + key, -61, 61, 92, 263, 2.2, "WC:M_Black", d0=5.5)''', '''if not (face == "-x" and y == 400 and z == UZ):
        # dark glass: nothing behind a window shows from the yard (the one exception is the lamp she leaves burning)
        piece("WinGlass_" + key, -61, 61, 92, 263, 2.2, "WC:M_Black", d0=5.5)
    else:
        # the one lit window: lamplight behind a torn blind.  It goes dark when he knocks (tag L_Welcome).
        piece("WinGlass_" + key, -61, 61, 92, 263, 1.0, "WC:M_Black", d0=4.2)
        for (a0, a1, b0, b1) in ((-58, -6, 96, 259), (-2, 58, 132, 259), (-2, 30, 96, 128)):
            lit = box(f"WinWarm_{key}_{a0}_{b0}", x + ox - 8.4, x + ox - 5.6, y + a0, y + a1, z + b0, z + b1, surf("GlowWarm", "M_WindowWarm"), EX + "/Windows", collide=False, shadow=False, tags=["L_Welcome"])
        box("WinWarmBar_" + key, x + ox - 9.4, x + ox - 8.4, y - 3, y + 3, z + 93, z + 262, M_TRIM, EX + "/Windows", collide=False, shadow=False)
        box("WinWarmBarH_" + key, x + ox - 9.4, x + ox - 8.4, y - 60, y + 60, z + 176, z + 181, M_TRIM, EX + "/Windows", collide=False, shadow=False)
        light_point("Lamp_WelcomeSpill", x + ox - 46, y, z + 190, 55, (1.0, 0.6, 0.28), 420, "Lights/Lamps", tags=["L_Welcome"], shadows=False, vol=1.2, source=10.0)'''),
])
edit(R + "WCAuto.cpp", [
    ('''		Wait(4.f);
		for (const FName& N : Names) { AutoSteps.Add({ A_Tele, N, 0.f }); Wait(2.6f); Shot(*N.ToString()); }''', '''if (FParse::Param(FCommandLine::Get(), TEXT("WCLights")))
		{
			for (TPair<FName, FRoomLights>& Rm : Rooms) SwitchRoom(Rm.Key, true, false);
			if (AWCCharacter* Pl = Player()) Pl->SetFlashlight(false, false);
		}
		Wait(4.f);
		for (const FName& N : Names) { AutoSteps.Add({ A_Tele, N, 0.f }); Wait(2.6f); Shot(*N.ToString()); }'''),
])
print("ok")
