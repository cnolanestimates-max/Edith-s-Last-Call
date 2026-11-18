import io
L = "C:/GameDev/Unreal/WellnessCheck/Scripts/level/"


def edit(f, fn):
    s = io.open(L + f, encoding="utf-8").read()
    s = fn(s)
    io.open(L + f, "w", encoding="utf-8", newline="\n").write(s)


def sub(s, old, new):
    assert old in s, old[:80]
    return s.replace(old, new, 1)


# ---------------------------------------------------------------- forest.py small fixes
def forest(s):
    s = sub(s, '''point("DriverSeat", CRX + 6, CRY - 37, -40 + 119, 0, tags=["DriverSeat"], folder="Cruiser")
cpart(Find_last_point := actors.get_all_level_actors()[-1])''', '''cpart(point("DriverSeat", CRX + 6, CRY - 37, -40 + 119, 0, tags=["DriverSeat"], folder="Cruiser"))''')
    s = sub(s, '((330, 470, "big", 0.9), (560, 800, "big", 0.75), (900, 1300, "big", 0.5), (1400, 2100, "big", 0.35))', '((330, 470, "big", 0.85), (560, 800, "big", 0.6), (900, 1300, "big", 0.35), (1400, 2100, "big", 0.2))')
    s = sub(s, "for i in range(150):\n    x, y = _fr.uniform(-3400, XB + 2300), _fr.uniform(-2600, 2600)", "for i in range(110):\n    x, y = _fr.uniform(-3400, XB + 2300), _fr.uniform(-2600, 2600)")
    return s


edit("forest.py", forest)


# ---------------------------------------------------------------- lighting.py: the cruiser moved to forest.py; shafts for the new windows
def lighting(s):
    a = s.index("# ---------------------------------------------------------------- the cruiser: light bar and headlights wash the front of the house")
    b = s.index("# ---------------------------------------------------------------- moonlight through the boards (and warm dawn light later)")
    s = s[:a] + s[b:]
    s = sub(s, 'shaft("W_U_master", 200, 730, UZ + 250, -90)', '''shaft("W_U_master", 200, 730, UZ + 250, -90)
shaft("W_G_den", 1800, -730, GZ + 250, 90)
shaft("W_G_bath", 2600, -730, GZ + 250, 90)
shaft("W_G_pantry", 1800, 730, GZ + 250, -90)
shaft("W_G_sick", 2600, 730, GZ + 250, -90)
shaft("W_U_daniel", 1800, -730, UZ + 250, 90)
shaft("W_U_sewing", 2600, -730, UZ + 250, 90)
shaft("W_U_aide", 1800, 730, UZ + 250, -90)
shaft("W_U_bath2", 2600, 730, UZ + 250, -90)
shaft("W_G_back", XB + 120, 400, GZ + 250, 180)
shaft("W_U_back", XB + 120, 0, UZ + 250, 180)''')
    s = sub(s, "# The rule: the house has no power.", "# The rule: the power was cut off a year ago, and the lights burn anyway (switches.py), dim and yellow and not for long.")
    return s


edit("lighting.py", lighting)


