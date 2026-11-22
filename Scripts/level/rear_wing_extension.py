"""Insert 6.2 m of upstairs corridor ahead of the sewing room and rear bath."""
import json
from pathlib import Path

import unreal as u


ADDITION = 620.0
INSERT_AT = 2400.0
OLD_END = 2800.0
NEW_END = OLD_END + ADDITION
UPSTAIRS = 350.0
ROOMS = "House/Dressing/RearStorage"
SHELL = "House/Shell/RearExtension"
KIT = "/Game/HorrorHouseKit"


def dress():
    sub = u.get_editor_subsystem(u.EditorActorSubsystem)
    actors = list(sub.get_all_level_actors())
    by_name = {a.get_actor_label(): a for a in actors}
    if "RearWing_Floor" in by_name:
        return

    V = u.Vector
    R = u.Rotator
    load = u.EditorAssetLibrary.load_asset
    cube = load("/Engine/BasicShapes/Cube.Cube")
    materials = json.loads(Path(__file__).with_name("overrides.json").read_text(encoding="utf-8"))
    kit_index = {
        str(a.asset_name): str(a.package_name)
        for a in u.AssetRegistryHelpers.get_asset_registry().get_assets_by_path(KIT + "/Meshes", recursive=True)
    }

    def shift(a, dx):
        a.set_actor_location(a.get_actor_location() + V(dx, 0, 0), False, True)

    def mesh(name, model, at, folder, yaw=0., scale=(1., 1., 1.), material=None, collide=True):
        a = sub.spawn_actor_from_class(u.StaticMeshActor, V(*at), R(yaw=yaw))
        a.set_actor_label(name)
        a.set_folder_path(folder)
        a.set_actor_scale3d(V(*scale))
        c = a.static_mesh_component
        c.set_static_mesh(model)
        if material:
            c.set_material(0, material)
        else:
            for i, slot in enumerate(c.get_material_slot_names()):
                replacement = materials.get(str(slot))
                if replacement:
                    root, item = (KIT, replacement[4:]) if replacement.startswith("KIT:") else ("/Game/WC", replacement)
                    m = load(f"{root}/Materials/{item}")
                    if m:
                        c.set_material(i, m)
        c.set_collision_profile_name("BlockAll" if collide else "NoCollision")
        channels = u.LightingChannels()
        channels.set_editor_property("channel0", True)
        channels.set_editor_property("channel1", not folder.startswith("House/Shell/Exterior"))
        c.set_editor_property("lighting_channels", channels)
        return a

    def piece(name, kit_mesh, at, folder, yaw=0., scale=(1., 1., 1.), material=None, collide=True):
        return mesh(name, load(kit_index["SM_" + kit_mesh]), at, folder, yaw, scale, material, collide)

    def box(name, bounds, material, folder=SHELL, collide=True):
        x0, x1, y0, y1, z0, z1 = bounds
        return mesh(name, cube, ((x0+x1)/2, (y0+y1)/2, (z0+z1)/2), folder,
                    scale=((x1-x0)/100, (y1-y0)/100, (z1-z0)/100),
                    material=material, collide=collide)

    def extend(a, local_axis):
        s = a.get_actor_scale3d()
        setattr(s, local_axis, getattr(s, local_axis) + ADDITION / 100.)
        a.set_actor_scale3d(s)
        shift(a, ADDITION / 2.)

    # Move the last upstairs module, including both rooms' interactables and
    # camera/AI markers. Keep the lower back exit and first pair of rooms in place.
    corner_boards = []
    moved = 0
    for a in actors:
        p = a.get_actor_location()
        name = a.get_actor_label()
        if name.startswith("CornerBoard_2852_"):
            corner_boards.append(a)
            continue
        final_module = INSERT_AT < p.x < 2890 and 349. <= p.z < 705. and abs(p.y) < 760.
        rear_gable = name.startswith(("WingGable", "WingRake"))
        if final_module or rear_gable:
            shift(a, ADDITION)
            moved += 1

    for name in ("WingRoof_-1", "WingRoof_1"):
        extend(by_name[name], "y")
    for name in ("WingRidgeCap", "Frieze_2", "AtticFloor_2", "AtticFloor_ceil_2"):
        extend(by_name[name], "x")

    floor = by_name["UpperFloor_3"].static_mesh_component.get_material(0)
    fascia = by_name["Frieze_2"].static_mesh_component.get_material(0)
    plaster = by_name["UpperFloor_ceil_3"].static_mesh_component.get_material(0)
    siding = load("/Game/WC/Materials/MI_SidingPaint")
    old_wall = by_name["Door_up_bath2"].get_actor_location()
    assert abs(old_wall.x - (2543.5 + ADDITION)) < 1., "Rear bath did not move with the hall"

    box("RearWing_Floor", (OLD_END, NEW_END, -600, 600, 330, UPSTAIRS), floor).tags = [u.Name("Floor_Wood")]
    box("RearWing_PorchSoffit", (OLD_END, NEW_END+58, -658, 658, 319, 330),
        plaster, "House/Shell/Exterior", collide=False)
    box("RearWing_PorchFascia", (OLD_END, NEW_END+58, -658, 658, 330, 350),
        fascia, "House/Shell/Exterior", collide=False)
    # The extension overhangs the lower back exit as a covered porch.
    for j, x in enumerate((2875., 3385.)):
        for side in (-1, 1):
            y = side * 625.
            box(f"RearWing_Post_{j}_{side}", (x-11, x+11, y-11, y+11, -12, 330),
                fascia, "House/Shell/Exterior")
            box(f"RearWing_PostFoot_{j}_{side}", (x-19, x+19, y-19, y+19, -39, 18),
                fascia, "House/Shell/Exterior")
    for a in corner_boards:
        p = a.get_actor_location()
        y = p.y
        c = a.get_actor_scale3d()
        a.set_actor_scale3d(V(c.x, c.y, c.z/2))
        a.set_actor_location(V(p.x, y, 175), False, True)
        box(f"RearWing_UpperCorner_{int(y)}", (p.x+ADDITION-9, p.x+ADDITION+9, y-9, y+9, 350, 700),
            fascia, "House/Shell/Exterior", collide=False)

    # Open entries make both storage rooms optional stops along the corridor.
    for side, paper in ((-1, "Wall_Wainscot_Grey"), (1, "Wall_Wainscot_Purple")):
        piece(f"RearWing_Entry_{side}", "Wall_Doorway", (2600, side*200, UPSTAIRS), SHELL)
        piece(f"RearWing_HallInfill_{side}", paper, (2910, side*200, UPSTAIRS), SHELL, scale=(.55, 1, 1))
        piece(f"RearWing_OuterWall_{side}", "Wall_Plain_Simple", (2710, side*600, UPSTAIRS),
              SHELL, scale=(1.55, 1, 1))
        piece(f"RearWing_Clapboard_{side}", "Wall_Exterior_Siding", (2710, side*636, UPSTAIRS),
              "House/Shell/Exterior", scale=(1.55, 1, 1), material=siding)
        piece(f"RearWing_Divider_{side}", paper, (3020, side*400, UPSTAIRS), SHELL, yaw=90)
    for y in (-600, -200, 200, 600):
        piece(f"RearWing_PostAtRoom_{y}", "Wall_Corner_Post", (3020, y, UPSTAIRS), SHELL, collide=False)

    for label, model, x, y, yaw in (
        ("LinenCupboard", "Wardrobe_Open_Clothes", 2490, 542, 180),
        ("LinenHamper", "Laundry_Cart", 2890, 460, 27),
        ("LinenChest", "Chest_Trunk", 2890, 550, 180),
        ("BoxRoomShelf", "Bookshelf_Tall", 2487, -550, 0),
        ("BoxRoomCoveredChair", "Armchair_Sheet_Covered", 2880, -518, 24),
        ("BoxRoomCrates", "Box_Cardboard_Stack", 2860, -330, 38),
    ):
        piece("RearWing_" + label, model, (x, y, UPSTAIRS), ROOMS, yaw=yaw)
    for y in (-395, 385):
        piece(f"RearWing_Rug_{y}", "Rug_Persian_Worn", (2640, y, UPSTAIRS),
              ROOMS, yaw=90, scale=(.72, .72, .72), collide=False)
    piece("RearWing_HallRunner", "Rug_Persian_Worn", (2730, 0, UPSTAIRS),
          ROOMS, yaw=90, scale=(.9, 1.35, 1.), collide=False)

    # The cool light uses the same aim as the approved scare, but belongs to the
    # map. It is visible on the plaster before Edith spawns.
    anchor = old_wall + V(56.5, 0, 0)
    source = anchor + V(-130, -234, 217)
    target = anchor + V(76, -107, 263)
    lamp = sub.spawn_actor_from_class(u.SpotLight, source, u.MathLibrary.find_look_at_rotation(source, target))
    lamp.set_actor_label("RearWing_CornerLight")
    lamp.set_folder_path("House/Lights/House")
    lamp.tags = [u.Name("RearWingCornerLight"), u.Name("Hide_dawn")]
    c = lamp.light_component
    c.set_mobility(u.ComponentMobility.MOVABLE)
    c.set_editor_property("intensity_units", u.LightUnits.LUMENS)
    c.set_intensity(1050.)
    c.set_attenuation_radius(510.)
    c.set_inner_cone_angle(24.)
    c.set_outer_cone_angle(44.)
    c.set_light_color(u.LinearColor(.53, .69, 1., 1.))
    c.set_cast_shadows(True)
    c.set_editor_property("specular_scale", .38)
    c.set_editor_property("volumetric_scattering_intensity", .3)
    channels = u.LightingChannels()
    channels.set_editor_property("channel0", False)
    channels.set_editor_property("channel1", True)
    c.set_editor_property("lighting_channels", channels)
    cord = by_name["Cord_uprear"].static_mesh_component.get_material(0)
    box("RearWing_FixtureCord", (source.x-.6, source.x+.6, source.y-.6, source.y+.6, source.z+12, 667),
        cord, "House/Lights/House", collide=False)
    bulb = by_name["BulbOn_uprear"].static_mesh_component
    bulb_scale = by_name["BulbOn_uprear"].get_actor_scale3d()
    fixture = mesh("RearWing_FixtureBulb", bulb.static_mesh, (source.x, source.y, source.z+11),
                   "House/Lights/House", scale=(bulb_scale.x, bulb_scale.y, bulb_scale.z),
                   material=bulb.get_material(0), collide=False)
    fixture.static_mesh_component.set_editor_property("cast_shadow", False)

    trigger = by_name["T_t_up_ell"]
    ext = trigger.get_editor_property("box").get_unscaled_box_extent()
    trigger.get_editor_property("box").set_box_extent(V(ext.x+ADDITION/2, ext.y, ext.z))
    shift(trigger, ADDITION/2)

    def node(name, x, y, edges):
        n = sub.spawn_actor_from_class(u.TargetPoint, V(x, y, UPSTAIRS), R())
        n.set_actor_label("Nav_" + name)
        n.set_folder_path("House/Nav")
        n.tags = [u.Name(s) for s in ("NavNode", "N_"+name, *("E_"+e for e in edges))]

    for name, end in (("up_hallF", "up_hallG"), ("up_hallG", "up_hallF")):
        n = by_name["Nav_" + name]
        n.tags = [u.Name("E_up_storage") if str(t) == "E_" + end else t for t in n.tags]
    node("up_storage", 2600, 0, ("up_hallF", "up_hallG", "linen_d", "boxroom_d"))
    for name, side in (("linen", 1), ("boxroom", -1)):
        node(name+"_d", 2600, side*200, ("up_storage", name))
        node(name, 2600, side*388, (name+"_d",))
    bounds = by_name["NavBounds"]
    s = bounds.get_actor_scale3d()
    bounds.set_actor_scale3d(V(s.x+ADDITION/200, s.y, s.z))
    shift(bounds, ADDITION/2)

    u.log_warning(f"WC_REAR_WING inserted {ADDITION:.0f} cm, moved {moved} actors, rear bath x={old_wall.x:.1f}")
