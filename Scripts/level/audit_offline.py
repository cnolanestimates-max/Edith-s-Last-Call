"""Second half of audit_props.py, outside Unreal: which side of each piece of furniture has a wall, from the dumped
bounds of the house shell (traces in a loaded map in a commandlet hit nothing).  Writes furniture_shots.txt and a report."""
import json, math
A = "C:/GameDev/Unreal/WellnessCheck/Saved/_audit/"
rows = json.load(open(A + "props.json", encoding="utf-8"))
walls = []
for r in rows:
    if "Shell" not in r["folder"]:
        continue
    mn, mx = r["world_min"], r["world_max"]
    dx, dy, dz = mx[0] - mn[0], mx[1] - mn[1], mx[2] - mn[2]
    if dz > 60 and min(dx, dy) < 45 and max(dx, dy) > 40:
        walls.append((mn, mx, r["label"]))


def ray(ox, oy, z, dx, dy, maxd=400.0):
    best, lab = maxd, ""
    for mn, mx, l in walls:
        if not (mn[2] <= z <= mx[2]):
            continue
        tmin, tmax = 0.0, maxd
        ok = True
        for o, d, lo, hi in ((ox, dx, mn[0], mx[0]), (oy, dy, mn[1], mx[1])):
            if abs(d) < 1e-6:
                if o < lo or o > hi:
                    ok = False
                    break
            else:
                t1, t2 = (lo - o) / d, (hi - o) / d
                t1, t2 = min(t1, t2), max(t1, t2)
                tmin, tmax = max(tmin, t1), min(tmax, t2)
                if tmin > tmax:
                    ok = False
                    break
        if ok and tmin < best:
            best, lab = tmin, l
    return best, lab


FLOORS = [-350.0, 0.0, 350.0, 700.0]
TALL = ("wardrobe", "bookshelf", "bookcase", "shelf", "cabinet", "armoire", "hutch", "cupboard", "locker", "upright", "fridge", "clock")
shots, rep = [], []
for r in rows:
    if not r.get("furniture"):
        continue
    mn, mx = r["world_min"], r["world_max"]
    cx, cy = (mn[0] + mx[0]) / 2, (mn[1] + mx[1]) / 2
    zb = mn[2]
    z = zb + max(25.0, (mx[2] - zb) / 3)
    yaw = math.radians(r["yaw"])
    lx, ly = r["local"][0], r["local"][1]
    ax = (math.cos(yaw), math.sin(yaw)) if lx <= ly else (-math.sin(yaw), math.cos(yaw))
    half = min(lx, ly) / 2
    d_pos, l_pos = ray(cx, cy, z, ax[0], ax[1])
    d_neg, l_neg = ray(cx, cy, z, -ax[0], -ax[1])
    d_pos -= half; d_neg -= half
    sgn = 1 if d_pos >= d_neg else -1
    room = d_pos if sgn > 0 else d_neg
    back = d_neg if sgn > 0 else d_pos
    # the local axis (and sign) that points to the open room: a piece with its back to a wall has its front this way
    local_axis = ("X" if lx <= ly else "Y") + ("+" if sgn > 0 else "-")
    floor = min(FLOORS, key=lambda f: abs(zb - f))
    dist = half + max(80.0, min(room - 25.0, 180.0))
    camx, camy = cx + ax[0] * sgn * dist, cy + ax[1] * sgn * dist
    name = (r["label"] + " " + r["mesh"]).lower()
    tz = zb + (mx[2] - zb) * (0.55 if any(k in name for k in TALL) else 0.6)
    pitch = max(-38.0, min(8.0, math.degrees(math.atan2(tz - (floor + 156), dist))))
    lyaw = math.degrees(math.atan2(cy - camy, cx - camx))
    r.update(back_gap=round(back), room_in_front=round(room), open_local=local_axis, back_wall=(l_neg if sgn > 0 else l_pos))
    shots.append(f"{r['shot']}|{camx:.0f},{camy:.0f},{floor + 92:.0f},{lyaw:.1f},{pitch:.1f}")
    rep.append(r)
open(A + "furniture_shots.txt", "w", encoding="utf-8").write("\n".join(shots) + "\n")
json.dump(rep, open(A + "furniture.json", "w", encoding="utf-8"), indent=0)
for r in rep:
    print(f"{r['shot'][:42]:42s} {r['mesh'].split('/')[-1][:30]:30s} yaw{r['yaw']:7.1f} open={r['open_local']} back_gap={r['back_gap']:5d} room={r['room_in_front']:5d}")
