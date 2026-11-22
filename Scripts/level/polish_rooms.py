"""The room part of the polish pass (Cheyenne, 2026-11-21: every prop "AAA", the tall empty cabinets turned into something
that makes sense).  Safe on the saved map (apply_polish.py step "polish_rooms") and at the end of the level build, after
polish_pass.py has turned the furniture to face its rooms.  Idempotent: the sets have fixed labels and follow their cabinet.

  - the empty glass cabinets get what they would hold (Scripts/art/polish_furniture.py): Edith's china in the dining room,
    books and Walter's things in the den, dishes and preserves in the kitchen, the medicine in the sickroom.  The kitchen and
    sickroom cabinets are the hospital kit's, so its own bottles and boxes are hidden first.
  - Danny's plain kit wardrobe becomes a walnut two-door with drawers and his army duffel on top; the hospital steel cabinet
    in the pantry becomes a painted pantry cupboard with glazed doors."""
import unreal as u

SETS = [  # cabinet label, end of its folder, the set, kit slots to hide
    ("ChinaCabinet", "/Dining", "SM_PolishChinaSet", ()),
    ("GunCabinet", "/Den", "SM_PolishDenSet", ()),
    ("Cabinet_Medicine_Glass_Open", "/Kitchen", "SM_PolishKitchenSet", (2, 3, 4)),
    ("Cabinet_Medicine_Glass_Open", "/Sickroom", "SM_PolishMedicineSet", (2, 3, 4)),
]


REPLACE = [  # kit piece label, end of its folder, the new piece
    ("Wardrobe_Tall", "/Daniel", "SM_PolishDanielWardrobe"),
    ("Cabinet_Steel_Tall", "/Pantry", "SM_PolishPantryCupboard"),
]


def dress():
    sub = u.get_editor_subsystem(u.EditorActorSubsystem)
    actors = list(sub.get_all_level_actors())
    labels = {a.get_actor_label(): a for a in actors}
    hidden = u.EditorAssetLibrary.load_asset("/Game/WC/Materials/M_ShelfHidden")
    n = 0
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
    # furniture replaced outright: the new piece takes the kit piece's place (same pivot, back on the same wall)
    for label, folder, mesh_name in REPLACE:
        a = next((x for x in actors if x.get_actor_label() == label and str(x.get_folder_path()).endswith(folder)), None)
        mesh = u.EditorAssetLibrary.load_asset("/Game/WC/Props/Polish/" + mesh_name)
        if not a or not mesh:
            u.log_warning(f"WC_POLISH rooms: {label}{folder} or {mesh_name} missing")
            continue
        c = a.static_mesh_component
        c.set_static_mesh(mesh)
        c.set_editor_property("override_materials", [])
        c.set_collision_profile_name("BlockAll")
        n += 1
    u.log_warning(f"WC_POLISH rooms: {n} cabinets filled or replaced")
