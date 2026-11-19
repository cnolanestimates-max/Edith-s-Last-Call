"""Pass 115: the television is a TV and video recorder in one (Cheyenne 2026-11-19 19:49 UTC: "make the tv a vcr and tv combo so
the player can just plug in the vhs tapes").  The set gets a tape slot and its keys under the screen; the separate recorder
that sat on top is gone."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
R = "C:/GameDev/Unreal/WellnessCheck/"
edit(R + "Scripts/art/build_items.py", [
    ('''    P.append(cyl(0.045, 0.02, (0.05, 0.02, 0.83), m="Polymer", v=20))''', '''    # the built-in video recorder: a slot under the screen with its flap, four keys, a little counter window
    P.append(box(0.60, 0.010, 0.056, (-0.11, -0.2335, 0.246), m="Gunmetal"))
    P.append(box(0.200, 0.010, 0.024, (-0.215, -0.2380, 0.248), m="Polymer"))
    P.append(box(0.196, 0.004, 0.020, (-0.215, -0.2435, 0.2485), (0.14, 0, 0), "Polymer"))
    for k in range(4):
        P.append(box(0.022, 0.010, 0.012, (-0.060 + k * 0.030, -0.2400, 0.243), m="Brass"))
    P.append(box(0.050, 0.008, 0.014, (0.115, -0.2390, 0.247), m="Screen"))
    P.append(cyl(0.045, 0.02, (0.05, 0.02, 0.83), m="Polymer", v=20))'''),
])
p = R + "Source/WellnessCheck/WCEvents.cpp"
s = open(p, encoding="utf-8").read()
a = s.index("		static bool bVCRTried = false;")
b = s.index("		Tv->Prompt = (HasItem(TEXT(\"tape1\"))", a)
s = s[:a] + "		// (the set has its own tape slot under the screen: SM_Item_TV)\n" + s[b:]
s = s.replace('TEXT("Put the tape in the recorder") : TEXT("Look at the television")', 'TEXT("Put the tape in") : TEXT("Look at the television")')
s = s.replace('TEXT("The recorder is empty. There were more tapes than this.") : TEXT("An old console set, and a video recorder on top of it. No tape in it.")',
              'TEXT("The slot is empty. There were more tapes than this.") : TEXT("An old console set with a tape slot under the screen. Nothing in it.")')
s = s.replace('goes into the recorder"), PlaySeconds, Have);', 'goes into the set"), PlaySeconds, Have);')
open(p, "w", encoding="utf-8", newline="\n").write(s)
edit(R + "Source/WellnessCheck/WCDirector.h", [
    ('''	TWeakObjectPtr<class UStaticMeshComponent> VCRMesh;        // the recorder on top of the set''', '''	// (the recorder is part of the television's own model)'''),
])
edit(R + "Source/WellnessCheck/WCGame.cpp", [
    ('''InvSay(TEXT("It needs a video recorder."));''', '''InvSay(TEXT("It goes in the television."));'''),
])
edit(R + "Source/WellnessCheck/WCAuto.cpp", [
    ('''Shot(TEXT("spot_12_television_and_recorder"));''', '''Shot(TEXT("spot_12_television_with_tape_slot"));'''),
])
print("pass 115 applied")
