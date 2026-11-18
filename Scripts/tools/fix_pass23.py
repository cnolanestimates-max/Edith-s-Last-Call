"""Stalks start inside the house only, and never right on the heels of a scripted scare."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
R = "C:/GameDev/Unreal/WellnessCheck/Source/WellnessCheck/"
edit(R + "WCHouse.cpp", [
    ('''			if (D < 850.f || D > 2400.f) continue;''', '''			if (D < 850.f || D > 2400.f || N.X < 60.f) continue;        // never out in the yard'''),
])
edit(R + "WCStory.cpp", [
    ('''								bBusy = false;
								float T2 = Say(TEXT("d_after_kitchen"), 0.3f);''', '''								bBusy = false;
								Rest(170.f);
								float T2 = Say(TEXT("d_after_kitchen"), 0.3f);'''),
    ('''					Say(TEXT("d_musicbox"), 2.2f);
					Checkpoint(TEXT("underbed"));''', '''					Say(TEXT("d_musicbox"), 2.2f);
					Rest(130.f);
					Checkpoint(TEXT("underbed"));'''),
    ('''						Set(TEXT("attic_done"));''', '''						Set(TEXT("attic_done"));
						Rest(120.f);'''),
])
print("ok")
