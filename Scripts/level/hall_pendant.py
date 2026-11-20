"""Replace the centre hall bulb at its existing ceiling rose with one articulated pendant."""
import unreal as u


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
    # Handled by the same room circuit as the other first-floor hall fitting.
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
    light.set_editor_property('tags',['RoomLight','Room_hall','HallPendantBeam'])
