"""Fixes from the polish pass that patch the saved House map (apply_polish.py step "polish_fixes", and the end of the level
build, where they find nothing to do).

  - the upstairs back bathroom (Bath2) had a rotted-through square in the middle of its floor, walled off by an invisible
    block that filled the doorway so the player could not get in (Cheyenne, 2026-11-22: "patch it with regular floor").
    build_house.py no longer cuts it; on a map built before that, this lays the boards and the sickroom ceiling under them
    back over the gap, puts the room's grime over the new boards, and takes away the block and its look-at note."""
import unreal as u

HOLE = (2480.0, 2600.0, 330.0, 450.0)


def dress():
    sub = u.get_editor_subsystem(u.EditorActorSubsystem)
    actors = list(sub.get_all_level_actors())
    by = {a.get_actor_label(): a for a in actors}
    x0, x1, y0, y1 = HOLE
    # (an earlier run also laid tiles over the gap; the room's tile layer does not show in the game, the boards do)
    if by.get("Bath2Tiles_Patch"):
        sub.destroy_actor(by.pop("Bath2Tiles_Patch"))

    def patch(src_label, new_label, z0, z1):
        src = by.get(src_label)
        if not src:
            u.log_warning(f"WC_POLISH fixes: {src_label} missing")
            return
        # a copy of the piece next to the gap: same mesh, materials and collision (duplicate_actor crashes in a commandlet)
        a = by.get(new_label) or sub.spawn_actor_from_class(u.StaticMeshActor, src.get_actor_location(), src.get_actor_rotation())
        a.set_actor_label(new_label)
        a.set_folder_path(src.get_folder_path())
        sc, dc = src.static_mesh_component, a.static_mesh_component
        dc.set_static_mesh(sc.static_mesh)
        for i, m in enumerate(sc.get_materials()):
            dc.set_material(i, m)
        dc.set_collision_profile_name(sc.get_collision_profile_name())
        dc.set_collision_enabled(sc.get_collision_enabled())
        a.set_actor_rotation(src.get_actor_rotation(), False)
        a.set_editor_property("tags", list(src.tags))
        o, e = src.get_actor_bounds(False)
        sl, ss = src.get_actor_location(), src.get_actor_scale3d()
        size = (x1 - x0, y1 - y0, z1 - z0)
        old = (2 * e.x, 2 * e.y, 2 * e.z)
        k = [size[i] / old[i] if old[i] > 1e-3 else 1.0 for i in range(3)]
        centre = u.Vector((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
        off = sl - o
        a.set_actor_scale3d(u.Vector(ss.x * k[0], ss.y * k[1], ss.z * k[2]))
        a.set_actor_location(u.Vector(centre.x + off.x * k[0], centre.y + off.y * k[1], centre.z + off.z * k[2]), False, True)
        by[new_label] = a

    block = by.get("HoleBlock_2540_350")
    if block:
        patch("UpperFloor_4", "UpperFloor_Bath2Patch", 330.0, 350.0)
        patch("UpperFloor_ceil_4", "UpperFloor_ceil_Bath2Patch", 327.0, 330.0)
        sub.destroy_actor(block)
        for a in actors:
            if a.get_actor_label() == "Look_bath2_hole":
                sub.destroy_actor(a)
        u.log_warning("WC_POLISH fixes: back bathroom floor patched")
    if False:   # (the grime over the new boards: no longer wanted once the white trim covers it, mock_round2.py, 2026-11-22)
        # the same grime as the boards round it, so the new boards do not read as a clean square
        for i, (name, dx, dy, size, yaw) in enumerate((("MD_dirt_01", -10, 15, 95, 40), ("MD_filth_01", 25, -20, 80, 200), ("MD_mold_02", -30, -35, 70, 120))):
            d = sub.spawn_actor_from_class(u.DecalActor, u.Vector((x0 + x1) / 2 + dx, (y0 + y1) / 2 + dy, 351.0), u.Rotator(roll=0, pitch=-90, yaw=yaw))
            d.set_actor_label(f"Decal_Bath2Patch_{i}")
            d.set_folder_path("House/Decay/Decals")
            d.decal.set_decal_material(u.EditorAssetLibrary.load_asset("/Game/WC/Decals/" + name))
            d.decal.set_editor_property("decal_size", u.Vector(14, size, size))
        u.log_warning("WC_POLISH fixes: grime laid over the patched boards")
