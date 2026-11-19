# She has been there the whole time.  exec'd by build_house.py.
# Eyes in holes in the walls, and hanks of her hair hanging from gaps overhead.  Nothing triggers them and nothing pays
# off: if the player looks straight at one, it is gone.  Plus the shelf for the bookshelf scare in Walter's den.
WF = "Watchers"


def watcher(wid, x, y, z, yaw=0.0, pitch=0.0, kind=0, radius=5.2, scripted=False):
    a = actors.spawn_actor_from_class(WC["WCWatcher"], V(x, y, z), R(yaw, pitch, 0))
    a.set_actor_label("Watcher_" + wid)
    a.set_editor_property("wc_id", unreal.Name(wid))
    a.set_editor_property("kind", kind)
    a.set_editor_property("radius", float(radius))
    a.set_editor_property("scripted", scripted)
    tag(a, ["W_" + wid])
    a.set_folder_path("House/" + WF)
    count["game"] += 1
    return a


def wall_eye(wid, x, y, z, face, radius=5.2, scripted=False, hole=10.0):
    """An eye in a ragged hole in a wall.  (x, y) is ON the wall surface; face is the way the wall looks ('x+', 'y-', ...)."""
    dx, dy = {"x+": (1, 0), "x-": (-1, 0), "y+": (0, 1), "y-": (0, -1)}[face]
    yaw = {"x+": 0.0, "x-": 180.0, "y+": 90.0, "y-": -90.0}[face]
    # the hole: a black, uneven patch just proud of the plaster, with cracks running from it
    for i, (oy, oz, s) in enumerate(((0, 0, 1.0), (hole * 0.45, hole * 0.3, 0.6), (-hole * 0.4, -hole * 0.35, 0.55), (hole * 0.2, -hole * 0.5, 0.5))):
        px, py = x + dx * 0.4 + (-dy) * oy, y + dy * 0.4 + dx * oy
        a = place(SPHERE, px, py, z + oz, yaw, WF, name=f"Hole_{wid}_{i}", scale=(0.012, hole * s / 50.0, hole * s * 0.9 / 50.0), mats={0: "WC:M_Black"}, collide=False, shadow=False)
    wall_decal("crack_01", x, y, z + 6, face, hole * 7.0)
    place("Debris_Plaster_Pile", x + dx * 22, y + dy * 22, math.floor(z / 350.0) * 350.0, yaw + 40, WF, collide=False, scale=0.7)
    return watcher(wid, x + dx * 1.0, y + dy * 1.0, z, yaw, 0.0, 0, radius, scripted)


# ---------------------------------------------------------------- eyes
wall_eye("hall_stair", 560, 24, GZ + 222, "y+")                     # high on the stair wall as you come in
wall_eye("kitchen_fridge", 1584, 470, GZ + 214, "x-")               # above the fridge
wall_eye("uphall", 1310, -184, UZ + 226, "y+")                      # upstairs hall, by the portrait with the eyes
wall_eye("daniel", 2384, -360, UZ + 208, "x-")                      # Daniel's room, over the wardrobe
wall_eye("attic_gable", 1120, 588, AZ + 96, "y-", radius=5.8)       # low in the attic gable
wall_eye("cellar", 16, -60, CZ + 204, "x+")                         # the cellar's front wall
watcher("fireplace", 600, -571, GZ + 58, 90.0, 12.0, 0, 5.0)        # in the living-room chimney, looking out of the firebox
watcher("ceiling_hole", 1310, -372, UZ - 30, 0.0, -78.0, 0, 5.6)    # looking down through the hole in the sitting-room ceiling

# ---------------------------------------------------------------- hair
# (removed 2026-11-19 at Cheyenne's request: the hanks of hair drawn up into the ceiling read as a stiff plank, not hair)

