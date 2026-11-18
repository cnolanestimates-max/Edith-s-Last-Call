"""The big house: rear wing (X 1600..2800) on both floors, new doors, windows, triggers, and hooks for the new level modules."""
import io
P = "C:/GameDev/Unreal/WellnessCheck/Scripts/level/build_house.py"
s = io.open(P, encoding="utf-8").read()


def sub(old, new):
    global s
    assert old in s, old[:80]
    s = s.replace(old, new, 1)


def cut(a, b, new):
    """Replace everything from marker a up to (not including) marker b."""
    global s
    i, j = s.index(a), s.index(b)
    assert i < j
    s = s[:i] + new + s[j:]


sub('for cls in ("WCDoor", "WCNote", "WCPickup", "WCUsable", "WCTrigger", "WCEntity"):', 'for cls in ("WCDoor", "WCNote", "WCPickup", "WCUsable", "WCTrigger", "WCEntity", "WCLook"):')
sub('SX0, SX1, SY0, SY1 = 400.0, 800.0, -184.0, 8.0          # stair tower footprint (inner)',
    'SX0, SX1, SY0, SY1 = 400.0, 800.0, -184.0, 8.0          # stair tower footprint (inner)\nXB = 2800.0                                              # back wall of the house (the rear wing runs X 1600..2800)')
sub('''HOLES = {GZ: [(470, 620, -560, -440)], UZ: [(1290, 1440, -430, -310)], AZ: [(1280, 1400, 300, 420)]}''',
    '''HOLES = {GZ: [(470, 620, -560, -440)], UZ: [(1290, 1440, -430, -310), (2480, 2600, 330, 450)], AZ: [(1280, 1400, 300, 420)]}''')
sub('''    parts = [(0, SX0, -600, 600), (SX1, 1600, -600, 600), (SX0, SX1, -600, SY0), (SX0, SX1, SY1 + 16, 600)]''',
    '''    parts = [(0, SX0, -600, 600), (SX1, XB, -600, 600), (SX0, SX1, -600, SY0), (SX0, SX1, SY1 + 16, 600)]''')

# ---------------------------------------------------------------- walls
cut("PLAIN, WAIN, DOORW, WIN = ", "# ================================================================== EXTERIOR SHELL", '''PLAIN, WAIN, DOORW, WIN = "Wall_Plain_Simple", "Wall_Wainscot_Green", "Wall_Doorway", "Wall_Window"
PEEL = "Wall_Peeling"
# ---- ground: front block (living, dining, kitchen, her sitting room) + rear wing (den, bath, pantry, sickroom)
run_y(0, GZ, [WIN, DOORW, WIN], "Shell/Ground")                                   # front
run_y(1600, GZ, [PLAIN, "Wall_Doorway_Arched", DOORW], "Shell/Ground")            # old back wall: hall arch, kitchen -> pantry
run_y(XB, GZ, [WIN, DOORW, WIN], "Shell/Ground")                                  # back
run_x(-600, GZ, [PEEL, "Wall_Fireplace_Breast", WIN, "Wall_Wainscot_Grey", WIN, "Wall_Fireplace_Breast", WIN], "Shell/Ground")
run_x(600, GZ, [WIN, PEEL, WIN, "Wall_Exposed_Brick", WIN, PEEL, WIN], "Shell/Ground")
run_x(-200, GZ, ["Wall_Doorway_Double", "Wall_Wainscot_Red", "Wall_Wainscot_Grey", DOORW, DOORW, "Wall_Wainscot_Red", DOORW], "Shell/Ground")   # hall | living, sitting, den, bath
run_x(200, GZ, ["Wall_Doorway_Arched", WAIN, DOORW, PLAIN, WAIN, DOORW, "Wall_Wainscot_Grey"], "Shell/Ground")                               # hall | dining, kitchen, pantry, sickroom
wall("Wall_Wainscot_Red", 800, -400, GZ, "y", "Shell/Ground")                     # living | sitting
wall(DOORW, 800, 400, GZ, "y", "Shell/Ground")                                    # dining | kitchen
wall("Wall_Wainscot_Grey", 2400, -400, GZ, "y", "Shell/Ground")                   # den | bath
wall(PEEL, 2000, 400, GZ, "y", "Shell/Ground")                                    # pantry | sickroom
# ---- upper: master, Ruth's room, bath, prayer room + rear wing (Daniel's room, sewing room, the aide's room, second bath)
run_y(0, UZ, [WIN, WIN, WIN], "Shell/Upper")
run_y(1600, UZ, ["Wall_Striped_Green", DOORW, "Wall_Striped_Purple"], "Shell/Upper")
run_y(XB, UZ, [PLAIN, WIN, PLAIN], "Shell/Upper")
run_x(-600, UZ, [WIN, PEEL, WIN, "Wall_Exposed_Brick", WIN, PEEL, WIN], "Shell/Upper")
run_x(600, UZ, [WIN, PEEL, "Wall_Striped_Purple", PEEL, WIN, PEEL, WIN], "Shell/Upper")
run_x(-200, UZ, [DOORW, "Wall_Striped_Green", DOORW, PLAIN, DOORW, "Wall_Striped_Green", DOORW], "Shell/Upper")               # hall | Ruth's, bath, Daniel's, sewing
run_x(200, UZ, [DOORW, "Wall_Wainscot_Purple", DOORW, "Wall_Striped_Purple", DOORW, "Wall_Wainscot_Purple", DOORW], "Shell/Upper")   # hall | master, prayer, aide's, bath 2
wall("Wall_Striped_Green", 800, -400, UZ, "y", "Shell/Upper")
wall("Wall_Wainscot_Purple", 800, 400, UZ, "y", "Shell/Upper")
wall("Wall_Striped_Green", 2400, -400, UZ, "y", "Shell/Upper")
wall(PEEL, 2400, 400, UZ, "y", "Shell/Upper")
# corner posts hide the seams
for z, f in ((GZ, "Ground"), (UZ, "Upper")):
    for x in (0, 800, 1600, 2400, 2800):
        for y in (-600, -200, 200, 600):
            if (x, y) in ((800, -200),):
                continue
            place("Wall_Corner_Post", x, y, z, 0, "Shell/" + f, collide=False)
    place("Wall_Corner_Post", 2000, 200, GZ, 0, "Shell/Ground", collide=False)
    place("Wall_Corner_Post", 2000, 600, GZ, 0, "Shell/Ground", collide=False)

exec(open(os.path.join(HERE, "exterior.py"), encoding="utf-8").read())
log("shell done")

''')
# drop the old exterior block (now exterior.py): from its header to the windows header
cut("# ================================================================== EXTERIOR SHELL", "# ================================================================== WINDOWS (boarded from the inside), fake doors", "")

