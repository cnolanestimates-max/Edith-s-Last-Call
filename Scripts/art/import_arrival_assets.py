"""Import the ground-level yard sound, bin and particle assets in Unreal Editor."""
from pathlib import Path
import unreal as u

root = Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir()))
assets = u.EditorAssetLibrary
tools = u.AssetToolsHelpers.get_asset_tools()
edit = u.MaterialEditingLibrary
folder = '/Game/WC/Materials'
prop = u.MaterialProperty

def imported(file, destination, options=None):
    task = u.AssetImportTask()
    task.filename, task.destination_path = str(file), destination
    task.automated = task.replace_existing = task.save = True
    if options: task.options = options
    tools.import_asset_tasks([task])
    obj = assets.load_asset(destination + '/' + file.stem)
    if not obj: raise RuntimeError(str(file))
    return obj

def new_material(name):
    path = folder+'/'+name
    m = assets.load_asset(path) if assets.does_asset_exist(path) else tools.create_asset(name,folder,u.Material,u.MaterialFactoryNew())
    edit.delete_all_material_expressions(m)
    return m

def node(m, cls, x, y): return edit.create_material_expression(m, cls, x, y)
def color(m, rgb):
    c=node(m,u.MaterialExpressionConstant3Vector,-300,-140)
    c.set_editor_property('constant',u.LinearColor(*rgb,1))
    assert edit.connect_material_property(c,'',prop.MP_BASE_COLOR)
def custom(m, sources, code, output):
    n=node(m,u.MaterialExpressionCustom,-120,160)
    n.set_editor_property('code',code)
    n.set_editor_property('output_type',output)
    inputs=[]
    for pin, src in sources:
        i=u.CustomInput(); i.set_editor_property('input_name',pin); inputs.append(i)
    n.set_editor_property('inputs',inputs)
    for pin,src in sources: assert edit.connect_material_expressions(src,'',n,pin)
    return n
def finish(m):
    edit.recompile_material(m)
    assert assets.save_loaded_asset(m,False)
def build_dust():
    m=new_material('M_DriftingDust')
    m.set_editor_property('blend_mode',u.BlendMode.BLEND_TRANSLUCENT)
    m.set_editor_property('two_sided',True)
    edit.set_material_usage(m,u.MaterialUsage.MATUSAGE_INSTANCED_STATIC_MESHES)
    color(m,(.68,.59,.43))
    glow=node(m,u.MaterialExpressionConstant3Vector,-380,-290)
    glow.set_editor_property('constant',u.LinearColor(.075,.064,.047,1))
    assert edit.connect_material_property(glow,'',prop.MP_EMISSIVE_COLOR)
    uv=node(m,u.MaterialExpressionTextureCoordinate,-620,60)
    rand=node(m,u.MaterialExpressionPerInstanceRandom,-620,160)
    depth=node(m,u.MaterialExpressionPixelDepth,-620,270)
    opacity=custom(m,[('UV',uv),('Seed',rand),('Dist',depth)],"""
float2 p=UV*2-1;
p.x += 0.16*sin(4.1*p.y + Seed*6.28);
float shape=length(p*float2(1.1+Seed*1.4,1.15));
return (1-smoothstep(.03,.94,shape))*(.35+.48*Seed)*smoothstep(22.,55.,Dist);
""",u.CustomMaterialOutputType.CMOT_FLOAT1)
    assert edit.connect_material_property(opacity,'',prop.MP_OPACITY)
    finish(m)

def build():
    for name in ['amb_yard','amb_dawn','trash_crash']:
        s=imported(root/'SourceArt/Audio'/(name+'.wav'),'/Game/WC/Audio')
        s.set_editor_property('looping',name.startswith('amb_'))
        assert assets.save_loaded_asset(s,False)
    for name in ['musicbox','phone_ring','radio_static_loop','her_breath_loop','flies_buzz']:
        s=assets.load_asset('/Game/WC/Audio/'+name) if assets.does_asset_exist('/Game/WC/Audio/'+name) else None
        if s and s.get_editor_property('looping'):
            s.set_editor_property('looping',False)
            assert assets.save_loaded_asset(s,False)
    ui=u.FbxImportUI()
    ui.import_materials=False; ui.import_textures=False; ui.import_as_skeletal=False
    ui.static_mesh_import_data.combine_meshes=True
    fly=imported(root/'SourceArt/Props/SM_HouseFly.fbx','/Game/WC/Props',ui)
    shades={'FlyBody':(.030,.024,.018),'FlyWing':(.28,.26,.21),'FlyEye':(.090,.024,.018)}
    for idx,slot in enumerate(fly.static_materials):
        key=str(slot.material_slot_name)
        if key not in shades: raise RuntimeError('Unexpected fly material '+key)
        m=new_material('M_'+key); color(m,shades[key])
        edit.set_material_usage(m,u.MaterialUsage.MATUSAGE_INSTANCED_STATIC_MESHES)
        finish(m); fly.set_material(idx,m)
    assert len(fly.static_materials)==3
    assert assets.save_loaded_asset(fly,False)
    build_dust()
    m=new_material('M_YardFootpath')
    m.set_editor_property('blend_mode',u.BlendMode.BLEND_MASKED)
    uv=node(m,u.MaterialExpressionTextureCoordinate,-670,0)
    pos=node(m,u.MaterialExpressionWorldPosition,-670,150)
    tex=node(m,u.MaterialExpressionTextureObject,-670,320)
    tex.set_editor_property('texture',assets.load_asset('/Game/WC/Textures/Gravel/BaseColor'))
    shade=custom(m,[('Pos',pos),('Gravel',tex)],"""
float3 c=Texture2DSample(Gravel,GravelSampler,Pos.xy/120.).rgb;
return c*float3(.82,.74,.62)+float3(.052,.044,.033);
""",u.CustomMaterialOutputType.CMOT_FLOAT3)
    mask=custom(m,[('UV',uv),('Pos',pos),('Gravel',tex)],"""
float grain=Texture2DSample(Gravel,GravelSampler,Pos.xy/100.).r;
float wobble=.035*sin(Pos.x*.035+Pos.y*.017)+.025*sin(Pos.y*.091);
return saturate((min(UV.y,1.-UV.y)+wobble+.18*grain-.095)*20.);
""",u.CustomMaterialOutputType.CMOT_FLOAT1)
    assert edit.connect_material_property(shade,'',prop.MP_BASE_COLOR)
    assert edit.connect_material_property(mask,'',prop.MP_OPACITY_MASK)
    finish(m)
    print('WC_ARRIVAL_ASSETS_READY',fly.get_bounding_box())
if __name__=='__main__': build()
