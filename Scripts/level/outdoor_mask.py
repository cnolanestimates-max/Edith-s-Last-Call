"""Where grass may not grow, taken from the map survey (Saved/Outdoors/survey.json, written by outdoor_survey.py):
the house, porch and shed, the gravel paths and the drive, the footprints of the yard props and the trunks.
Also the forest road, so its verges can be planted.   python outdoor_mask.py   ->  SourceArt/Outdoors/grass_mask.json"""
import json, os

ROOT = "C:/GameDev/Unreal/WellnessCheck"
R = json.load(open(ROOT + "/Saved/Outdoors/survey.json"))


def short(m):
    return m.split("/")[-1].split(".")[0] if m else ""


def bounds(rows, pad=0.0):
    xs = [r["org"][0] - r["ext"][0] for r in rows] + [r["org"][0] + r["ext"][0] for r in rows]
    ys = [r["org"][1] - r["ext"][1] for r in rows] + [r["org"][1] + r["ext"][1] for r in rows]
    return [min(xs) - pad, max(xs) + pad, min(ys) - pad, max(ys) + pad]


rects = [[-30.0, 2894.0, -694.0, 694.0]]                                     # the house
rects.append(bounds([r for r in R if r["folder"].startswith("House/Shell/Exterior/Shed")], 15.0))
rear = [r for r in R if r["folder"].startswith("House/Shell/RearExtension") and r["cls"] == "StaticMeshActor"]
if rear:
    rects.append(bounds(rear, 5.0))                                          # the rear extension stands on the yard too
porch = [r for r in R if r["folder"].startswith("House/Shell/Exterior/Porch")]
if porch:
    rects.append(bounds(porch, 10.0))
for r in R:
    if r["label"] in ("Path", "Drive"):
        rects.append(bounds([r], 12.0))
circles = []
for r in R:
    f = r["folder"]
    m = short(r.get("mesh", ""))
    if r["cls"] != "StaticMeshActor" or "Fence" in m:
        continue
    if f.startswith(("House/Shell/Exterior/Yard", "House/Shell/Exterior/BackYard", "House/Shell/Exterior/Plot")) and m != "Cube":
        e = max(r["ext"][0], r["ext"][1])
        if 12.0 < e < 320.0 and not m.startswith(("SM_Bramble", "SM_Bush", "SM_Tree")):
            circles.append([r["org"][0], r["org"][1], round(e * 0.75, 1)])
    if m.startswith("SM_Tree_") and -3000 < r["loc"][0] < 5400 and -2200 < r["loc"][1] < 2200:
        circles.append([r["loc"][0], r["loc"][1], 28.0])
    if f.startswith("House/Cruiser") and r["ext"][0] > 80:
        circles.append([r["org"][0], r["org"][1], round(max(r["ext"][0], r["ext"][1]) * 0.9, 1)])
road = [[r["loc"][0], r["loc"][1], r["rot"][2], r["scale"][0] * 100.0, r["scale"][1] * 100.0] for r in R
        if r["folder"] == "House/Forest/Road" and r["label"].startswith("Road_")]
paths = [[(-710, 0), (-649, -340), (-536, -654), (-216, -1000), (53, -1184), (463, -1184), (760, -1000), (1410, -845), (2695, -836), (3230, -755), (3556, -745)],
         [(-710, 0), (-595, 400), (-507, 685), (-431, 911), (-325, 993), (825, 993), (1100, 875), (2610, 802), (3130, 760), (3335, 480), (3345, -482), (3230, -755)]]
os.makedirs(ROOT + "/SourceArt/Outdoors", exist_ok=True)
json.dump({"rects": rects, "circles": circles, "road": road, "paths": paths, "path_half": 112.0, "ground": -40.0},
          open(ROOT + "/SourceArt/Outdoors/grass_mask.json", "w"))
print(len(rects), "rects,", len(circles), "circles,", len(road), "road pieces")
for r in rects:
    print("  rect", [round(v) for v in r])
