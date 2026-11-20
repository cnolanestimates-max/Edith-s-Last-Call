"""Install the approved Company face and the two spatial voices for Ruth's door."""
from pathlib import Path
import runpy
import unreal as u

root = Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir()))
base = runpy.run_path(str(root/'Scripts/art/import_arrival_assets.py'))
lib = u.EditorAssetLibrary
edit = u.MaterialEditingLibrary
atlas = base['imported'](root/'SourceArt/TV/mask_A_or_B.png','/Game/WC/Textures/Harrow')
mat = base['new_material']('M_CompanyMask')
mat.set_editor_property('two_sided',True)
sample = base['node'](mat,u.MaterialExpressionTextureSample,-520,0)
sample.set_editor_property('texture',atlas)
assert edit.connect_material_property(sample,'RGB',u.MaterialProperty.MP_BASE_COLOR)
glow = base['node'](mat,u.MaterialExpressionMultiply,-230,220)
glow.set_editor_property('const_b',.09)
assert edit.connect_material_expressions(sample,'RGB',glow,'A')
assert edit.connect_material_property(glow,'',u.MaterialProperty.MP_EMISSIVE_COLOR)
rough = base['node'](mat,u.MaterialExpressionConstant,-215,430)
rough.set_editor_property('r',.82)
assert edit.connect_material_property(rough,'',u.MaterialProperty.MP_ROUGHNESS)
base['finish'](mat)
ui = u.FbxImportUI()
ui.import_materials = ui.import_textures = ui.import_as_skeletal = False
ui.static_mesh_import_data.auto_generate_collision = False
mesh = base['imported'](root/'SourceArt/Props/HarrowFurniture/SM_CompanyMask.fbx','/Game/WC/Props/HouseDetails',ui)
mesh.set_material(0,mat)
assert mesh.get_num_triangles(0)>4000 and lib.save_loaded_asset(mesh,False)
for name, minimum_length in (('door_weeping',12.49),('door_whispering',12.49),('door_room_scream',2.0)):
    wave = base['imported'](root/'SourceArt/Audio'/(name+'.wav'),'/Game/WC/Audio')
    wave.set_editor_property('looping',False)
    assert wave.duration>=minimum_length and lib.save_loaded_asset(wave,False)
print('CRACK_ASSETS_OK',mesh.get_num_triangles(0))
