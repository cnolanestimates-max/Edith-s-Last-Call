# The outside of the Harrow house.  exec'd by build_house.py (shares its helpers).
#
# Cheyenne: it must look like a house that was once beautiful.  So: an asymmetrical Victorian farmhouse in faded
# butter-yellow clapboard with what is left of white trim and dark green shutters; a wraparound porch with turned
# posts and brackets, an entry gable, a bay window, a round side turret with a witch's-hat roof, dormers, brick
# chimneys, a lower rear wing.  Then two hundred years and fourteen months of nobody: boards missing, shutters
# hanging, a rusted tin roof, brambles against the foundation.  No window is lit.
EX = "Shell/Exterior"
M_BODY = surf("SidingDark", "MI_SidingPaint")
M_BODY2 = surf("SidingDark", "MI_SidingPaintDark")
M_TRIM = surf("WoodBleached", "MI_TrimPaint")
M_SHUT = surf("WoodDark", "MI_ShutterPaint")
M_BRICK = surf("Brick", "MI_Brick")
M_ROT = surf("WoodRotten", "MI_WoodRotten")
M_FOREST = surf("GraveDirtDark", "MI_ForestFloor")
M_ROAD = surf("Sand", "MI_DirtRoad")
OVERRIDES_EXT = dict(OVERRIDES)
if eal.does_asset_exist(f"{G}/Materials/MI_SidingPaint"):
    OVERRIDES_EXT["M_Siding"] = asset(f"{G}/Materials/MI_SidingPaint")
    OVERRIDES_EXT["M_SidingDark"] = asset(f"{G}/Materials/MI_SidingPaint")
if eal.does_asset_exist(f"{G}/Materials/MI_TrimPaint"):
    for _slot in ("M_WoodVictorian", "M_WoodBleached", "M_WoodLight", "M_WoodPainted"):
        OVERRIDES_EXT[_slot] = asset(f"{G}/Materials/MI_TrimPaint")


def ext(mesh, x, y, z, yaw=0.0, name=None, scale=1.0, collide=True, pitch=0.0, roll=0.0, folder=EX, tags=()):
    """Kit piece dressed in the exterior paint (siding -> faded yellow, kit woods -> trim white)."""
    a = place(mesh, x, y, z, yaw, folder, name=name, scale=scale, collide=collide, pitch=pitch, roll=roll, tags=tags)
    c = a.static_mesh_component
    for i, n in enumerate(c.get_material_slot_names()):
        if str(n) in OVERRIDES_EXT:
            c.set_material(i, OVERRIDES_EXT[str(n)])
    return a


