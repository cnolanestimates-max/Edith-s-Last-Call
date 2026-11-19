# The rot pass.  exec'd by build_house.py after the clean layout (shares its helpers).
#
# Cheyenne's direction: a 200-year-old settler farmhouse that an old woman with dementia lived and died in, months ago.
# Nothing is clean.  Filth on the walls, peeling paper, mold, damp, rust, broken glass, rubbish underfoot, flies,
# puddles, holes in the floors, rotten food, a kitchen and bathroom you would not touch.
import random

rng = random.Random(1140)
DEC = "Decay/"
count["decal"] = 0


def fab_mesh(folder):
    """Megascans static mesh by its /Game/Fab/<folder> name (None if that pack is not installed)."""
    reg = unreal.AssetRegistryHelpers.get_asset_registry()
    for a in reg.get_assets_by_path("/Game/Fab/" + folder, recursive=True):
        if str(a.asset_class_path.asset_name) == "StaticMesh":
            return a.get_asset()
    log("fab mesh missing: " + folder)
    return None


def fab(folder, x, y, z, yaw=0.0, sub="Fab", scale=1.0, collide=True, pitch=0.0, roll=0.0, tags=(), name=None):
    m = fab_mesh(folder)
    if not m:
        return None
    return place(m, x, y, z, yaw, DEC + sub, name=name or folder[:40], scale=scale, collide=collide, pitch=pitch, roll=roll, tags=tags)


DECALS = {}
for n in ("mold_01", "mold_02", "mold_03", "water_01", "water_02", "filth_01", "filth_02", "filth_03", "rust_01", "dirt_01", "dirt_02",
          "crack_01", "blood_old", "scratches", "puddle_01", "puddle_02"):
    p = f"{G}/Decals/MD_{n}"
    if eal.does_asset_exist(p):
        DECALS[n] = asset(p)
log(f"{len(DECALS)} decal materials")


def decal(name, x, y, z, rot, size, depth=24.0, tags=()):
    if name not in DECALS:
        return None
    a = actors.spawn_actor_from_class(unreal.DecalActor, V(x, y, z), rot)
    d = a.decal
    d.set_decal_material(DECALS[name])
    d.set_editor_property("decal_size", V(depth, size[0] / 2.0, size[1] / 2.0))
    a.set_actor_label("Decal_" + name)
    tag(a, tags)
    a.set_folder_path("House/" + DEC + "Decals")
    count["decal"] += 1
    return a


UPRIGHT = {"water_01", "rust_01", "filth_02", "filth_03"}       # these have a "down"
ROLL_UP = float(os.environ.get("WC_DECAL_ROLL", "90"))           # roll that puts the texture's bottom toward the floor


def wall_decal(name, x, y, z, facing, w, h=None):
    """facing: 'x+' means the wall surface faces +X (the decal looks along -X into it), etc."""
    yaw = {"x+": 180.0, "x-": 0.0, "y+": -90.0, "y-": 90.0}[facing]
    roll = ROLL_UP if name in UPRIGHT else rng.uniform(0, 360)
    return decal(name, x, y, z, R(yaw, 0, roll), (w, h or w))


def floor_decal(name, x, y, z, w, h=None):
    return decal(name, x, y, z, R(rng.uniform(0, 360), -90, 0), (w, h or w), depth=14.0)


def ceil_decal(name, x, y, z, w):
    return decal(name, x, y, z, R(rng.uniform(0, 360), 90, 0), (w, w), depth=14.0)


