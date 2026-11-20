"""Import the pierced-brass fitting and the sealed letter with existing house materials."""
from pathlib import Path
import runpy
import unreal as u

def build():
    root=Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir()))
    imported=runpy.run_path(str(root/'Scripts/art/import_arrival_assets.py'))['imported']
    for name in ('SM_HallPendant','SM_BathLetter'):
        ui=u.FbxImportUI()
        ui.import_materials=ui.import_textures=ui.import_as_skeletal=False
        ui.static_mesh_import_data.combine_meshes=True
        ui.static_mesh_import_data.auto_generate_collision=False
        mesh=imported(root/'SourceArt/Props/HarrowFurniture'/(name+'.fbx'),'/Game/WC/Props/HouseDetails',ui)
        for i,slot in enumerate(mesh.static_materials):
            s=str(slot.material_slot_name)
            path='/Game/HorrorHouseKit/Materials/MI_BrassOld' if s=='M_BrassOld' else '/Game/WC/Materials/'+s
            mat=u.load_asset(path)
            assert mat,path
            mesh.set_material(i,mat)
        assert u.EditorAssetLibrary.save_loaded_asset(mesh,False)
    pant=imported(root/'SourceArt/Audio/deputy_pant.wav','/Game/WC/Audio')
    pant.set_editor_property('looping',False)
    assert u.EditorAssetLibrary.save_loaded_asset(pant,False)

if __name__=='__main__':build()
