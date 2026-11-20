"""Place the bedroom screwdriver and jewelry box, and clear the kitchen drawing's spot."""
import unreal as u


def dress():
    actors = u.get_editor_subsystem(u.EditorActorSubsystem)
    all_actors = actors.get_all_level_actors()
    named = {a.get_actor_label(): a for a in all_actors}
    bedside = next(a for a in all_actors if a.get_actor_label().startswith('SM_Table_Small_01a') and
                   (a.get_actor_location() - u.Vector(700,300,350)).length() < 4)
    stand = named.get('MasterEntryTable') or actors.spawn_actor_from_class(u.StaticMeshActor,u.Vector(210,392,350),u.Rotator())
    source, target = bedside.static_mesh_component, stand.static_mesh_component
    target.set_static_mesh(source.static_mesh)
    for i,mat in enumerate(source.get_materials()): target.set_material(i,mat)
    target.set_collision_profile_name(source.get_collision_profile_name())
    target.set_editor_property('lighting_channels',source.get_editor_property('lighting_channels'))
    stand.set_actor_scale3d(bedside.get_actor_scale3d())
    stand.set_folder_path(bedside.get_folder_path())
    stand.set_actor_label('MasterEntryTable')
    stand.set_actor_location(u.Vector(210,392,350),False,True)
    def bottom_at(actor, x, y, height):
        comp = actor.get_component_by_class(u.StaticMeshComponent)
        origin, extent, _ = u.SystemLibrary.get_component_bounds(comp)
        delta = u.Vector(x-origin.x, y-origin.y, height-origin.z+extent.z)
        actor.add_actor_world_offset(delta,False,True)
    top, e = stand.get_actor_bounds(False)
    tool = named['Pickup_pick_screwdriver']
    tool.set_actor_rotation(u.Rotator(yaw=8),False)
    bottom_at(tool,211,374,top.z+e.z+.2)
    top, e = bedside.get_actor_bounds(False)
    for label in ('Usable_jewelbox','JewelBoxOpen'):
        box = named[label]
        box.set_actor_rotation(u.Rotator(yaw=25),False)
        bottom_at(box,726,315,top.z+e.z+.1)
    lid = named['JewelBoxOpen'].get_actor_location()
    eye = named['Pickup_pick_keep_eye']
    bottom_at(eye,lid.x,lid.y,lid.z+4.5)
    bottom_at(named['Note_note_box'],679,286,top.z+e.z+.15)
    # The seance table has raised detail at its centre. Its flat wooden edge is the same
    # surface that carries the mug and plates. Clear the heap off the paper's footprint.
    bones = next(a for a in all_actors if a.get_actor_label().startswith('Bones_Pile') and
                 str(a.get_folder_path()).endswith('/Kitchen'))
    bottom_at(bones,1467,531,.15)
    plates = next(a for a in all_actors if a.get_actor_label().startswith('Plates_Stack_Dusty') and
                  str(a.get_folder_path()).endswith('/Kitchen'))
    o,e,_ = u.SystemLibrary.get_component_bounds(plates.static_mesh_component)
    paper = named['Drawing_1_1262_452']
    paper.set_actor_rotation(u.Rotator(yaw=-7),False)
    bottom_at(paper,1239,460,o.z-e.z+.20)
    print('WC_REVIEW_SET',tool.get_actor_location(),paper.get_actor_location(),lid)
