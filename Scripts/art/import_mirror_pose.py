"""Import the wheelchair-only performance on Edith's existing skeleton."""
from pathlib import Path
import unreal as u


def build(name='Wheelchair'):
    root=Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir()))
    task=u.AssetImportTask()
    task.filename=str(root/f'SourceArt/Her/export/A_Her_{name}.fbx')
    task.destination_path='/Game/WC/Her'
    task.destination_name='A_Her_'+name
    task.automated=task.save=task.replace_existing=True
    opts=u.FbxImportUI()
    opts.automated_import_should_detect_type=False
    opts.import_mesh=False
    opts.import_animations=True
    opts.skeleton=u.load_asset('/Game/WC/Her/SK_Her_Skeleton')
    opts.mesh_type_to_import=u.FBXImportType.FBXIT_ANIMATION
    opts.anim_sequence_import_data.set_editor_property('animation_length',u.FBXAnimationLengthImportType.FBXALIT_EXPORTED_TIME)
    opts.anim_sequence_import_data.set_editor_property('import_bone_tracks',True)
    task.options=opts
    u.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    assert u.load_asset('/Game/WC/Her/A_Her_'+name)


if __name__=='__main__':
    for name in ('Wheelchair','Threshold'): build(name)
