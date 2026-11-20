"""Replace the centre hall bulb at its existing ceiling rose with one articulated pendant."""
import unreal as u


def wire_switch():
    actors = u.get_editor_subsystem(u.EditorActorSubsystem)
    by_label = {a.get_actor_label(): a for a in actors.get_all_level_actors()}
    # Match the existing wall hardware and interaction volume. Both plates face into the hall.
    for label in ('SwitchPlate', 'SwitchNub', 'Usable_sw'):
        source = by_label[label + '_uphall']
        name = label + '_pendant'
        pos = source.get_actor_location() + u.Vector(212, 0, -350)
        part = by_label.get(name)
        if not part:
            part = actors.spawn_actor_from_class(source.get_class(), pos, source.get_actor_rotation())
            part.set_actor_label(name)
        part.set_actor_location(pos, False, False)
        part.set_folder_path('House/Lights/MainHall')
        if label == 'Usable_sw':
            part.set_editor_property('wc_id', u.Name('sw_pendant'))
            part.set_editor_property('prompt', 'Hall pendant switch')
            for prop in ('grab_extent', 'grab_offset'):
                part.set_editor_property(prop, source.get_editor_property(prop))
        else:
            mesh = part.static_mesh_component
            mesh.set_static_mesh(source.static_mesh_component.static_mesh)
            mesh.set_material(0, source.static_mesh_component.get_material(0))
            mesh.set_collision_profile_name('NoCollision')
            mesh.set_editor_property('lighting_channels', source.static_mesh_component.get_editor_property('lighting_channels'))
            part.set_actor_scale3d(source.get_actor_scale3d())
    by_label['HallPendantBeam'].set_editor_property('tags', ['RoomLight', 'Room_pendant', 'HallPendantBeam'])


def dress():
    actors=u.get_editor_subsystem(u.EditorActorSubsystem)
    items=list(actors.get_all_level_actors())
    for a in items:
        p=a.get_actor_location()
        if 1198<p.x<1202 and 28<p.y<32 and 240<p.z<326 and a.get_actor_label() in (
                'Cord_hall','Socket_hall','BulbOff_hall','BulbOn_hall','RoomLight_hall'):
            actors.destroy_actor(a)
    def part(label,cls,pos):
        a=next((a for a in items if a.get_actor_label()==label),None)
        if not a:
            a=actors.spawn_actor_from_class(cls,u.Vector(*pos))
            a.set_actor_label(label)
        a.set_folder_path('House/Lights/MainHall')
        return a
    pivot=u.Vector(1200,30,327)
    shade=part('HarrowHallPendant',u.StaticMeshActor,pivot.to_tuple())
    mesh=shade.static_mesh_component
    mesh.set_mobility(u.ComponentMobility.MOVABLE)
    mesh.set_static_mesh(u.load_asset('/Game/WC/Props/HouseDetails/SM_HallPendant'))
    mesh.set_collision_profile_name('NoCollision')
    shade.set_actor_location(pivot,False,False)
    shade.set_editor_property('tags',['HallPendant'])
    rose=part('HallPendantRose',u.StaticMeshActor,(1200,30,326.5))
    rose.static_mesh_component.set_static_mesh(u.load_asset('/Engine/BasicShapes/Cylinder'))
    rose.static_mesh_component.set_material(0,u.load_asset('/Game/WC/Materials/M_PhoneBrass'))
    rose.static_mesh_component.set_collision_profile_name('NoCollision')
    rose.set_actor_scale3d(u.Vector(.19,.19,.023))
    # The moving beam has its own switch on the hall side of the kitchen wall.
    light=part('HallPendantBeam',u.SpotLight,(1200,30,225))
    c=light.light_component
    c.set_mobility(u.ComponentMobility.MOVABLE)
    c.set_editor_property('intensity_units',u.LightUnits.LUMENS)
    c.set_intensity(6100.)
    c.set_light_color(u.LinearColor(1,.63,.30,1))
    c.set_attenuation_radius(590.)
    c.set_inner_cone_angle(25.)
    c.set_outer_cone_angle(47.)
    c.set_editor_property('source_radius',2.5)
    c.set_cast_shadows(True)
    channels=u.LightingChannels()
    channels.set_editor_property('channel0',True)
    channels.set_editor_property('channel1',True)
    c.set_editor_property('lighting_channels',channels)
    c.set_editor_property('volumetric_scattering_intensity',.35)
    light.set_actor_location(u.Vector(1200,30,225),False,False)
    light.set_actor_rotation(u.Rotator(pitch=-68,yaw=-90),False)
    light.attach_to_actor(shade,'',u.AttachmentRule.KEEP_WORLD,u.AttachmentRule.KEEP_WORLD,u.AttachmentRule.KEEP_WORLD,False)
    wire_switch()
