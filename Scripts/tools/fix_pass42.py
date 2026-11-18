"""Bot: when the game returns to the menu after the credits, the test run is over (it was starting a second play-through)."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
R = "C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/"
edit(R + "WCDirector.cpp", [
    ('''	if ((bAuto && PendingStart == 0) || FParse::Param(FCommandLine::Get(), TEXT("WCNewGame"))) PendingStart = 1;''',
     '''	static int32 AutoRuns = 0;
	if (bAuto && PendingStart == 0 && AutoRuns > 0)
	{
		UE_LOG(LogWC, Display, TEXT("WCAUTO DONE back at the menu after a complete play-through"));
		FPlatformMisc::RequestExit(false);
		return;
	}
	if (bAuto) ++AutoRuns;
	if ((bAuto && PendingStart == 0) || FParse::Param(FCommandLine::Get(), TEXT("WCNewGame"))) PendingStart = 1;'''),
])
print("ok")
