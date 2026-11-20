"""Import the chassis and axle-centred wheels, keeping the existing chair's material assignments."""
from pathlib import Path
import runpy
import unreal as u

root=Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir()))
original='/Game/HorrorHouseKit/Meshes/Asylum_Hospital/SM_Wheelchair_Rusted_NoFootrest'

def export_source():
    task=u.AssetExportTask()
    task.object=u.load_asset(original)
    task.filename=str(root/'Saved/BathChairSource.fbx')
    task.automated=task.replace_identical=True
    task.prompt=False
    task.exporter=u.StaticMeshExporterFBX()
    assert u.Exporter.run_asset_export_task(task)

def build():
    imported=runpy.run_path(str(root/'Scripts/art/import_arrival_assets.py'))['imported']
    mats={slot.material_interface.get_name():slot.material_interface for slot in u.load_asset(original).static_materials}
    folder='/Game/WC/Props/HouseDetails'
    for part in ('Frame','LeftWheel','RightWheel','Caster'):
        ui=u.FbxImportUI()
        ui.import_materials=ui.import_textures=ui.import_as_skeletal=False
        ui.static_mesh_import_data.combine_meshes=True
        ui.static_mesh_import_data.auto_generate_collision=False
        mesh=imported(root/'SourceArt/Props/HarrowFurniture'/('SM_BathChair'+part+'.fbx'),folder,ui)
        for i,slot in enumerate(mesh.static_materials):
            name=str(slot.material_slot_name)
            mesh.set_material(i,mats[name])
        assert u.EditorAssetLibrary.save_loaded_asset(mesh,False)
        print('WCCHAIRPART',part,mesh.get_bounding_box())
    for sound in ('wheel_on_boards','wheel_baseboard','wheel_sidefall','wheel_axle_rub'):
        wave=imported(root/'SourceArt/Audio'/(sound+'.wav'),'/Game/WC/Audio')
        wave.set_editor_property('looping',sound=='wheel_on_boards')
        assert u.EditorAssetLibrary.save_loaded_asset(wave,False)
    print('WCCHAIR_ASSETS_READY')

if __name__=='__main__':build()
