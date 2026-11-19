"""Pass 92: Cheyenne picked the VHS camcorder look (2026-11-19 14:39 UTC: "lets go with the vhs for now"; she also liked the
fisheye, so every look stays selectable).  It is a saved option, "Picture", in the options menu; VHS is the default."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit

R = "C:/GameDev/Unreal/WellnessCheck/"
edit(R + "Source/WellnessCheck/WCDirector.h", [
    ('bool bCameraShake = true;', 'bool bCameraShake = true;\n\tint32 Filter = 1;           // picture: 0 clean, 1 VHS camcorder (Cheyenne\'s pick), 2 old film, 3 cold, 4 fisheye bodycam, 5 night vision'),
])
edit(R + "Source/WellnessCheck/WCDirector.cpp", [
    ('GConfig->GetBool(Sec, TEXT("CameraShake"), bCameraShake, Ini);', 'GConfig->GetBool(Sec, TEXT("CameraShake"), bCameraShake, Ini);\n\tGConfig->GetInt(Sec, TEXT("Picture"), Filter, Ini);'),
    ('GConfig->SetBool(Sec, TEXT("CameraShake"), bCameraShake, Ini);', 'GConfig->SetBool(Sec, TEXT("CameraShake"), bCameraShake, Ini);\n\tGConfig->SetInt(Sec, TEXT("Picture"), Filter, Ini);'),
    ('''D->ApplyVolumes();
		if (AWCCharacter* P = D->Player()) P->ApplySettings();''', '''D->ApplyVolumes();
		if (AWCCharacter* P = D->Player()) P->ApplySettings();
		int32 Forced = 0;
		if (!FParse::Value(FCommandLine::Get(), TEXT("WCFilter="), Forced)) D->SetFilter(Filter);'''),
])
edit(R + "Source/WellnessCheck/WCHouse.cpp", [
    ('if (!bFilterInit) { bFilterInit = true; int32 L = 0; if (FParse::Value(FCommandLine::Get(), TEXT("WCFilter="), L)) SetFilter(L); }',
     'if (!bFilterInit) { bFilterInit = true; int32 L = Settings.Filter; FParse::Value(FCommandLine::Get(), TEXT("WCFilter="), L); SetFilter(L); }'),
])
edit(R + "Source/WellnessCheck/WCGame.cpp", [
    ('Add(TEXT("Camera shake"), OnOff(S.bCameraShake), TEXT("shake"));', '''Add(TEXT("Camera shake"), OnOff(S.bCameraShake), TEXT("shake"));
		static const TCHAR* Pic[6] = { TEXT("Clean"), TEXT("VHS camcorder"), TEXT("Old film"), TEXT("Cold"), TEXT("Fisheye bodycam"), TEXT("Night vision") };
		Add(TEXT("Picture"), Pic[FMath::Clamp(S.Filter, 0, 5)], TEXT("picture"));'''),
    ('else if (Id == TEXT("shake")) S.bCameraShake = !S.bCameraShake;', 'else if (Id == TEXT("shake")) S.bCameraShake = !S.bCameraShake;\n\telse if (Id == TEXT("picture")) S.Filter = (S.Filter + (Dir < 0 ? 5 : 1)) % 6;'),
])
print("pass 92 applied")
