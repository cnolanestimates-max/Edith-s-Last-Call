# The forest road, the trees that close it in, and the cruiser (with what you see from the driver's seat).
# exec'd by build_house.py after lighting.py (shares its helpers; `beam` comes from exterior.py).
#
# The game opens on this road: a rutted dirt track through tall pines, headlights only, down to the Harrow gate.
import random as _rnd
_fr = _rnd.Random(9)
FO = "Forest"
MP = "/Game/Megaplant_Library"

# ---------------------------------------------------------------- the road (control points; the car follows the same curve)
CRX, CRY = -1480.0, 300.0
ROAD = [(-33000, 1500), (-30000, 900), (-27000, 1500), (-24000, 2300), (-21000, 1900), (-18000, 900), (-15000, 300), (-12000, 800),
        (-9000, 1300), (-6000, 700), (-4000, 320), (-2600, 300), (CRX, CRY)]


def _cr(p0, p1, p2, p3, t):
    t2, t3 = t * t, t * t * t
    return tuple(0.5 * ((2 * p1[k]) + (-p0[k] + p2[k]) * t + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t2 + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * t3) for k in (0, 1))


def road_samples(step=260.0):
    pts = [ROAD[0]] + ROAD + [ROAD[-1]]
    out = []
    for i in range(1, len(pts) - 2):
        seg = math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1])
        n = max(2, int(seg / step))
        for k in range(n):
            out.append(_cr(pts[i - 1], pts[i], pts[i + 1], pts[i + 2], k / float(n)))
    out.append(ROAD[-1])
    return out


SAMPLES = road_samples()
# drive path for the director: one point about every 5 m, in order
for i, (x, y) in enumerate(SAMPLES[::2] + [SAMPLES[-1]]):
    point(f"Drive_{i:03d}", x, y, -40, 0, tags=[f"Drive_{i:03d}", "DrivePath"], folder="Drive")
# the dirt: overlapping boards along the curve, with two darker ruts
for i in range(len(SAMPLES) - 1):
    (x0, y0), (x1, y1) = SAMPLES[i], SAMPLES[i + 1]
    if x1 > -2600:
        break                                   # the gravel drive takes over at the gate
    d = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / d, (y1 - y0) / d
    beam(f"Road_{i}", (x0 - ux * 40, y0 - uy * 40, -40.2 + (i % 2) * 0.15), (x1 + ux * 40, y1 + uy * 40, -40.2 + (i % 2) * 0.15), 430, 3.0, M_ROAD, wdir=(-uy, ux, 0), collide=False, shadow=False, folder=FO + "/Road")
    if i % 2 == 0:
        for off in (-95, 95):
            beam(f"Rut_{i}_{off}", (x0 - uy * off, y0 + ux * off, -38.9), (x1 - uy * off + ux * 240, y1 + ux * off + uy * 240, -38.9), 46, 0.6, M_DIRT, wdir=(-uy, ux, 0), collide=False, shadow=False, folder=FO + "/Road")


def near_road(x, y, clear):
    for (sx, sy) in SAMPLES[::2]:
        if abs(sx - x) < clear and abs(sy - y) < clear and math.hypot(sx - x, sy - y) < clear:
            return True
    return False


def in_yard(x, y):
    return -2640 < x < XB + 1500 and -1260 < y < 1260


# ---------------------------------------------------------------- trees
def sk(path):
    return eal.load_asset(path) if eal.does_asset_exist(path) else None


PINES = [m for m in (sk(f"{MP}/Tree_Baltic_Pine/Tree_Baltic_Pine_01/Tree_Baltic_Pine_01_{c}") for c in "ABCD") if m]
SAPS = [m for m in (sk(f"{MP}/Tree_Baltic_Pine/Tree_Baltic_Pine_Saplings_01/Tree_Baltic_Pine_Sapling_01_{c}") for c in "ABC") if m]
DEAD = [m for m in (sk(f"{MP}/Tree_Dead_Pine/Tree_Dead_Pine_01/Tree_Dead_Pine_{c}") for c in "ABCD") if m]
FERNS = [m for m in (sk(f"{MP}/Plant_Bracken_Fern/Plant_Bracken_Fern_01/Plant_Bracken_Fern_01_{c}") for c in "ABC") if m]
KIT_TREES = ["Tree_Twisted_01", "Tree_Twisted_02", "Tree_Twisted_03", "Tree_Twisted_04", "Tree_Twisted_05", "Tree_Twisted_06", "Tree_Dead_Tall_Snag", "Tree_Graveyard_Dead"]
count["tree"] = 0
TREE_SPOTS = []


