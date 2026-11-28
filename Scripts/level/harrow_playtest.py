"""Mount the two bedroom plaques and update the playtest's note and examine text."""
import ast
import json
from pathlib import Path
import unreal as u

ROOT = Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir()))
PROPS = "/Game/WC/Props/HouseDetails"


def dress_bath():
    actors = u.get_editor_subsystem(u.EditorActorSubsystem).get_all_level_actors()
    # The narrow chest sits between the cast-iron bath and the sink. Its drawers
    # face the clear floor, and the use box surrounds the top drawer's handle.
    positions = {"Hide_drawer": -554.4, "Show_drawer": -539.4}
    for tag, y in positions.items():
        dresser, = [a for a in actors if a.actor_has_tag(tag) and str(a.get_folder_path()).endswith("/Bath")]
        dresser.set_actor_location(u.Vector(1140, y, 350), False, True)
        dresser.set_actor_rotation(u.Rotator(0, 0, 0), False)
        dresser.set_actor_scale3d(u.Vector(.68, 1, 1))
    by_label = {a.get_actor_label(): a for a in actors}
    drawer = by_label["Harrow_bath_dresser"]
    drawer.set_actor_location(u.Vector(1140, -516, 422), False, True)
    drawer.set_editor_property("grab_extent", u.Vector(30, 12, 14))
    by_label["DrawerPoint"].set_actor_location(u.Vector(1140, -524, 422), False, True)

    # Raise the rear bath's existing surface into the bowl and give it the
    # same opaque, reflective water material as the draining bath.
    surface = by_label.get("TubWater")
    if surface:
        p = surface.get_actor_location()
        surface.set_actor_location(u.Vector(p.x, p.y, 425), False, True)
        scale = surface.get_actor_scale3d()
        surface.set_actor_scale3d(u.Vector(scale.x * 1.08 if scale.x < .7 else scale.x,
                                          scale.y * 1.04 if scale.y < 1.46 else scale.y, scale.z))
        water = u.load_asset("/Game/WC/Materials/M_KitchenTar")
        assert water, "Missing bath water material"
        surface.static_mesh_component.set_material(0, water)


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
