import unreal
reg = unreal.AssetRegistryHelpers.get_asset_registry()
out = []
for a in reg.get_assets_by_path('/Game/Megaplant_Library', recursive=True):
    c = str(a.asset_class_path.asset_name)
    if 'Texture' in c:
        continue
    line = c + ' ' + str(a.package_name)
    if c in ('SkeletalMesh', 'StaticMesh'):
        o = a.get_asset()
        b = o.get_bounds()
        line += ' extent=' + str((round(b.box_extent.x), round(b.box_extent.y), round(b.box_extent.z)))
        if c == 'SkeletalMesh':
            try:
                line += ' bones=' + str(len(o.skeleton.get_reference_pose().get_bone_names())) + ' mats=' + str(len(o.materials))
            except Exception as e:
                line += ' ' + str(e)[:60]
    out.append(line)
result = '\n'.join(out)
