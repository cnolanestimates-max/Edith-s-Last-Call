"""Import the movable furniture pieces with the same materials as the rest of the house."""
from pathlib import Path
import runpy
import unreal as u

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
        ui.static_mesh_import_data.auto_generate_collision=name not in ('LoosePianoKey','PianoDrawer','HarrowFridgeDoor','BathWater')
        mesh=imported(root/'SourceArt/Props/HarrowFurniture'/('SM_'+name+'.fbx'),dest,ui)
        for i,slot in enumerate(mesh.static_materials):
            material=u.EditorAssetLibrary.load_asset('/Game/WC/Materials/'+str(slot.material_slot_name))
            assert material,slot.material_slot_name
            mesh.set_material(i,material)
        assert u.EditorAssetLibrary.save_loaded_asset(mesh,False)
    if only:return
    for name in ('piano_answer','bath_drain'):
        sound=imported(root/'SourceArt/Audio'/(name+'.wav'),'/Game/WC/Audio')
        assert u.EditorAssetLibrary.save_loaded_asset(sound,False)
