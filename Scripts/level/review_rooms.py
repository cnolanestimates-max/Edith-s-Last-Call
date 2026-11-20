"""Apply the room-by-room prop review to a built House level."""
import runpy
from pathlib import Path
import unreal as u

ART='/Game/WC/Props/HouseDetails/'
MAT='/Game/WC/Materials/M_'


def dress():
    subsystem=u.get_editor_subsystem(u.EditorActorSubsystem)
    actors=list(subsystem.get_all_level_actors())
    labels={a.get_actor_label():a for a in actors}
    placement=runpy.run_path(str(Path(__file__).with_name('playtest_props.py')))
    bottom_at,fit_grab=placement['bottom_at'],placement['fit_grab']

    def find(label,folder):
        return next(a for a in actors if a.get_actor_label()==label and str(a.get_folder_path())==folder)

    def asset(path):
        obj=u.EditorAssetLibrary.load_asset(path)
        if not obj:raise ValueError(path)
        return obj

    def detail(name,mesh,owner):
        loc,rot=owner.get_actor_location(),owner.get_actor_rotation()
        a=labels.get(name) or subsystem.spawn_actor_from_class(u.StaticMeshActor,loc,rot)
        a.set_actor_label(name)
        a.set_folder_path(owner.get_folder_path())
        a.set_actor_transform(owner.get_actor_transform(),False,True)
        a.static_mesh_component.set_static_mesh(asset(ART+mesh))
        a.static_mesh_component.set_collision_enabled(u.CollisionEnabled.NO_COLLISION)
        return a

    for a in actors:
        name,folder=a.get_actor_label(),str(a.get_folder_path())
        loc=a.get_actor_location()
        sick=2000<loc.x<2800 and 200<loc.y<600 and -10<loc.z<345
        if ((name=='Bottles_Empty_Group' and folder.endswith('/Kitchen')) or
            (name=='Wheelchair_Tipped' and folder=='House/Dressing/RearHall') or name=='Look_hall_wheelchair' or
            (name.startswith('BookHole_') and folder=='House/Watchers') or
            (folder=='House/Decay/Soft' and name.startswith('Urban_') and
             any((loc-u.Vector(*p)).length()<2 for p in [(640,300,350),(560,420,412)])) or
            (sick and ((folder=='House/Decay/Holes' and name.startswith(('Plank','Urban_Ruin_Scatter_Debris_Wood','Debris_Plaster_Pile'))) or
                       (folder=='House/Decay/Ceilings' and name=='Ceiling_Panel_4x4_Broken') or
                       (folder=='House/Decay/Sickroom' and name.startswith('Urban_Shanty_Town_Blanket'))))):
            subsystem.destroy_actor(a)

    barrel=find('Barrel_Tipped_Spilled','House/Shell/Exterior/BackYard')
    barrel.static_mesh_component.set_material(2,asset(MAT+'BarrelSludge'))
    table=find('Table_Seance_Round','House/Dressing/Kitchen')
    hidden=asset(MAT+'ShelfHidden')
    table.static_mesh_component.set_material(6,hidden)
    tar=detail('KitchenTableTar','SM_KitchenTar',table)
    tar.set_actor_location(u.Vector(1250,420,72.8),False,True)
    for shelf_name, mesh_name, glass, filling in [
        ('Specimen_Jar_Shelf','SM_PantrySpecimens',(1,4),(3,5)),
        ('Jar_Herbs_Shelf','SM_PantryPreserves',(1,),(2,4,5,6))]:
        shelf=find(shelf_name,'House/Dressing/Pantry')
        for slot in glass:shelf.static_mesh_component.set_material(slot,asset(MAT+'JarGlass'))
        for slot in filling:shelf.static_mesh_component.set_material(slot,hidden)
        detail(mesh_name[3:],mesh_name,shelf)

    wall=next(a for a in actors if a.get_actor_label()=='Wall_Wainscot_Red' and
              (a.get_actor_location()-u.Vector(600,-200,0)).length()<2)
    wall.static_mesh_component.set_static_mesh(asset(ART+'SM_StairPeepholeWall'))
    edge=detail('StairPlasterEdge','SM_BrokenPlasterEdge',wall)
    edge.set_actor_location(u.Vector(551.54554,-200,154),False,True)
    clock=find('Clock_Grandfather','House/Dressing/Hall')
    clock.tags=list(dict.fromkeys([*clock.tags,u.Name('HallClockSource')]))
    for name,tag in [('Crow_Perched_Post','CrowGate'),('Crows_On_Branch','CrowBranch')]:
        perch=find(name,'House/Shell/Exterior/Yard')
        perch.tags=list(dict.fromkeys([*perch.tags,u.Name(tag)]))
    den=find('SM_Table_Small_01a','House/Dressing/Den')
    o,e=den.get_actor_bounds(False)
    top=o.z+e.z
    bottom_at(labels['DenRadio'],1880,-550,top+.1)
    paper=labels['Note_note_doctor']
    paper.set_actor_rotation(u.Rotator(yaw=-2),False)
    paper.mesh.set_relative_scale3d(u.Vector(.34,.34,.13))
    bottom_at(paper,1919,-536,top+.12)
    fit_grab(paper,(15,15,3))
    phone=labels['Usable_phone']
    phone.mesh.set_static_mesh(asset(ART+'SM_HarrowTelephone'))
    phone.mesh.set_editor_property('override_materials',[])
    phone.mesh.set_relative_scale3d(u.Vector(1,1,1))
    phone.set_actor_rotation(u.Rotator(yaw=180),False)
    desk=next(a for a in actors if a.get_actor_label().startswith('SM_Table_Small_01a') and
              str(a.get_folder_path())=='House/Dressing/Kitchen' and abs(a.get_actor_location().x-868)<2)
    desk.set_actor_location(u.Vector(868,502,0),False,True)
    o,e=desk.get_actor_bounds(False)
    bottom_at(phone,862,500,o.z+e.z+.04)
    fit_grab(phone,(13,9,8))
    labels['PhonePoint'].set_actor_location(u.Vector(862,502,o.z+e.z+14),False,True)
    print('WC_ROOM_REVIEW_APPLIED')
