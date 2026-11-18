"""Forest road polish: the pines stand closer, with saplings and ferns thick at eye level along both verges, and the
headlights show as beams in the mist."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
L = "C:/GameDev/Unreal/WellnessCheck/Scripts/level/"
edit(L + "forest.py", [
    ('''((330, 470, "big", 0.8), (560, 800, "big", 0.45), (900, 1300, "kit", 0.5), (1400, 2100, "kit", 0.3))''',
     '''((275, 390, "big", 0.9), (470, 720, "big", 0.55), (820, 1250, "kit", 0.5), (1350, 2100, "kit", 0.3))'''),
    ('''        if _fr.random() < 0.5:
            off = _fr.uniform(250, 330) * side
            try_tree(x0 - uy * off + ux * _fr.uniform(-200, 200), y0 + ux * off + uy * _fr.uniform(-200, 200), "small")''',
     '''for _rep in range(2):
            if _fr.random() < 0.8:
                off = _fr.uniform(235, 430) * side
                try_tree(x0 - uy * off + ux * _fr.uniform(-240, 240), y0 + ux * off + uy * _fr.uniform(-240, 240), "small")'''),
    ('''    if near_road(x, y, 330) or in_yard(x, y):''', '''    if near_road(x, y, 228 if kind == "small" else 262) or in_yard(x, y):'''),
    ('''        if abs(tx - x) < 150 and abs(ty - y) < 150:''', '''        if abs(tx - x) < 110 and abs(ty - y) < 110:'''),
    ('''        elif r < 0.75 and FERNS:
            for k in range(2):''', '''        elif r < 0.92 and FERNS:
            for k in range(3):'''),
    ('''28, 0, -2.5, 6500, (1.0, 0.95, 0.84), 5200, 14, 34, "Cruiser", tags=["Hide_dawn", "Headlight"], shadows=(i == 0), vol=1.5))''',
     '''28, 0, -2.5, 6500, (1.0, 0.95, 0.84), 5200, 14, 34, "Cruiser", tags=["Hide_dawn", "Headlight"], shadows=(i == 0), vol=3.2))'''),
])
print("ok")