# ---------------------------------------------------------------- the settlers book (S10) in Walter's den
BKX0, BKX1, BKY, BKZ = 470.0, 624.0, -216.0, GZ + 141.0             # the settlers book's shelf: its hole is at the height of his eyes (it was a low shelf, and in the den)
M_SHELF = surf("WoodDark", "MI_WoodDark")
_leathers = [surf("LeatherOld", m) for m in ("MI_LeatherRed", "MI_LeatherGreen", "MI_LeatherBlue", "MI_LeatherTan", "MI_Leather")]
# a tall open bookcase against the wall: two uprights, a top, four shelves of county histories
for bx in (BKX0 - 3.0, BKX1):
    box(f"BookCaseSide_{int(bx)}", bx, bx + 3.0, BKY - 22, BKY, GZ, GZ + 182, M_SHELF, "Dressing/Living", collide=False)
box("BookCaseTop", BKX0 - 3.0, BKX1 + 3.0, BKY - 23, BKY, GZ + 179, GZ + 182, M_SHELF, "Dressing/Living", collide=False)
box("BookCaseKick", BKX0, BKX1, BKY - 20, BKY, GZ, GZ + 9, M_SHELF, "Dressing/Living", collide=False)
box("BookCaseBlock", BKX0 - 3.0, BKX1 + 3.0, BKY - 22, BKY, GZ, GZ + 60, M_SHELF, "Dressing/Living", collide=True, hidden=True)      # he cannot walk through it; the books above stay reachable
SETTLERS_X = None
for _row, _z in enumerate((GZ + 33.0, GZ + 69.0, GZ + 105.0, BKZ)):
    box(f"BookShelfBoard_{_row}", BKX0, BKX1, BKY - 21, BKY, _z - 3, _z, M_SHELF, "Dressing/Living", collide=False)
    _bk = random.Random(42 + _row * 7)
    bx = BKX0 + 5.0
    k = 0
    while bx < BKX1 - 8:
        w = _bk.uniform(3.4, 6.2)
        h = _bk.uniform(19.0, 25.0)
        d = _bk.uniform(13.0, 16.5)
        if _z == BKZ and SETTLERS_X is None and bx > (BKX0 + BKX1) / 2 - 6:
            SETTLERS_X = bx + 2.6
            b_ = box("SettlersBook", bx, bx + 5.2, BKY - 17.5, BKY - 2.0, BKZ, BKZ + 24.0, surf("LeatherOld", "MI_Leather"), "Dressing/Living", collide=False, tags=["SettlersBook"])
            b_.static_mesh_component.set_mobility(unreal.ComponentMobility.MOVABLE)
            bx += 5.6
            continue
        if _row < 3 and _bk.random() < 0.12:
            bx += _bk.uniform(6.0, 14.0)                 # a gap where one has gone
            continue
        box(f"ShelfBook_{_row}_{k}", bx, bx + w, BKY - d - 1.5, BKY - 1.5, _z, _z + h, _bk.choice(_leathers), "Dressing/Living", collide=False, roll=_bk.choice((0, 0, 0, 4, -3)))
        bx += w + 0.5
        k += 1
interact("WCUsable", "book_settlers", None, SETTLERS_X, BKY - 12, BKZ + 12, 0, "Pull the book out", (7, 12, 14), (0, 0, 0))
# the hole behind it, and what is in the hole
for i, (ox, oz, s_) in enumerate(((0, 0, 1.0), (4.2, 3.0, 0.6), (-3.6, -3.2, 0.55))):
    place(SPHERE, SETTLERS_X + ox, BKY - 0.4, BKZ + 13 + oz, -90, WF, name=f"BookHole_{i}", scale=(0.012, 8.6 * s_ / 50.0, 8.0 * s_ / 50.0), mats={0: "WC:M_Black"}, collide=False, shadow=False)
watcher("book_eye", SETTLERS_X, BKY - 1.2, BKZ + 13, -90.0, 0.0, 0, 5.6, scripted=True)
# the key that falls out of the hollowed book
pickup("pick_key_desk", "key_desk", "Small desk key", ("KeyDesk", CUBE, (0.05, 0.018, 0.005), {0: "BrassOld"}), SETTLERS_X + 8, BKY - 52, GZ + 2.0, 35, tags=["Show_bookkey"])
log("watchers: 8 eyes, the settlers book")
