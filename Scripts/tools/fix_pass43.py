"""Pistol: the model's barrel is its -X (it was aimed back at the player, then off to the right): turn it round; darker sleeve.
Book scare: shelf lower so the flashlight is not shadowed by the board; no flicker until the eye has been seen.
Test runs photograph every grab and memory."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
R = "C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/"
L = "C:/GameDev/Unreal/WellnessCheck/Scripts/level/"
edit(R + "WCCharacter.cpp", [
    ('''	Gun->SetRelativeRotation(FRotator(0.f, -96.f, 0.f));''', '''	Gun->SetRelativeRotation(FRotator(0.f, 173.f, 0.f));'''),
])
edit(L + "import_more.py", [('''unreal.LinearColor(0.50, 0.46, 0.44, 1))''', '''unreal.LinearColor(0.26, 0.23, 0.22, 1))''')])
edit(L + "watchers.py", [('''BKX0, BKX1, BKY, BKZ = 2168.0, 2322.0, -216.0, GZ + 138.0''', '''BKX0, BKX1, BKY, BKZ = 2168.0, 2322.0, -216.0, GZ + 104.0''')])
edit(R + "WCHouse.cpp", [
    ('''#include "Engine/PostProcessVolume.h"''', '''#include "Engine/PostProcessVolume.h"
#include "UnrealClient.h"
#include "Misc/Paths.h"'''),
    ('''		if (Pl) { Pl->AddShake(0.9f); Pl->FlickerLight(0.5f, 0.85f); }
		Tension = 1.f;''', '''		if (Pl) { Pl->AddShake(0.9f); Pl->SetLightScale(1.f); }
		Tension = 1.f;'''),
    ('''	GrabHoldUntil = Clock + Hold;''', '''	GrabHoldUntil = Clock + Hold;
	if (bAuto && !AutoShotDir.IsEmpty())
	{
		static int32 GrabShots = 0;
		const FString File = AutoShotDir / FString::Printf(TEXT("grab_%02d.png"), ++GrabShots);
		After(FMath::Min(0.85f, Hold * 0.7f), [File]() { FScreenshotRequest::RequestScreenshot(File, false, false); });
	}'''),
    ('''		Say(FName(*FString::Printf(TEXT("m_mem%d"), N)), 1.8f);
	});''', '''		Say(FName(*FString::Printf(TEXT("m_mem%d"), N)), 1.8f);
	});
	if (bAuto && !AutoShotDir.IsEmpty())
	{
		const FString File = AutoShotDir / FString::Printf(TEXT("memory_%d.png"), N);
		After(4.4f, [File]() { FScreenshotRequest::RequestScreenshot(File, false, false); });
	}'''),
])
print("ok")
