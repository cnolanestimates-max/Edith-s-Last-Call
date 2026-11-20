"""Import the authored print, enamel, label and food textures as physically based materials."""
from pathlib import Path
import runpy
import unreal as u
def build(only=()):
    root=Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir()))
    base=runpy.run_path(str(root/'Scripts/art/import_arrival_assets.py'))
    textures='/Game/WC/Textures/Harrow'
    lib=u.EditorAssetLibrary;edit=u.MaterialEditingLibrary;prop=u.MaterialProperty
    def texture(name,usage='color'):
        tex=base['imported'](root/'SourceArt/Textures/Harrow'/(('T_'+name if name.startswith('Dress') else 'T_Harrow'+name)+'.png'),textures)
        if usage!='color':
            tex.set_editor_property('srgb',False)
            tex.set_editor_property('compression_settings',u.TextureCompressionSettings.TC_NORMALMAP if usage=='normal' else u.TextureCompressionSettings.TC_MASKS)
        assert lib.save_loaded_asset(tex,False)
        return tex
    weave=None
    for name in ('Calico','Burgundy','Brocade','Gingham','Walnut','Burr','Enamel','Fruit','Wrapper','Preserve','PearLabel','PlumLabel','DressDogwood','DressSunday','DressWedding','DressPoppy'):
        if only and name not in only:continue
        cloth=name in ('Calico','Burgundy','Brocade','Gingham')
        if cloth and weave is None:weave=texture('Weave_N','normal')
        label=name.endswith('Label')
        m=base['new_material'](('M_' if name.startswith('Dress') else 'M_Harrow')+name)
        m.set_editor_property('two_sided',cloth or label)
        def sample(tex,typ,output,y,channel):
            node=base['node'](m,u.MaterialExpressionTextureSample,-320,y)
            node.set_editor_property('texture',tex);node.set_editor_property('sampler_type',typ)
            assert edit.connect_material_property(node,channel,output)
        sample(texture(name),u.MaterialSamplerType.SAMPLERTYPE_COLOR,prop.MP_BASE_COLOR,0,'RGB')
        if not label:
            sample(weave if cloth else texture(name+'_N','normal'),u.MaterialSamplerType.SAMPLERTYPE_NORMAL,prop.MP_NORMAL,260,'RGB')
        if cloth or label:
            val=base['node'](m,u.MaterialExpressionConstant,-320,520)
            val.set_editor_property('r',.81 if cloth else .68)
            assert edit.connect_material_property(val,'',prop.MP_ROUGHNESS)
        else:sample(texture(name+'_R','rough'),u.MaterialSamplerType.SAMPLERTYPE_MASKS,prop.MP_ROUGHNESS,520,'R')
        base['finish'](m)