def lean_skel(c):
    """Megaplants are skinned meshes (for wind).  Ours never move: no GPU skin cache, no ray-tracing copy, no pose ticking.
    (300 of them with the skin cache on took over a gigabyte of video memory and crashed the first build.)"""
    for prop, val in (("visible_in_ray_tracing", False), ("affect_distance_field_lighting", False), ("affect_dynamic_indirect_lighting", False),
                      ("visibility_based_anim_tick_option", unreal.VisibilityBasedAnimTickOption.ONLY_TICK_POSE_WHEN_RENDERED),
                      ("enable_update_rate_optimizations", True), ("no_skeleton_update", True), ("disable_morph_target", True),
                      ("skin_cache_usage", [unreal.SkinCacheUsage.DISABLED] * 8)):
        try:
            c.set_editor_property(prop, val)
        except Exception as exc:
            if prop not in _lean_warned:
                _lean_warned.add(prop)
                log(f"lean_skel {prop}: {str(exc)[:90]}")
    try:
        c.set_component_tick_enabled(False)
    except Exception:
        pass


_lean_warned = set()


def tree(mesh, x, y, scale, sub="Trees", lean=0.0, toward=None):
    rot = R(_fr.uniform(0, 360))
    if lean and toward:
        # spun about its own trunk first, then tipped toward a point (the road)
        rot = unreal.MathLibrary.compose_rotators(rot, R(math.degrees(math.atan2(toward[1] - y, toward[0] - x)), -lean))
    a = actors.spawn_actor_from_class(unreal.SkeletalMeshActor, V(x, y, -44 - (18 if lean > 12 else 0)), rot)
    a.set_actor_label("Pine")
    c = a.skeletal_mesh_component
    c.set_skeletal_mesh_asset(mesh)
    a.set_actor_scale3d(V(scale, scale, scale * _fr.uniform(0.92, 1.1)))
    c.set_collision_profile_name("NoCollision")
    lean_skel(c)
    for prop, val in (("component_use_fixed_skel_bounds", True),):
        try:
            c.set_editor_property(prop, val)
        except Exception:
            pass
    a.set_folder_path(f"House/{FO}/{sub}")
    count["tree"] += 1
    return a


def try_tree(x, y, kind):
    if near_road(x, y, 228 if kind == "small" else 262) or in_yard(x, y):
        return
    for (tx, ty) in TREE_SPOTS[-40:]:
        if abs(tx - x) < 110 and abs(ty - y) < 110:
            return
    TREE_SPOTS.append((x, y))
    if kind == "big" and PINES:
        tree(_fr.choice(PINES[:2] if _fr.random() < 0.7 else PINES), x, y, _fr.uniform(0.85, 1.2))
    elif kind == "dead" and DEAD:
        tree(_fr.choice(DEAD), x, y, _fr.uniform(0.9, 1.3))
    elif kind == "small" and (SAPS or PINES):
        tree(_fr.choice(SAPS or PINES[2:]), x, y, _fr.uniform(0.9, 1.5), "Saplings")
    else:
        place(_fr.choice(KIT_TREES), x, y, -45, _fr.uniform(0, 360), FO + "/Trees", scale=_fr.uniform(1.5, 2.2), collide=False)
        count["tree"] += 1


# along the road: a tunnel.  Three ranks of tall pines each side, the first leaning in; young pines bent over the road
# between them; nothing but trees and ferns (the kit rocks, stumps and logs read as grey slabs in the headlights).
def road_tree(x, y, kind, lean, toward, scale):
    if in_yard(x, y) or near_road(x, y, 205):
        return
    for (tx, ty) in TREE_SPOTS[-60:]:
        if abs(tx - x) < 70 and abs(ty - y) < 70:
            return
    TREE_SPOTS.append((x, y))
    if kind == "small" and SAPS:
        tree(_fr.choice(SAPS), x, y, scale, "Saplings", lean, toward)
    elif kind == "dead" and DEAD:
        tree(_fr.choice(DEAD), x, y, scale, "Trees", lean, toward)
    elif PINES:
        tree(_fr.choice(PINES), x, y, scale, "Trees", lean, toward)


