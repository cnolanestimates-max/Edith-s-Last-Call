import io
p = "C:/GameDev/Unreal/WellnessCheck/Scripts/level/build_house.py"
s = io.open(p, encoding="utf-8").read()


def sub(old, new, count=1):
    global s
    assert old in s, old[:70]
    s = s.replace(old, new, count)


# ---- slabs with holes
old = s[s.index("def slab(name, z_top, mat, folder, surface, thick=20.0, ceil_mat=None):"):s.index('slab("GroundFloor"')]
new = '''# places where a floor has rotted through: (x0, x1, y0, y1) per level
HOLES = {GZ: [(470, 620, -560, -440)], UZ: [(1290, 1440, -430, -310)], AZ: [(1280, 1400, 300, 420)]}
HOLE_LIST = []      # (x0, x1, y0, y1, z of this floor, z of the floor below) for decay.py


def cut(rects, hole):
    hx0, hx1, hy0, hy1 = hole
    out = []
    for (x0, x1, y0, y1) in rects:
        if hx1 <= x0 or hx0 >= x1 or hy1 <= y0 or hy0 >= y1:
            out.append((x0, x1, y0, y1))
            continue
        if hx0 > x0:
            out.append((x0, hx0, y0, y1))
        if hx1 < x1:
            out.append((hx1, x1, y0, y1))
        mx0, mx1 = max(x0, hx0), min(x1, hx1)
        if hy0 > y0:
            out.append((mx0, mx1, y0, hy0))
        if hy1 < y1:
            out.append((mx0, mx1, hy1, y1))
    return out


def slab(name, z_top, mat, folder, surface, thick=20.0, ceil_mat=None):
    parts = [(0, SX0, -600, 600), (SX1, 1600, -600, 600), (SX0, SX1, -600, SY0), (SX0, SX1, SY1 + 16, 600)]
    for h in HOLES.get(z_top, []):
        parts = cut(parts, h)
        HOLE_LIST.append((h[0], h[1], h[2], h[3], z_top, z_top - 350.0))
    for i, (x0, x1, y0, y1) in enumerate(parts):
        box(f"{name}_{i}", x0, x1, y0, y1, z_top - thick, z_top, mat, folder, tags=["Floor_" + surface])
        if ceil_mat:
            box(f"{name}_ceil_{i}", x0, x1, y0, y1, z_top - thick - 3, z_top - thick, ceil_mat, folder, collide=False)


'''
s = s.replace(old, new)
# cellar ceiling must be open under the ground-floor hole too
sub('box("CellarCeil", 0, SX0, -600, 600, GZ - 26, GZ - 20, M_ATTIC, "Shell/Cellar", collide=False)',
    'for _i, (_x0, _x1, _y0, _y1) in enumerate(cut([(0, SX0, -600, 600)], HOLES[GZ][0]) if False else [(0, SX0, -600, 600)]):\n    box(f"CellarCeil_{_i}", _x0, _x1, _y0, _y1, GZ - 26, GZ - 20, M_ATTIC, "Shell/Cellar", collide=False)')
sub('box("CellarCeil4", SX0, SX1, -600, SY0, GZ - 26, GZ - 20, M_ATTIC, "Shell/Cellar", collide=False)',
    'for _i, (_x0, _x1, _y0, _y1) in enumerate(cut([(SX0, SX1, -600, SY0)], HOLES[GZ][0])):\n    box(f"CellarCeil4_{_i}", _x0, _x1, _y0, _y1, GZ - 26, GZ - 20, M_ATTIC, "Shell/Cellar", collide=False)')
# ---- damaged walls
sub('run_x(-600, GZ, ["Wall_Wainscot_Red", "Wall_Fireplace_Breast", WIN, "Wall_Wainscot_Grey"], "Shell/Ground")',
    'run_x(-600, GZ, ["Wall_Peeling", "Wall_Fireplace_Breast", WIN, "Wall_Wainscot_Grey"], "Shell/Ground")')
