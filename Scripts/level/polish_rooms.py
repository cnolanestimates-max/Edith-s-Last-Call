"""The room part of the polish pass (Cheyenne, 2026-11-21: every prop "AAA", the tall empty cabinets turned into something
that makes sense).  Safe on the saved map (apply_polish.py step "polish_rooms") and at the end of the level build, after
polish_pass.py has turned the furniture to face its rooms.  Idempotent: the sets have fixed labels and follow their cabinet.

  - the empty glass cabinets get what they would hold (Scripts/art/polish_furniture.py): Edith's china in the dining room,
    books and Walter's things in the den, dishes and preserves in the kitchen, the medicine in the sickroom.  The kitchen and
    sickroom cabinets are the hospital kit's, so its own bottles and boxes are hidden first.
  - Danny's plain kit wardrobe becomes a walnut two-door with drawers and his army duffel on top; the hospital steel cabinet
    in the pantry becomes a painted pantry cupboard with glazed doors.
  - round two (2026-11-22): the hospital kit swapped for a farmhouse sink, a pedestal basin, wicker hampers, an oak file and
    cellar shelving; the open wardrobes filled (the aide's clothes, Edith's sewing, and in the attic, opened up, the
    Christmas presents for Danny and Ruth that were never opened)."""
import math, os, runpy
import unreal as u

SETS = [  # cabinet label, end of its folder, the set, kit slots to hide
    ("ChinaCabinet", "/Dining", "SM_PolishChinaSet", ()),
    ("GunCabinet", "/Den", "SM_PolishDenSet", ()),
    ("Cabinet_Medicine_Glass_Open", "/Kitchen", "SM_PolishKitchenSet", (2, 3, 4)),
    ("Cabinet_Medicine_Glass_Open", "/Sickroom", "SM_PolishMedicineSet", (2, 3, 4)),
    # round two (2026-11-22): the open kit wardrobes, their one rag of a garment hidden, filled with what they would hold
    ("Wardrobe_Open_Clothes", "/Aide", "SM_PolishAideWardrobe", (4, 5, 6, 7)),
    ("Wardrobe_Open_Clothes", "/Sewing", "SM_PolishSewingWardrobe", (4, 5, 6, 7)),
    ("Wardrobe_Leaning", "/Attic", "SM_PolishAtticPresents", (4, 5, 6, 7)),
]


REPLACE = [  # kit piece label, end of its folder, the new piece, seat its back against the wall behind it
    ("Wardrobe_Tall", "/Daniel", "SM_PolishDanielWardrobe", False),
    ("Cabinet_Steel_Tall", "/Pantry", "SM_PolishPantryCupboard", False),
    # round two (2026-11-22): the hospital kit swapped for what a farmhouse would have
    ("Sink_Hospital", "/Kitchen", "SM_PolishKitchenSink", True),
    ("Sink_Hospital", "/Bath2", "SM_PolishPedestalSink", True),
    ("Laundry_Cart", "/Bath", "SM_PolishHamper", False),
    ("Laundry_Cart", "/Bath2", "SM_PolishHamper", False),
    ("Filing_Cabinet_4", "/Den", "SM_PolishFileCabinet", True),
    ("Lockers_Row_4_Dented", "/Cellar", "SM_PolishCellarShelves", True),
    # the attic's closed slab of a wardrobe opened up, for the presents its look-at note talks about
    ("Wardrobe_Leaning", "/Attic", "/Game/HorrorHouseKit/Meshes/Haunted_Furniture/SM_Wardrobe_Open_Clothes", True),
]


def dress():
    sub = u.get_editor_subsystem(u.EditorActorSubsystem)
    actors = list(sub.get_all_level_actors())
    labels = {a.get_actor_label(): a for a in actors}
    hidden = u.EditorAssetLibrary.load_asset("/Game/WC/Materials/M_ShelfHidden")
    n = 0
    # furniture replaced outright first (its contents below then follow it): the new piece takes the kit piece's place
    room_of = runpy.run_path(os.path.join(os.path.dirname(os.path.abspath(__file__)), "polish_pass.py"))["room_of"]
    for label, folder, mesh_name, seat in REPLACE:
        a = next((x for x in actors if x.get_actor_label() == label and str(x.get_folder_path()).endswith(folder)), None)
        mesh = u.EditorAssetLibrary.load_asset(mesh_name if mesh_name.startswith("/") else "/Game/WC/Props/Polish/" + mesh_name)
        if not a or not mesh:
            u.log_warning(f"WC_POLISH rooms: {label}{folder} or {mesh_name} missing")
            continue
        c = a.static_mesh_component
        c.set_static_mesh(mesh)
        c.set_editor_property("override_materials", [])
        c.set_collision_profile_name("BlockAll")
        if seat:
            # its back two centimetres off the wall behind it (the new piece is not as deep as the kit one was)
            o, e = a.get_actor_bounds(False)
            _, b = room_of(o.x, o.y, o.z - e.z)
            if b:
                fy = math.radians(a.get_actor_rotation().yaw)
                fx_, fy_ = -math.sin(fy), math.cos(fy)
                loc = a.get_actor_location()
                if abs(fx_) > 0.9:
                    want = (b[0] if fx_ > 0 else b[1]) + (e.x + 2.0) * (1 if fx_ > 0 else -1)
                    a.set_actor_location(u.Vector(loc.x + (want - o.x), loc.y, loc.z), False, True)
                elif abs(fy_) > 0.9:
                    want = (b[2] if fy_ > 0 else b[3]) + (e.y + 2.0) * (1 if fy_ > 0 else -1)
                    a.set_actor_location(u.Vector(loc.x, loc.y + (want - o.y), loc.z), False, True)
        n += 1
    # the attic wardrobe, now the kit's open one, takes the dark wood the other open wardrobes wear (the kit's own reads pink)
    attic = next((x for x in actors if x.get_actor_label() == "Wardrobe_Leaning" and str(x.get_folder_path()).endswith("/Attic")), None)
    model = next((x for x in actors if x.get_actor_label() == "Wardrobe_Open_Clothes" and str(x.get_folder_path()).endswith("/Aide")), None)
    if attic and model:
        for i, m in enumerate(model.static_mesh_component.get_materials()[:4]):
            attic.static_mesh_component.set_material(i, m)
    # what the cabinets and wardrobes hold, at the cabinet's own transform
    for label, folder, mesh_name, hide in SETS:
        cab = next((a for a in actors if a.get_actor_label() == label and str(a.get_folder_path()).endswith(folder)), None)
        mesh = u.EditorAssetLibrary.load_asset("/Game/WC/Props/Polish/" + mesh_name)
        if not cab or not mesh:
            u.log_warning(f"WC_POLISH rooms: {label}{folder} or {mesh_name} missing")
            continue
        for slot in hide:
            cab.static_mesh_component.set_material(slot, hidden)
        set_label = mesh_name.replace("SM_Polish", "Contents_")
        a = labels.get(set_label) or sub.spawn_actor_from_class(u.StaticMeshActor, cab.get_actor_location(), cab.get_actor_rotation())
        a.set_actor_label(set_label)
        a.set_folder_path(cab.get_folder_path())
        a.set_actor_transform(cab.get_actor_transform(), False, True)
        c = a.static_mesh_component
        c.set_static_mesh(mesh)
        c.set_collision_profile_name("NoCollision")
        n += 1
    u.log_warning(f"WC_POLISH rooms: {n} pieces filled or replaced")
