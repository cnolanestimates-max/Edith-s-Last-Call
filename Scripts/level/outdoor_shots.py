"""Photo list for the outdoor polish pass (-WCShotFile): the same spots before and after, so the two can be laid side by side.
  python outdoor_shots.py <out file>
Coordinates: x, y, z of the deputy (yard ground is -40, he stands at about 60), yaw (0 = +X, toward the back yard), pitch."""
import math, sys

def look(name, frm, at, z=60, pitch=None):
    yaw = math.degrees(math.atan2(at[1] - frm[1], at[0] - frm[0]))
    if pitch is None:
        d = math.hypot(at[0] - frm[0], at[1] - frm[1])
        pitch = math.degrees(math.atan2((at[2] if len(at) > 2 else 0) - (z + 66), d))
    return f"{name}|{frm[0]:.0f},{frm[1]:.0f},{z},{yaw:.0f},{pitch:.0f}"

SHOTS = [
    look("01_wheelbarrow_back", (3330, 30), (3520, 150, 10)),
    look("02_wheelbarrow_back_close", (3640, 230), (3520, 150, 20)),
    look("03_stump_back", (3470, 430), (3660, 510, 0)),
    look("04_backyard_wide", (3050, 330), (3700, 400, 60)),
    look("05_treeline_back", (3900, 0), (5000, 100, 250)),
    look("06_treeline_south", (1500, -950), (1700, -1850, 250)),
    look("07_treeline_north", (1500, 850), (1300, 1850, 250)),
    look("08_wheelbarrow_front", (-720, -640), (-900, -760, 10)),
    look("09_stump_front", (-1060, -690), (-1250, -780, 0)),
    look("10_frontyard_wide", (-2300, -100), (-600, -300, 100)),
    look("11_forest_road", (-2700, 150), (-4500, 600, 150)),
    look("12_ground_front", (-1300, 300), (-1000, 520, -40)),
    look("13_ground_back", (3850, -250), (3650, 50, -40)),
    look("14_yard_side", (1900, -980), (3300, -1000, 60)),
    look("16_rocks_back", (3780, 520), (4040, 660, -10)),
    look("17_stump_rotten", (3760, 640), (3900, 780, -10)),
    look("18_woodpile_back", (3600, 760), (3750, 937, 0)),
    look("15_forest_floor", (-2900, 300), (-3300, 700, -40)),
]
if __name__ == "__main__":
    open(sys.argv[1], "w").write("\n".join(SHOTS) + "\n")
    print(len(SHOTS), "shots")
