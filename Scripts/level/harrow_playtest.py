"""Mount the two bedroom plaques and update the playtest's note and examine text."""
import ast
import json
from pathlib import Path
import unreal as u

ROOT = Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir()))
PROPS = "/Game/WC/Props/HouseDetails"


def dress():
    actors = u.get_editor_subsystem(u.EditorActorSubsystem)
    by_label = {a.get_actor_label(): a for a in actors.get_all_level_actors()}
    mesh = u.load_asset(PROPS + "/SM_HarrowDoorPlaque")
    assert mesh, "Import the Harrow door plaque assets first"
    for name, door_id in (("Danny", "up_daniel"), ("Ruth", "up_kids")):
        door = by_label["Door_" + door_id]
        leaf = door.get_editor_property("mesh")
        material = u.load_asset(PROPS + "/M_HarrowPlaque" + name)
        assert material, name
        label = name + "'s door plaque"
        plaque = by_label.get(label)
        if not plaque:
            plaque = actors.spawn_actor_from_class(u.StaticMeshActor, door.get_actor_location())
            plaque.set_actor_label(label)
            plaque.set_folder_path("House/Doors")
        component = plaque.static_mesh_component
        component.set_mobility(u.ComponentMobility.MOVABLE)
        component.set_static_mesh(mesh)
        component.set_material(0, material)
        component.set_collision_profile_name("NoCollision")
        component.set_editor_property("lighting_channels", leaf.get_editor_property("lighting_channels"))
        assert plaque.attach_to_component(leaf, "", u.AttachmentRule.KEEP_RELATIVE, u.AttachmentRule.KEEP_RELATIVE,
                                          u.AttachmentRule.KEEP_RELATIVE, False)
        # The central panel is inset from the thick trim and hardware.
        plaque.set_actor_relative_location(u.Vector(0, 5.6, 156), False, False)
        plaque.set_actor_relative_rotation(u.Rotator(0, 0, 0), False, False)
        print(f"WCHARRPLAQ {name} {plaque.get_actor_location()} {mesh.get_bounding_box()}")

    # The former drawer position was directly behind an impassable floor hole.
    for prop, x, y in (("Hide_drawer", 1200, -256), ("Show_drawer", 1200, -268)):
        for actor in by_label.values():
            if actor.actor_has_tag(prop) and actor.get_actor_location().z == 350:
                actor.set_actor_location(u.Vector(x, y, 350), False, True)
    for label, y in (("Harrow_bath_dresser", -301), ("DrawerPoint", -268)):
        actor = by_label[label]
        actor.set_actor_location(u.Vector(1200, y, actor.get_actor_location().z), False, True)

    notes = json.loads((ROOT / "Scripts/level/notes.json").read_text(encoding="utf-8"))
    for note_id in ("note_letter1", "note_rem2"):
        by_label["Note_" + note_id].set_editor_property("body", notes[note_id]["body"])

    # These lines are shared with the full house builder so the authored level
    # and a fresh build use the same examine text.
    source = (ROOT / "Scripts/level/looks.py").read_text(encoding="utf-8").splitlines()
    for look_id in ("shed_bench", "aide_suitcase"):
        row = next(line for line in source if line.strip().startswith(f'("{look_id}",'))
        statement = ast.parse(row.strip().rstrip(","), mode="eval").body
        by_label["Look_" + look_id].set_editor_property("text", ast.literal_eval(statement.elts[4]))
