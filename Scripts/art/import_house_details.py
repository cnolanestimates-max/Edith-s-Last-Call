"""Build the local shelf opening, pantry contents, dark fluids and clock recordings in Unreal."""
from pathlib import Path
import runpy
import unreal as u

ROOT = Path(u.Paths.convert_relative_path_to_full(u.Paths.project_dir()))
base = runpy.run_path(str(ROOT / 'Scripts/art/import_arrival_assets.py'))
assets, edit, prop = u.EditorAssetLibrary, u.MaterialEditingLibrary, u.MaterialProperty
ART = '/Game/WC/Props/HouseDetails'
MAT = '/Game/WC/Materials'
node, finish = base['node'], base['finish']


def scalar(m, value, output):
    c = node(m,u.MaterialExpressionConstant,-200,150)
    c.set_editor_property('r',value)
    assert edit.connect_material_property(c,'',output)


def surface(name, a, b, rough, opacity=None):
    m = base['new_material']('M_'+name)
    if opacity is not None:
        m.set_editor_property('blend_mode',u.BlendMode.BLEND_TRANSLUCENT)
        m.set_editor_property('translucency_lighting_mode',u.TranslucencyLightingMode.TLM_SURFACE_PER_PIXEL_LIGHTING)
    pos = node(m,u.MaterialExpressionWorldPosition,-600,-70)
    noise = """float3 p=P*.41;
float v=.50+.17*sin(p.x*1.9+sin(p.z*3.1))+.17*sin(p.z*.76+p.y+sin(p.x))+.12*sin(dot(p,float3(1.8,2.6,2.1)));
return lerp(float3(%s),float3(%s),saturate(v));""" % (','.join(map(str,a)),','.join(map(str,b)))
    col=base['custom'](m,[('P',pos)],noise,u.CustomMaterialOutputType.CMOT_FLOAT3)
    assert edit.connect_material_property(col,'',prop.MP_BASE_COLOR)
    scalar(m,rough,prop.MP_ROUGHNESS)
    if opacity is not None:scalar(m,opacity,prop.MP_OPACITY)
    finish(m)


def build_materials():
    for n,a,b,r,alpha in [
        ('BarrelSludge',(.014,.006,.003),(.088,.032,.011),.31,None),
        ('KitchenTar',(.004,.003,.002),(.027,.016,.010),.25,None),
        ('JarSediment',(.030,.014,.006),(.16,.078,.021),.62,None),
        ('PickleOchre',(.11,.05,.012),(.45,.285,.083),.41,None),
        ('PickleRust',(.11,.024,.012),(.32,.106,.045),.39,None),
        ('PicklePale',(.22,.13,.064),(.57,.455,.24),.43,None),
        ('PickleBrine',(.09,.043,.012),(.31,.181,.041),.20,.21),
        ('JarGlass',(.16,.145,.113),(.36,.33,.24),.19,.11),
        ('ShelfHidden',(0,0,0),(0,0,0),.5,0.)]:
        surface(n,a,b,r,alpha)
    for name in ['SM_PantrySpecimens','SM_PantryPreserves','SM_KitchenTar']:
        ui=u.FbxImportUI();ui.import_materials=False;ui.import_textures=False;ui.import_as_skeletal=False
        ui.static_mesh_import_data.combine_meshes=True;ui.static_mesh_import_data.auto_generate_collision=False
        mesh=base['imported'](ROOT/'SourceArt/Props'/(name+'.fbx'),ART,ui)
        for i,slot in enumerate(mesh.static_materials):
            mat=assets.load_asset(MAT+'/M_'+str(slot.material_slot_name));assert mat,slot.material_slot_name
            mesh.set_material(i,mat)
        assert assets.save_loaded_asset(mesh,False)
    for name in ['clock_single_01','clock_single_02']:
        w=base['imported'](ROOT/'SourceArt/Audio'/(name+'.wav'),'/Game/WC/Audio')
        w.set_editor_property('looping',False);assert assets.save_loaded_asset(w,False)


def build_plaster():
    surface('BrokenPlaster',(.10,.068,.032),(.27,.19,.105),.94)
    surface('ExposedLath',(.026,.014,.006),(.077,.045,.021),.84)
    ui=u.FbxImportUI()
    ui.import_materials=False
    ui.import_textures=False
    ui.import_as_skeletal=False
    ui.static_mesh_import_data.combine_meshes=True
    ui.static_mesh_import_data.auto_generate_collision=False
    mesh=base['imported'](ROOT/'SourceArt/Props/SM_BrokenPlasterEdge.fbx',ART,ui)
    for i,slot in enumerate(mesh.static_materials):
        m=assets.load_asset(MAT+'/M_'+str(slot.material_slot_name))
        assert m
        mesh.set_material(i,m)
    assert assets.save_loaded_asset(mesh,False)


