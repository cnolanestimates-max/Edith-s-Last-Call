"""Floor plans of every room from Saved/_audit/props.json: each mesh's footprint as an oriented box, furniture labelled,
with an arrow out of its front (kit furniture faces local +Y), doorways marked.  Saved/_audit/plans/<room>.png"""
import json, math, re
from PIL import Image, ImageDraw
A = "C:/GameDev/Unreal/WellnessCheck/Saved/_audit/"
GZ, UZ, AZ, CZ = 0, 350, 700, -350
ROOMS = {
    "den": (1616, 2384, -584, -216, GZ), "bath_g": (2416, 2784, -584, -216, GZ), "pantry": (1616, 1984, 216, 584, GZ), "sickroom": (2016, 2784, 216, 584, GZ),
    "daniel": (1616, 2384, -584, -216, UZ), "sewing": (2416, 2784, -584, -216, UZ), "aide": (1616, 2384, 216, 584, UZ), "bath2": (2416, 2784, 216, 584, UZ),
    "living": (16, 784, -584, -216, GZ), "sitting": (816, 1584, -584, -216, GZ), "dining": (16, 784, 216, 584, GZ), "kitchen": (816, 1584, 216, 584, GZ),
    "kids": (16, 784, -584, -216, UZ), "bath": (816, 1584, -584, -216, UZ), "master": (16, 784, 216, 584, UZ), "prayer": (816, 1584, 216, 584, UZ),
    "hall": (16, 1584, -184, 184, GZ), "hall2": (1616, 2784, -184, 184, GZ), "uphall": (16, 1584, -184, 184, UZ), "uphall2": (1616, 2784, -184, 184, UZ),
    "attic": (40, 1560, -560, 560, AZ), "cellar": (16, 1584, -184, 184, CZ), "cellarwing": (16, 784, -584, -216, CZ), "root": (1216, 1584, 232, 584, CZ)}
rows = json.load(open(A + "props.json", encoding="utf-8"))
FURN = json.load(open(A + "furniture.json", encoding="utf-8"))
fl = {r["label"] + "|" + r["folder"] for r in FURN}
S = 1.25
for name, (x0, x1, y0, y1, z) in ROOMS.items():
    pad = 60
    W, H = int((x1 - x0 + 2 * pad) * S), int((y1 - y0 + 2 * pad) * S)
    im = Image.new("RGB", (W, H), (24, 24, 26))
    d = ImageDraw.Draw(im)
    P = lambda x, y: ((x - x0 + pad) * S, (y1 + pad - y) * S)          # +Y up the page, +X to the right
    d.rectangle([P(x0, y1), P(x1, y0)], outline=(200, 200, 200), width=3)
    items = []
    for r in rows:
        lx, ly, lz = r["loc"]
        if not (x0 - 20 < lx < x1 + 20 and y0 - 20 < ly < y1 + 20 and z - 30 < r["world_min"][2] < z + 260):
            continue
        if "Shell" in r["folder"] or "Tour" in r["folder"] or "Decal" in r["cls"]:
            if "Doorway" in r["label"] and z - 30 < r["world_min"][2] < z + 30:
                mn, mx = r["world_min"], r["world_max"]
                d.rectangle([P(mn[0], mx[1]), P(mx[0], mn[1])], outline=(90, 160, 255), width=2)
            continue
        mn, mx = r["world_min"], r["world_max"]
        if (mx[0] - mn[0]) * (mx[1] - mn[1]) < 400:
            continue
        yaw = math.radians(r["yaw"])
        hx, hy = r["local"][0] / 2, r["local"][1] / 2
        c = ((mn[0] + mx[0]) / 2, (mn[1] + mx[1]) / 2)
        pts = []
        for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            px, py = sx * hx, sy * hy
            pts.append(P(c[0] + px * math.cos(yaw) - py * math.sin(yaw), c[1] + px * math.sin(yaw) + py * math.cos(yaw)))
        f = (r["label"] + "|" + r["folder"]) in fl
        d.polygon(pts, outline=(255, 190, 60) if f else (120, 120, 120), width=2 if f else 1)
        if f:
            fx, fy = -math.sin(yaw), math.cos(yaw)                       # local +Y in the world
            a = P(*c); b = P(c[0] + fx * (hy + 35), c[1] + fy * (hy + 35))
            d.line([a, b], fill=(255, 80, 80), width=3)
            d.ellipse([b[0] - 4, b[1] - 4, b[0] + 4, b[1] + 4], fill=(255, 80, 80))
            items.append((a, re.sub(r"^(SM_|Urban_[A-Za-z]+_)", "", r["label"])[:22]))
    for a, t in items:
        d.text((a[0] - 30, a[1] - 6), t, fill=(255, 255, 255))
    d.text((6, 4), f"{name}  (+Y up, red = local +Y)", fill=(255, 255, 0))
    im.save(A + f"plans/{name}.png")
print("plans written")
