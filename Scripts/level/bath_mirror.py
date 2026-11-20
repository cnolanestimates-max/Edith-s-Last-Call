"""Dress the downstairs bathroom for Edith's mirror encounter."""
import unreal as u


def dress():
    actors = u.get_editor_subsystem(u.EditorActorSubsystem)
    room = {a.get_actor_label(): a for a in actors.get_all_level_actors()
            if 2410 < a.get_actor_location().x < 2785 and -585 < a.get_actor_location().y < -216
            and a.get_actor_location().z < 300}
    mirror = room['Mirror_Wall_Ornate_Cracked']
    mirror.set_actor_location(u.Vector(2426, -370, 97), False, False)
    mirror.set_actor_rotation(u.Rotator(yaw=-90),False)
    mirror.set_actor_scale3d(u.Vector(2.52, 1.05, 1.21))
    mirror.set_editor_property('tags', list(set(mirror.tags) | {u.Name('BathMirror')}))
    mirror.static_mesh_component.set_material(1, u.load_asset('/Game/WC/Materials/M_BathMirror'))
    mirror.static_mesh_component.set_material(2, u.load_asset('/Game/WC/Materials/M_MirrorCracksRemoved'))
    cabinet = room['Medicine_Cabinet_Wall_Broken']
    cabinet.set_actor_location(u.Vector(2423,-542,140),False,False)
    chair = room['Wheelchair_Rusted_NoFootrest']
    chair.set_actor_location(u.Vector(2622,-346,0),False,False)
    chair.set_actor_rotation(u.Rotator(yaw=183),False)
    chair.set_editor_property('tags',list(set(chair.tags) | {u.Name('BathWheelchair')}))
    chair.static_mesh_component.set_mobility(u.ComponentMobility.MOVABLE)
    edith = next(a for a in actors.get_all_level_actors() if isinstance(a,u.WCEntity))
    poses = dict(edith.get_editor_property('anims'))
    for pose in ('Wheelchair','Threshold'):
        poses[u.Name(pose)] = u.load_asset('/Game/WC/Her/A_Her_'+pose)
        assert poses[u.Name(pose)]
    edith.set_editor_property('anims',poses)

    note = room.get('BathMirrorLetter')
    if not note:
        note = actors.spawn_actor_from_class(u.load_class(None,'/Script/WellnessCheck.WCNote'),u.Vector(2616,-346,53.7))
        note.set_actor_label('BathMirrorLetter')
    note.set_actor_location(u.Vector(2616,-346,53.7),False,False)
    note.set_folder_path('House/Interact')
    note.set_actor_rotation(u.Rotator(yaw=12),False)
    note.set_editor_property('wc_id','note_bath_mirror')
    note.set_editor_property('prompt',"Pick up Edith's note")
    note.set_editor_property('title','The folded bath note')
    note.set_editor_property('body',"Walter,\n\nThe brass key to your desk is back in First Settlers. Living room, shelf by the stairs.\n\nI can see you from here.\n\nEdith")
    note.set_editor_property('style',1)
    note.set_editor_property('grab_extent',u.Vector(17,15,9))
    note.set_editor_property('grab_offset',u.Vector(0,0,4))
    note.mesh.set_static_mesh(u.load_asset('/Game/WC/Props/HouseDetails/SM_BathLetter'))
    note.mesh.set_relative_scale3d(u.Vector(1,1,1))
    note.mesh.set_collision_profile_name('NoCollision')
    note.mesh.set_editor_property('lighting_channels',mirror.static_mesh_component.get_editor_property('lighting_channels'))