def beam(name, p0, p1, width, thick, mat, wdir=(0, 1, 0), collide=False, shadow=True, folder=EX, tags=()):
    """A board from p0 to p1: `width` across (toward wdir), `thick` the other way.  Used for roofs, rakes, braces."""
    d = unreal.Vector(p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2])
    length = d.length()
    rot = unreal.MathLibrary.make_rot_from_xy(d, unreal.Vector(*wdir))
    a = actors.spawn_actor_from_class(unreal.StaticMeshActor, V((p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2, (p0[2] + p1[2]) / 2), rot)
    a.set_actor_label(name)
    c = a.static_mesh_component
    c.set_static_mesh(CUBE)
    c.set_material(0, kmi(mat))
    a.set_actor_scale3d(V(length / 100.0, width / 100.0, thick / 100.0))
    if not collide:
        c.set_collision_profile_name("NoCollision")
    if not shadow:
        c.set_editor_property("cast_shadow", False)
    tag(a, tags)
    a.set_folder_path("House/" + folder)
    count["mesh"] += 1
    return a


def gable_tri(name, axis, fixed, lo, hi, z0, height, mat, thick=20.0, step=50.0):
    """A triangular wall built from thin steps.  axis 'y': the wall runs along Y at X=fixed; axis 'x': along X at Y=fixed."""
    mid = (lo + hi) / 2.0
    half = (hi - lo) / 2.0
    n = max(2, int((hi - lo) / step))
    w = (hi - lo) / n
    for i in range(n):
        a0 = lo + i * w
        c = a0 + w / 2
        h = height * (1 - abs(c - mid) / half) + (height / n) * 0.5
        if h < 3:
            continue
        if axis == "y":
            box(f"{name}_{i}", fixed - thick / 2, fixed + thick / 2, a0, a0 + w, z0, z0 + h, mat, EX)
        else:
            box(f"{name}_{i}", a0, a0 + w, fixed - thick / 2, fixed + thick / 2, z0, z0 + h, mat, EX)


# ================================================================== WALLS: kit clapboard, windows where the rooms have them
FRONT_WIN = {GZ: (-400, 400), UZ: (-400, 0, 400)}
LEFT_WIN = {GZ: (1000, 1800, 2600), UZ: (200, 1000, 1800, 2600)}           # the -Y side
RIGHT_WIN = {GZ: (200, 1000, 1800, 2600), UZ: (200, 1800, 2600)}           # the +Y side
BACK_WIN = {GZ: (-400, 400), UZ: (0,)}
BROKEN = {(1400, -636, UZ), (2200, 636, GZ), (2200, -636, UZ), (600, 636, UZ)}
for z in (GZ, UZ):
    for i in range(3):
        y = -400 + i * 400
        ext("Wall_Exterior_Siding_Door" if (z == GZ and i == 1) else ("Wall_Exterior_Siding_Window" if y in FRONT_WIN[z] else "Wall_Exterior_Siding"), -36, y, z, 90)
        ext("Wall_Exterior_Siding_Door" if (z == GZ and i == 1) else ("Wall_Exterior_Siding_Window" if y in BACK_WIN[z] else "Wall_Exterior_Siding"), XB + 36, y, z, 90)
    for i in range(7):
        x = 200 + i * 400
        for side, wins in ((-1, LEFT_WIN[z]), (1, RIGHT_WIN[z])):
            piece = "Wall_Exterior_Siding_Window" if x in wins else ("Wall_Exterior_Siding_Broken" if (x, side * 636, z) in BROKEN else "Wall_Exterior_Siding")
            ext(piece, x, side * 636, z, 0)
_open = [(SX0, SX1, SY0, SY1 + 16)] + list(HOLES.get(GZ, []))          # where the house is open to the cellar below
_rects = [(-60, XB + 60, -660, 660)]
for _h in _open:
    _rects = cut(_rects, _h)
for _i, (_a, _b, _c, _d) in enumerate(_rects):
    box(f"Foundation_{_i}", _a, _b, _c, _d, -40, 0, M_STONE, EX)
# The three trim bands run right through the house as slabs (their tops are what you walk on indoors), so each one has to
# be open over the stair tower and over the places where its floor has rotted through.  They used to be solid: you walked
# up or down through a floor at the cellar, the upstairs landing and the attic.
for _nm, (_m, _lo, _hi, _lvl) in {"WaterTable": (64, -6, 8, GZ), "BandBoard": (58, 328, 352, UZ), "Frieze": (60, 662, 702, AZ)}.items():
    _rects = [(-_m, XB + _m, -600 - _m, 600 + _m)]
    for _h in [(SX0, SX1, SY0, SY1 + 16)] + list(HOLES.get(_lvl, [])):
        _rects = cut(_rects, _h)
    for _i, (_a, _b, _c, _d) in enumerate(_rects):
        box(f"{_nm}_{_i}", _a, _b, _c, _d, _lo, _hi, M_TRIM, EX, collide=False)
for (x, y) in ((-52, -652), (-52, 652), (XB + 52, -652), (XB + 52, 652), (1600, -652), (1600, 652)):
    box(f"CornerBoard_{int(x)}_{int(y)}", x - 9, x + 9, y - 9, y + 9, 0, 700, M_TRIM, EX, collide=False)

# ================================================================== MAIN ROOF (ridge along Y at X=800) and its side gables
RH = 380.0
SL = math.hypot(800, RH)
RA = math.degrees(math.atan2(RH, 800))
for name, cx, pitch in (("RoofFront", 400, RA), ("RoofBack", 1200, -RA)):
    a = actors.spawn_actor_from_class(unreal.StaticMeshActor, V(cx - math.copysign(13, pitch), 0, AZ + RH / 2 + 27), R(0, pitch, 0))
    a.set_actor_label(name)
    a.static_mesh_component.set_static_mesh(CUBE)
    a.static_mesh_component.set_material(0, kmi(M_ROOF))
    a.set_actor_scale3d(V((SL + 110) / 100.0, 13.9, 0.6))
    a.set_folder_path("House/" + EX)
for side in (-1, 1):
    for i in range(16):
        x0 = i * 100
        h = RH * (1 - abs((x0 + (100 if x0 < 800 else 0)) - 800) / 800.0)
        if h > 4:
            box(f"Gable_{side}_{i}", x0, x0 + 100, side * 600 - 10, side * 600 + 10, AZ, AZ + h, M_BODY2, EX)
    # bargeboards along the rakes, and a collar tie with a king post in the peak
    y = side * 664
    beam(f"RakeF_{side}", (-70, y, AZ - 4), (800, y, AZ + RH + 30), 12, 26, M_TRIM, wdir=(0, 1, 0))
    beam(f"RakeB_{side}", (1670, y, AZ - 4), (800, y, AZ + RH + 30), 12, 26, M_TRIM, wdir=(0, 1, 0))
    box(f"GableTie_{side}", 560, 1040, y - 5, y + 5, AZ + 255, AZ + 270, M_TRIM, EX, collide=False)
    box(f"GablePost_{side}", 793, 807, y - 5, y + 5, AZ + 262, AZ + RH + 20, M_TRIM, EX, collide=False)
    ext("Window_Arched_Broken", 800, side * 612, AZ + 70, 0, collide=False, name=f"GableWindow_{side}")
box("AtticKneeFront", 0, 14, -600, 600, AZ, AZ + 12, M_TRIM, EX, collide=False)
box("RidgeCap", 786, 814, -700, 700, AZ + RH + 36, AZ + RH + 50, M_ROOF, EX, collide=False)

# ================================================================== REAR WING ROOF (lower, ridge along X) and its back gable
RH2 = 290.0
for side in (-1, 1):
    beam(f"WingRoof_{side}", (1975, side * 668, AZ - 22), (1975, 0, AZ + RH2 + 12), 1790, 26, M_ROOF, wdir=(1, 0, 0), collide=True)
gable_tri("WingGable", "y", XB, -600, 600, AZ, RH2, M_BODY2)
beam("WingRakeL", (XB + 66, -668, AZ - 6), (XB + 66, 0, AZ + RH2 + 30), 12, 26, M_TRIM, wdir=(1, 0, 0))
beam("WingRakeR", (XB + 66, 668, AZ - 6), (XB + 66, 0, AZ + RH2 + 30), 12, 26, M_TRIM, wdir=(1, 0, 0))
box("WingRidgeCap", 1100, XB + 72, -12, 12, AZ + RH2 + 22, AZ + RH2 + 36, M_ROOF, EX, collide=False)
ext("Window_Arched_Broken", XB + 12, 0, AZ + 50, 90, collide=False, name="WingGableWindow")

# ================================================================== ENTRY GABLE over the front door, and two dormers
GH, GW = 190.0, 230.0                                   # height, half width
gable_tri("FrontGable", "y", -30, -GW, GW, AZ - 2, GH, M_BODY, thick=24, step=46)
GX = GH / RH * 800.0 + 40                               # where its ridge dies into the main roof
for side in (-1, 1):
    beam(f"FrontGableRoof_{side}", (GX / 2 - 60, side * (GW + 34), AZ - 16), (GX / 2 - 60, 0, AZ + GH + 14), GX + 150, 20, M_ROOF, wdir=(1, 0, 0))
    beam(f"FrontGableRake_{side}", (-104, side * (GW + 34), AZ - 12), (-104, 0, AZ + GH + 20), 10, 24, M_TRIM, wdir=(1, 0, 0))
box("FrontGableTie", -110, -100, -120, 120, AZ + 96, AZ + 108, M_TRIM, EX, collide=False)
box("FrontGablePost", -110, -100, -6, 6, AZ + 100, AZ + GH + 6, M_TRIM, EX, collide=False)
ext("Window_Arched_Broken", -44, 0, AZ + 22, 90, collide=False, name="FrontGableWindow", scale=0.85)
for dy in (-430, 430):
    dx0, dx1, dz = 150.0, 330.0, AZ + 150.0 * RH / 800.0
    box(f"Dormer_{dy}", dx0, dx1 + 60, dy - 62, dy + 62, dz - 30, dz + 118, M_BODY, EX, collide=False)
    gable_tri(f"DormerGable_{dy}", "y", dx0, dy - 62, dy + 62, dz + 118, 52, M_BODY, thick=8, step=31)
    for side in (-1, 1):
        beam(f"DormerRoof_{dy}_{side}", ((dx0 + dx1) / 2 + 40, dy + side * 82, dz + 106), ((dx0 + dx1) / 2 + 40, dy, dz + 180), dx1 - dx0 + 130, 9, M_ROOF, wdir=(1, 0, 0))
    box(f"DormerPane_{dy}", dx0 - 3, dx0 + 1, dy - 34, dy + 34, dz + 6, dz + 100, "WC:M_Black", EX, collide=False, shadow=False)
    for (a0, a1, b0, b1) in ((-42, 42, 100, 110), (-42, 42, -4, 6), (-42, -34, 6, 100), (34, 42, 6, 100), (-3, 3, 6, 100)):
        box(f"DormerTrim_{dy}_{a0}_{b0}", dx0 - 7, dx0 - 1, dy + a0, dy + a1, dz + b0, dz + b1, M_TRIM, EX, collide=False, shadow=False)

# ================================================================== WINDOW DRESS: casings, sills, hoods, shutters (some gone, some hanging)
import random as _random
_xr = _random.Random(1887)


def window_dress(x, y, z, face):
    """face: '-x' front, '+x' back, '-y' left side, '+y' right side.  (x, y) is the window centre on the wall line."""
    out = {"-x": (-1, 0), "+x": (1, 0), "-y": (0, -1), "+y": (0, 1)}[face]
    ox, oy = out[0] * 44.0, out[1] * 44.0            # the outside face of the kit siding
    along = (0, 1) if out[0] else (1, 0)

    def piece(nm, a0, a1, b0, b1, depth, mat, d0=0.0):
        cx0 = x + ox + out[0] * d0
        cy0 = y + oy + out[1] * d0
        if out[0]:
            box(nm, min(cx0, cx0 + out[0] * depth), max(cx0, cx0 + out[0] * depth), y + a0, y + a1, z + b0, z + b1, mat, EX + "/Windows", collide=False, shadow=False)
        else:
            box(nm, x + a0, x + a1, min(cy0, cy0 + out[1] * depth), max(cy0, cy0 + out[1] * depth), z + b0, z + b1, mat, EX + "/Windows", collide=False, shadow=False)
    key = f"{int(x)}_{int(y)}_{int(z)}"
    piece("WinHead_" + key, -76, 76, 262, 278, 9, M_TRIM)
    piece("WinHood_" + key, -84, 84, 278, 285, 16, M_TRIM)
    piece("WinSill_" + key, -78, 78, 84, 93, 14, M_TRIM)
    piece("WinJambL_" + key, -72, -60, 93, 262, 7, M_TRIM)
    piece("WinJambR_" + key, 60, 72, 93, 262, 7, M_TRIM)
    if not (face == "-x" and y == 400 and z == UZ):
        # dark glass: nothing behind a window shows from the yard (the one exception is the lamp she leaves burning)
        piece("WinGlass_" + key, -61, 61, 92, 263, 2.2, "WC:M_Black", d0=5.5)
    else:
        # the one lit window: lamplight behind a torn blind.  It goes dark when he knocks (tag L_Welcome).
        piece("WinGlass_" + key, -61, 61, 92, 263, 1.0, "WC:M_Black", d0=4.2)
        for (a0, a1, b0, b1) in ((-58, -6, 96, 259), (-2, 58, 132, 259), (-2, 30, 96, 128)):
            lit = box(f"WinWarm_{key}_{a0}_{b0}", x + ox - 8.4, x + ox - 5.6, y + a0, y + a1, z + b0, z + b1, surf("GlowWarm", "M_WindowWarm"), EX + "/Windows", collide=False, shadow=False, tags=["L_Welcome"])
        box("WinWarmBar_" + key, x + ox - 9.4, x + ox - 8.4, y - 3, y + 3, z + 93, z + 262, M_TRIM, EX + "/Windows", collide=False, shadow=False)
        box("WinWarmBarH_" + key, x + ox - 9.4, x + ox - 8.4, y - 60, y + 60, z + 176, z + 181, M_TRIM, EX + "/Windows", collide=False, shadow=False)
        light_point("Lamp_WelcomeSpill", x + ox - 46, y, z + 190, 55, (1.0, 0.6, 0.28), 420, "Lights/Lamps", tags=["L_Welcome"], shadows=False, vol=1.2, source=10.0)
    for s in (-1, 1):
        r = _xr.random()
        if r < 0.22:
            continue                                  # this shutter is in the brambles somewhere
        a0, a1 = (s * 74, s * 112) if s > 0 else (s * 112, s * 74)
        if r < 0.42:
            # hanging by one hinge
            cx0, cy0 = x + ox + out[0] * 6 + along[0] * s * 96, y + oy + out[1] * 6 + along[1] * s * 96
            a = actors.spawn_actor_from_class(unreal.StaticMeshActor, V(cx0, cy0, z + 160), R(90 if out[0] else 0, 0, 0))
            a.set_actor_label("ShutterHang_" + key)
            c = a.static_mesh_component
            c.set_static_mesh(CUBE)
            c.set_material(0, kmi(M_SHUT))
            a.set_actor_scale3d(V(0.38, 0.045, 1.66))
            a.set_actor_rotation(unreal.MathLibrary.make_rot_from_xz(unreal.Vector(along[0], along[1], 0), unreal.Vector(along[0] * 0.24 * s, along[1] * 0.24 * s, 1.0)), False)
            c.set_collision_profile_name("NoCollision")
            a.set_folder_path("House/" + EX + "/Windows")
            count["mesh"] += 1
        else:
            piece(f"Shutter_{key}_{s}", a0, a1, 92, 264, 5, M_SHUT, d0=1.0)


for z in (GZ, UZ):
    for y in FRONT_WIN[z]:
        if not (z == GZ and y == -400):                # the bay window covers that one
            window_dress(0, y, z, "-x")
    for y in BACK_WIN[z]:
        window_dress(XB, y, z, "+x")
    for x in LEFT_WIN[z]:
        if not (100 < x < 420):                        # the turret stands there
            window_dress(x, -600, z, "-y")
    for x in RIGHT_WIN[z]:
        window_dress(x, 600, z, "+y")
# the two windows without casings (behind the turret, beside the bay) get their dark glass too
for (gx, gy, gz) in ((200, -600, UZ),):
    box(f"WinGlassX_{gx}_{int(gz)}", gx - 61, gx + 61, gy - 52, gy - 49.5, gz + 92, gz + 263, "WC:M_Black", EX + "/Windows", collide=False, shadow=False)
# boards nailed over two upstairs windows from outside, long ago
ext("Window_Boarded_Cross", -54, -400, UZ + 95, 90, collide=False)
ext("Window_Boarded_Cross", 1800, 648, UZ + 95, 0, collide=False)

# ================================================================== BAY WINDOW (front left, living room)
BX0, BX1, BY0, BY1 = -150.0, -36.0, -560.0, -250.0
box("BayBase", BX0, BX1, BY0, BY1, -40, 70, M_BODY, EX)
box("BayTop", BX0, BX1, BY0, BY1, 270, 312, M_BODY, EX, collide=False)
for (y0, y1) in ((BY0, BY0 + 14), (BY0 + 96, BY0 + 110), (BY1 - 110, BY1 - 96), (BY1 - 14, BY1)):
    box(f"BayPost_{int(y0)}", BX0, BX0 + 14, y0, y1, 70, 270, M_TRIM, EX, collide=False)
box("BayGlass", BX0 + 4, BX0 + 8, BY0 + 10, BY1 - 10, 70, 270, "WC:M_Black", EX, collide=False, shadow=False)
box("BaySill", BX0 - 8, BX0 + 4, BY0 - 6, BY1 + 6, 64, 74, M_TRIM, EX, collide=False)
box("BayCornice", BX0 - 12, BX1, BY0 - 12, BY1 + 12, 300, 316, M_TRIM, EX, collide=False)
for (y0, y1, nm) in ((BY0, BY0 + 8, "L"), (BY1 - 8, BY1, "R")):
    box("BaySide" + nm, BX0, BX1, y0, y1, 70, 270, M_BODY, EX, collide=False)
beam("BayRoof", (BX0 - 22, (BY0 + BY1) / 2, 314), (BX1 + 4, (BY0 + BY1) / 2, 372), BY1 - BY0 + 44, 8, M_ROOF, wdir=(0, 1, 0))
for i, y in enumerate((BY0 + 55, (BY0 + BY1) / 2, BY1 - 55)):
    ext("Window_Boarded", BX0 + 2, y, 78, 90, collide=False, name=f"BayBoards_{i}", scale=(0.82, 1.0, 1.0))

# ================================================================== ROUND TURRET on the left side, with a witch's-hat roof
TX, TY, TR = 250.0, -772.0, 150.0
place(CYL, TX, TY, 390, 0, EX, name="Turret", scale=(TR / 50.0, TR / 50.0, 8.6), mats={0: M_BODY})
place(CYL, TX, TY, 836, 0, EX, name="TurretCornice", scale=(TR / 50.0 + 0.24, TR / 50.0 + 0.24, 0.16), mats={0: M_TRIM}, collide=False)
place(CYL, TX, TY, 340, 0, EX, name="TurretBand", scale=(TR / 50.0 + 0.08, TR / 50.0 + 0.08, 0.2), mats={0: M_TRIM}, collide=False)
place(CYL, TX, TY, -18, 0, EX, name="TurretBase", scale=(TR / 50.0 + 0.12, TR / 50.0 + 0.12, 0.46), mats={0: M_STONE}, collide=False)
CONE = asset("/Engine/BasicShapes/Cone.Cone")
place(CONE, TX, TY, 844 + 190, 0, EX, name="TurretRoof", scale=((TR + 34) / 50.0, (TR + 34) / 50.0, 3.8), mats={0: M_ROOF}, collide=False)
place(CYL, TX, TY, 1250, 0, EX, name="TurretFinial", scale=(0.05, 0.05, 0.9), mats={0: "Iron"}, collide=False)
place(SPHERE, TX, TY, 1228, 0, EX, name="TurretBall", scale=0.16, mats={0: "Iron"}, collide=False)
for lvl, zz in enumerate((90.0, 440.0)):
    for ang in (180.0, 240.0, 300.0):                   # looking out front, front-left and to the side
        ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        cx, cy = TX + ca * (TR + 1), TY + sa * (TR + 1)
        for (nm, w, h, dz, mat, d) in (("Pane", 52, 150, 0, "WC:M_Black", 2), ("Head", 70, 12, 81, M_TRIM, 6), ("Sill", 70, 8, -79, M_TRIM, 8)):
            a = actors.spawn_actor_from_class(unreal.StaticMeshActor, V(cx + ca * d * 0.5, cy + sa * d * 0.5, zz + 85 + dz), R(ang, 0, 0))
            a.set_actor_label(f"TurretWin{nm}_{lvl}_{int(ang)}")
            c = a.static_mesh_component
            c.set_static_mesh(CUBE)
            c.set_material(0, kmi(mat))
            a.set_actor_scale3d(V(d / 100.0 + 0.02, w / 100.0, h / 100.0))
            c.set_collision_profile_name("NoCollision")
            c.set_editor_property("cast_shadow", False)
            a.set_folder_path("House/" + EX + "/Windows")
            count["mesh"] += 1

# ================================================================== CHIMNEYS (brick, one of them losing its top)
def chimney(name, x, y, w, d, z0, z1, pots=2, lean=0.0):
    box(name + "_Stack", x - w / 2, x + w / 2, y - d / 2, y + d / 2, z0, z1, M_BRICK, EX, roll=lean)
    box(name + "_Cap", x - w / 2 - 8, x + w / 2 + 8, y - d / 2 - 8, y + d / 2 + 8, z1, z1 + 14, M_STONE, EX, collide=False, roll=lean)
    for i in range(pots):
        place(CYL, x + (i - (pots - 1) / 2.0) * 36, y, z1 + 36, 0, EX, name=f"{name}_Pot{i}", scale=(0.2, 0.2, 0.46), mats={0: M_BRICK}, collide=False)


box("ChimneyLivingBase", 520, 680, -700, -636, -40, 360, M_BRICK, EX)
box("ChimneyLivingShoulder", 540, 660, -690, -636, 360, 420, M_BRICK, EX, collide=False)
chimney("ChimneyLiving", 600, -664, 96, 56, 420, AZ + 470)
box("ChimneyDenBase", 2120, 2280, -700, -636, -40, 360, M_BRICK, EX)
chimney("ChimneyDen", 2200, -664, 96, 56, 360, AZ + 330, pots=1)
chimney("ChimneyKitchen", 1240, 330, 84, 84, AZ + 150, AZ + 400, pots=1, lean=3.0)
place("Brick_Pile", 1240, 700, -40, 30, EX, collide=False)

# ================================================================== THE PORCH: front right, wrapping round the dining-room side
PX0, PX1 = -340.0, -52.0
PY0, PY1 = -230.0, 640.0                     # along the front
SY1P = 910.0                                 # the wrap's outer edge on the +Y side
SX1P = 820.0                                 # how far back the wrap runs
M_PFLOOR = surf("WoodBleached", "MI_PorchPaint")
box("PorchFloor", PX0, PX1, PY0, PY1, -22, 0, M_PFLOOR, EX, tags=["Floor_Wood"])
box("PorchFloorWrap", PX0, SX1P, 640, SY1P, -22, 0, M_PFLOOR, EX, tags=["Floor_Wood"])
box("PorchSkirtF", PX0 - 2, PX0 + 6, PY0, SY1P, -40, -20, M_ROT, EX, collide=False)
box("PorchSkirtS", PX0, SX1P, SY1P - 6, SY1P + 2, -40, -20, M_ROT, EX, collide=False)
box("PorchSkirtL", PX0, PX1, PY0 - 2, PY0 + 6, -40, -20, M_ROT, EX, collide=False)
box("PorchStep1", -380, -340, -150, 150, -40, -11, M_PFLOOR, EX, tags=["Floor_Wood"])
box("PorchStep2", -420, -380, -150, 150, -40, -22, M_PFLOOR, EX, tags=["Floor_Wood"])
for y in (-176, 176):                         # brick cheek walls beside the steps
    box(f"StepPier_{y}", -430, -340, y - 26, y + 26, -40, 26, M_BRICK, EX)
    box(f"StepPierCap_{y}", -436, -334, y - 32, y + 32, 26, 36, M_STONE, EX, collide=False)
# floor boards gone in places (dark gaps), one plank sprung
for (x0, x1, y0, y1) in ((-250, -236, 300, 520), (-140, -128, -180, -60), (200, 420, 760, 774), (-300, -288, 660, 880)):
    box(f"PorchGap_{int(x0)}_{int(y0)}", x0, x1, y0, y1, -0.6, 0.6, "WC:M_Black", EX, collide=False, shadow=False)
place("Plank_Single", -200, 480, 2, 80, EX, collide=False, pitch=6)
# roof: a low shed roof on turned posts, with brackets
ROOF_IN, ROOF_OUT = 352.0, 292.0
beam("PorchRoofFront", (PX0 - 44, (PY0 + SY1P) / 2 + 14, ROOF_OUT), (PX1 + 20, (PY0 + SY1P) / 2 + 14, ROOF_IN), SY1P - PY0 + 80, 9, M_ROOF, wdir=(0, 1, 0), collide=True)
beam("PorchRoofSide", ((PX1 + SX1P) / 2 + 30, SY1P + 44, ROOF_OUT), ((PX1 + SX1P) / 2 + 30, 640 - 6, ROOF_IN), SX1P - PX1 + 60, 9, M_ROOF, wdir=(1, 0, 0), collide=True)
box("PorchBeamFront", PX0 + 2, PX0 + 22, PY0, SY1P, 266, 290, M_TRIM, EX, collide=False)
box("PorchBeamSide", PX0, SX1P, SY1P - 22, SY1P - 2, 266, 290, M_TRIM, EX, collide=False)
box("PorchBeamLeft", PX0, PX1, PY0, PY0 + 20, 266, 290, M_TRIM, EX, collide=False)
box("PorchBeamBack", SX1P - 20, SX1P, 640, SY1P, 266, 290, M_TRIM, EX, collide=False)
box("PorchCeil", PX0 + 20, PX1, PY0 + 20, 640, 288, 291, M_PFLOOR, EX, collide=False, shadow=False)
POSTS = [(PX0 + 12, y) for y in (PY0 + 10, -150, 150, 400, 650, SY1P - 12)] + [(x, SY1P - 12) for x in (-60, 220, 500, SX1P - 12)]
for i, (x, y) in enumerate(POSTS):
    box(f"PorchPostBase_{i}", x - 11, x + 11, y - 11, y + 11, 0, 70, M_TRIM, EX)
    place(CYL, x, y, 168, 0, EX, name=f"PorchPost_{i}", scale=(0.13, 0.13, 1.96), mats={0: M_TRIM})
    box(f"PorchPostCap_{i}", x - 12, x + 12, y - 12, y + 12, 252, 266, M_TRIM, EX, collide=False)
    for (dx, dy) in ((0, 1), (0, -1), (1, 0), (-1, 0)):      # scroll brackets, drawn as little braces
        ex, ey = x + dx * 46, y + dy * 46
        on_front = abs(x - (PX0 + 12)) < 1 and dx == 0 and PY0 <= ey <= SY1P
        on_side = abs(y - (SY1P - 12)) < 1 and dy == 0 and PX0 <= ex <= SX1P
        if on_front or on_side:
            beam(f"PorchBrace_{i}_{dx}_{dy}", (x, y, 214), (ex, ey, 264), 5, 7, M_TRIM, wdir=(dy, dx, 0), shadow=False)
# railings between the posts (the entry bay is open; one run has rotted away)
def rail(name, p0, p1, broken=False):
    (x0, y0), (x1, y1) = p0, p1
    length = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / length, (y1 - y0) / length
    drop = 22.0 if broken else 0.0
    beam(name + "_Top", (x0, y0, 86), (x1, y1, 86 - drop), 7, 6, M_TRIM, wdir=(-uy, ux, 0), collide=False)
    beam(name + "_Bot", (x0, y0, 14), (x1, y1, 14), 6, 5, M_TRIM, wdir=(-uy, ux, 0), collide=False)
    n = int(length / 15.0)
    for k in range(1, n):
        if broken and _xr.random() < 0.45:
            continue
        t = k / float(n)
        bx, by = x0 + (x1 - x0) * t, y0 + (y1 - y0) * t
        box(f"{name}_B{k}", bx - 2.2, bx + 2.2, by - 2.2, by + 2.2, 16, 84 - drop * t, M_TRIM, EX + "/Rails", collide=False, shadow=False)
    # one blocking box so nobody steps off the porch through the pickets
    box(name + "_Block", min(x0, x1) - 4, max(x0, x1) + 4, min(y0, y1) - 4, max(y0, y1) + 4, 0, 96, "WC:M_Collision", EX + "/Rails", hidden=True)


rail("RailF0", (PX0 + 12, PY0 + 10), (PX0 + 12, -150))
rail("RailF2", (PX0 + 12, 150), (PX0 + 12, 400), broken=True)
rail("RailF3", (PX0 + 12, 400), (PX0 + 12, 650))
rail("RailF4", (PX0 + 12, 650), (PX0 + 12, SY1P - 12))
rail("RailS0", (PX0 + 12, SY1P - 12), (-60, SY1P - 12))
rail("RailS1", (-60, SY1P - 12), (220, SY1P - 12), broken=True)
rail("RailS2", (220, SY1P - 12), (500, SY1P - 12))
rail("RailS3", (500, SY1P - 12), (SX1P - 12, SY1P - 12))
rail("RailS4", (SX1P - 12, SY1P - 12), (SX1P - 12, 650))
rail("RailL", (PX0 + 12, PY0 + 10), (PX1 - 6, PY0 + 10))
# the little gable over the steps
gable_tri("PorticoGable", "y", PX0 - 30, -190, 190, 296, 96, M_BODY, thick=10, step=38)
for side in (-1, 1):
    beam(f"PorticoRoof_{side}", (PX0 + 60, side * 214, 288), (PX0 + 60, 0, 404), 240, 8, M_ROOF, wdir=(1, 0, 0))
    beam(f"PorticoRake_{side}", (PX0 - 38, side * 214, 290), (PX0 - 38, 0, 406), 8, 18, M_TRIM, wdir=(1, 0, 0))
box("PorticoSun", PX0 - 37, PX0 - 33, -60, 60, 300, 306, M_TRIM, EX, collide=False, shadow=False)
# what is on the porch: her chair, the swing, fourteen months of deliveries nobody took in
place("Rocking_Chair", -200, 470, 0, 250, EX + "/Porch", tags=["PorchRocker"])
place("Crate_Wood_Small", -110, -150, 0, 20, EX + "/Porch")
place("Crate_Wood_Small", -150, -185, 0, 70, EX + "/Porch")
place("Bottles_Empty_Group", -120, -110, 0, 0, EX + "/Porch", collide=False)
place("Newspaper_Pile", -90, 110, 0, 40, EX + "/Porch", collide=False)
place("Newspaper_Pile", -130, 150, 0, 110, EX + "/Porch", collide=False)
place("Plant_Stand_Dead_Fern", -80, 300, 0, 0, EX + "/Porch")
place("Lantern_Iron_Wall", -50, -110, 170, 90, EX + "/Porch", collide=False)
box("SwingSeat", 120, 290, 740, 790, 46, 52, M_ROT, EX + "/Porch", collide=False, roll=7)
box("SwingBack", 120, 290, 786, 792, 52, 100, M_ROT, EX + "/Porch", collide=False, roll=7)
for sx in (128, 282):
    beam(f"SwingChain_{sx}", (sx, 765, 288), (sx, 765, 52), 1.2, 1.2, "Iron", shadow=False)
place("Bramble_Bush_Dead", -380, 420, -40, 30, EX + "/Yard", collide=False)

# ================================================================== BACK STOOP and the cellar bulkhead
box("BackStoop", XB + 60, XB + 220, -150, 150, -22, 0, M_PFLOOR, EX, tags=["Floor_Wood"])
box("BackStep", XB + 220, XB + 260, -110, 110, -40, -12, M_PFLOOR, EX, tags=["Floor_Wood"])
beam("BackStoopRoof", (XB + 250, 0, 270), (XB + 40, 0, 330), 340, 8, M_ROOF, wdir=(0, 1, 0))
for y in (-140, 140):
    box(f"BackPost_{y}", XB + 200, XB + 214, y - 7, y + 7, 0, 268, M_TRIM, EX)
beam("BulkheadDoors", (1000, 762, -30), (1000, 664, 40), 230, 8, M_SHUT, wdir=(1, 0, 0), collide=True)
box("BulkheadCheekA", 880, 890, 660, 770, -40, 44, M_STONE, EX)
box("BulkheadCheekB", 1110, 1120, 660, 770, -40, 44, M_STONE, EX)
beam("BulkheadChain", (900, 716, 10), (1100, 712, 14), 3, 3, "Iron", wdir=(0, 1, 0), shadow=False)

# ================================================================== siding gone in patches (dark sheathing shows), a gutter hanging
for i, (x, y, z, w, h, face) in enumerate(((-37, -120, 420, 150, 60, "x"), (-37, 520, 180, 90, 110, "x"), (1400, -637, 200, 200, 70, "y"), (700, 637, 470, 160, 90, "y"),
                                             (2500, -637, 480, 220, 60, "y"), (300, -637, 560, 120, 80, "y"), (-37, 200, 600, 180, 50, "x"))):
    if face == "x":
        box(f"SidingGone_{i}", x - 4, x + 1, y - w / 2, y + w / 2, z, z + h, M_ROT, EX, collide=False, shadow=False)
    else:
        box(f"SidingGone_{i}", x - w / 2, x + w / 2, y - (4 if y < 0 else -1), y + (1 if y < 0 else 4), z, z + h, M_ROT, EX, collide=False, shadow=False)
beam("GutterFront", (-78, -660, 688), (-78, 100, 690), 9, 8, "Rust", wdir=(1, 0, 0), shadow=False)
beam("GutterFallen", (-80, 100, 690), (-120, 560, 560), 9, 8, "Rust", wdir=(1, 0, 0), shadow=False)
beam("Downspout", (-70, -655, 690), (-70, -655, 0), 8, 8, "Rust", wdir=(0, 1, 0), shadow=False)

# ================================================================== THE YARD
# the ground stops at the house: under it are the foundation slab and the cellar, not a second floor of forest dirt
_rects = cut([(-40000, 9000, -9000, 9000)], (-58, XB + 58, -658, 658))
for _i, (_a, _b, _c, _d) in enumerate(_rects):
    box(f"ForestGround_{_i}", _a, _b, _c, _d, -70, -41, M_FOREST, EX, tags=["Floor_Gravel"])
for _i, (_a, _b, _c, _d) in enumerate(cut([(-2600, XB + 1600, -2400, 2400)], (-58, XB + 58, -658, 658))):
    box(f"Yard_{_i}", _a, _b, _c, _d, -60, -40, M_GROUND, EX, tags=["Floor_Gravel"])
box("Path", -1700, -420, -90, 90, -40, -38.5, M_GRAVEL, EX, collide=False)
box("Drive", -2600, -1150, 110, 500, -40, -38.5, M_GRAVEL, EX, collide=False)
# invisible limits: the whole yard, front and back (he looks round the outside before he goes in)
YARD_BACK = XB + 1460.0
for name, (x0, x1, y0, y1) in {"LimFront": (-2460, -2440, -1100, 1100), "LimLeft": (-2460, YARD_BACK + 20, -1100, -1080), "LimRight": (-2460, YARD_BACK + 20, 1080, 1100),
                                "LimBack": (YARD_BACK, YARD_BACK + 20, -1100, 1100)}.items():
    box(name, x0, x1, y0, y1, -40, 400, "WC:M_Collision", EX, hidden=True)
for i in range(11):
    y = -1000 + i * 200
    if 100 < y < 500:
        continue                               # the gate
    place("Fence_Wood_Broken_01" if i in (2, 9) else "Fence_Wood_Old", -2440, y, -40, 90, EX + "/Yard")
place("Fence_Wood_Old", -2470, 80, -40, 150, EX + "/Yard", name="GateLeafOpen")
for y in (100, 500):
    box(f"GatePost_{y}", -2452, -2428, y - 12, y + 12, -40, 150, M_ROT, EX + "/Yard")
box("MailboxPost", -2520, -2510, 560, 570, -40, 78, M_ROT, EX + "/Yard")
box("Mailbox", -2540, -2492, 554, 576, 78, 102, "Rust", EX + "/Yard", collide=False)
box("MailboxFlag", -2500, -2496, 576, 578, 96, 118, "Rust", EX + "/Yard", collide=False)
for i in range(34):
    if -2340 + i * 200 > YARD_BACK:
        break
    place("Fence_Wood_Broken_01" if i % 5 == 3 else "Fence_Wood_Old", -2340 + i * 200, -1080, -40, 0, EX + "/Yard")
    place("Fence_Wood_Broken_01" if i % 4 == 2 else "Fence_Wood_Old", -2340 + i * 200, 1080, -40, 0, EX + "/Yard")
for i in range(11):
    place("Fence_Wood_Broken_01" if i in (3, 7) else "Fence_Wood_Old", YARD_BACK, -1000 + i * 200, -40, 90, EX + "/Yard")
YARD_TREES = [("Tree_Graveyard_Gnarled_Willow", -620, 820, 40, 1.9), ("Tree_Twisted_03", -1900, -760, 140, 1.7), ("Tree_Dead_Tall_Snag", -2200, 880, 60, 1.5),
              ("Tree_Twisted_05", -700, -900, 80, 1.6), ("Tree_Hanging_Moss", -1300, 900, 300, 1.7), ("Tree_Twisted_01", 700, -1500, 110, 2.0),
              ("Tree_Twisted_06", 1500, 1500, 30, 2.0), ("Tree_Graveyard_Dead", 2400, -1400, 0, 1.9), ("Tree_Leaning_Swamp", 3300, 900, 200, 1.8)]
for n, x, y, yaw, s in YARD_TREES:
    place(n, x, y, -45, yaw, EX + "/Trees", scale=s, collide=False)
place("Scarecrow_Tattered_Crow", -2050, -880, -40, 35, EX + "/Yard")
place("Well_Old_Stone", -1500, -620, -40, 0, EX + "/Yard")
place("Bucket_Rusty", -1420, -560, -40, 30, EX + "/Yard")
place("Woodpile_Rotten", -300, -900, -40, 90, EX + "/Yard")
place("Stump_Axe", -420, -780, -40, 200, EX + "/Yard")
place("Wheelbarrow_Old", -900, -760, -40, 200, EX + "/Yard")
place("Signpost_Woods_Crooked", -2520, 60, -40, 0, EX + "/Yard")
place("Crow_Perched_Post", -2440, 100, 150, 180, EX + "/Yard", collide=False)
place("Crows_On_Branch", -640, 800, 330, 20, EX + "/Yard", collide=False)
place("Shovel_Stuck_In_Dirt", -520, 980, -40, 60, EX + "/Yard", collide=False)
# brambles and dead shrubs against the foundation and the fence
for i, (x, y, yaw, sc) in enumerate(((-110, -640, 10, 1.2), (-420, -330, 80, 1.0), (-100, -830, 200, 1.4), (500, -900, 60, 1.3), (-420, 700, 10, 1.1), (-2380, -500, 0, 1.3),
                                       (-2380, 800, 90, 1.2), (-1700, 1020, 40, 1.4), (-900, -1030, 0, 1.3), (-1500, -1030, 70, 1.1), (-380, -520, 30, 0.9), (900, 960, 20, 1.3))):
    place("Bramble_Bush_Dead" if i % 2 == 0 else "Bush_Thorny_Dead", x, y, -40, yaw, EX + "/Yard", scale=sc, collide=False)
for i, (x, y) in enumerate(((-1100, -400), (-2100, 300), (-800, 560), (-1750, -300), (-2250, -900), (-350, 1000))):
    place(("Rock_Fog_Small", "Rock_Cluster_Mossy", "Rock_Fog_Medium")[i % 3], x, y, -42, i * 67, EX + "/Yard", collide=False)
# the clothes line: two posts, a sagging line, what she hung out and never brought in
for x in (-1300, -820):
    box(f"LinePost_{x}", x - 5, x + 5, 500, 510, -40, 170, M_ROT, EX + "/Yard")
    box(f"LineCross_{x}", x - 5, x + 5, 460, 550, 160, 168, M_ROT, EX + "/Yard", collide=False)
beam("ClothesLineA", (-1300, 505, 164), (-1060, 505, 146), 1, 1, "Iron", shadow=False)
beam("ClothesLineB", (-1060, 505, 146), (-820, 505, 164), 1, 1, "Iron", shadow=False)
# the family plot under the willow: Walter, and a stone for the son who never came home
place("Tombstone_Rounded_Tall", -560, 960, -40, 100, EX + "/Plot", name="Grave_Walter")
place("Tombstone_Flat_Slab_Upright", -700, 990, -40, 95, EX + "/Plot", name="Grave_Daniel")
place("Grave_Sunken_Kerb", -520, 960, -40, 100, EX + "/Plot", collide=False)
place("Vase_Grave_Dead_Flowers", -560, 925, -40, 0, EX + "/Plot", collide=False)
place("Cross_Wood_Leaning_Rotten", -820, 1010, -40, 80, EX + "/Plot", collide=False)
# ================================================================== THE BACK YARD: a tree line, and the tool shed
import random as _rnd
_tr = _rnd.Random(41)
_KT = ["Tree_Twisted_03", "Tree_Dead_Tall_Snag", "Tree_Twisted_05", "Tree_Hanging_Moss", "Tree_Twisted_01", "Tree_Twisted_06", "Tree_Graveyard_Dead", "Tree_Leaning_Swamp",
       "Tree_Graveyard_Gnarled_Willow"]
_n = 0
# two ragged ranks outside the fence down both sides (from the front corner back), three deep along the back
for _x in range(-200, int(YARD_BACK) + 700, 230):
    for _side in (-1, 1):
        for _rank, _off in ((0, 1190), (1, 1480), (2, 1800)):
            if _rank == 2 and _tr.random() < 0.4:
                continue
            _ta = place(_tr.choice(_KT), _x + _tr.uniform(-90, 90), _side * (_off + _tr.uniform(-70, 110)), -46, _tr.uniform(0, 360), EX + "/TreeLine",
                        scale=_tr.uniform(1.7, 2.6), collide=False)
            _ta.static_mesh_component.set_editor_property("cast_shadow", False)       # the moon has to reach the yard
            _n += 1
for _y in range(-1900, 1901, 220):
    for _rank, _off in ((0, 150), (1, 430), (2, 760)):
        _ta = place(_tr.choice(_KT), YARD_BACK + _off + _tr.uniform(-80, 110), _y + _tr.uniform(-90, 90), -46, _tr.uniform(0, 360), EX + "/TreeLine",
                    scale=_tr.uniform(1.8, 2.8), collide=False)
        _ta.static_mesh_component.set_editor_property("cast_shadow", False)
        _n += 1
log(f"tree line: {_n} trees")
for _i in range(26):                                                     # brambles and rocks along the fences and in the long grass
    _x, _y = _tr.uniform(200, YARD_BACK - 80), _tr.choice((-1, 1)) * _tr.uniform(760, 1040)
    place(("Bramble_Bush_Dead", "Bush_Thorny_Dead", "Rock_Fog_Small")[_i % 3], _x, _y, -41, _tr.uniform(0, 360), EX + "/BackYard", scale=_tr.uniform(0.9, 1.5), collide=False)
for _i in range(10):
    place(("Bramble_Bush_Dead", "Rock_Cluster_Mossy")[_i % 2], _tr.uniform(XB + 500, YARD_BACK - 100), _tr.uniform(-900, 900), -41, _tr.uniform(0, 360), EX + "/BackYard",
          scale=_tr.uniform(0.9, 1.4), collide=False)
place("Wheelbarrow_Old", XB + 610, -330, -40, 70, EX + "/BackYard")
place("Stump_Axe", XB + 520, 520, -40, 30, EX + "/BackYard")
place("Woodpile_Rotten", XB + 380, 760, -40, 0, EX + "/BackYard")
place("Barrel_Tipped_Spilled", XB + 300, -520, -40, 20, EX + "/BackYard")
place("Tree_Graveyard_Dead", XB + 900, 420, -45, 200, EX + "/BackYard", scale=1.8, collide=False)

# ---- the shed: back left corner, door toward the house.  Boards, a rusted roof, forty years of tools.
SH = EX + "/Shed"
SX0, SX1, SY0, SY1 = XB + 760.0, XB + 1140.0, -900.0, -580.0
box("ShedFloor", SX0, SX1, SY0, SY1, -40, -33, M_PFLOOR, SH, tags=["Floor_Wood"])
box("ShedWallS", SX0, SX1, SY0, SY0 + 8, -40, 200, M_ROT, SH)
box("ShedWallN", SX0, SX1, SY1 - 8, SY1, -40, 200, M_ROT, SH)
box("ShedWallE", SX1 - 8, SX1, SY0, SY1, -40, 200, M_ROT, SH)
_DY0, _DY1 = -790.0, -700.0                                              # the doorway, in the wall that faces the house
box("ShedWallW_a", SX0, SX0 + 8, SY0, _DY0, -40, 200, M_ROT, SH)
box("ShedWallW_b", SX0, SX0 + 8, _DY1, SY1, -40, 200, M_ROT, SH)
box("ShedLintel", SX0, SX0 + 8, _DY0, _DY1, 158, 200, M_ROT, SH)
box("ShedDoor", SX0 - 84, SX0, _DY1 - 2, _DY1 + 5, -34, 156, M_SHUT, SH, yaw=-14)        # hanging open on one hinge
for _k, _y in enumerate((-880, -850, -660, -612)):                       # boards gone: black gaps you can see the yard through
    box(f"ShedGap_{_k}", SX0 - 1, SX0 + 9, _y, _y + 9, 20 + 30 * (_k % 2), 190, "WC:M_Void" if False else M_SHUT, SH, collide=False, shadow=False)
_ridge = (SY0 + SY1) / 2
beam("ShedRoofS", ((SX0 + SX1) / 2, _ridge, 292), ((SX0 + SX1) / 2, SY0 - 30, 192), SX1 - SX0 + 50, 6, M_ROOF, wdir=(1, 0, 0))
beam("ShedRoofN", ((SX0 + SX1) / 2, _ridge, 292), ((SX0 + SX1) / 2, SY1 + 30, 192), SX1 - SX0 + 50, 6, M_ROOF, wdir=(1, 0, 0))
gable_tri("ShedGableW", "y", SX0 + 4, SY0, SY1, 200, 92, M_ROT, thick=8.0, step=32.0)
gable_tri("ShedGableE", "y", SX1 - 4, SY0, SY1, 200, 92, M_ROT, thick=8.0, step=32.0)
# inside: a bench under the back wall, barrels and crates, what is left on the shelves
box("ShedBenchTop", SX1 - 78, SX1 - 10, SY0 + 40, SY1 - 40, 44, 50, M_ROT, SH)
for _k, (_x, _y) in enumerate(((SX1 - 74, SY0 + 44), (SX1 - 16, SY0 + 44), (SX1 - 74, SY1 - 44), (SX1 - 16, SY1 - 44))):
    box(f"ShedBenchLeg_{_k}", _x - 4, _x + 4, _y - 4, _y + 4, -33, 44, M_ROT, SH, collide=False)
box("ShedShelf", SX0 + 60, SX1 - 110, SY1 - 30, SY1 - 8, 118, 122, M_ROT, SH, collide=False)
place("Tin_Cans_Rusty", SX0 + 150, SY1 - 20, 122, 30, SH, collide=False)
place("Paint_Can_Spilled", SX0 + 230, SY1 - 20, 122, 200, SH, collide=False)
place("Flashlight_Camping_Lantern", SX1 - 44, SY0 + 90, 50, 40, SH, collide=False)
place("Tin_Cans_Rusty", SX1 - 40, SY1 - 90, 50, 110, SH, collide=False)
place("Bucket_Rusty", SX1 - 46, _ridge + 10, 50, 0, SH, collide=False)
place("Barrel_Old", SX0 + 60, SY1 - 60, -33, 0, SH)
place("Crate_Wood_Small", SX0 + 150, SY1 - 62, -33, 20, SH)
place("Crate_Wood_Open", SX0 + 250, SY1 - 70, -33, 80, SH)
place("Planks_Pile", SX1 - 150, SY0 + 46, -33, 0, SH, collide=False)
place("Box_Cardboard_Stack", SX1 - 60, SY1 - 30, -33, 10, SH, collide=False)
place("Cobweb_Corner", SX1 - 12, SY1 - 12, 150, 180, SH, collide=False)
place("Cobweb_Corner", SX0 + 14, SY0 + 14, 150, 0, SH, collide=False)
# the tools on the south wall: two shovels, a pitchfork, a pickaxe, and a rake hung on nails
for _k, (_m, _x, _pitch) in enumerate((("Shovel", SX0 + 90, 0), ("Shovel", SX0 + 130, 0), ("Pitchfork_Rusty", SX0 + 180, 0), ("Pickaxe", SX0 + 235, 0))):
    place(_m, _x, SY0 + 18, -33, 90 + 12 * (_k % 2), SH, collide=False, roll=6)
beam("RakeHandle", (SX0 + 300, SY0 + 12, 8), (SX0 + 296, SY0 + 12, 178), 3.2, 3.2, M_ROT, wdir=(1, 0, 0), collide=False)
box("RakeHead", SX0 + 276, SX0 + 316, SY0 + 10, SY0 + 13, 176, 180, "Rust", SH, collide=False)
for _k in range(9):
    box(f"RakeTine_{_k}", SX0 + 277.5 + _k * 4.5, SX0 + 278.7 + _k * 4.5, SY0 + 10, SY0 + 12, 168, 177, "Rust", SH, collide=False)
for _k in range(3):
    box(f"WallNail_{_k}", SX0 + 110 + _k * 60, SX0 + 111 + _k * 60, SY0 + 8, SY0 + 13, 150, 151, "Rust", SH, collide=False, shadow=False)
point("A_Shed", SX0 - 140, (_DY0 + _DY1) / 2, GZ, 0, folder="Auto")
point("A_ShedIn", SX0 + 110, (_DY0 + _DY1) / 2, -33, 0, folder="Auto")
point("A_BackStoop", XB + 190, 0, 0, 180, folder="Auto")
point("A_BackYard", XB + 620, 60, GZ, 180, folder="Auto")
trigger("t_shed", SX0 + 30, SX1 - 10, SY0 + 10, SY1 - 10, -40, 190)
log("exterior done")
