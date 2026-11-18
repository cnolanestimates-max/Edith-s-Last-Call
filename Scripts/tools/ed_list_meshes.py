import unreal
reg = unreal.AssetRegistryHelpers.get_asset_registry()
out = []
seen_dirs = {}
for root in ('/Game',):
    for a in reg.get_assets_by_path(root, recursive=True):
        p = str(a.package_name)
        if p.startswith(('/Game/WC', '/Game/HorrorHouseKit', '/Game/Megaplant_Library')) or p.startswith('/Game/Fab/Urban') or p.startswith('/Game/Fab/Blood') or p.startswith('/Game/Fab/Broken') or p.startswith('/Game/Fab/Damaged') or p.startswith('/Game/Fab/Dusty') or p.startswith('/Game/Fab/Old_') or p.startswith('/Game/Fab/Stained'):
            continue
        c = str(a.asset_class_path.asset_name)
        if c == 'StaticMesh':
            o = a.get_asset()
            b = o.get_bounding_box()
            out.append('%s  [%d %d %d]..[%d %d %d]' % (p, b.min.x, b.min.y, b.min.z, b.max.x, b.max.y, b.max.z))
        elif c in ('SkeletalMesh', 'Blueprint', 'World'):
            out.append(c + ' ' + p)
result = '\n'.join(out)