# ---------------------------------------------------------------- windows
cut("for z in (GZ, UZ):\n    for y in (-400, 400):\n        window_y(0, y, z, 1)", "# ================================================================== DOORS", '''for z in (GZ, UZ):
    for y in (-400, 400):
        window_y(0, y, z, 1)
    window_x(200, 600, z, -1)
    window_x(200 if z == UZ else 1000, -600, z, 1)
    for x in (1800, 2600):
        window_x(x, -600, z, 1)
window_y(0, 0, UZ, 1); window_y(XB, 0, UZ, -1)
window_y(XB, -400, GZ, -1); window_y(XB, 400, GZ, -1)
window_x(1000, 600, GZ, -1); window_x(1000, -600, UZ, 1)
window_x(1800, 600, GZ, -1); window_x(2600, 600, GZ, -1); window_x(1800, 600, UZ, -1); window_x(2600, 600, UZ, -1)

''')

# ---------------------------------------------------------------- doors
sub('door("back", 1600, -56.5, GZ, 90, 95, locked=True, mesh="Door_Boarded")', '''door("back", XB, -56.5, GZ, 90, 95, locked=True, mesh="Door_Boarded")
door("pantry", 1600, 343.5, GZ, 90, -95)
door("den", 1743.5, -200, GZ, 0, -95)
door("bath_g", 2543.5, -200, GZ, 0, -95, start_open=True)
door("sickroom", 2143.5, 200, GZ, 0, 95)
door("up_ell", 1600, -56.5, UZ, 90, 95, locked=True, key="key_ell")
door("up_daniel", 1743.5, -200, UZ, 0, -95)
door("up_sewing", 2543.5, -200, UZ, 0, -95)
door("up_aide", 1743.5, 200, UZ, 0, 95)
door("up_bath2", 2543.5, 200, UZ, 0, 95, start_open=True)''')

# ---------------------------------------------------------------- tiles
sub('''for _n, (_x0, _x1, _y0, _y1, _z) in {"KitchenTiles": (816, 1584, 216, 584, GZ), "BathTiles": (816, 1584, -584, -216, UZ)}.items():''',
    '''for _n, (_x0, _x1, _y0, _y1, _z) in {"KitchenTiles": (816, 1584, 216, 584, GZ), "BathTiles": (816, 1584, -584, -216, UZ), "PantryTiles": (1616, 1984, 216, 584, GZ),
                                      "BathGTiles": (2416, 2784, -584, -216, GZ), "Bath2Tiles": (2416, 2784, 216, 584, UZ)}.items():''')
sub('''surf("TileDark", "MI_MegaTilesOld" if _n == "KitchenTiles" else "MI_MegaTilesStained")''', '''surf("TileDark", "MI_MegaTilesOld" if _n in ("KitchenTiles", "PantryTiles") else "MI_MegaTilesStained")''')

# ---------------------------------------------------------------- hall end pieces move to the new back of the house; keys move
sub('place("Mirror_Covered_Sheet", 1530, 120, GZ, 250, D + "Hall")', 'place("Mirror_Covered_Sheet", 2730, 120, GZ, 250, D + "Hall")')
sub('place("Bust_Pedestal", 1540, -140, GZ, 110, D + "Hall")', 'place("Bust_Pedestal", 1540, -150, GZ, 110, D + "Hall")')
sub('place("Radiator_Cast_Iron", 1560, 480, GZ, 270, K)', 'place("Radiator_Cast_Iron", 1320, 578, GZ, 180, K)')
sub('pickup("pick_key_attic", "key_attic", "Attic key", CUBE, 1235, 540, UZ + 102, 110, (0.075, 0.022, 0.006), mats={0: "BrassOld"})\n', '')