sub('run_x(600, GZ, [WIN, WAIN, WIN, PLAIN], "Shell/Ground")', 'run_x(600, GZ, [WIN, "Wall_Peeling", WIN, "Wall_Exposed_Brick"], "Shell/Ground")')
sub('run_x(-600, UZ, [WIN, "Wall_Striped_Green", WIN, PLAIN], "Shell/Upper")', 'run_x(-600, UZ, [WIN, "Wall_Peeling", WIN, "Wall_Exposed_Brick"], "Shell/Upper")')
sub('run_x(600, UZ, [WIN, "Wall_Wainscot_Purple", "Wall_Striped_Purple", "Wall_Striped_Purple"], "Shell/Upper")',
    'run_x(600, UZ, [WIN, "Wall_Peeling", "Wall_Striped_Purple", "Wall_Peeling"], "Shell/Upper")')
# ---- materials: tin roof, tiles in the wet rooms
sub('M_ROOF = surf("Slate", "MI_RoofShingle")', 'M_ROOF = surf("Rust", "MI_RoofTin")')
sub('log("walls, doors, cellar done")',
    'for _n, (_x0, _x1, _y0, _y1, _z) in {"KitchenTiles": (816, 1584, 216, 584, GZ), "BathTiles": (816, 1584, -584, -216, UZ)}.items():\n'
    '    _rects = [(_x0, _x1, _y0, _y1)]\n'
    '    for _h in HOLES.get(_z, []):\n'
    '        _rects = cut(_rects, _h)\n'
    '    for _i, (_a, _b, _c, _d) in enumerate(_rects):\n'
    '        box(f"{_n}_{_i}", _a, _b, _c, _d, _z, _z + 1.2, surf("TileDark", "MI_MegaTilesOld" if _n == "KitchenTiles" else "MI_MegaTilesStained"), "Shell/Tiles", tags=["Floor_Stone"])\n'
    'log("walls, doors, cellar done")')
# ---- furniture: nothing intact
sub('place("Sofa_Sheet_Covered", 420, -540, GZ, 0, L)', 'place("Sofa_Sagging_Broken", 420, -540, GZ, 0, L)')
sub('place("Armchair_Sheet_Covered", 620, -330, GZ, 120, L)', 'place("Armchair_Tipped", 620, -330, GZ, 120, L)')
sub('place("Bathtub_Hydrotherapy", 1000, -500, UZ, 0, B)\nplace("Sink_Hospital", 1250, -570, UZ, 0, B)\nplace("Toilet_Steel", 1450, -560, UZ, 0, B)\n', '')
sub('place("Sink_Hospital", 1050, 570, GZ, 180, K)\n', 'place("Sink_Hospital", 1050, 570, GZ, 180, K)\n')
sub('place("Bed_Hospital_Bare_Springs", 250, -520, UZ, 0, KD)', 'place("Bed_Hospital_Rusty", 250, -520, UZ, 0, KD)')
sub('place("Bed_FourPoster_Curtains", 560, 440, UZ, 90, MB)', 'place("Bed_FourPoster_Broken", 560, 440, UZ, 90, MB)')
sub('place("Vanity_Dresser", 420, 565, UZ, 180, MB)', 'place("Vanity_Dresser_Smashed", 420, 565, UZ, 180, MB)')
sub('place("Wardrobe_Tall", 60, 500, UZ, 90, MB)', 'place("Wardrobe_Open_Clothes", 60, 500, UZ, 90, MB)')
sub('place("Chair_Dining_HighBack", 510, 470, GZ, yaw, DI)' if False else 'place("Chandelier_Unlit_Dusty", 420, 400, GZ + 210, 0, DI, collide=False)',
    'place("Chandelier_Fallen", 600, 300, GZ, 30, DI, collide=False)')
sub('place("Rocking_Horse", 420, -300, UZ, 200, KD)', 'place("Rocking_Horse_Broken", 420, -300, UZ, 200, KD)')
# ---- run the rot pass before lighting
sub('exec(open(os.path.join(HERE, "lighting.py"), encoding="utf-8").read())',
    'exec(open(os.path.join(HERE, "decay.py"), encoding="utf-8").read())\nexec(open(os.path.join(HERE, "lighting.py"), encoding="utf-8").read())')
io.open(p, "w", encoding="utf-8", newline="\n").write(s)
print("ok")
