"""Drive: Space skips it (for a second play-through); a hint says so."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
R = "C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/"
edit(R + "WCHouse.cpp", [
    ('''	TickDrive(0.f);
	UE_LOG(LogWCHouse, Display, TEXT("WCDRIVE begin: %.0f m of road"), DriveTotal / 100.f);''', '''	TickDrive(0.f);
	After(5.f, [this]() { if (bDriving) ShowHint(TEXT("Mouse: look around        Space: skip the drive"), 6.f); });
	UE_LOG(LogWCHouse, Display, TEXT("WCDRIVE begin: %.0f m of road"), DriveTotal / 100.f);'''),
    ('''	const float Left = DriveTotal - DriveDist;
	const float Want = Left < 2600.f''', '''	if (PC && PC->WasInputKeyJustPressed(EKeys::SpaceBar) && DriveDist > 200.f && DriveTotal - DriveDist > 3200.f)
	{
		// skipped: drop the rest of the radio traffic and roll up to the gate
		Steps.Reset();
		Subtitles.Reset();
		BigTarget = 0.f;
		HintUntil = 0.0;
		FadeTo(0.f, 1.f);
		DriveDist = DriveTotal - 3000.f;
	}
	const float Left = DriveTotal - DriveDist;
	const float Want = Left < 2600.f'''),
])
print("ok")