for i in range(0, len(SAMPLES) - 1):
    (x0, y0), (x1, y1) = SAMPLES[i], SAMPLES[i + 1]
    if x0 > -2500:
        break
    d = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / d, (y1 - y0) / d
    for side in (-1, 1):
        def at(off, along):
            return x0 + ux * along - uy * off * side, y0 + uy * along + ux * off * side
        mid = (x0 + ux * 60, y0 + uy * 60)
        # first rank: at the very edge of the dirt, leaning in so the crowns meet overhead
        px, py = at(_fr.uniform(238, 292), _fr.uniform(-90, 90))
        road_tree(px, py, "big" if _fr.random() > 0.1 else "dead", _fr.uniform(6, 12), mid, _fr.uniform(1.05, 1.4))
        # second and third ranks, upright, so there is no seeing through
        if _fr.random() < 0.85:
            px, py = at(_fr.uniform(360, 520), _fr.uniform(-120, 120))
            road_tree(px, py, "big", _fr.uniform(2, 6), mid, _fr.uniform(0.95, 1.3))
        if _fr.random() < 0.6:
            px, py = at(_fr.uniform(600, 900), _fr.uniform(-120, 120))
            road_tree(px, py, "big" if _fr.random() > 0.2 else "dead", 0.0, None, _fr.uniform(0.9, 1.25))
        if i % 2 == 0 and _fr.random() < 0.5:
            px, py = at(_fr.uniform(1000, 1700), _fr.uniform(-200, 200))
            road_tree(px, py, "big", 0.0, None, _fr.uniform(0.9, 1.2))
        # young pines bent right over the road: the roof of the tunnel, low enough for the headlights
        # (they used to stand at the road edge leaning 16 to 36 degrees: their branches came through the windshield)
        for _rep in range(2):
            if _fr.random() < 0.5:
                px, py = at(_fr.uniform(262, 330), _fr.uniform(-125, 125))
                road_tree(px, py, "small", _fr.uniform(8, 17), mid, _fr.uniform(1.8, 2.8))
# round the yard: the forest stands right behind the fence on every side
for i in range(150):
    x, y = _fr.uniform(-3400, XB + 2300), _fr.uniform(-2600, 2600)
    if in_yard(x, y):
        continue
    near_fence = min(abs(x + 2640), abs(abs(y) - 1260)) < 500 and x < 600
    if near_fence or _fr.random() < 0.6:
        try_tree(x, y, "big" if _fr.random() < 0.8 else "dead")
log(f"forest: {count['tree']} trees ({len(PINES)} pine types, {len(DEAD)} dead, {len(SAPS)} saplings)")

# ferns thick along both verges
n_under = 0
for i in range(0, len(SAMPLES) - 1, 1):
    (x0, y0), (x1, y1) = SAMPLES[i], SAMPLES[i + 1]
    if x0 > -2700:
        break
    d = math.hypot(x1 - x0, y1 - y0)
    ux, uy = (x1 - x0) / d, (y1 - y0) / d
    for side in (-1, 1):
        if not FERNS or _fr.random() > 0.9:
            continue
        off = _fr.uniform(222, 330) * side
        px, py = x0 - uy * off + ux * _fr.uniform(-120, 120), y0 + ux * off + uy * _fr.uniform(-120, 120)
        # dead brush with the ferns, so the ground between the trunks is not bare dirt
        for k in range(2):
            bo = _fr.uniform(205, 640) * side
            bx, by = x0 - uy * bo + ux * _fr.uniform(-130, 130), y0 + ux * bo + uy * _fr.uniform(-130, 130)
            place(_fr.choice(("Bramble_Bush_Dead", "Bush_Thorny_Dead")), bx, by, -43, _fr.uniform(0, 360), FO + "/Under", scale=_fr.uniform(0.8, 1.6), collide=False)
        for k in range(6):
            a = actors.spawn_actor_from_class(unreal.SkeletalMeshActor, V(px + _fr.uniform(-150, 150), py + _fr.uniform(-150, 150), -42), R(_fr.uniform(0, 360)))
            a.set_actor_label("Fern")
            c = a.skeletal_mesh_component
            c.set_skeletal_mesh_asset(_fr.choice(FERNS))
            s_ = _fr.uniform(1.4, 2.5)
            a.set_actor_scale3d(V(s_, s_, s_))
            c.set_collision_profile_name("NoCollision")
            c.set_editor_property("cast_shadow", False)
            lean_skel(c)
            a.set_folder_path(f"House/{FO}/Ferns")
        n_under += 1
