"""Extend the ground-floor wall behind the living-room TV into the side yard."""
import unreal


def enlarge_living_room():
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    level = actors.get_all_level_actors()
    names = {a.get_actor_label(): a for a in level}
    if "LivingExtensionFloor" in names:
        return

    def match(label, x, y, z):
        choices = [a for a in level if a.get_actor_label() == label and
                   (a.get_actor_location() - unreal.Vector(x, y, z)).length() < 1]
        if len(choices) != 1:
            raise RuntimeError(f"Expected one {label} at {(x, y, z)}, found {len(choices)}")
        return choices[0]

    depth = 150
    plain = match("Wall_Peeling", 200, -600, 0)
    fireplace = match("Wall_Fireplace_Breast", 600, -600, 0)
    siding = match("Wall_Exterior_Siding", 200, -636, 0)
    move = [plain, fireplace, siding, match("Wall_Exterior_Siding", 600, -636, 0),
            match("Portrait_Slashed", 250, -581, 165), match("Portrait_Small", 470, -581, 175)]
    move.extend(names[n] for n in ("Usable_tv", "Fireplace_Wood_Overmantel", "Mantel_Clock",
                                   "Look_mantel_photos", "Watcher_fireplace"))
    for a in level:
        n, p, folder = a.get_actor_label(), a.get_actor_location(), str(a.get_folder_path())
        # These objects are attached visually to this wall or sit directly in its new footprint.
        if n.startswith(("Turret", "ChimneyLiving")) and folder.startswith("House/Shell/Exterior"):
            move.append(a)
        elif 0 <= p.x <= 800 and 0 < p.z < 320 and abs(p.y + 584) < 0.6 and folder == "House/Decay/Decals":
            move.append(a)
        elif n == "Cobweb_Corner" and folder == "House/Decay/Cobwebs" and abs(p.x - 780) < 1 and abs(p.y + 580) < 1 and p.z < 320:
            move.append(a)
        elif n in ("Bramble_Bush_Dead", "Rock_Fog_Small") and 0 < p.x < 800 and -830 < p.y < -600 and p.z < 0:
            move.append(a)

    def piece(template, name, xyz, scale, yaw=0):
        copy = actors.spawn_actor_from_class(unreal.StaticMeshActor, unreal.Vector(*xyz), unreal.Rotator(yaw=yaw))
        if not copy:
            raise RuntimeError(f"Could not create {name}")
        copy.set_actor_label(name)
        src, dst = template.static_mesh_component, copy.static_mesh_component
        dst.set_static_mesh(src.static_mesh)
        for index, material in enumerate(src.get_materials()):
            dst.set_material(index, material)
        dst.set_collision_profile_name(src.get_collision_profile_name())
        dst.set_editor_property("lighting_channels", src.get_editor_property("lighting_channels"))
        dst.set_cast_shadow(src.cast_shadow)
        copy.set_editor_property("tags", template.tags)
        copy.set_folder_path(template.get_folder_path())
        copy.set_actor_scale3d(unreal.Vector(*scale))
        return copy

    for a in move:
        p = a.get_actor_location()
        a.modify()
        a.set_actor_location(unreal.Vector(p.x, p.y - depth, p.z), False, True)
    # Continue the exact floor, ceiling and exterior materials from the existing level.
    piece(names["GroundFloor_4"], "LivingExtensionFloor", (400, -675, -10), (8, 1.5, 0.2))
    piece(names["UpperFloor_ceil_0"], "LivingExtensionCeiling", (400, -675, 328.5), (8, 1.5, 0.03))
    piece(names["Foundation_4"], "LivingExtensionFoundation", (400, -735, -20), (8.6, 1.5, 0.4))
    piece(names["RoofFront"], "LivingExtensionRoof", (400, -710, 337), (8.85, 2.3, 0.14))
    for x, outer_x, side in ((0, -36, "Front"), (800, 836, "Rear")):
        piece(plain, "LivingExtension" + side + "Wall", (x, -675, 0), (depth / 400, 1, 1), 90)
        piece(siding, "LivingExtension" + side + "Siding", (outer_x, -711, 0), (depth / 400, 1, 1), 90)

    sofa = names["Sofa_Sagging_Broken"]
    sofa.modify()
    # Leave its front edge ahead of the original rotten floor opening.
    sofa.set_actor_location(unreal.Vector(430, -395, sofa.get_actor_location().z), False, True)
    trigger = names["T_t_living"]
    trigger.modify()
    p = trigger.get_actor_location()
    trigger.set_actor_location(unreal.Vector(p.x, p.y - depth / 2, p.z), False, True)
    box = trigger.get_editor_property("box")
    box.modify()
    extent = box.get_unscaled_box_extent()
    box.set_box_extent(unreal.Vector(extent.x, extent.y + depth / 2, extent.z))
    for name, x, y in (("living", 220, -285), ("livingS", 365, -290), ("livingE", 540, -290)):
        point = names["Nav_" + name]
        point.modify()
        point.set_actor_location(unreal.Vector(x, y, point.get_actor_location().z), False, True)