# ---------------------------------------------------------------- her points, triggers
sub('point("Her_Hall0", 1480, 100, GZ, 180)', 'point("Her_Hall0", 150, 60, GZ, 0)')
sub('trigger("t_cruiser", -1700, -1250, 40, 520, -40, 250)', '''trigger("t_cruiser", -1700, -1250, 40, 520, -40, 250)
trigger("t_up_corridor", 420, 700, 24, 184, UZ, UZ + 250)
trigger("t_sitting", 816, 1584, -584, -216, GZ, GZ + 250)
trigger("t_backhall", 2000, 2780, -180, 180, GZ, GZ + 250)
trigger("t_den", 1620, 2380, -580, -220, GZ, GZ + 250)
trigger("t_sickroom", 2020, 2780, 220, 580, GZ, GZ + 250)
trigger("t_pantry", 1620, 1980, 220, 580, GZ, GZ + 250)
trigger("t_bath_g", 2420, 2780, -580, -220, GZ, GZ + 250)
trigger("t_daniel", 1620, 2380, -580, -220, UZ, UZ + 250)
trigger("t_sewing", 2420, 2780, -580, -220, UZ, UZ + 250)
trigger("t_aide", 1620, 2380, 220, 580, UZ, UZ + 250)
trigger("t_bath2", 2420, 2780, 220, 580, UZ, UZ + 250)
trigger("t_up_ell", 1620, 2780, -180, 180, UZ, UZ + 250)
trigger("t_attic", 420, 1560, -560, 560, AZ, AZ + 250)
trigger("t_hall_mid", 900, 1500, -180, 180, GZ, GZ + 250)''')

# ---------------------------------------------------------------- bot / tour points
sub('("A_Kitchen", 1000, 380, GZ, 20), ("A_BackDoor", 1500, 0, GZ, 0),', '("A_Kitchen", 1000, 380, GZ, 20), ("A_BackDoor", 2700, 0, GZ, 0), ("A_Den", 2000, -380, GZ, 250), ("A_Sickroom", 2400, 380, GZ, 60), ("A_Pantry", 1800, 400, GZ, 60), ("A_BathG", 2600, -380, GZ, 250),\n                        ("A_Daniel", 2000, -380, UZ, 250), ("A_Sewing", 2600, -380, UZ, 250), ("A_Aide", 2000, 380, UZ, 60), ("A_Bath2", 2600, 380, UZ, 60), ("A_UpEll", 1750, 0, UZ, 0),')
sub('TOUR = [("yard", -1900, -200, 52, 8),', 'TOUR = [("road", -9000, 300, 60, 0), ("gate", -3300, 320, 60, -5), ("yard", -1900, -200, 52, 8), ("yard_side", -1200, -1500, 52, 50), ("yard_back", 3900, 1300, 52, 200),\n        ("den", 1640, -240, 92, -40), ("den2", 2360, -560, 92, 140), ("bath_g", 2440, -240, 92, -50), ("pantry", 1640, 240, 92, 45), ("sickroom", 2040, 240, 92, 40), ("sickroom2", 2760, 560, 92, 220),\n        ("hall_rear", 2760, 100, 92, 180), ("up_ell", 1640, 100, UZ + 92, 0), ("daniel", 1640, -240, UZ + 92, -40), ("daniel2", 2360, -560, UZ + 92, 140), ("sewing", 2440, -240, UZ + 92, -50),\n        ("aide", 1640, 240, UZ + 92, 40), ("bath2", 2440, 240, UZ + 92, 45),')
sub('nav.set_actor_scale3d(V(24.0, 13.0, 7.0))', 'nav.set_actor_scale3d(V(36.0, 13.0, 7.0))')
sub('cam = actors.spawn_actor_from_class(unreal.CameraActor, V(-2050, -420, 120), R(12, 6))', 'cam = actors.spawn_actor_from_class(unreal.CameraActor, V(-2150, -620, 110), R(16, 9))')

# ---------------------------------------------------------------- new modules
sub('''exec(open(os.path.join(HERE, "nav.py"), encoding="utf-8").read())
exec(open(os.path.join(HERE, "decay.py"), encoding="utf-8").read())
exec(open(os.path.join(HERE, "lighting.py"), encoding="utf-8").read())''', '''exec(open(os.path.join(HERE, "nav.py"), encoding="utf-8").read())
exec(open(os.path.join(HERE, "decay.py"), encoding="utf-8").read())
exec(open(os.path.join(HERE, "ell.py"), encoding="utf-8").read())
exec(open(os.path.join(HERE, "looks.py"), encoding="utf-8").read())
exec(open(os.path.join(HERE, "lighting.py"), encoding="utf-8").read())
exec(open(os.path.join(HERE, "switches.py"), encoding="utf-8").read())
exec(open(os.path.join(HERE, "forest.py"), encoding="utf-8").read())''')
io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("ok")
