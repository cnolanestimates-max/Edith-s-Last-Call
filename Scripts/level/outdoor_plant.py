"""Where the grass grows.  Plain Python:  python outdoor_plant.py   ->  SourceArt/Outdoors/grass_points.json

Reads SourceArt/Outdoors/grass_mask.json (outdoor_mask.py) and plants clumps (SM_Grass_* from Scripts/art/outdoor_grass.py):
  - the yard, inside the fence and a strip beyond it: patchy, thicker along the walls, the path edges and round things left
    standing, none on the gravel, under the house or inside a prop
  - the verges of the forest road, thickest at the edge of the ruts and thinning into the trees, with sprouts in the crown
Each point: [x, y, yaw degrees, scale].  polish_outdoors.py turns them into instances."""
import json, math, random

ROOT = "C:/GameDev/Unreal/WellnessCheck"
M = json.load(open(ROOT + "/SourceArt/Outdoors/grass_mask.json"))
half = M["path_half"]
rr = random.Random(1993)
KINDS = {"T": ["T1", "T2", "T3"], "S": ["S1", "S2"], "C": ["C1", "C2", "C3", "C4"], "B": ["B1", "B2"], "L": ["L1", "L2"], "F": ["F1", "F2"]}


def _h(ix, iy, s):
    n = (ix * 374761393 + iy * 668265263 + s * 2147483647) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((n ^ (n >> 16)) & 0xFFFF) / 65535.0


def noise(x, y, s=0):
    """Smooth value noise, -0.5 .. 0.5."""
    ix, iy = math.floor(x), math.floor(y)
    fx, fy = x - ix, y - iy
    fx, fy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    a = _h(ix, iy, s) * (1 - fx) + _h(ix + 1, iy, s) * fx
    b = _h(ix, iy + 1, s) * (1 - fx) + _h(ix + 1, iy + 1, s) * fx
    return a * (1 - fy) + b * fy - 0.5


def seg_dist(px, py, a, b):
    ax, ay = b[0] - a[0], b[1] - a[1]
    t = max(0.0, min(1.0, ((px - a[0]) * ax + (py - a[1]) * ay) / (ax * ax + ay * ay or 1.0)))
    return math.hypot(px - a[0] - t * ax, py - a[1] - t * ay)


def blocked(x, y, m=0.0):
    for x0, x1, y0, y1 in M["rects"]:
        if x0 - m < x < x1 + m and y0 - m < y < y1 + m:
            return True
    for poly in M["paths"]:
        for a, b in zip(poly, poly[1:]):
            if seg_dist(x, y, a, b) < half + m:
                return True
    for cx, cy, r in M["circles"]:
        if abs(x - cx) < r + m and abs(y - cy) < r + m and math.hypot(x - cx, y - cy) < r + m:
            return True
    return False


def on_road(x, y, m=0.0):
    for cx, cy, yaw, ln, wd in M["road"]:
        if abs(x - cx) > ln + wd or abs(y - cy) > ln + wd:
            continue
        c, s = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
        lx, ly = (x - cx) * c + (y - cy) * s, -(x - cx) * s + (y - cy) * c
        if abs(lx) < ln / 2 + 30 and abs(ly) < wd / 2 + m:
            return True
    return False


out = {v: [] for vs in KINDS.values() for v in vs}


def plant(x, y, d):
    u = rr.random()
    if d < 0:
        k = "F"
    elif u < 0.06 + 0.16 * d:
        k = "T"
    elif u < 0.09 + 0.22 * d:
        k = "S"
    elif u < 0.36 + 0.20 * d:
        k = "C"
    elif u < 0.46 + 0.18 * d:
        k = "B"
    elif u < 0.80:
        k = "L"
    else:
        k = "F"
    out[rr.choice(KINDS[k])].append([round(x, 1), round(y, 1), round(rr.uniform(0, 360), 1), round(rr.uniform(0.82, 1.22), 3)])


# ---- the yard
X0, X1, Y0, Y1 = -2700.0, 4560.0, -1500.0, 1500.0
ny = 0
for k in range(int((X1 - X0) * (Y1 - Y0) / 10000.0 * 15.0)):
    x, y = rr.uniform(X0, X1), rr.uniform(Y0, Y1)
    if blocked(x, y) or on_road(x, y, 40.0):
        continue
    d = 0.42 + 0.95 * noise(x * 0.0026, y * 0.0026, 1) + 0.40 * noise(x * 0.009, y * 0.009, 2)
    if blocked(x, y, 85.0):
        d += 0.30
    if not (-2460 < x < 4260 and -1090 < y < 1090):
        d *= 0.75
    if rr.random() < d:
        plant(x, y, max(0.0, min(1.0, d)))
        ny += 1
# ---- the road
nr = 0
for cx, cy, yaw, ln, wd in M["road"]:
    c, s = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    for k in range(int(ln * 2 * 520 / 10000.0 * 3.4)):
        lx = rr.uniform(-ln / 2, ln / 2)
        off = wd / 2 - 25.0 + 520.0 * rr.random() ** 1.6
        ly = off * rr.choice((-1, 1))
        x, y = cx + lx * c - ly * s, cy + lx * s + ly * c
        if on_road(x, y, -30.0) or x > X0 + 40.0:
            continue
        d = 0.9 - 0.6 * (off - wd / 2) / 520.0 + 0.5 * noise(x * 0.006, y * 0.006, 3)
        if rr.random() < d:
            plant(x, y, max(0.0, min(1.0, d)))
            nr += 1
    for k in range(int(ln / 100.0 * 1.4)):                                   # the crown of the road, between the ruts
        lx, ly = rr.uniform(-ln / 2, ln / 2), rr.uniform(-26.0, 26.0)
        plant(cx + lx * c - ly * s, cy + lx * s + ly * c, -1.0)
        nr += 1
json.dump({"ground": M["ground"], "clumps": out}, open(ROOT + "/SourceArt/Outdoors/grass_points.json", "w"))
print(f"{ny} clumps in the yard, {nr} along the road:", {k: len(v) for k, v in out.items()})