# the thing on the road: half way in, at the right-hand edge of the dirt, facing the car that is coming
_si = int(len(SAMPLES) * 0.47)
(_sx0, _sy0), (_sx1, _sy1) = SAMPLES[_si], SAMPLES[_si + 1]
_sd = math.hypot(_sx1 - _sx0, _sy1 - _sy0)
_sux, _suy = (_sx1 - _sx0) / _sd, (_sy1 - _sy0) / _sd
_shx, _shy = _sx0 + _suy * 168, _sy0 - _sux * 168          # to the driver's right
# (the smoke figure that stood here was removed 2026-11-19 at Cheyenne's request)
place("Sign_Turn_Back", -5200, 1010, -40, 200, FO + "/Under", collide=False)
place("Sign_Keep_Out", -2600, 20, -40, 180, FO + "/Under", collide=False)
log(f"forest: {n_under} verge pieces")

# ---------------------------------------------------------------- the cruiser: one movable car with everything attached
car_mesh = asset(G + "/Props/SM_Cruiser", must=False)
CAR_YAW = float(os.environ.get("WC_CAR_YAW", "90"))
if car_mesh:
    car = place(car_mesh, CRX, CRY, -40, CAR_YAW, "Cruiser", name="Cruiser", tags=["Cruiser"])
else:
    car = box("Cruiser", CRX - 240, CRX + 240, CRY - 95, CRY + 95, -15, 75, "WC:M_Black", "Cruiser", tags=["Cruiser"])
car.static_mesh_component.set_mobility(unreal.ComponentMobility.MOVABLE)
CAR_PARTS = []


def cpart(a):
    """Anything that rides with the car."""
    try:
        a.root_component.set_mobility(unreal.ComponentMobility.MOVABLE)
    except Exception:
        pass
    CAR_PARTS.append(a)
    return a


# lights (the bar stays dark: this is a quiet welfare check, not a traffic stop)
for i, dy in enumerate((-62, 62)):
    cpart(light_spot(f"Headlight_{i}", CRX + 245, CRY + dy, 28, 0, -2.5, 4400, (1.0, 0.95, 0.84), 5200, 14, 34, "Cruiser", tags=["Hide_dawn", "Headlight"], shadows=(i == 0), vol=3.2))
# what the headlights do to the road itself: a wide wash from above the bumper, falling on the dirt and the verges
cpart(light_spot("RoadWash", CRX + 230, CRY, 120, 0, -17, 5600, (1.0, 0.93, 0.8), 3600, 34, 62, "Cruiser", tags=["Hide_dawn", "Headlight"], shadows=False, vol=0.5))
# and a dimmer, cooler one tilted up into the branches, so the roof of the tunnel shows
cpart(light_spot("CanopyWash", CRX + 200, CRY, 150, 0, 24, 4200, (0.86, 0.92, 1.0), 3400, 30, 58, "Cruiser", tags=["Hide_dawn", "Headlight"], shadows=False, vol=0.25))
cpart(light_point("TailGlow", CRX - 262, CRY, 60, 900, (1.0, 0.05, 0.03), 2600, "Cruiser", tags=["Hide_dawn", "CarRunning"], shadows=False, vol=1.0, source=10))
cpart(light_point("DashGlow", CRX + 44, CRY - 37, -40 + 92, 5.0, (0.55, 1.0, 0.7), 60, "Cruiser", tags=["CarRunning"], shadows=False, vol=0.0, source=1))
cpart(light_point("CabinFill", CRX - 10, CRY - 10, -40 + 138, 30.0, (0.55, 0.66, 1.0), 170, "Cruiser", tags=["CarRunning"], shadows=False, vol=0.0, source=6))
cpart(box("LightbarR", CRX - 20, CRX + 5, CRY + 8, CRY + 60, 136, 148, "WC:M_Black", "Cruiser", collide=False, shadow=False))
cpart(box("LightbarB", CRX - 20, CRX + 5, CRY - 60, CRY - 8, 136, 148, "WC:M_Black", "Cruiser", collide=False, shadow=False))
# the cabin from the driver's seat (the car model has no interior): dash, wheel, pillars, roof, mirror, radio
CAB = "Cruiser/Cabin"
DASH = "WC:M_Dash"


def cab(name, f0, f1, l0, l1, u0, u1, mat=DASH):
    """Box in car space: f = forward of the car's middle, l = to the driver's left, u = up from the ground."""
    return cpart(box(name, CRX + f0, CRX + f1, CRY - l1, CRY - l0, -40 + u0, -40 + u1, mat, CAB, collide=False, shadow=False, tags=["CabinOnly"]))


