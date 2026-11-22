"""The prop polish pass (Cheyenne, 2026-11-21: "anything that is placed weird, like a dresser facing the wall instead of
the room, needs to be fixed").  Safe to run on the saved map (Scripts/level/apply_polish.py) or at the end of the level
build (build_house.py runs it last).  Idempotent: every change is written as the state it should end in.

Found by Scripts/level/audit_props.py + audit_offline.py (photos of all 121 pieces from the room side): these stood with
their fronts to the wall.  The kit furniture (HorrorHouseKit, OldWest VOL1) faces local +Y."""
import math
import unreal as u

GZ, UZ, AZ, CZ = 0.0, 350.0, 700.0, -350.0
# interior faces of each room's walls (decay.py ROOMS)
ROOMS = {
    "den": (1616, 2384, -584, -216, GZ), "bath_g": (2416, 2784, -584, -216, GZ), "pantry": (1616, 1984, 216, 584, GZ), "sickroom": (2016, 2784, 216, 584, GZ),
    "daniel": (1616, 2384, -584, -216, UZ), "sewing": (2416, 2784, -584, -216, UZ), "aide": (1616, 2384, 216, 584, UZ), "bath2": (2416, 2784, 216, 584, UZ),
    "living": (16, 784, -584, -216, GZ), "sitting": (816, 1584, -584, -216, GZ), "dining": (16, 784, 216, 584, GZ), "kitchen": (816, 1584, 216, 584, GZ),
    "kids": (16, 784, -584, -216, UZ), "bath": (816, 1584, -584, -216, UZ), "master": (16, 784, 216, 584, UZ), "prayer": (816, 1584, 216, 584, UZ)}

# (label, the end of its folder path, the yaw it should have, seat its back against the wall)
TURN = [
    ("Dresser_Drawers", "/Kitchen", 90.0, True),                 # drawers were to the east wall
    ("Dresser_Drawers", "/Bath", 180.0, True),                   # upstairs bath: both dressers showed their backs
    ("Dresser_Drawers_Open", "/Bath", 180.0, True),
    ("Mirror_Standing_Cheval", "/Prayer", 220.0, False),         # the glass to the room
    ("Mirror_Standing_Cheval", "/Aide", -50.0, False),
    ("GunCabinet", "/Den", 90.0, True),
    ("Filing_Cabinet_4", "/Den", 90.0, True),
    ("Clock_Grandfather_Broken", "/Den", -90.0, True),
    ("Clock_Grandfather_Broken", "/Dining", 180.0, True),
    ("Cabinet_Medicine_Glass_Open", "/Sickroom", 90.0, True),
    ("Cabinet_Steel_Tall", "/Pantry", 90.0, True),
    ("Wardrobe_Tall", "/Daniel", 90.0, True),
    ("AideDresser", "/Aide", -90.0, True),                       # the "desk" turned round: an old chest of drawers
    ("Wardrobe_Open_Clothes", "/Aide", 90.0, True),              # and it stood 27 cm into the wall
]


def room_of(x, y, z):
    for n, (x0, x1, y0, y1, fz) in ROOMS.items():
        if x0 - 30 <= x <= x1 + 30 and y0 - 30 <= y <= y1 + 30 and abs(z - fz) < 60:
            return n, (x0, x1, y0, y1)
    return None, None


def dress():
    sub = u.get_editor_subsystem(u.EditorActorSubsystem)
    actors = sub.get_all_level_actors()
    done = []
    for label, folder, yaw, seat in TURN:
        hits = [a for a in actors if a.get_actor_label() == label and str(a.get_folder_path()).endswith(folder)]
        if len(hits) != 1:
            u.log_warning(f"WC_POLISH {label} {folder}: {len(hits)} found, skipped")
            continue
        a = hits[0]
        a.modify()
        rot = a.get_actor_rotation()
        o, e = a.get_actor_bounds(False)
        d = math.radians(yaw - rot.yaw)
        if abs(math.remainder(yaw - rot.yaw, 360.0)) > 0.5:
            loc = a.get_actor_location()
            rx, ry = loc.x - o.x, loc.y - o.y
            a.set_actor_location(u.Vector(o.x + rx * math.cos(d) - ry * math.sin(d), o.y + rx * math.sin(d) + ry * math.cos(d), loc.z), False, True)
            a.set_actor_rotation(u.Rotator(roll=rot.roll, pitch=rot.pitch, yaw=yaw), False)
        if seat:
            # its back to the nearest wall behind it, two centimetres off the plaster
            o, e = a.get_actor_bounds(False)
            n, b = room_of(o.x, o.y, o.z - e.z)
            if b:
                fy = math.radians(yaw)
                fx_, fy_ = -math.sin(fy), math.cos(fy)              # local +Y, the front, in the world
                loc = a.get_actor_location()
                if abs(fx_) > 0.9:
                    wall = b[0] if fx_ > 0 else b[1]                  # the wall behind it
                    want = wall + (e.x + 2.0) * (1 if fx_ > 0 else -1)
                    a.set_actor_location(u.Vector(loc.x + (want - o.x), loc.y, loc.z), False, True)
                elif abs(fy_) > 0.9:
                    wall = b[2] if fy_ > 0 else b[3]
                    want = wall + (e.y + 2.0) * (1 if fy_ > 0 else -1)
                    a.set_actor_location(u.Vector(loc.x, loc.y + (want - o.y), loc.z), False, True)
        done.append(f"{label}{folder}")
    u.log_warning("WC_POLISH turned " + str(len(done)) + ": " + ", ".join(done))
    return done
