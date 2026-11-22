"""The yard part of the polish pass (Cheyenne, 2026-11-21).  Safe on the saved map (apply_polish.py, step "polish_yard")
or at the end of the level build.  Idempotent: actors it makes have fixed labels and are moved, not duplicated.

  - the tipped barrel by the back of the house: the kit's wooden keg on a checkered disc becomes a rusted 55-gallon oil
    drum (SM_Item_OilDrum) with a real spill (SM_Item_OilSpill), and dark wet ground round it from soft decals."""
import json
import math
import unreal as u

P = "/Game/WC/Props/"


def asset(path):
    a = u.EditorAssetLibrary.load_asset(path)
    if not a:
        raise RuntimeError("missing " + path)
    return a


def dress():
    sub = u.get_editor_subsystem(u.EditorActorSubsystem)
    actors = sub.get_all_level_actors()
    by = {}
    for a in actors:
        by.setdefault(a.get_actor_label(), []).append(a)

    def one(label, cls=u.StaticMeshActor, loc=u.Vector(0, 0, 0), rot=u.Rotator(0, 0, 0), folder="House/Shell/Exterior/BackYard"):
        a = (by.get(label) or [None])[0] or sub.spawn_actor_from_class(cls, loc, rot)
        a.set_actor_label(label)
        a.set_folder_path(folder)
        a.set_actor_location_and_rotation(loc, rot, False, True)
        return a

    # ------------------------------------------------------------------ the drum and its spill
    kit = [a for a in by.get("Barrel_Tipped_Spilled", []) if "BackYard" in str(a.get_folder_path())]
    old = [a for a in by.get("OilDrum", [])]
    base = (kit or old)[0]
    loc = base.get_actor_location()
    bx, by_ = loc.x, loc.y
    ground = -40.0
    yaw = 20.0
    drum = one("OilDrum", loc=u.Vector(bx, by_, ground), rot=u.Rotator(roll=0, pitch=0, yaw=yaw))
    c = drum.static_mesh_component
    c.set_static_mesh(asset(P + "SM_Item_OilDrum"))
    c.set_editor_property("override_materials", [])
    c.set_collision_profile_name("BlockAll")
    drum.set_actor_scale3d(u.Vector(1, 1, 1))
    for a in kit:
        if a is not drum:
            sub.destroy_actor(a)
    # the open bung is in the head at the drum's +X end: the pool spreads out from there, downhill of it
    hx, hy = math.cos(math.radians(yaw)), math.sin(math.radians(yaw))
    sx, sy = bx + hx * 95.0, by_ + hy * 95.0
    spill = one("OilSpill", loc=u.Vector(sx, sy, ground + 1.2), rot=u.Rotator(roll=0, pitch=0, yaw=yaw + 8.0))
    sc = spill.static_mesh_component
    sc.set_static_mesh(asset(P + "SM_Item_OilSpill"))
    sc.set_collision_profile_name("NoCollision")
    sc.set_cast_shadow(False)
    sc.set_editor_property("receives_decals", False)                 # the stain decals round it must not paint over the oil
    # soft dark soaked ground round the pool (decals: their edges fade, which a mesh cannot)
    for i, (name, dx, dy, w, h, r) in enumerate((("MD_water_02", 0, 0, 300, 230, 15), ("MD_puddle_01", 25, -25, 260, 210, 70), ("MD_water_02", -45, 30, 220, 180, 140))):
        d = one(f"OilStain_{i}", u.DecalActor, u.Vector(sx + dx, sy + dy, ground), u.Rotator(roll=r, pitch=-90, yaw=yaw))
        d.decal.set_decal_material(asset("/Game/WC/Decals/" + name))
        d.decal.set_editor_property("decal_size", u.Vector(30, w / 2, h / 2))
    u.log_warning(f"WC_POLISH yard: oil drum at ({bx:.0f},{by_:.0f}), spill at ({sx:.0f},{sy:.0f})")

    # ------------------------------------------------------------------ the gravel track
    meta_path = "C:/GameDev/Unreal/WellnessCheck/SourceArt/Road/road_chunks.json"
    try:
        meta = json.load(open(meta_path))
    except OSError:
        meta = {}
    placed = 0
    for name, (x, y, z) in sorted(meta.items()):
        mesh = u.EditorAssetLibrary.load_asset("/Game/WC/Road/" + name)
        if not mesh:
            continue
        a = one(name.replace("SM_", ""), loc=u.Vector(x, y, z), folder="House/Shell/Exterior/Footpaths")
        c = a.static_mesh_component
        c.set_static_mesh(mesh)
        c.set_collision_profile_name("NoCollision")
        c.set_editor_property("cast_shadow", True)
        a.set_actor_scale3d(u.Vector(1, 1, 1))
        a.set_editor_property("tags", ["YardTrack"])
        placed += 1
    if placed:
        # the old flat gravel planes go under the yard (hiding them did not hold in the game, and they showed through the
        # ruts); they stay in the map for Codex's path check, which only uses where they are along the ground
        for a in actors:
            if a.get_actor_label().startswith("YardTrail_"):
                p_ = a.get_actor_location()
                if p_.z > -50.0:
                    a.set_actor_location(u.Vector(p_.x, p_.y, -60.0), False, True)
                a.static_mesh_component.set_visibility(False)
                a.set_actor_hidden_in_game(True)
    u.log_warning(f"WC_POLISH yard: {placed} chunks of gravel track laid")
