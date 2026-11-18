"""Moon shafts no longer glow outside the windows; house bulbs bright enough to matter; clear path through the kitchen to the pantry."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
L = "C:/GameDev/Unreal/WellnessCheck/Scripts/level/"
edit(L + "lighting.py", [
    ('''def shaft(name, x, y, z, yaw, pitch=-24.0):
    m_ = light_spot(name + "_moon", x, y, z, yaw, pitch, 1900, (0.5, 0.63, 1.0), 950, 10, 26, "Lights/Windows", tags=["Hide_dawn"], shadows=True, vol=2.2)''',
     '''def shaft(name, x, y, z, yaw, pitch=-15.0):
    # The lamp sits IN the window opening (not out in the yard), so the lit fog starts at the boards: from outside the
    # window stays dark, inside the light fans down through the gaps.
    x += math.cos(math.radians(yaw)) * 78.0
    y += math.sin(math.radians(yaw)) * 78.0
    z -= 42.0
    m_ = light_spot(name + "_moon", x, y, z, yaw, pitch, 9000, (0.5, 0.63, 1.0), 900, 36, 62, "Lights/Windows", tags=["Hide_dawn"], shadows=True, vol=2.0)'''),
    ('''    light_spot(name + "_dawn", x, y, z, yaw, pitch + 8, 9000, (1.0, 0.7, 0.45), 1100, 12, 30, "Lights/Windows", tags=["Show_dawn"], shadows=True, vol=2.6)''',
     '''    light_spot(name + "_dawn", x, y, z, yaw, pitch + 4, 42000, (1.0, 0.7, 0.45), 1100, 36, 62, "Lights/Windows", tags=["Show_dawn"], shadows=True, vol=2.4)'''),
])
edit(L + "switches.py", [('''BULB_LUMENS = float(os.environ.get("WC_BULB", "46"))''', '''BULB_LUMENS = float(os.environ.get("WC_BULB", "330"))''')])
edit(L + "build_house.py", [
    ('''place("Chair_Dining_HighBack", 1250, 330, GZ, 180, K)''', '''# (no chair on the hall side of the table: that is the way through to the pantry)'''),
])
edit(L + "nav.py", [
    ('''"kitchen_d": (1000, 200, GZ), "kitchen": (1000, 380, GZ), "kitchen2": (1420, 380, GZ),''', '''"kitchen_d": (1000, 200, GZ), "kitchen": (1000, 380, GZ), "kitchen_b": (1060, 290, GZ), "kitchen2": (1440, 290, GZ),'''),
    ('''("kitchen", "kitchen2"),''', '''("kitchen", "kitchen_b"), ("kitchen_d", "kitchen_b"), ("kitchen_b", "kitchen2"),'''),
    ('''"pantry_d": (1600, 400, GZ), "pantry": (1800, 400, GZ), "kitchen3": (1480, 400, GZ),''', '''"pantry_d": (1600, 400, GZ), "pantry": (1800, 400, GZ), "kitchen3": (1500, 400, GZ),'''),
])
print("ok")