# ---------------------------------------------------------------- rooms: (x0, x1, y0, y1, floor z, filth level 0..1, kind)
ROOMS = {
    "hall": (16, 1584, -184, 184, GZ, 0.7, "hall"), "hall2": (1616, 2784, -184, 184, GZ, 0.7, "hall"),
    "den": (1616, 2384, -584, -216, GZ, 0.7, "room"), "bath_g": (2416, 2784, -584, -216, GZ, 1.0, "wet"),
    "pantry": (1616, 1984, 216, 584, GZ, 1.0, "wet"), "sickroom": (2016, 2784, 216, 584, GZ, 0.9, "room"),
    "uphall2": (1616, 2784, -184, 184, UZ, 0.7, "hall"), "daniel": (1616, 2384, -584, -216, UZ, 0.6, "room"),
    "sewing": (2416, 2784, -584, -216, UZ, 0.8, "room"), "aide": (1616, 2384, 216, 584, UZ, 0.7, "room"),
    "bath2": (2416, 2784, 216, 584, UZ, 1.0, "wet"), "living": (16, 784, -584, -216, GZ, 0.8, "room"), "sitting": (816, 1584, -584, -216, GZ, 0.9, "room"),
    "dining": (16, 784, 216, 584, GZ, 0.9, "room"), "kitchen": (816, 1584, 216, 584, GZ, 1.0, "wet"),
    "uphall": (16, 1584, -184, 184, UZ, 0.7, "hall"), "kids": (16, 784, -584, -216, UZ, 0.8, "room"), "bath": (816, 1584, -584, -216, UZ, 1.0, "wet"),
    "master": (16, 784, 216, 584, UZ, 0.9, "room"), "prayer": (816, 1584, 216, 584, UZ, 0.9, "room"),
    "attic": (40, 1560, -560, 560, AZ, 0.6, "attic"), "cellar": (16, 1584, -184, 184, CZ, 0.9, "cellar"),
    "cellarwing": (16, 784, -584, -216, CZ, 0.9, "cellar"), "root": (1216, 1584, 232, 584, CZ, 1.0, "cellar"),
}
WALL_POOL = ["mold_01", "mold_02", "mold_03", "water_01", "water_01", "filth_01", "filth_02", "filth_03", "rust_01", "crack_01", "mold_03", "mold_01"]
FLOOR_POOL = ["dirt_01", "dirt_02", "dirt_01", "water_02", "mold_02", "filth_01"]
SMALL = ["Debris_Plaster_Pile", "Debris_Wall_Chunk", "Glass_Shards_Small", "Glass_Shards_Large", "Plank_Single", "Plank_Broken", "Newspaper_Single",
         "Newspaper_Pile", "Bottles_Empty_Group", "Tin_Cans_Rusty", "Letters_Scattered", "Book_Pile_Fallen", "Plate_Broken", "Teacup_Broken",
         "Brick_Pile", "Chair_Broken_Pieces", "Lamp_Shade_Broken", "Picture_Frame_Fallen", "Picture_Frame_Broken_Glass", "Rat", "Rat_Standing"]
MEGA_SMALL = ["Urban_Ruin_Scatter_Can_Metal_S_07", "Urban_Ruin_Scatter_Can_Metal_S_09", "Urban_Ruin_Scatter_Debris_Wood_L_02", "Urban_Ruin_Scatter_Debris_Wood_L_03",
              "Urban_Ruin_Plank_Wood_M", "Urban_Shanty_Town_Rag_Fabric_Worn", "Urban_Australian_Desolation_Mug_Metal_Rusty"]
STAIR = (380, 820, -200, 30)


def in_stair(x, y):
    return STAIR[0] < x < STAIR[1] and STAIR[2] < y < STAIR[3]


