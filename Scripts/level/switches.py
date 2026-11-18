# House lights.  exec'd by build_house.py after lighting.py.
#
# Cheyenne: "He tries the lights. The lights turn on. They do, but they're very dim yellow light, nasty light, and
# they don't stay on all the time. She turns lights off. Sometimes lights flicker. Sometimes they go out completely,
# and you're forced to pull out your flashlight."
#
# Each room: bare bulbs on cords (point lights tagged RoomLight + Room_<name>, off until switched) and a wall switch
# (a usable called sw_<name>).  The director (WCHouse.cpp) does the rest: flicker, brown-outs, her turning them off.
SWF = "Lights/House"
BULB_LUMENS = float(os.environ.get("WC_BULB", "4200"))     # the map is exposed five stops down, so "dim" still needs real output
BULB_COL = (1.0, 0.66, 0.30)


def bulb(room, x, y, z_floor, drop=62.0, lumens=None, radius=760.0):
    zc = z_floor + 327.0
    zb = zc - drop
    place(CYL, x, y, zc - drop / 2.0, 0, SWF, name=f"Cord_{room}", scale=(0.012, 0.012, drop / 100.0), mats={0: "WC:M_Black"}, collide=False, shadow=False)
    place(CYL, x, y, zb + 5, 0, SWF, name=f"Socket_{room}", scale=(0.05, 0.05, 0.07), mats={0: "BrassOld"}, collide=False, shadow=False)
    place(SPHERE, x, y, zb - 4, 0, SWF, name=f"BulbOff_{room}", scale=(0.085, 0.085, 0.11), mats={0: "WC:M_BulbOff"}, collide=False, shadow=False)
    place(SPHERE, x, y, zb - 4, 0, SWF, name=f"BulbOn_{room}", scale=(0.09, 0.09, 0.115), mats={0: "WC:M_GlowBulb"}, collide=False, shadow=False, tags=[f"BulbOn_{room}", "BulbOn"])
    light_point(f"RoomLight_{room}", x, y, zb - 16, lumens or BULB_LUMENS, BULB_COL, radius, SWF, tags=["RoomLight", f"Room_{room}"], shadows=True, vol=1.6, source=3.0)


def switch(room, x, y, z_floor, face):
    """face: which way the plate looks ('x+', 'x-', 'y+', 'y-')."""
    z = z_floor + 126.0
    dx, dy = {"x+": (1, 0), "x-": (-1, 0), "y+": (0, 1), "y-": (0, -1)}[face]
    if dx:
        box(f"SwitchPlate_{room}", x, x + dx * 1.6, y - 4.2, y + 4.2, z - 6.5, z + 6.5, "BrassOld", SWF, collide=False, shadow=False)
        box(f"SwitchNub_{room}", x + dx * 1.6, x + dx * 3.2, y - 0.9, y + 0.9, z - 1.0, z + 2.6, "WC:M_Black", SWF, collide=False, shadow=False)
    else:
        box(f"SwitchPlate_{room}", x - 4.2, x + 4.2, y, y + dy * 1.6, z - 6.5, z + 6.5, "BrassOld", SWF, collide=False, shadow=False)
        box(f"SwitchNub_{room}", x - 0.9, x + 0.9, y + dy * 1.6, y + dy * 3.2, z - 1.0, z + 2.6, "WC:M_Black", SWF, collide=False, shadow=False)
    interact("WCUsable", "sw_" + room, None, x + dx * 4, y + dy * 4, z, 0, "Light switch", (11, 11, 13), (0, 0, 0))


# room: ([bulbs (x, y)], floor z, switch (x, y, face))      rooms with no bulbs have a switch that does nothing
HOUSE_LIGHTS = {
    "hall": ([(250, 0), (1200, 30)], GZ, (16.5, -96, "x+")),
    "hallrear": ([(2000, 0), (2560, 0)], GZ, (1616.5, 150, "x+")),
    "living": ([(420, -400)], GZ, (348, -216.5, "y-")),
    "dining": ([], GZ, (348, 216.5, "y+")),                         # the chandelier is on the floor
    "kitchen": ([(1200, 400)], GZ, (905, 216.5, "y+")),
    "sitting": ([(1200, -400)], GZ, (1300, -216.5, "y-")),
    "den": ([(2000, -400)], GZ, (1890, -216.5, "y-")),
    "bathg": ([(2600, -400)], GZ, (2690, -216.5, "y-")),
    "pantry": ([(1800, 400)], GZ, (1616.5, 300, "x+")),
    "sickroom": ([(2400, 400)], GZ, (2295, 216.5, "y+")),
    "uphall": ([(1150, 30), (250, 60)], UZ, (880, 183.5, "y-")),
    "uprear": ([(2000, 0), (2560, 0)], UZ, (1616.5, 150, "x+")),
    "master": ([(400, 400)], UZ, (290, 216.5, "y+")),
    "kids": ([(400, -400)], UZ, (290, -216.5, "y-")),
    "upbath": ([(1200, -400)], UZ, (1090, -216.5, "y-")),
    "prayer": ([], UZ, (1090, 216.5, "y+")),                         # she took the bulb out: candles only
    "daniel": ([(2000, -400)], UZ, (1890, -216.5, "y-")),
    "sewing": ([(2600, -400)], UZ, (2690, -216.5, "y-")),
    "aide": ([(2000, 400)], UZ, (1890, 216.5, "y+")),
    "bath2": ([(2640, 480)], UZ, (2690, 216.5, "y+")),
    "cellar": ([(700, 60), (1300, 60)], CZ, (330, 199.5, "y-")),
}
n_b = 0
for room, (bulbs, zf, sw) in HOUSE_LIGHTS.items():
    for i, (x, y) in enumerate(bulbs):
        bulb(room if i == 0 else f"{room}", x, y, zf, drop=62.0 if zf != CZ else 30.0, lumens=BULB_LUMENS * (0.7 if zf == CZ else 1.0))
        n_b += 1
    switch(room, sw[0], sw[1], zf, sw[2])
# dead fixtures where a room has none that work
place("Bulb_Hanging_Broken", 1200, 400, UZ + 327, 0, SWF, collide=False)
log(f"house lights: {n_b} bulbs, {len(HOUSE_LIGHTS)} switches")