cab("DashTop", 62, 108, -80, 80, 92, 104)
cab("DashFace", 56, 64, -80, 80, 60, 100)
cab("Binnacle", 50, 64, 18, 58, 100, 112)
for _g, (_l0, _l1) in enumerate(((27, 33), (35.5, 40.5), (43, 49))):
    cab(f"Gauge{_g}", 49.4, 50.2, _l0, _l1, 105.2, 106.6, "WC:M_DashGlow")
cab("RadioBox", 49, 58, -18, 12, 78, 94)
cab("RadioGlow", 48.4, 49.2, -9, 3, 86.4, 87.6, "WC:M_DashGlow")
cab("Console", -40, 56, -14, 14, 40, 66)
cab("RoofLiner", -160, 46, -70, 70, 148, 153)
cab("WindHeader", 30, 50, -72, 72, 141, 150)
cab("Mirror", 40, 43, -13, 13, 132, 141)
cab("DoorL", -160, 100, 76, 82, 40, 104)
cab("DoorR", -160, 100, -82, -76, 40, 104)
cab("PillarBL", -30, -18, 74, 80, 100, 150)
cab("PillarBR", -30, -18, -80, -74, 100, 150)
# the windscreen pillars (the car body itself is hidden while he sits in it)
for _sgn in (-1, 1):
    cpart(beam(f"PillarA_{_sgn}", (CRX + 100, CRY - _sgn * 74, -40 + 102), (CRX + 44, CRY - _sgn * 70, -40 + 150), 7, 6, DASH, wdir=(0, 1, 0), shadow=False, folder=CAB, tags=["CabinOnly"]))
cab("Hood", 110, 250, -82, 82, 86, 96)
# what he sees when he turns round in his seat: the seat backs, the cage, the rear shelf and the frame of the back window
cab("SeatBackDriver", -24, -13, 14, 62, 50, 116)
cab("SeatBackPass", -24, -13, -62, -14, 50, 112)
cab("CageBar", -34, -30, -74, 74, 118, 122)
cab("RearSeat", -122, -102, -66, 66, 40, 104)
cab("RearShelf", -200, -122, -70, 70, 94, 101)
cab("PillarCL", -208, -196, 62, 80, 100, 150)
cab("PillarCR", -208, -196, -80, -62, 100, 150)
cab("RearHeader", -208, -192, -72, 72, 141, 150)
cab("RearSill", -212, -200, -72, 72, 94, 103)
cab("SeatBackR", -34, -22, -60, -16, 50, 118)
for side, l in (("L", 77), ("R", -77)):
    cpart(beam("PillarA" + side, (CRX + 104, CRY - l, -40 + 102), (CRX + 44, CRY - l * 0.9, -40 + 150), 7, 9, DASH, wdir=(0, 1, 0), shadow=False, folder=CAB))
# steering wheel: a ring of short bars, tilted toward the driver, with a column
WX, WL, WU, WR = 38.0, 37.0, 97.0, 19.0
for k in range(14):
    a0, a1 = math.radians(k * 360.0 / 14), math.radians((k + 1) * 360.0 / 14)

    def wp(a):
        # ring in a plane tilted 22 degrees back from vertical
        return (CRX + WX - math.sin(a) * WR * 0.38, CRY - (WL + math.cos(a) * WR), -40 + WU + math.sin(a) * WR * 0.93)
    cpart(beam(f"Wheel_{k}", wp(a0), wp(a1), 3.4, 3.4, DASH, wdir=(1, 0, 0), shadow=False, folder=CAB, tags=["CabinOnly"]))
cpart(beam("WheelSpoke", (CRX + WX, CRY - (WL - WR), -40 + WU), (CRX + WX, CRY - (WL + WR), -40 + WU), 3.0, 3.0, DASH, wdir=(1, 0, 0), shadow=False, folder=CAB, tags=["CabinOnly"]))
cpart(beam("WheelColumn", (CRX + WX, CRY - WL, -40 + WU), (CRX + 62, CRY - WL, -40 + 86), 7, 7, DASH, wdir=(0, 1, 0), shadow=False, folder=CAB, tags=["CabinOnly"]))
cpart(point("DriverSeat", CRX + 6, CRY - 37, -40 + 126, 0, tags=["DriverSeat"], folder="Cruiser"))
for a in CAR_PARTS:
    a.attach_to_actor(car, unreal.Name(""), unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, unreal.AttachmentRule.KEEP_WORLD, False)
interact("WCUsable", "cruiser", None, CRX + 30, CRY - 100, 40, 0, "Radio it in", (90, 30, 50), (0, 0, 0))
log(f"cruiser: {len(CAR_PARTS)} parts attached")