for rname, (x0, x1, y0, y1, z, filth, kind) in ROOMS.items():
    top = 330.0 if kind != "attic" else 150.0
    per_m = 0.34 * filth
    # walls: -Y wall faces +Y etc.
    sides = (("y+", x0, x1, y0), ("y-", x0, x1, y1), ("x+", y0, y1, x0), ("x-", y0, y1, x1))
    for facing, a0, a1, fixed in sides:
        if kind == "attic" and facing[0] == "x":
            continue
        n = int((a1 - a0) / 100.0 * per_m + rng.random())
        for _ in range(n):
            name = rng.choice(WALL_POOL)
            t = rng.uniform(a0 + 50, a1 - 50)
            size = rng.uniform(90, 230)
            if name in ("water_01", "rust_01", "filth_02"):
                hz = z + top - size * 0.45 - rng.uniform(0, 40)
            elif name in ("mold_01", "mold_02", "mold_03"):
                hz = z + rng.choice((rng.uniform(30, 90), rng.uniform(220, top - 30)))
            else:
                hz = z + rng.uniform(60, 220)
            if facing[0] == "y":
                if in_stair(t, fixed):
                    continue
                wall_decal(name, t, fixed, hz, facing, size)
            else:
                wall_decal(name, fixed, t, hz, facing, size)
    # floor filth, puddles, ceiling damp
    area = (x1 - x0) * (y1 - y0) / 10000.0
    for _ in range(int(area * 0.16 * filth) + 2):
        x, y = rng.uniform(x0 + 60, x1 - 60), rng.uniform(y0 + 60, y1 - 60)
        if not in_stair(x, y):
            floor_decal(rng.choice(FLOOR_POOL), x, y, z + 1, rng.uniform(140, 320))
    if kind in ("wet", "cellar"):
        for _ in range(3 if kind == "wet" else 2):
            floor_decal(rng.choice(("puddle_01", "puddle_02")), rng.uniform(x0 + 90, x1 - 90), rng.uniform(y0 + 90, y1 - 90), z + 1, rng.uniform(120, 240))
    if kind != "attic" and kind != "cellar":
        for _ in range(int(area * 0.07) + 1):
            x, y = rng.uniform(x0 + 80, x1 - 80), rng.uniform(y0 + 80, y1 - 80)
            if not in_stair(x, y):
                ceil_decal(rng.choice(("water_02", "mold_03", "mold_01")), x, y, z + 329, rng.uniform(150, 300))
    # rubbish underfoot (never blocks: you can walk through it)
    for _ in range(int(area * 0.22 * filth) + 3):
        x, y = rng.uniform(x0 + 35, x1 - 35), rng.uniform(y0 + 35, y1 - 35)
        if in_stair(x, y):
            continue
        if rng.random() < 0.35:
            fab(rng.choice(MEGA_SMALL), x, y, z + 0.5, rng.uniform(0, 360), "Scatter", collide=False)
        else:
            place(rng.choice(SMALL), x, y, z, rng.uniform(0, 360), DEC + "Scatter", collide=False)
    # cobwebs up in the corners
    if kind != "attic":
        for cx, cy, yaw in ((x0 + 4, y0 + 4, 0), (x1 - 4, y0 + 4, 90), (x1 - 4, y1 - 4, 180), (x0 + 4, y1 - 4, 270)):
            if rng.random() < 0.75 and not in_stair(cx, cy):
                place("Cobweb_Corner", cx, cy, z + 330 - 80, yaw, DEC + "Cobwebs", collide=False, shadow=False)
log(f"rot: {count['decal']} decals")

# ---------------------------------------------------------------- broken glass under every window, rags of curtain
for (x, y, z) in ((40, -400, GZ), (40, 400, GZ), (2760, -400, GZ), (2760, 400, GZ), (200, 560, GZ), (1000, 560, GZ), (1000, -560, GZ), (1800, -560, GZ), (2600, 560, GZ), (1800, 560, UZ), (2600, -560, UZ), (1800, -560, UZ),
                  (40, -400, UZ), (40, 0, UZ), (40, 400, UZ), (200, 560, UZ), (200, -560, UZ), (1000, -560, UZ), (2760, 0, UZ)):
    place("Glass_Shards_Window_Pile", x, y, z, rng.uniform(0, 360), DEC + "Glass", collide=False)

# ---------------------------------------------------------------- holes: the floor has given way in places (blocked so nobody falls)
for (x0, x1, y0, y1, zt, zb) in HOLE_LIST:
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    box(f"HoleBlock_{int(cx)}_{int(zt)}", x0 - 22, x1 + 22, y0 - 22, y1 + 22, zt, zt + 190, "WC:M_Collision", DEC + "Holes", hidden=True)
    for k in range(9):
        ang = rng.uniform(0, 360)
        ex, ey = cx + math.cos(math.radians(ang)) * (x1 - x0) * 0.55, cy + math.sin(math.radians(ang)) * (y1 - y0) * 0.55
        m = rng.choice(("Plank_Broken", "Plank_Single", "Plank_Broken"))
        place(m, ex, ey, zt - rng.uniform(4, 30), ang + rng.uniform(-30, 30), DEC + "Holes", collide=False, pitch=rng.uniform(-40, 10), roll=rng.uniform(-15, 15))
    for k in range(3):
        fab("Urban_Ruin_Scatter_Debris_Wood_L_02", cx + rng.uniform(-40, 40), cy + rng.uniform(-40, 40), zt - 60, rng.uniform(0, 360), "Holes", collide=False, pitch=rng.uniform(40, 80))
    place("Planks_Pile", cx + rng.uniform(-30, 30), cy + rng.uniform(-30, 30), zb, rng.uniform(0, 360), DEC + "Holes", collide=False)
    place("Debris_Plaster_Pile", cx + 40, cy - 30, zb, rng.uniform(0, 360), DEC + "Holes", collide=False)
    floor_decal("dirt_01", cx, cy, zb + 1, 300)

