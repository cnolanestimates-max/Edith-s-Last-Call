"""Test runs photograph the forest drive by themselves (one picture every 35 m), and -WCDriveOnly stops after the car parks."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
R = "C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/"
edit(R + "WCHouse.cpp", [
    ('''	DriveDist = FMath::Min(DriveTotal, DriveDist + DriveSpeed * Dt);''', '''	DriveDist = FMath::Min(DriveTotal, DriveDist + DriveSpeed * Dt);
	if (bAuto && !AutoShotDir.IsEmpty())
	{
		static int32 DriveShotN = -1;
		const int32 ShotN = (int32)(DriveDist / 3500.f);
		if (ShotN != DriveShotN) { DriveShotN = ShotN; FScreenshotRequest::RequestScreenshot(AutoShotDir / FString::Printf(TEXT("drive_%02d.png"), ShotN), false, false); }
	}'''),
    ('''	if (!bDriving) return;
	bDriving = false;
	Set(TEXT("arrived"));''', '''	if (!bDriving) return;
	bDriving = false;
	Set(TEXT("arrived"));
	if (FParse::Param(FCommandLine::Get(), TEXT("WCDriveOnly")))
	{
		const FString Dir0 = AutoShotDir;
		After(5.f, [Dir0]() { if (!Dir0.IsEmpty()) FScreenshotRequest::RequestScreenshot(Dir0 / TEXT("drive_parked.png"), false, false); });
		After(7.f, [this]() { UKismetSystemLibrary::QuitGame(this, UGameplayStatics::GetPlayerController(this, 0), EQuitPreference::Quit, false); });
	}'''),
    ('''#include "Kismet/GameplayStatics.h"''', '''#include "Kismet/GameplayStatics.h"
#include "Kismet/KismetSystemLibrary.h"'''),
])
print("ok")
