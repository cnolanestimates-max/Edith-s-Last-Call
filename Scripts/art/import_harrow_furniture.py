"""Import the movable furniture pieces with the same materials as the rest of the house."""
from pathlib import Path
import math
import runpy
import unreal as u

def wardrobe_collision(mesh):
    # Interchange preserves the old convex hull on reimport. It crossed the open
    # cabinet and caught the Use ray before it could reach the laundry-ticket clue.
    boxes = []
    def box(center, size, yaw=0):
        elem = u.KBoxElem()
        elem.set_editor_property('center',u.Vector(*center))
        elem.set_editor_property('rotation',u.Rotator(0,0,yaw))
        for axis, length in zip(('x','y','z'),size):
            elem.set_editor_property(axis,length)
        boxes.append(elem)
    box((0,0,105),(52,176,208))
    angle = math.radians(92)
    for side in (-1,1):
        box((26+37*math.sin(angle),side*(86-37*math.cos(angle)),107),(4.4,74,180),side*92)
    geom = u.KAggregateGeom()
    geom.set_editor_property('box_elems',boxes)
    body = mesh.get_editor_property('body_setup')
    body.modify()
    body.set_editor_property('agg_geom',geom)

def build(only=()):
    root=Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir()))
    if not only:
        runpy.run_path(str(root/'Scripts/art/import_harrow_materials.py'))['build']()
    imported=runpy.run_path(str(root/'Scripts/art/import_arrival_assets.py'))['imported']
    dest='/Game/WC/Props/HouseDetails'
    for name in ('EdithWardrobe','DenBooks1','DenBooks2','HarrowUpright','LoosePianoKey','PianoDrawer','HarrowFridge','HarrowFridgeDoor','HarrowBath','BathWater','HarrowDesk'):
        if only and name not in only:continue
        ui=u.FbxImportUI()
        ui.import_materials=False
        ui.import_textures=False
        ui.import_as_skeletal=False
        ui.static_mesh_import_data.combine_meshes=True
        ui.static_mesh_import_data.auto_generate_collision=name not in ('EdithWardrobe','LoosePianoKey','PianoDrawer','HarrowFridgeDoor','BathWater')
        mesh=imported(root/'SourceArt/Props/HarrowFurniture'/('SM_'+name+'.fbx'),dest,ui)
        if name=='EdithWardrobe':
            wardrobe_collision(mesh)
        for i,slot in enumerate(mesh.static_materials):
            material=u.EditorAssetLibrary.load_asset('/Game/WC/Materials/'+str(slot.material_slot_name))
            assert material,slot.material_slot_name
            mesh.set_material(i,material)
        assert u.EditorAssetLibrary.save_loaded_asset(mesh,False)
    if only:return
    for name in ('piano_answer','bath_drain'):
        sound=imported(root/'SourceArt/Audio'/(name+'.wav'),'/Game/WC/Audio')
        assert u.EditorAssetLibrary.save_loaded_asset(sound,False)