# ---------------------------------------------------------------- ceilings coming down
for (x, y, z) in ((1200, 0, GZ), (400, 400, GZ), (1300, -420, GZ), (1200, 420, UZ), (300, -420, UZ), (1350, 60, UZ), (2300, 0, GZ), (2100, -420, GZ), (2500, 420, GZ), (2200, 0, UZ), (2000, 420, UZ)):
    place("Ceiling_Panel_4x4_Broken", x, y, z + 300, rng.choice((0, 90, 180, 270)), DEC + "Ceilings", collide=False, scale=0.6)
    place("Debris_Plaster_Pile", x + rng.uniform(-60, 60), y + rng.uniform(-60, 60), z, rng.uniform(0, 360), DEC + "Ceilings", collide=False, scale=1.5)
    place("Debris_Wall_Chunk", x + rng.uniform(-90, 90), y + rng.uniform(-90, 90), z, rng.uniform(0, 360), DEC + "Ceilings", collide=False)
for (x, y, z, yaw) in ((700, 400, GZ, 90), (1250, -380, GZ, 0), (500, -400, UZ, 90), (1250, 380, UZ, 0)):
    place("Ceiling_Beam_Sagging", x, y, z + 276, yaw, DEC + "Ceilings", collide=False)
fab("Urban_Ruin_Wall_Plaster_L", 30, 150, GZ, 90, "Walls", collide=False)
fab("Urban_Ruin_Wall_Plaster_L", 2770, -150, UZ, 270, "Walls", collide=False)
fab("Urban_Ruin_Molding_Ceiling_Wood_Weathered", 900, 150, GZ, 20, "Walls", collide=False)

# ---------------------------------------------------------------- the kitchen: months of rot
KX = DEC + "Kitchen"
fab("Urban_Asylum_Equipment_Stove_Metal_Weathered", 1180, 560, GZ, 180, "Kitchen", scale=1.35)
fab("Urban_Australian_Desolation_Oven_Metal_Broken", 1300, 560, GZ, 180, "Kitchen", scale=1.3)
fab("Urban_Australian_Desolation_Kettle_Metal_Worn", 1170, 555, GZ + 86, 30, "Kitchen", collide=False)
fab("Urban_Australian_Desolation_Pan_Metal_Rusty", 1230, 400, GZ + 89, 70, "Kitchen", collide=False)
fab("Urban_Australian_Desolation_Mug_Metal_Rusty", 1290, 440, GZ + 89, 0, "Kitchen", collide=False)
fab("Urban_Asylum_Equipment_Bowl_Metal_Worn", 1270, 380, GZ + 89, 0, "Kitchen", collide=False)
fab("Urban_Australian_Desolation_Basin_Metal_Rusty", 1050, 520, GZ, 0, "Kitchen", collide=False)
fab("Urban_Australian_Desolation_Bucket_Metal_Weathered", 960, 480, GZ, 40, "Kitchen")
fridge = asset(G + "/Props/SM_Fridge", must=False)
if fridge:
    place(fridge, 1545, 520, GZ, float(os.environ.get("WC_FRIDGE_YAW", "180")), KX, name="Fridge")
    point("Flies_fridge", 1500, 500, GZ + 110, tags=["Flies"])
for n, x, y, zz in (("Pumpkin_Rotten", 1220, 440, 89), ("Plates_Stack_Dusty", 1042, 562, 82), ("Plate_Broken", 1120, 300, 0), ("Bottles_Empty_Group", 1082, 560, 82),
                    ("Tin_Cans_Rusty", 1340, 350, 0), ("Rat_Group", 1420, 520, 0), ("Bones_Pile", 1260, 450, 86), ("Teapot_Old", 1290, 400, 89)):
    place(n, x, y, GZ + zz, rng.uniform(0, 360), KX, collide=False, scale=0.6 if n in ("Pumpkin_Rotten", "Bones_Pile") else 1.0)
for (x, y) in ((1250, 420), (1050, 540), (900, 540)):
    floor_decal("filth_01", x, y, GZ + 1, 200)
floor_decal("blood_old", 1250, 300, GZ + 1, 180)
wall_decal("filth_03", 1100, 584, GZ + 150, "y-", 260)
wall_decal("filth_02", 1400, 584, GZ + 200, "y-", 240)
wall_decal("mold_03", 1584, 420, GZ + 120, "x-", 300)
point("Flies_kitchen", 1250, 420, GZ + 115, tags=["Flies"])
point("Flies_sink", 1050, 560, GZ + 110, tags=["Flies"])
point("Flies_dining", 420, 400, GZ + 110, tags=["Flies"])
# dining: the four set places, long rotten
for (x, y) in ((330, 380), (510, 380), (330, 420), (510, 420)):
    place("Plate_Broken" if rng.random() < 0.4 else "Plates_Stack_Dusty", x, y, GZ + 80, rng.uniform(0, 360), DEC + "Dining", collide=False, scale=0.8)
