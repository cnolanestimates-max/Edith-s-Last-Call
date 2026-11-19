"""Pass 99: level fixes from Cheyenne's play-test (2026-11-19 15:26 to 15:28 UTC).
  - the hanging-hair watchers are gone ("like you're hanging a 2x4 and raising it through the roof ... remove that scare")
  - the smoke figure on the road is gone (she leaned toward removing it; nothing replaces it)
  - forest road: the bent saplings stand further back and lean less, so nothing comes through the windshield; twice the
    ferns and dead brush on the verges, so the ground is not bare
  - papers that hung in the air: the settle pass now also drops flat drawings and the two flat reminder notes onto whatever is
    under them; the child's drawing by the kitchen sink is on the kitchen table"""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit

R = "C:/GameDev/Unreal/WellnessCheck/"

edit(R + "Scripts/level/watchers.py", [
    ('''watcher("hair_stairs", 640, -150, UZ + 322, 0, 0, 1, 5.2)           # hanging in the stairwell from the attic flight
watcher("hair_sitting", 1420, -330, UZ - 24, 0, 0, 1, 4.4)          # through the hole in her sitting-room ceiling
watcher("hair_attic", 1340, 360, AZ - 22, 0, 0, 1, 4.8)             # through the hole in the attic floor, into the prayer room
watcher("hair_bath2", 2540, 390, UZ - 22, 0, 0, 1, 4.6)             # through the rotted bathroom floor, over the sickroom bed
watcher("hair_backhall", 2350, 60, GZ + 326, 0, 0, 1, 3.6)          # from a gap in the rear-hall ceiling''',
     '''# (removed 2026-11-19 at Cheyenne's request: the hanks of hair drawn up into the ceiling read as a stiff plank, not hair)'''),
    ('log("watchers: 8 eyes, 5 hanks of hair, the settlers book")', 'log("watchers: 8 eyes, the settlers book")'),
])

edit(R + "Scripts/level/forest.py", [
    ('''_fig = smoke_man("RoadShadow", _shx, _shy, -41, math.degrees(math.atan2(-_suy, -_sux)), 310, "RoadShadow")
log(f"road shadow at ({_shx:.0f},{_shy:.0f}), sample {_si} of {len(SAMPLES)}")''',
     '''# (the smoke figure that stood here was removed 2026-11-19 at Cheyenne's request)'''),
    ('''for _rep in range(2):
            if _fr.random() < 0.62:
                px, py = at(_fr.uniform(214, 268), _fr.uniform(-125, 125))
                road_tree(px, py, "small", _fr.uniform(16, 36), mid, _fr.uniform(1.6, 2.7))''',
     '''# (they used to stand at the road edge leaning 16 to 36 degrees: their branches came through the windshield)
        for _rep in range(2):
            if _fr.random() < 0.5:
                px, py = at(_fr.uniform(262, 330), _fr.uniform(-125, 125))
                road_tree(px, py, "small", _fr.uniform(8, 17), mid, _fr.uniform(1.8, 2.8))'''),
    ('''        for k in range(3):
            a = actors.spawn_actor_from_class(unreal.SkeletalMeshActor, V(px + _fr.uniform(-90, 90), py + _fr.uniform(-90, 90), -42), R(_fr.uniform(0, 360)))''',
     '''        # dead brush with the ferns, so the ground between the trunks is not bare dirt
        for k in range(2):
            bo = _fr.uniform(205, 640) * side
            bx, by = x0 - uy * bo + ux * _fr.uniform(-130, 130), y0 + ux * bo + uy * _fr.uniform(-130, 130)
            place(_fr.choice(("Bramble_Bush_Dead", "Bush_Thorny_Dead")), bx, by, -43, _fr.uniform(0, 360), FO + "/Under", scale=_fr.uniform(0.8, 1.6), collide=False)
        for k in range(6):
            a = actors.spawn_actor_from_class(unreal.SkeletalMeshActor, V(px + _fr.uniform(-150, 150), py + _fr.uniform(-150, 150), -42), R(_fr.uniform(0, 360)))'''),
])

edit(R + "Scripts/level/settle.py", [
    ('''"Switch", "Fuse", "Knot", "Window", "Drawing", "Lantern",''', '''"Switch", "Fuse", "Knot", "Window", "Lantern",'''),
    ('''"Tour", "Nav", "A_", "Light", "note_rem", "note_calendar", "Drawing_", "Mem",''', '''"Tour", "Nav", "A_", "Light", "note_calendar", "Mem",'''),
    ('''    if any(str(t).startswith(("Show_", "Hide_")) for t in a.tags):
        continue''', '''    if any(str(t).startswith(("Show_", "Hide_")) for t in a.tags):
        continue
    _rot = a.get_actor_rotation()
    if abs(_rot.roll) > 45 or abs(_rot.pitch) > 45:
        continue                                           # pinned to a wall'''),
    ('''    if max(extent.x, extent.y) > 48 or extent.z > 45 or (extent.x + extent.y + extent.z) < 0.5:
        continue                                           # furniture, or nothing to see''',
     '''    if max(extent.x, extent.y) > 48 or extent.z > 45 or (extent.x + extent.y + extent.z) < 0.5:
        continue                                           # furniture, or nothing to see
    if label.startswith("Drawing_") and extent.z > 3:
        continue                                           # a drawing on a wall (the flat ones on floors and tables do settle)'''),
])

edit(R + "Scripts/level/memory.py", [
    ('''drawing(1, 1305, 520, GZ + 96, None, w=22, h=28, yaw=15)           # on the kitchen table''',
     '''drawing(1, 1262, 452, GZ + 96, None, w=22, h=28, yaw=15)           # on the kitchen table (it was at 1305, 520: in the air beside the sink)'''),
])
print("pass 99 applied")
