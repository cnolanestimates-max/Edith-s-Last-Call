"""The yard and forest edge (Cheyenne, 2026-11-28: "outside the forest looks really janky ... some of the forest trees don't
have any collisions ... stumps ... need to look like stumps ... the grass needs to be revamped ... a wheelbarrow that
literally looks janky, like it's out of Roblox").  A polish step for the saved map (Scripts/tools/polish.ps1 -Steps
polish_outdoors) and safe to run again: it only touches kit pieces that are still there, and rebuilds what it made itself.

  - the kit wheelbarrows, stumps, woodpiles and rocks become the modelled ones (SM_Item_Wheelbarrow, _Stump, _StumpAxe,
    _StumpRot, _Woodpile, _RockA/B/C), solid; a few more stumps go in where trees were felled
  - the kit trees (the seven in the yard and the tree line outside the fence: blocky trunks, stretched bark) become the
    forest's own pines, dead pines and saplings
  - every trunk a player can reach gets an invisible post, so no tree can be walked through
  - grass: the clumps of SourceArt/Outdoors/grass_points.json planted as instances (one actor, "GrassField")
Needs the assets of Scripts/level/import_outdoors.py and the forest meshes in /Game/WC/Forest."""
import json, math, zlib
import unreal as u

ROOT = "C:/GameDev/Unreal/WellnessCheck"
P = "/Game/WC/Props/SM_Item_"
F = "/Game/WC/Forest/"
GROUND = -40.0
WALK = (-2460.0, 4260.0, -1100.0, 1100.0)                 # the invisible limits of the yard (exterior.py)
PATHS = [[(-710, 0), (-649, -340), (-536, -654), (-216, -1000), (53, -1184), (463, -1184), (760, -1000), (1410, -845), (2695, -836), (3230, -755), (3556, -745)],
         [(-710, 0), (-595, 400), (-507, 685), (-431, 911), (-325, 993), (825, 993), (1100, 875), (2610, 802), (3130, 760), (3335, 480), (3345, -482), (3230, -755)]]
EXTRA_STUMPS = [(-1820, 620, "StumpRot", 40), (-2150, -430, "Stump", 200), (2000, -1010, "StumpRot", 120), (4050, -250, "Stump", 300),
                (3900, 780, "StumpRot", 15), (1400, 1010, "Stump", 250)]
TRUNK = {"SM_Tree_Dead_Pine_A": 21.0, "SM_Tree_Dead_Pine_B": 19.0, "SM_Tree_Dead_Pine_C": 16.0, "SM_Tree_Dead_Pine_D": 11.0,
         "SM_Tree_Baltic_Pine_01_A": 24.0, "SM_Tree_Baltic_Pine_01_B": 24.0, "SM_Tree_Baltic_Pine_01_C": 16.0, "SM_Tree_Baltic_Pine_01_D": 12.0,
         "SM_Tree_Baltic_Pine_Sapling_01_A": 7.0, "SM_Tree_Baltic_Pine_Sapling_01_B": 7.0, "SM_Tree_Baltic_Pine_Sapling_01_C": 5.0}


def asset(path):
    a = u.EditorAssetLibrary.load_asset(path)
    if not a:
        raise RuntimeError("missing " + path)
    return a


def seg_dist(px, py, a, b):
    ax, ay = b[0] - a[0], b[1] - a[1]
    t = max(0.0, min(1.0, ((px - a[0]) * ax + (py - a[1]) * ay) / (ax * ax + ay * ay or 1.0)))
    return math.hypot(px - a[0] - t * ax, py - a[1] - t * ay)


def path_dist(x, y):
    return min(seg_dist(x, y, a, b) for poly in PATHS for a, b in zip(poly, poly[1:]))


GRAVEL = [(-2612.0, -1138.0, 98.0, 512.0), (-1712.0, -408.0, -102.0, 102.0)]       # the drive (the cruiser comes in over it) and the front path


