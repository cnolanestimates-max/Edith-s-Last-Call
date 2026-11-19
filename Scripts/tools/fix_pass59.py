"""Forest drive, after its first automatic capture: the road and verges were black (headlights only graze the ground) and
the gauge glow was a big flat green slab at the bottom of the screen.  A wide low wash lights the road ahead of the car;
the gauges become three small dim marks."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
L = "C:/GameDev/Unreal/WellnessCheck/Scripts/level/"
edit(L + "forest.py", [
    ('''cpart(light_point("TailGlow",''', '''# what the headlights do to the road itself: a wide wash from above the bumper, falling on the dirt and the verges
cpart(light_spot("RoadWash", CRX + 230, CRY, 120, 0, -17, 5200, (1.0, 0.93, 0.8), 3600, 34, 62, "Cruiser", tags=["Hide_dawn", "Headlight"], shadows=False, vol=0.5))
cpart(light_point("TailGlow",'''),
    ('''cab("Gauges", 49.4, 50.2, 22, 54, 102, 110, "WC:M_DashGlow")''', '''for _g, (_l0, _l1) in enumerate(((27, 33), (35.5, 40.5), (43, 49))):
    cab(f"Gauge{_g}", 49.4, 50.2, _l0, _l1, 105.2, 106.6, "WC:M_DashGlow")'''),
    ('''cab("RadioGlow", 48.4, 49.2, -14, 8, 84, 90, "WC:M_DashGlow")''', '''cab("RadioGlow", 48.4, 49.2, -9, 3, 86.4, 87.6, "WC:M_DashGlow")'''),
])
edit(L + "import_assets.py", [
    ('''flat_material("M_DashGlow", (0.25, 0.85, 0.55), 0.5, emissive=3.0)''', '''flat_material("M_DashGlow", (0.25, 0.85, 0.55), 0.5, emissive=0.9)'''),
])
print("ok")
