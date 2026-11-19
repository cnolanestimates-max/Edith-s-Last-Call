"""Forest drive, for filming: the driver sits a little higher so the hood takes less of the picture, the instrument glow
is enough to show the dash and wheel as shapes, and the steering wheel pieces vanish with the rest of the cabin when he
gets out.  -WCVideo=<dir> writes every frame of the opening (drive, then the walk up to the house) as numbered pictures."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
P = "C:/GameDev/Unreal/WellnessCheck/"
edit(P + "Scripts/level/forest.py", [
    ('''    cpart(beam(f"Wheel_{k}", wp(a0), wp(a1), 3.4, 3.4, DASH, wdir=(1, 0, 0), shadow=False, folder=CAB))''',
     '''    cpart(beam(f"Wheel_{k}", wp(a0), wp(a1), 3.4, 3.4, DASH, wdir=(1, 0, 0), shadow=False, folder=CAB, tags=["CabinOnly"]))'''),
    ('''cpart(beam("WheelSpoke", (CRX + WX, CRY - (WL - WR), -40 + WU), (CRX + WX, CRY - (WL + WR), -40 + WU), 3.0, 3.0, DASH, wdir=(1, 0, 0), shadow=False, folder=CAB))''',
     '''cpart(beam("WheelSpoke", (CRX + WX, CRY - (WL - WR), -40 + WU), (CRX + WX, CRY - (WL + WR), -40 + WU), 3.0, 3.0, DASH, wdir=(1, 0, 0), shadow=False, folder=CAB, tags=["CabinOnly"]))'''),
    ('''cpart(beam("WheelColumn", (CRX + WX, CRY - WL, -40 + WU), (CRX + 62, CRY - WL, -40 + 86), 7, 7, DASH, wdir=(0, 1, 0), shadow=False, folder=CAB))''',
     '''cpart(beam("WheelColumn", (CRX + WX, CRY - WL, -40 + WU), (CRX + 62, CRY - WL, -40 + 86), 7, 7, DASH, wdir=(0, 1, 0), shadow=False, folder=CAB, tags=["CabinOnly"]))'''),
    ('''cpart(point("DriverSeat", CRX + 6, CRY - 37, -40 + 119, 0, tags=["DriverSeat"], folder="Cruiser"))''',
     '''cpart(point("DriverSeat", CRX + 6, CRY - 37, -40 + 126, 0, tags=["DriverSeat"], folder="Cruiser"))'''),
    ('''cpart(light_point("DashGlow", CRX + 44, CRY - 37, -40 + 92, 0.16,''', '''cpart(light_point("DashGlow", CRX + 44, CRY - 37, -40 + 92, 5.0,'''),
    ('''cpart(light_point("CabinFill", CRX - 10, CRY - 10, -40 + 138, 0.55,''', '''cpart(light_point("CabinFill", CRX - 10, CRY - 10, -40 + 138, 30.0,'''),
])
R = P + "Source/WellnessCheck/"
edit(R + "WCHouse.cpp", [
    ('''void AWCDirector::HouseTick(float Dt)
{''', '''void AWCDirector::HouseTick(float Dt)
{
	{
		// -WCVideo=<dir>: every frame of the opening as a numbered picture (run with -UseFixedTimeStep -FPS=30)
		static FString VideoDir;
		static bool bVideoInit = false;
		static int32 VideoFrame = 0;
		if (!bVideoInit)
		{
			bVideoInit = true;
			if (FParse::Value(FCommandLine::Get(), TEXT("WCVideo="), VideoDir)) { VideoDir = FPaths::ConvertRelativePathToFull(VideoDir); IFileManager::Get().MakeDirectory(*VideoDir, true); }
		}
		if (!VideoDir.IsEmpty() && Mode == EWCMode::Playing && VideoFrame < 4500) FScreenshotRequest::RequestScreenshot(VideoDir / FString::Printf(TEXT("f_%05d.png"), VideoFrame++), false, false);
	}'''),
    ('''		After(5.f, [Dir0]() { if (!Dir0.IsEmpty()) FScreenshotRequest::RequestScreenshot(Dir0 / TEXT("drive_parked.png"), false, false); });
		After(7.f, [this]() { UKismetSystemLibrary::QuitGame(this, UGameplayStatics::GetPlayerController(this, 0), EQuitPreference::Quit, false); });''',
     '''		After(5.f, [Dir0]() { if (!Dir0.IsEmpty()) FScreenshotRequest::RequestScreenshot(Dir0 / TEXT("drive_parked.png"), false, false); });
		// when filming, stay until he has walked up to the house
		After(FParse::Param(FCommandLine::Get(), TEXT("WCFilm")) ? 34.f : 7.f, [this]() { UKismetSystemLibrary::QuitGame(this, UGameplayStatics::GetPlayerController(this, 0), EQuitPreference::Quit, false); });'''),
    ('''#include "Kismet/KismetSystemLibrary.h"''', '''#include "Kismet/KismetSystemLibrary.h"
#include "HAL/FileManager.h"'''),
])
print("ok")
