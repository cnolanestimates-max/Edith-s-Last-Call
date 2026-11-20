"""Dress Edith's working desk and seat the kitchen drawing on the clear table edge."""
import unreal as u


def bottom_at(actor, x, y, height):
    comp = actor.get_component_by_class(u.StaticMeshComponent)
    origin, extent, _ = u.SystemLibrary.get_component_bounds(comp)
    actor.add_actor_world_offset(u.Vector(x-origin.x,y-origin.y,height-origin.z+extent.z),False,True)


def fit_grab(actor, extent):
    origin, _, _ = u.SystemLibrary.get_component_bounds(actor.mesh)
    offset = actor.get_actor_transform().inverse_transform_location(origin)
    actor.set_editor_property('grab_offset',offset)
    actor.set_editor_property('grab_extent',u.Vector(*extent))


def dress():
    actors = u.get_editor_subsystem(u.EditorActorSubsystem)
    all_actors = actors.get_all_level_actors()
    named = {a.get_actor_label(): a for a in all_actors}
    bedside = next(a for a in all_actors if a.get_actor_label().startswith('SM_Table_Small_01a') and
                   (a.get_actor_location() - u.Vector(700,300,350)).length() < 4)
    if 'MasterEntryTable' in named:
        actors.destroy_actor(named['MasterEntryTable'])
    bedside.set_actor_scale3d(u.Vector(1.40,1.22,1))
    center,extent = bedside.get_actor_bounds(False)
    surface = center.z+extent.z+.1
    lamp = next(a for a in all_actors if a.get_actor_label() in ('Oil_Lamp_Broken_Unlit','EdithDeskLamp')
                and str(a.get_folder_path())=='House/Dressing/Master')
    lamp.static_mesh_component.set_static_mesh(u.EditorAssetLibrary.load_asset('/Game/HorrorHouseKit/Meshes/Lights_Ambience/SM_Desk_Lamp_Green'))
    lamp.static_mesh_component.set_editor_property('override_materials',[])
    lamp.set_actor_label('EdithDeskLamp')
    lamp.set_actor_rotation(u.Rotator(yaw=12),False)
    lamp.set_actor_scale3d(u.Vector(.63,.63,.63))
    bottom_at(lamp,739,280,surface)
    book=named['Note_note_diary1']
    book.mesh.set_relative_scale3d(u.Vector(.72,.72,.72))
    book.set_actor_rotation(u.Rotator(yaw=7),False)
    bottom_at(book,666,293,surface)
    fit_grab(book,(16,12,4))
    tool=named['Pickup_pick_screwdriver']
    tool.set_actor_rotation(u.Rotator(yaw=-6),False)
    bottom_at(tool,692,324,surface+.05)
    fit_grab(tool,(13,5,4))
    for label in ('Usable_jewelbox','JewelBoxOpen'):
        box=named[label]
        box.set_actor_rotation(u.Rotator(yaw=25),False)
        bottom_at(box,726,315,surface)
    fit_grab(named['Usable_jewelbox'],(10,10,6))
    lid = named['JewelBoxOpen'].get_actor_location()
    bottom_at(named['Pickup_pick_keep_eye'],lid.x,lid.y,lid.z+4.5)
    note=named['Note_note_box']
    note.mesh.set_relative_scale3d(u.Vector(.25,.25,.17))
    note.set_actor_rotation(u.Rotator(yaw=-10),False)
    bottom_at(note,702,282,surface+.03)
    fit_grab(note,(11,10,3))
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