def off_tracks(x, y, margin=70.0):
    """The nearest place to (x, y), sideways, that is not on the drive, the front path or a footpath."""
    for dy in (0, 90, -90, 180, -180, 270, -270, 360, -360, 450, -450, 540, -540):
        yy = y + dy
        if any(x0 - margin < x < x1 + margin and y0 - margin < yy < y1 + margin for x0, x1, y0, y1 in GRAVEL):
            continue
        if path_dist(x, yy) < 112.0 + margin:
            continue
        return x, yy
    return x, y


def dress():
    sub = u.get_editor_subsystem(u.EditorActorSubsystem)
    actors = list(sub.get_all_level_actors())

    def mesh_of(a):
        if not isinstance(a, u.StaticMeshActor):
            return ""
        m = a.static_mesh_component.static_mesh
        return m.get_path_name() if m else ""

    def name_of(a):
        return mesh_of(a).split("/")[-1].split(".")[0]

    def swap(a, mesh, z=GROUND, scale=1.0, collide="BlockAll", yaw=None, xy=None):
        c = a.static_mesh_component
        c.set_static_mesh(mesh)
        c.set_editor_property("override_materials", [])
        l = a.get_actor_location()
        r = a.get_actor_rotation()
        x, y = xy if xy else (l.x, l.y)
        a.set_actor_location_and_rotation(u.Vector(x, y, z), u.Rotator(roll=0, pitch=0, yaw=r.yaw if yaw is None else yaw), False, True)
        a.set_actor_scale3d(u.Vector(scale, scale, scale))
        c.set_collision_profile_name(collide)
        return a

    def spawn(label, mesh, x, y, z, yaw, folder, scale=1.0, collide="BlockAll"):
        a = sub.spawn_actor_from_class(u.StaticMeshActor, u.Vector(x, y, z), u.Rotator(roll=0, pitch=0, yaw=yaw))
        a.set_actor_label(label)
        a.set_folder_path(folder)
        c = a.static_mesh_component
        c.set_static_mesh(mesh)
        a.set_actor_scale3d(u.Vector(scale, scale, scale))
        c.set_collision_profile_name(collide)
        return a

    # what this step made on an earlier run goes, and is made again
    made = [a for a in actors if a.get_actor_label().startswith(("TreeBlock_", "StumpExtra_", "RockExtra_")) or a.get_actor_label() == "GrassField"]
    for a in made:
        sub.destroy_actor(a)
    actors = [a for a in actors if a not in made]

    # ------------------------------------------------------------------ wheelbarrows, stumps, woodpiles
    n = {"barrow": 0, "stump": 0, "pile": 0, "rock": 0}
    for a in actors:
        nm = name_of(a)
        if nm == "SM_Wheelbarrow_Old":
            swap(a, asset(P + "Wheelbarrow"), yaw=a.get_actor_rotation().yaw + 90.0)      # the kit one ran along Y; ours runs along X
            n["barrow"] += 1
        elif nm == "SM_Stump_Axe":
            front = a.get_actor_location().x < 0
            swap(a, asset(P + ("StumpAxe" if front else "Stump")), scale=1.15 if front else 1.3)
            n["stump"] += 1
        elif nm == "SM_Woodpile_Rotten":
            swap(a, asset(P + "Woodpile"), scale=0.85)
            n["pile"] += 1
    for i, (x, y, kind, yaw) in enumerate(EXTRA_STUMPS):
        if path_dist(x, y) > 150.0:
            spawn(f"StumpExtra_{i}", asset(P + kind), x, y, GROUND, yaw, "House/Shell/Exterior/Yard" if x < 2800 else "House/Shell/Exterior/BackYard",
                  1.05 + 0.3 * ((i * 37) % 10) / 10.0)
            n["stump"] += 1

    # ------------------------------------------------------------------ rocks
    rocks = {k: asset(P + k) for k in ("RockA", "RockB", "RockC")}
    half = {}
    for k, m in rocks.items():
        bb = m.get_bounding_box()
        half[k] = (max(bb.max.x - bb.min.x, bb.max.y - bb.min.y) / 2.0, bb.max.z - bb.min.z)
    extra = moved = 0
    for a in actors:
        nm = name_of(a)
        if not nm.startswith("SM_Rock_") or "HorrorHouseKit" not in mesh_of(a):
            continue
        o, e = a.get_actor_bounds(False)
        l = a.get_actor_location()
        h = zlib.crc32(f"{l.x:.0f},{l.y:.0f}".encode())
        size = max(e.x, e.y)
        folder = str(a.get_folder_path())
        px, py = off_tracks(l.x, l.y)                       # the kit slabs lay flat on the drive and the paths; stones do not
        moved += (px, py) != (l.x, l.y)
        if "Cluster" in nm:                                   # a flat cluster of slabs: one large stone and two beside it
            k = "RockC"
            s = min(1.1, max(0.7, size * 0.40 / half[k][0]))
            swap(a, rocks[k], z=GROUND - 1.0, scale=s, collide="BlockAll" if half[k][1] * s > 30 else "NoCollision", xy=(px, py))
            for j, (kk, ang) in enumerate((("RockA", 0.7), ("RockB", 3.6))):
                ang += (h % 100) / 50.0
                d = half[k][0] * s * 1.05
                ss = 0.7 + ((h >> (4 * j)) % 10) / 20.0
                ex, ey = off_tracks(px + d * math.cos(ang), py + d * math.sin(ang))
                spawn(f"RockExtra_{extra}", rocks[kk], ex, ey, GROUND - 1.0, (h >> j) % 360, folder, ss, "BlockAll" if half[kk][1] * ss > 30 else "NoCollision")
                extra += 1
        else:
            k = "RockB" if size < 60 else ("RockA" if h % 2 else "RockC")
            s = min(1.6, max(0.35, size * 0.85 / half[k][0]))
            swap(a, rocks[k], z=GROUND - 1.0, scale=s, collide="BlockAll" if half[k][1] * s > 30 else "NoCollision", yaw=h % 360, xy=(px, py))
        n["rock"] += 1
    u.log_warning(f"WC_POLISH outdoors: {n['barrow']} wheelbarrows, {n['stump']} stumps, {n['pile']} woodpiles, {n['rock']} rocks (+{extra} beside the clusters, {moved} moved off the gravel)")

    # ------------------------------------------------------------------ the kit trees become forest trees
    def forest(c, mesh, shadow):
        c.set_collision_profile_name("NoCollision")
        c.set_editor_property("visible_in_ray_tracing", False)
        c.set_editor_property("affect_dynamic_indirect_lighting", False)
        c.set_editor_property("affect_distance_field_lighting", False)
        c.set_cull_distance(10000)
        c.set_cast_shadow(shadow)
    yard_set = ["Dead_Pine_A", "Dead_Pine_C", "Dead_Pine_B", "Dead_Pine_A", "Dead_Pine_C", "Dead_Pine_B", "Dead_Pine_D"]
    nt = ny = 0
    for a in actors:
        nm = name_of(a)
        if not nm.startswith("SM_Tree_") or "HorrorHouseKit" not in mesh_of(a):
            continue
        l = a.get_actor_location()
        h = zlib.crc32(f"{l.x:.0f},{l.y:.0f}".encode())
        inside = WALK[0] < l.x < WALK[1] and WALK[2] < l.y < WALK[3]
        z = -44.0
        if inside:
            kind = "SM_Tree_" + yard_set[ny % len(yard_set)]
            s = 1.0 + (h % 25) / 100.0
            ny += 1
        else:
            r = h % 100
            if r < 46:
                v = "ABC"[(h >> 8) % 3]
                kind = "SM_Tree_Baltic_Pine_Sapling_01_" + v
                s = 1.8 + ((h >> 12) % 90) / 100.0
                z = -44.0 if v == "C" else -62.0
            elif r < 76:
                kind = "SM_Tree_Dead_Pine_" + "DC"[(h >> 8) % 2]
                s = 0.95 + ((h >> 12) % 40) / 100.0
            elif r < 90:
                kind = "SM_Tree_Dead_Pine_" + "AB"[(h >> 8) % 2]
                s = 0.95 + ((h >> 12) % 35) / 100.0
            else:
                kind = "SM_Tree_Baltic_Pine_01_" + "CD"[(h >> 8) % 2]
                s = 0.95 + ((h >> 12) % 40) / 100.0
        swap(a, asset(F + kind), z=z, scale=s, collide="NoCollision", yaw=h % 360)
        forest(a.static_mesh_component, kind, inside)
        nt += 1
    u.log_warning(f"WC_POLISH outdoors: {nt} kit trees replaced by forest trees ({ny} of them in the yard)")

    # ------------------------------------------------------------------ no tree can be walked through
    cyl = asset("/Engine/BasicShapes/Cylinder")
    nb = 0
    for a in actors:
        nm = name_of(a)
        if nm not in TRUNK:
            continue
        l = a.get_actor_location()
        if not (WALK[0] - 160 < l.x < WALK[1] + 160 and WALK[2] - 160 < l.y < WALK[3] + 160):
            continue
        r = TRUNK[nm] * a.get_actor_scale3d().x
        b = spawn(f"TreeBlock_{nb}", cyl, l.x, l.y, GROUND + 150.0, 0.0, "House/Shell/Exterior/TreeBlocks", 1.0, "BlockAll")
        b.set_actor_scale3d(u.Vector(r / 50.0, r / 50.0, 3.2))
        b.static_mesh_component.set_cast_shadow(False)
        b.static_mesh_component.set_editor_property("visible_in_ray_tracing", False)
        b.static_mesh_component.set_editor_property("affect_dynamic_indirect_lighting", False)
        b.static_mesh_component.set_editor_property("affect_distance_field_lighting", False)
        b.set_actor_hidden_in_game(True)
        nb += 1
    u.log_warning(f"WC_POLISH outdoors: {nb} trunks made solid")

    # ------------------------------------------------------------------ grass
    pts = json.load(open(ROOT + "/SourceArt/Outdoors/grass_points.json"))
    field = sub.spawn_actor_from_class(u.Actor, u.Vector(0, 0, 0), u.Rotator(0, 0, 0))
    field.set_actor_label("GrassField")
    field.set_folder_path("House/Shell/Exterior")
    sds = u.get_engine_subsystem(u.SubobjectDataSubsystem)
    lib = u.SubobjectDataBlueprintFunctionLibrary
    total = 0
    for var in sorted(pts["clumps"]):
        rows = pts["clumps"][var]
        if not rows:
            continue
        handles = sds.k2_gather_subobject_data_for_instance(field)
        h, fail = sds.add_new_subobject(u.AddNewSubobjectParams(parent_handle=handles[0], new_class=u.HierarchicalInstancedStaticMeshComponent, blueprint_context=None))
        c = lib.get_object(lib.get_data(h))
        if not c:
            raise RuntimeError(f"no grass component for {var}: {fail}")
        c.set_static_mesh(asset(f"/Game/WC/Outdoors/SM_Grass_{var}"))
        c.set_collision_profile_name("NoCollision")
        c.set_cast_shadow(False)
        c.set_editor_property("visible_in_ray_tracing", False)
        c.set_editor_property("affect_dynamic_indirect_lighting", False)
        c.set_editor_property("affect_distance_field_lighting", False)
        c.set_editor_property("mobility", u.ComponentMobility.STATIC)
        c.set_cull_distances(2600, 3900)
        xf = [u.Transform(u.Vector(x, y, pts["ground"] - 1.5), u.Rotator(roll=0, pitch=0, yaw=yaw), u.Vector(s, s, s)) for x, y, yaw, s in rows]
        c.add_instances(xf, False, True)
        total += c.get_instance_count()
    u.log_warning(f"WC_POLISH outdoors: {total} clumps of grass planted")
