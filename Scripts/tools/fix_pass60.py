"""Second bathroom: the water in the tub follows the tub's real bounds (and the bounds are logged, to route the bot round it).
Sewing room: the chair no longer stands between the room and the shears; the old stand-in second blade is gone now that the
shears are a real model."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
L = "C:/GameDev/Unreal/WellnessCheck/Scripts/level/"
edit(L + "ell.py", [
    ('''fab("Urban_Australian_Desolation_Bathtub_Metal_Rusty", 2700, 300, UZ, 90, "Bath2", scale=1.15)''',
     '''_tub2 = fab("Urban_Australian_Desolation_Bathtub_Metal_Rusty", 2700, 300, UZ, 90, "Bath2", scale=1.15)
TUB2 = None
if _tub2:
    _to, _te = _tub2.get_actor_bounds(False)
    TUB2 = (_to.x, _to.y, _te.x, _te.y)
    log(f"Tub2 centre ({_to.x:.0f},{_to.y:.0f}) half ({_te.x:.0f},{_te.y:.0f},{_te.z:.0f})")'''),
    ('''box("TubWater", 2664, 2738, 232, 372, UZ + 46, UZ + 47.5, "WC:M_Black", B2, collide=False, shadow=False)''',
     '''if TUB2:
    box("TubWater", TUB2[0] - TUB2[2] * 0.74, TUB2[0] + TUB2[2] * 0.74, TUB2[1] - TUB2[3] * 0.80, TUB2[1] + TUB2[3] * 0.80, UZ + 44, UZ + 45.5, "WC:M_Black", B2, collide=False, shadow=False)'''),
    ('''place("Chair_Dining_HighBack", 2525, -470, UZ, 270, SW)''', '''place("Chair_Dining_HighBack", 2530, -335, UZ, 205, SW)'''),
    ('''put(CUBE, 2456, -492, UZ + 74.6, 62, SW, name="ShearsBlade2", scale=(0.21, 0.03, 0.007), mats={0: "Iron"}, tags=["Hide_shears"])''',
     '''if not ITEM("Shears"):
    put(CUBE, 2456, -492, UZ + 74.6, 62, SW, name="ShearsBlade2", scale=(0.21, 0.03, 0.007), mats={0: "Iron"}, tags=["Hide_shears"])'''),
])
print("ok")
