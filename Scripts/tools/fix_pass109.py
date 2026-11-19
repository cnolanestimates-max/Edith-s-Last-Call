"""Pass 109: the things in Walter's desk.  The bot has never been able to look at the key ring or the cartridges (auto14, auto15:
"could not focus pick_key_ell"), and the chair stood square in front of them.  The chair is pushed back and aside, and the level
build now reports from where a standing man can actually see each of the two (so they can be put where he can)."""
import sys
sys.path.insert(0, "C:/GameDev/Unreal/WellnessCheck/Scripts/tools")
from patchlib import edit
R = "C:/GameDev/Unreal/WellnessCheck/"
edit(R + "Scripts/level/ell.py", [
    ('''place("Chair_Dining_HighBack", 2255, -330, GZ, 90, DN)''', '''place("Chair_Dining_HighBack", 2205, -425, GZ, 55, DN)          # pushed back from the desk and aside: he has to be able to stand at it'''),
    ('''ammo("ammo_desk", 2314, -306, GZ + 78, 70, tags=["Show_deskammo"])''', '''ammo("ammo_desk", 2314, -306, GZ + 78, 70, tags=["Show_deskammo"])


def sight_report(what, tx, ty, tz):
    """From where can a standing man see this?  (eye 156 cm; a line trace against everything that blocks sight)"""
    out = []
    for (ex, ey) in ((2190, -352), (2225, -352), (2250, -352), (2225, -300), (2250, -300), (2225, -400), (2250, -290), (2270, -330)):
        try:
            hit = unreal.SystemLibrary.line_trace_single(_world, V(ex, ey, GZ + 156), V(tx, ty, tz + 1.0), unreal.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [],
                                                         unreal.DrawDebugTrace.NONE, True)
            t = hit.to_tuple() if hit else None
            if t and t[0]:
                gap = ((t[4].x - tx) ** 2 + (t[4].y - ty) ** 2 + (t[4].z - tz) ** 2) ** 0.5
                who = t[9].get_actor_label() if t[9] else "?"
                out.append(f"({ex},{ey}): {'SEEN' if gap < 9 else 'blocked by ' + who + ' ' + str(int(gap)) + ' cm short'}")
            else:
                out.append(f"({ex},{ey}): nothing hit")
        except Exception as exc:
            out.append(f"trace failed: {str(exc)[:80]}")
            break
    log(f"sight {what} at ({tx:.0f},{ty:.0f},{tz:.0f}): " + "; ".join(out))


for _a in actors.get_all_level_actors():
    if _a.get_actor_label() in ("Pickup_pick_key_ell", "Pickup_pick_ammo_desk"):
        _l = _a.get_actor_location()
        sight_report(_a.get_actor_label(), _l.x, _l.y, _l.z)'''),
])
print("pass 109 applied")
