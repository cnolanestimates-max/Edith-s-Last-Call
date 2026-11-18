"""From bot run 4: the aide's chair blocked her doorway; Ruth's music box was swallowed by the new bed; the bot's route to the den desk."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
L = "C:/GameDev/Unreal/WellnessCheck/Scripts/level/"
edit(L + "ell.py", [
    ('''place("Chair_Dining_HighBack", 1790, 262, UZ, 20, AD, pitch=-28, name="ChairUnderKnob")''', '''place("Chair_Dining_Broken", 1905, 268, UZ, 110, AD, name="ChairUnderKnob")'''),
])
edit(L + "looks.py", [
    ('''("aide_chair", 1790, 262, 60, "A chair jammed under the doorknob. From the inside. She slept like that.", (30, 30, 50)),''',
     '''("aide_chair", 1905, 268, UZ + 40, "A chair, split along the top rail where it was jammed under the doorknob. From the inside. She slept like that.", (30, 30, 40)),'''),
])
edit(L + "build_house.py", [
    ('''pickup("pick_keep_ruth", "keep_ruth", "Ruth's music box", "Music_Box_Closed", 600, -430, UZ + 1, 30, grab=(16, 16, 12))
point("MusicBoxPoint", 600, -430, UZ + 20)''', '''pickup("pick_keep_ruth", "keep_ruth", "Ruth's music box", "Music_Box_Closed", 600, -338, UZ + 1, 30, grab=(16, 16, 12))
point("MusicBoxPoint", 600, -338, UZ + 20)'''),
    ('''point("Her_Under", 640, -520, UZ, 90)''', '''point("Her_Under", 640, -430, UZ, 90)'''),
])
edit(L + "nav.py", [
    ('''"den_d": (1800, -200, GZ), "den": (2000, -380, GZ),''', '''"den_d": (1800, -200, GZ), "den": (2000, -380, GZ), "den_desk": (2230, -340, GZ), "den_shelf": (2240, -290, GZ),'''),
    ('''("hallE", "den_d"), ("den_d", "den"),''', '''("hallE", "den_d"), ("den_d", "den"), ("den", "den_desk"), ("den_desk", "den_shelf"),'''),
])
print("ok")
