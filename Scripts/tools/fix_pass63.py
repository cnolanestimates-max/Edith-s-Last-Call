"""Second bathroom: the mirror and sink were hung across the boarded window.  They move to the wall beside it; the cabinet
goes over the toilet; the laundry cart stands under the window."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
L = "C:/GameDev/Unreal/WellnessCheck/Scripts/level/"
edit(L + "ell.py", [
    ('''place("Sink_Hospital", 2600, 572, UZ, 180, B2)''', '''place("Sink_Hospital", 2738, 572, UZ, 180, B2)'''),
    ('''place("Mirror_Wall_Oval", 2600, 582, UZ + 150, 180, B2, collide=False)''', '''place("Mirror_Wall_Oval", 2738, 582, UZ + 150, 180, B2, collide=False)'''),
    ('''place("Medicine_Cabinet_Wall_Open", 2720, 582, UZ + 140, 180, B2, collide=False)''', '''place("Medicine_Cabinet_Wall_Open", 2462, 582, UZ + 150, 180, B2, collide=False)'''),
    ('''place("Laundry_Cart", 2740, 540, UZ, 20, B2)''', '''place("Laundry_Cart", 2596, 540, UZ, 8, B2)'''),
])
print("ok")
