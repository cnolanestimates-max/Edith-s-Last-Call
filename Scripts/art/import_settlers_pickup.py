"""Import the pivoted cover, hollow page block and deputy's reaching glove."""
from pathlib import Path
import runpy
import unreal as u

root=Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir()))
base=runpy.run_path(str(root/'Scripts/art/import_arrival_assets.py'))
import_asset=base['imported']
m=base['new_material']('M_SettlersLeaves')
sample=base['node'](m,u.MaterialExpressionTextureSample,-260,0)
sample.texture=import_asset(root/'SourceArt/Props/HarrowFurniture/T_SettlersLeaves.png','/Game/WC/Props/HouseDetails')
assert u.MaterialEditingLibrary.connect_material_property(sample,'RGB',u.MaterialProperty.MP_BASE_COLOR)
rough=base['node'](m,u.MaterialExpressionConstant,-260,220)
rough.set_editor_property('r',.87)
assert u.MaterialEditingLibrary.connect_material_property(rough,'',u.MaterialProperty.MP_ROUGHNESS)
base['finish'](m)
for part in ('Pages','Cover','Glove'):
    name='SM_Settlers'+part
    ui=u.FbxImportUI()
    ui.import_materials=ui.import_textures=ui.import_as_skeletal=False
    ui.static_mesh_import_data.combine_meshes=True
    ui.static_mesh_import_data.auto_generate_collision=False
    mesh=import_asset(root/'SourceArt/Props/HarrowFurniture'/(name+'.fbx'),'/Game/WC/Props/HouseDetails',ui)
    for i,slot in enumerate(mesh.static_materials):
        slot_name=str(slot.material_slot_name)
        mat=m if slot_name=='M_SettlersLeaves' else u.load_asset('/Game/HorrorHouseKit/Materials/'+slot_name)
        assert mat, slot.material_slot_name
        mesh.set_material(i,mat)
    assert u.EditorAssetLibrary.save_loaded_asset(mesh,False)
    print('WCBOOKASSET',name,mesh.get_bounding_box())
key=u.load_asset('/Game/WC/Props/SM_Item_KeyDesk')
print('WCBOOK_KEY_BOUNDS',key.get_bounding_box())