place("Pumpkin_Rotten", 440, 395, GZ + 80, 0, DEC + "Dining", collide=False, scale=0.5)
place("Bones_Pile", 380, 410, GZ + 78, 30, DEC + "Dining", collide=False, scale=0.45)
floor_decal("filth_01", 420, 300, GZ + 1, 260)

# ---------------------------------------------------------------- the bathroom
BX = "Bath"
fab("Urban_Australian_Desolation_Bathtub_Metal_Rusty", 1000, -520, UZ, 0, BX, scale=1.15)
fab("Urban_Australian_Desolation_Sink_Mixed_Weathered", 1250, -560, UZ, 0, BX)
toilet = asset(G + "/Props/SM_Toilet", must=False)
if toilet:
    place(toilet, 1470, -545, UZ, float(os.environ.get("WC_TOILET_YAW", "90")), DEC + BX, name="Toilet")
point("Flies_toilet", 1470, -530, UZ + 70, tags=["Flies"])
point("Flies_tub", 1000, -520, UZ + 80, tags=["Flies"])
for (n, x, y, face, s) in (("filth_03", 1000, -584, "y+", 280), ("mold_03", 1250, -584, "y+", 300), ("rust_01", 1100, -584, "y+", 200),
                           ("filth_02", 1470, -584, "y+", 240), ("mold_01", 1584, -400, "x-", 280), ("water_01", 816, -420, "x+", 260)):
    wall_decal(n, x, y, UZ + 150, face, s)
for (x, y, n) in ((1000, -440, "puddle_01"), (1400, -480, "puddle_02"), (1200, -400, "filth_01"), (1470, -480, "filth_01"), (1100, -300, "blood_old")):
    floor_decal(n, x, y, UZ + 1, 220)
fab("Urban_Shanty_Town_Rag_Fabric_Worn", 1100, -480, UZ + 1, 30, BX, collide=False, roll=90)
fab("Urban_Australian_Desolation_Bucket_Metal_Weathered", 1350, -540, UZ, 100, BX)

# ---------------------------------------------------------------- beds, couches, clothes: lived in, then left
fab("Urban_Shanty_Town_Mattress_Fabric_Damaged", 250, -520, UZ + 46, 0, "Soft", collide=False, scale=(0.95, 0.6, 1.0))
fab("Urban_Shanty_Town_Couch_Fabric_Worn", 1000, -540, GZ, 0, "Soft", scale=1.25)
fab("Urban_Shanty_Town_Blanket_Fabric_Worn", 560, 420, UZ + 62, 90, "Soft", collide=False, pitch=-90)
fab("Urban_Shanty_Town_Dress_Fabric_Worn", 150, 430, UZ + 2, 40, "Soft", collide=False, roll=90)
fab("Urban_Shanty_Town_Dress_Fabric_Worn", 1300, -540, GZ + 150, 0, "Soft", collide=False)
fab("Urban_Shanty_Town_Chair_Wood_Damaged", 300, 150, UZ, 200, "Soft")
fab("Urban_Shanty_Town_Chair_Mixed_Damaged", 1350, 140, GZ, 70, "Soft", collide=False)
fab("Urban_Australian_Desolation_Bookshelf_Wood_Weathered", 60, -540, GZ, 90, "Soft", scale=1.8)
fab("Urban_Australian_Desolation_Suitcase_Leather_Worn", 640, 300, UZ, 20, "Soft")
# scratches where she has been at the walls and doors
for (x, y, z, face) in ((1343, -184, GZ + 120, "y+"), (800 + 16, -90, GZ + 130, "x+"), (144, 184, UZ + 150, "y-"), (943, 184, UZ + 140, "y-"), (1400, 232, CZ + 130, "y+")):
    wall_decal("scratches", x, y, z, face, 110)
floor_decal("blood_old", 1400, 470, CZ + 1, 200)
point("Flies_root", 1400, 540, CZ + 120, tags=["Flies"])
floor_decal("puddle_01", 600, 40, CZ + 1, 300)
floor_decal("puddle_02", 1100, -60, CZ + 1, 260)

log(f"rot done: {count}")