# ---------------------------------------------------------------- decay.py: rooms of the rear wing rot too; glass under the new windows; no lit lamps
def decay(s):
    s = sub(s, '''    "hall": (16, 1584, -184, 184, GZ, 0.7, "hall"),''', '''    "hall": (16, 1584, -184, 184, GZ, 0.7, "hall"), "hall2": (1616, 2784, -184, 184, GZ, 0.7, "hall"),
    "den": (1616, 2384, -584, -216, GZ, 0.7, "room"), "bath_g": (2416, 2784, -584, -216, GZ, 1.0, "wet"),
    "pantry": (1616, 1984, 216, 584, GZ, 1.0, "wet"), "sickroom": (2016, 2784, 216, 584, GZ, 0.9, "room"),
    "uphall2": (1616, 2784, -184, 184, UZ, 0.7, "hall"), "daniel": (1616, 2384, -584, -216, UZ, 0.6, "room"),
    "sewing": (2416, 2784, -584, -216, UZ, 0.8, "room"), "aide": (1616, 2384, 216, 584, UZ, 0.7, "room"),
    "bath2": (2416, 2784, 216, 584, UZ, 1.0, "wet"),''')
    s = sub(s, "(40, -400, GZ), (40, 400, GZ), (1560, -400, GZ), (1560, 400, GZ), (200, 560, GZ), (1000, 560, GZ), (1000, -560, GZ),",
            "(40, -400, GZ), (40, 400, GZ), (2760, -400, GZ), (2760, 400, GZ), (200, 560, GZ), (1000, 560, GZ), (1000, -560, GZ), (1800, -560, GZ), (2600, 560, GZ), (1800, 560, UZ), (2600, -560, UZ), (1800, -560, UZ),")
    s = sub(s, "(40, -400, UZ), (40, 0, UZ), (40, 400, UZ), (200, 560, UZ), (200, -560, UZ), (1000, -560, UZ), (1560, 0, UZ)):", "(40, -400, UZ), (40, 0, UZ), (40, 400, UZ), (200, 560, UZ), (200, -560, UZ), (1000, -560, UZ), (2760, 0, UZ)):")
    s = sub(s, 'for (x, y, z) in ((1200, 0, GZ), (400, 400, GZ), (1300, -420, GZ), (1200, 420, UZ), (300, -420, UZ), (1350, 60, UZ)):',
            'for (x, y, z) in ((1200, 0, GZ), (400, 400, GZ), (1300, -420, GZ), (1200, 420, UZ), (300, -420, UZ), (1350, 60, UZ), (2300, 0, GZ), (2100, -420, GZ), (2500, 420, GZ), (2200, 0, UZ), (2000, 420, UZ)):')
    s = sub(s, 'fab("Urban_Ruin_Wall_Plaster_L", 1570, -150, UZ, 270, "Walls", collide=False)', 'fab("Urban_Ruin_Wall_Plaster_L", 2770, -150, UZ, 270, "Walls", collide=False)')
    s = sub(s, 'fab("Urban_Shanty_Town_Chair_Mixed_Damaged", 1350, 120, GZ, 70, "Soft", collide=False)', 'fab("Urban_Shanty_Town_Chair_Mixed_Damaged", 1350, 140, GZ, 70, "Soft", collide=False)')
    # the oil lamps "with no business being lit" are gone: no window glows now.  (Candles in the prayer room and root cellar stay.)
    a = s.index("# ---------------------------------------------------------------- a few warm lights that have no business being lit")
    b = s.index('log(f"rot done: {count}")')
    s = s[:a] + s[b:]
    return s


edit("decay.py", decay)


# ---------------------------------------------------------------- nav.py: waypoints for the rear wing
def nav(s):
    s = sub(s, '''"hallA": (300, 100, GZ), "hallB": (600, 104, GZ), "hallC": (900, 70, GZ), "hallD": (1300, 0, GZ), "back": (1500, 0, GZ),''',
            '''"hallA": (300, 100, GZ), "hallB": (600, 104, GZ), "hallC": (900, 70, GZ), "hallD": (1300, 0, GZ), "arch": (1600, 0, GZ), "hallE": (1750, 0, GZ),
    "hallF": (2150, 0, GZ), "hallG": (2550, 0, GZ), "back": (2700, 0, GZ), "den_d": (1800, -200, GZ), "den": (2000, -380, GZ), "bathg_d": (2600, -200, GZ), "bathg": (2600, -380, GZ),
    "sick_d": (2200, 200, GZ), "sick": (2400, 380, GZ), "pantry_d": (1600, 400, GZ), "pantry": (1800, 400, GZ), "kitchen3": (1480, 400, GZ),''')
    s = sub(s, '''"up_hallD": (1300, 0, UZ),''', '''"up_hallD": (1300, 0, UZ), "up_ell_d": (1600, 0, UZ), "up_hallE": (1750, 0, UZ), "up_hallF": (2150, 0, UZ), "up_hallG": (2550, 0, UZ),
    "daniel_d": (1800, -200, UZ), "daniel": (2000, -380, UZ), "sewing_d": (2600, -200, UZ), "sewing": (2600, -380, UZ), "aide_d": (1800, 200, UZ), "aide": (2000, 380, UZ),
    "bath2_d": (2600, 200, UZ), "bath2": (2600, 380, UZ),''')
    s = sub(s, '''("hallC", "hallD"), ("hallD", "back"), ("hallD", "sitting_d"),''', '''("hallC", "hallD"), ("hallD", "arch"), ("arch", "hallE"), ("hallE", "hallF"), ("hallF", "hallG"), ("hallG", "back"), ("hallD", "sitting_d"),
         ("hallE", "den_d"), ("den_d", "den"), ("hallG", "bathg_d"), ("bathg_d", "bathg"), ("hallF", "sick_d"), ("sick_d", "sick"),
         ("kitchen2", "kitchen3"), ("kitchen3", "pantry_d"), ("pantry_d", "pantry"),
         ("up_hallD", "up_ell_d"), ("up_ell_d", "up_hallE"), ("up_hallE", "up_hallF"), ("up_hallF", "up_hallG"), ("up_hallE", "daniel_d"), ("daniel_d", "daniel"),
         ("up_hallG", "sewing_d"), ("sewing_d", "sewing"), ("up_hallE", "aide_d"), ("aide_d", "aide"), ("up_hallG", "bath2_d"), ("bath2_d", "bath2"),''')
    return s


edit("nav.py", nav)
print("ok")
