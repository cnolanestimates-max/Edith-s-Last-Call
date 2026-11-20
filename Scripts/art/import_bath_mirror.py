"""Build the aged silver glass material used on the original mirror's glass slot."""
from pathlib import Path
import runpy
import unreal as u


def build(glass_only=False):
    root=Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir()))
    lib=runpy.run_path(str(root/'Scripts/art/import_arrival_assets.py'))
    m=lib['new_material']('M_BathMirror')
    m.set_editor_property('shading_model',u.MaterialShadingModel.MSM_UNLIT)
    node, custom, edit=lib['node'],lib['custom'],u.MaterialEditingLibrary
    pos=node(m,u.MaterialExpressionWorldPosition,-760,0)
    uv=custom(m,[('P',pos)],'return float2(.5+(P.y+370)/260., .5-(P.z-185.8)/177.6);',u.CustomMaterialOutputType.CMOT_FLOAT2)
    tex=node(m,u.MaterialExpressionTextureSampleParameter2D,-100,50)
    tex.set_editor_property('parameter_name','Reflect')
    path='/Game/WC/Materials/RT_BathMirror'
    target=u.EditorAssetLibrary.load_asset(path) if u.EditorAssetLibrary.does_asset_exist(path) else None
    if not target:
        target=u.AssetToolsHelpers.get_asset_tools().create_asset('RT_BathMirror','/Game/WC/Materials',
            u.TextureRenderTarget2D,u.TextureRenderTargetFactoryNew())
    target.set_editor_property('size_x',640)
    target.set_editor_property('size_y',440)
    target.set_editor_property('render_target_format',u.TextureRenderTargetFormat.RTF_RGBA16F)
    assert u.EditorAssetLibrary.save_loaded_asset(target,False)
    tex.set_editor_property('texture',target)
    tex.set_editor_property('sampler_type',u.MaterialSamplerType.SAMPLERTYPE_LINEAR_COLOR)
    assert edit.connect_material_expressions(uv,'',tex,'Coordinates')
    out=custom(m,[('C',tex),('UV',uv)],"""
float e=min(min(UV.x,1-UV.x),min(UV.y,1-UV.y));
float grain=frac(sin(dot(floor(UV*float2(1100,740)),float2(41.23,27.713)))*4563.72);
float silver=smoothstep(.003,.024+.011*grain,e);
return C.rgb*float3(.91,.96,.92)*lerp(.38,1.,silver)+float3(.009,.012,.010)*(1.-silver)*grain;
""",u.CustomMaterialOutputType.CMOT_FLOAT3)
    assert edit.connect_material_property(out,'',u.MaterialProperty.MP_EMISSIVE_COLOR)
    lib['finish'](m)
    if glass_only: return
    cracks=lib['new_material']('M_MirrorCracksRemoved')
    cracks.set_editor_property('blend_mode',u.BlendMode.BLEND_MASKED)
    zero=node(cracks,u.MaterialExpressionConstant,-150,0)
    assert edit.connect_material_property(zero,'',u.MaterialProperty.MP_OPACITY_MASK)
    lib['finish'](cracks)


if __name__=='__main__':
    build()
