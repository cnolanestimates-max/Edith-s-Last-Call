"""Import the six indoor one-shots and the isolated reaching arm."""
import runpy
from pathlib import Path
import unreal as u

root = Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir()))
imported = runpy.run_path(str(root / 'Scripts/art/import_arrival_assets.py'))['imported']
for cue in ('whimper', 'groan', 'snicker'):
    for take in (1, 2):
        imported(root / f'SourceArt/Audio/VO/edith_{cue}_{take:02}.wav', '/Game/WC/Audio/VO')

options = u.FbxImportUI()
options.automated_import_should_detect_type = False
options.import_as_skeletal = options.import_mesh = True
options.mesh_type_to_import = u.FBXImportType.FBXIT_SKELETAL_MESH
options.import_animations = options.import_materials = options.import_textures = False
options.create_physics_asset = False
options.skeletal_mesh_import_data.set_editor_property('import_morph_targets', True)
options.skeletal_mesh_import_data.set_editor_property('normal_import_method', u.FBXNormalImportMethod.FBXNIM_COMPUTE_NORMALS)
arm = imported(root / 'SourceArt/Her/export/SK_BedArm.fbx', '/Game/WC/Her', options)
print("Bed arm morphs", arm.get_all_morph_target_names())
assert 'Grip' in [str(n) for n in arm.get_all_morph_target_names()]
