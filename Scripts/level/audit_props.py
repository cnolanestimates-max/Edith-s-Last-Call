"""Inventory of the built House map for the prop polish pass (2026-11-21).

  UnrealEditor-Cmd WellnessCheck.uproject -run=pythonscript -script=<this> -unattended -nosplash

Writes Saved/_audit/props.json (every mesh-bearing actor: label, folder, class, mesh, location, rotation, scale, local and
world extents) and Saved/_audit/furniture_shots.txt (a camera on the open side of every large piece of furniture,
looking back at it, for -WCShotFile).  For furniture it also traces outward along both depth directions to find which
side has a wall: a piece whose back is not to the wall, or that stands with its front against one, shows up in the photos.
Reads the map only; changes nothing."""
import json, math, os
import unreal as u

ROOT = "C:/GameDev/Unreal/WellnessCheck"
OUT = ROOT + "/Saved/_audit"
os.makedirs(OUT, exist_ok=True)
u.get_editor_subsystem(u.LevelEditorSubsystem).load_level("/Game/WC/Maps/House")
world = u.get_editor_subsystem(u.UnrealEditorSubsystem).get_editor_world()
actors = u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()

FURN = ("dresser", "desk", "wardrobe", "bookshelf", "bookcase", "shelf", "cabinet", "armoire", "chest", "hutch", "sideboard", "vanity",
        "piano", "bureau", "cupboard", "nightstand", "drawers", "commode", "locker", "dresser", "upright", "fridge", "stove", "oven",
        "sofa", "couch", "bed", "crib", "cradle", "table", "chair", "wardrobe", "trunk", "safe", "clock", "sink", "tub", "toilet", "mirror")
TALL = ("wardrobe", "bookshelf", "bookcase", "shelf", "cabinet", "armoire", "hutch", "cupboard", "locker", "upright", "fridge", "clock")
FLOORS = [(-350.0, "cellar"), (0.0, "ground"), (350.0, "upper"), (700.0, "attic")]


def V(x, y, z):
    return u.Vector(x, y, z)


rows, shots = [], []
for a in actors:
    comps = a.get_components_by_class(u.StaticMeshComponent)
    if not comps:
        continue
    c = comps[0]
    m = c.get_editor_property("static_mesh")
    if not m:
        continue
    lab = a.get_actor_label()
    folder = str(a.get_folder_path())
    loc, rot, sc = a.get_actor_location(), a.get_actor_rotation(), a.get_actor_scale3d()
    bb = m.get_bounding_box()
    ext = [(bb.max.x - bb.min.x) * sc.x, (bb.max.y - bb.min.y) * sc.y, (bb.max.z - bb.min.z) * sc.z]
    o, e = a.get_actor_bounds(False)
    row = dict(label=lab, cls=a.get_class().get_name(), folder=folder, mesh=m.get_path_name().split(".")[0], loc=[round(loc.x), round(loc.y), round(loc.z)],
               yaw=round(rot.yaw, 1), pitch=round(rot.pitch, 1), roll=round(rot.roll, 1), scale=[round(sc.x, 2), round(sc.y, 2), round(sc.z, 2)],
               local=[round(v) for v in ext], world_min=[round(o.x - e.x), round(o.y - e.y), round(o.z - e.z)], world_max=[round(o.x + e.x), round(o.y + e.y), round(o.z + e.z)])
    name = (lab + " " + m.get_name()).lower()
    inside = "Shell" not in folder and "Forest" not in folder and "Tour" not in folder and -900 < loc.x < 3000 and -800 < loc.y < 800
    if inside and any(k in name for k in FURN) and max(ext[0], ext[1]) > 40 and ext[2] > 35:
        # trace outward from the middle of the piece, along both of its short horizontal directions, at a third of its height
        yaw = math.radians(rot.yaw)
        ax_x = (math.cos(yaw), math.sin(yaw))
        ax_y = (-math.sin(yaw), math.cos(yaw))
        depth_axis, half = (ax_x, ext[0] / 2) if ext[0] <= ext[1] else (ax_y, ext[1] / 2)
        mid = V((o.x), (o.y), o.z - e.z + max(25.0, ext[2] / 3))
        hits = {}
        for sgn in (1, -1):
            d = (depth_axis[0] * sgn, depth_axis[1] * sgn)
            start = V(mid.x + d[0] * (half + 2), mid.y + d[1] * (half + 2), mid.z)
            end = V(start.x + d[0] * 260, start.y + d[1] * 260, mid.z)
            h = u.SystemLibrary.line_trace_single(world, start, end, u.TraceTypeQuery.TRACE_TYPE_QUERY1, True, [a], u.DrawDebugTrace.NONE, True)
            t = h.to_tuple() if h else None
            if t and t[0]:
                other = t[9]
                hits[sgn] = (round(t[3]), other.get_actor_label() if other else "?", str(other.get_folder_path()) if other else "")
            else:
                hits[sgn] = (999, "", "")
        # the open side is the one with more room in front of it; the camera stands there and looks back
        sgn = 1 if hits[1][0] >= hits[-1][0] else -1
        room = min(hits[sgn][0], 230)
        back_gap = hits[-sgn][0]
        dist = half + max(90.0, min(room - 20.0, 190.0))
        cam_x = o.x + depth_axis[0] * sgn * dist
        cam_y = o.y + depth_axis[1] * sgn * dist
        floor = min(FLOORS, key=lambda f: abs((o.z - e.z) - f[0]))[0]
        look_yaw = math.degrees(math.atan2(o.y - cam_y, o.x - cam_x))
        tall = any(k in name for k in TALL)
        target_z = o.z - e.z + ext[2] * (0.55 if tall else 0.6)
        pitch = math.degrees(math.atan2(target_z - (floor + 92 + 64), dist))
        row.update(furniture=True, open_side=sgn, room_in_front=hits[sgn][0], back_gap=back_gap, back_hit=hits[-sgn][1], front_hit=hits[sgn][1])
        nm = f"F_{len(shots):03d}_{lab}".replace(" ", "_").replace("|", "_")[:60]
        shots.append(f"{nm}|{cam_x:.0f},{cam_y:.0f},{floor + 92:.0f},{look_yaw:.1f},{max(-35.0, min(10.0, pitch)):.1f}")
        row["shot"] = nm
    rows.append(row)

json.dump(rows, open(OUT + "/props.json", "w", encoding="utf-8"), indent=0)
open(OUT + "/furniture_shots.txt", "w", encoding="utf-8").write("\n".join(shots) + "\n")
u.log_warning(f"WC_AUDIT {len(rows)} mesh actors, {len(shots)} furniture pieces photographed")
