"""Pass 93: from the bot run with the short reach.
  - reach 115 cm (105 left the bot, and so a person, unable to use a door or a table from where they naturally stop)
  - the bot walks right up to things; it walks to the doorway for the first peek, as a person would
  - the sofa crowded the living-room doorway: moved further in and to the right, clear of the door"""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit

R = "C:/GameDev/Unreal/WellnessCheck/"
edit(R + "Source/WellnessCheck/WCCharacter.h", [
    ('float InteractReach = 105.f;', 'float InteractReach = 115.f;'),
])
edit(R + "Source/WellnessCheck/WCAuto.cpp", [
    ('if (bToUse && BoxGap < P->InteractReach - 30.f &&', 'if (bToUse && BoxGap < P->InteractReach - 62.f &&'),
    ('''LookHer(1.0f); Shot(TEXT("09_S1_peek")); LookHer(2.5f);
	Flag(TEXT("peek_done"), 40.f); Wait(5.f);''', '''LookHer(1.0f); Shot(TEXT("09_S1_peek")); LookHer(2.5f);
	Go(TEXT("Her_Peek"));                       // she is only found close to: walk to the doorway with the light on it
	Flag(TEXT("peek_done"), 40.f); Wait(5.f);'''),
])
edit(R + "Scripts/level/build_house.py", [
    ('place("Sofa_Sagging_Broken", 370, -300, GZ, 180, L)', 'place("Sofa_Sagging_Broken", 430, -335, GZ, 180, L)'),
    ('("A_Living", 372, -425, GZ, 270)', '("A_Living", 250, -430, GZ, 300)'),
])
print("pass 93 applied")