def build_yard_calls():
    for i in range(1,5):
        name=f'yard_caw_{i:02}'
        wave=base['imported'](ROOT/'SourceArt/Audio'/(name+'.wav'),'/Game/WC/Audio')
        wave.set_editor_property('looping',False)
        assert assets.save_loaded_asset(wave,False)


def build_opening():
    source=assets.load_asset('/Game/HorrorHouseKit/Meshes/Mansion_Modular/SM_Wall_Wainscot_Red')
    path=ART+'/SM_StairPeepholeWall'
    wall=assets.load_asset(path) if assets.does_asset_exist(path) else assets.duplicate_asset(source.get_path_name(),path)
    geo=u.DynamicMesh();tool=u.DynamicMesh()
    _,ok=u.GeometryScript_AssetUtils.copy_mesh_from_static_mesh(source,geo,u.GeometryScriptCopyMeshFromAssetOptions(),u.GeometryScriptMeshReadLOD())
    assert ok==u.GeometryScriptOutcomePins.SUCCESS
    # Local X and Z offsets around the book's eye opening. The tool crosses both plaster faces.
    contour=runpy.run_path(str(ROOT/'Scripts/art/stair_opening.py'))['OUTLINE']
    poly=[u.Vector2D(x,-z) for x,z in reversed(contour)]
    u.GeometryScript_Primitives.append_simple_extrude_polygon(tool,u.GeometryScriptPrimitiveOptions(),u.Transform(),poly,65)
    cut=u.Transform(location=u.Vector(-48.45446,-32,154),rotation=u.Rotator(roll=90))
    u.GeometryScript_MeshBooleans.apply_mesh_boolean(geo,u.Transform(),tool,cut,u.GeometryScriptBooleanOperation.SUBTRACT,u.GeometryScriptMeshBooleanOptions())
    _,ok=u.GeometryScript_AssetUtils.copy_mesh_to_static_mesh(geo,wall,u.GeometryScriptCopyMeshToAssetOptions(),u.GeometryScriptMeshWriteLOD())
    assert ok==u.GeometryScriptOutcomePins.SUCCESS
    wall.get_editor_property('body_setup').set_editor_property('collision_trace_flag',u.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
    assert assets.save_loaded_asset(wall,False)
    print('WC_OPENING_BUILT',wall.get_path_name())


def build_phone():
    folder=ROOT/'SourceArt/Phone'
    atlas=base['imported'](folder/'T_PhonePatina.png',ART)
    m=base['new_material']('M_PhoneBakelite')
    tex=node(m,u.MaterialExpressionTextureSample,-650,-100)
    tex.set_editor_property('texture',atlas)
    col=base['custom'](m,[('Patina',tex)],"""
float f=saturate(dot(Patina,float3(.28,.57,.15)));
return lerp(float3(.0025,.0022,.0019),float3(.023,.019,.015),f);
""",u.CustomMaterialOutputType.CMOT_FLOAT3)
    assert edit.connect_material_property(col,'',prop.MP_BASE_COLOR)
    rough=base['custom'](m,[('Patina',tex)],'return .33+.15*saturate(Patina.r);',u.CustomMaterialOutputType.CMOT_FLOAT1)
    assert edit.connect_material_property(rough,'',prop.MP_ROUGHNESS)
    scalar(m,.19,prop.MP_SPECULAR)
    finish(m)
    for n,a,b,r in [
        ('PhoneRubber',(.009,.008,.007),(.023,.020,.016),.62),
        ('PhoneIvory',(.43,.30,.155),(.69,.53,.32),.43),
        ('PhoneBrass',(.20,.125,.056),(.40,.30,.17),.32),
        ('PhoneDial',(.030,.026,.021),(.072,.061,.048),.33),
        ('PhonePaper',(.38,.27,.15),(.58,.46,.28),.74)]:
        surface(n,a,b,r)
    ui=u.FbxImportUI()
    ui.import_materials=False
    ui.import_textures=False
    ui.import_as_skeletal=False
    ui.static_mesh_import_data.combine_meshes=True
    ui.static_mesh_import_data.auto_generate_collision=True
    mesh=base['imported'](folder/'SM_HarrowTelephone.fbx',ART,ui)
    for i,slot in enumerate(mesh.static_materials):
        mat=assets.load_asset(MAT+'/M_'+str(slot.material_slot_name))
        assert mat,slot.material_slot_name
        mesh.set_material(i,mat)
    assert assets.save_loaded_asset(mesh,False)
    print('WC_PHONE_IMPORTED',mesh.get_bounding_box())



if __name__=='__main__':
    build_opening()
    build_materials()
    build_phone()
    build_yard_calls()
    build_plaster()
