"""Add the Harrow house's music alcove, scullery and upstairs shortcuts."""
import json
from pathlib import Path

import unreal as u


KIT = "/Game/HorrorHouseKit"
SHELL = "House/Shell/Connections"
EXTERIOR = "House/Shell/Exterior/Connections"
PROPS = "House/Dressing/Connections"
PLASTER = "MI_MegaPlaster"
WM = "MI_WoodTrim"
NOTE_IDS = ("music_lesson", "scullery_service", "linen_checkout", "boxroom_patterns")


def dress():
    sub = u.get_editor_subsystem(u.EditorActorSubsystem)
    actors = list(sub.get_all_level_actors())
    by_name = {a.get_actor_label(): a for a in actors}
    V, R = u.Vector, u.Rotator
    notes = json.loads(Path(__file__).with_name("notes.json").read_text(encoding="utf8"))

    def apply_note(a, id):
        writing = notes[id]
        for field in ("title", "body", "style"):
            a.set_editor_property(field, writing[field])
        a.set_editor_property("prompt", "Read " + writing["title"].lower())
        a.set_editor_property("grab_extent", V(9, 6, 5))
        a.get_editor_property("mesh").set_relative_scale3d(V(.30, .30, .30))

    by_name["RearWing_CornerLight"].light_component.set_intensity(1050.)
    # Keep the Fab couch in the sitting room and clear the new doorway behind it.
    couch = by_name.get("Urban_Shanty_Town_Couch_Fabric_Worn")
    if couch:
        pos = couch.get_actor_location()
        couch.set_actor_location(V(pos.x, -365., pos.z), False, True)
    if "Connections_MusicFloorWest" in by_name:
        if "Look_boxroom_patterns" in by_name:
            patterns = by_name["Look_boxroom_patterns"]
            patterns.set_editor_property("wc_id", u.Name("boxroom_pattern_stack"))
            patterns.set_actor_label("Look_boxroom_pattern_stack")
        for id in NOTE_IDS:
            apply_note(by_name["Note_" + id], id)
        by_name["Connections_Metronome"].set_actor_rotation(R(yaw=0.), False)
        return

    load = u.EditorAssetLibrary.load_asset
    cube = load("/Engine/BasicShapes/Cube.Cube")
    oldwest = "/Game/OldWest/VOL1/Meshes"
    polish = "/Game/WC/Props/Polish"
    paths = {
        str(a.asset_name): str(a.package_name)
        for a in u.AssetRegistryHelpers.get_asset_registry().get_assets_by_path(KIT + "/Meshes", recursive=True)
    }
    overrides = json.loads(Path(__file__).with_name("overrides.json").read_text(encoding="utf8"))
    channels = u.LightingChannels()
    channels.set_editor_property("channel0", True)
    channels.set_editor_property("channel1", True)

    def asset(model):
        path = model if model.startswith("/") else paths["SM_" + model]
        result = load(path)
        assert isinstance(result,u.StaticMesh), path
        return result

    def wc_mat(name):
        root, label = (KIT, name[4:]) if name.startswith("KIT:") else ("/Game/WC", name)
        return load(f"{root}/Materials/{label}")

    def set_mesh(c, model, indoors=True, material=None, collide=True):
        c.set_static_mesh(model)
        c.set_collision_profile_name("BlockAll" if collide else "NoCollision")
        if indoors:
            c.set_editor_property("lighting_channels", channels)
        if material:
            c.set_material(0, wc_mat(material))
        elif model.get_path_name().startswith(KIT):
            for i, slot in enumerate(c.get_material_slot_names()):
                replacement = overrides.get(str(slot))
                if replacement:
                    c.set_material(i, wc_mat(replacement))

    def solid(name, bounds, mat, folder=SHELL, collide=True, pitch=0.):
        x0,x1,y0,y1,z0,z1 = bounds
        a = sub.spawn_actor_from_class(u.StaticMeshActor, V((x0+x1)/2,(y0+y1)/2,(z0+z1)/2), R(pitch=pitch))
        a.set_actor_label("Connections_" + name)
        a.set_folder_path(folder)
        set_mesh(a.static_mesh_component, cube, folder != EXTERIOR, mat, collide)
        a.set_actor_scale3d(V((x1-x0)/100,(y1-y0)/100,(z1-z0)/100))
        return a

    def prop(name, model, p, room, yaw=0, collide=True, height=None, snap=True):
        a = sub.spawn_actor_from_class(u.StaticMeshActor, V(*p), R(yaw=yaw))
        a.set_actor_label("Connections_" + name)
        a.set_folder_path(PROPS + "/" + room)
        set_mesh(a.static_mesh_component, asset(model), collide=collide)
        center, ext = a.get_actor_bounds(False)
        if height:
            ratio = height / (ext.z * 2)
            a.set_actor_scale3d(V(ratio,ratio,ratio))
            center, ext = a.get_actor_bounds(False)
        if snap:
            pos = a.get_actor_location()
            a.set_actor_location(pos + V(p[0]-center.x,p[1]-center.y,p[2]-(center.z-ext.z)),False,True)
        return a

    def ceiling(name, p, strength, rgb, radius):
        a = sub.spawn_actor_from_class(u.PointLight, V(*p))
        a.set_actor_label("Connections_" + name)
        a.set_folder_path("House/Lights/Connections")
        c = a.light_component
        c.set_mobility(u.ComponentMobility.MOVABLE)
        c.set_editor_property("intensity_units", u.LightUnits.LUMENS)
        c.set_intensity(strength)
        c.set_attenuation_radius(radius)
        c.set_light_color(u.LinearColor(*rgb, 1))
        c.set_cast_shadows(True)
        c.set_editor_property("source_radius", 5.)
        c.set_editor_property("volumetric_scattering_intensity", .11)

    def match(label,x,y,z):
        candidates = [a for a in actors if a.get_actor_label()==label
                      and (a.get_actor_location()-V(x,y,z)).length()<1.]
        assert len(candidates)==1,(label,x,y,z,len(candidates))
        return candidates[0]

    def shift(a,dx,dy):
        a.set_actor_location(a.get_actor_location()+V(dx,dy,0),False,True)

    def relocate_window(x,y,new_x,new_y,moon):
        side = 1 if y>0 else -1
        dx,dy = new_x-x,new_y-y
        for a in (match("Wall_Window",x,y,0),match("Wall_Exterior_Siding_Window",x,y+side*36,0),
                  match("Window_Boarded",x,y-side*4,95)):
            shift(a,dx,dy)
        old = f"_{x}_{y}_0"
        for a in actors:
            if str(a.get_folder_path())=="House/Shell/Exterior/Windows" and old in a.get_actor_label():
                shift(a,dx,dy)
        for label in (moon+"_moon",moon+"_dawn"):
            if label in by_name:
                shift(by_name[label],dx,dy)

    def portal(name, axis, fixed, lo, hi, opening, z, thickness=38.):
        start,end = opening-56.5,opening+56.5
        def fill(suffix,a,b,bottom,top,material=PLASTER,width=thickness):
            if b-a < .04:
                return
            q,r=fixed-width/2,fixed+width/2
            dims=(a,b,q,r,bottom,top) if axis=="x" else (q,r,a,b,bottom,top)
            solid(name+suffix,dims,material)
        fill("_Before",lo,start,z,z+330)
        fill("_After",end,hi,z,z+330)
        fill("_Lintel",start,end,z+219,z+330)
        fill("_TrimLeft",start-4,start,z,z+223,WM,thickness+6)
        fill("_TrimRight",end,end+4,z,z+223,WM,thickness+6)
        fill("_TrimHead",start,end,z+219,z+224,WM,thickness+6)
        fill("_BaseLeft",lo,start-4,z,z+12,WM,thickness+4)
        fill("_BaseRight",end+4,hi,z,z+12,WM,thickness+4)

    def interactable(kind,id,p,prompt,extent,model=None,yaw=0,scale=1.):
        cls=u.load_class(None,"/Script/WellnessCheck."+kind)
        a=sub.spawn_actor_from_class(cls,V(*p),R(yaw=yaw))
        a.set_actor_label(kind[2:]+"_"+id)
        a.set_folder_path("House/Interact/Connections")
        a.set_editor_property("wc_id",u.Name(id))
        a.set_editor_property("prompt",prompt)
        a.set_editor_property("grab_extent",V(*extent))
        if model:
            set_mesh(a.get_editor_property("mesh"),asset(model),collide=False)
            a.get_editor_property("mesh").set_relative_scale3d(V(scale,scale,scale))
        return a

    def door(id,axis,fixed,center,z,locked=False,key=None):
        hinge=(center-56.5,fixed,z) if axis=="x" else (fixed,center-56.5,z)
        a=interactable("WCDoor",id,hinge,"Open",(0,0,0),"Door_Victorian_Closed",0 if axis=="x" else 90)
        a.set_folder_path("House/Doors")
        a.set_editor_property("locked",locked)
        if key:
            a.set_editor_property("key_id",u.Name(key))
        c=a.get_editor_property("mesh")
        c.set_collision_profile_name("BlockAll")
        c.set_relative_location(V(56.5,0,0),False,False)
        return a

    def note(id,p,yaw=0):
        a=interactable("WCNote",id,p,"Read",(9,6,5),"Letters_Scattered",yaw,.30)
        apply_note(a, id)

    def look(id,p,title,body,extent=(14,12,12)):
        a=interactable("WCLook",id,p,"Examine "+title,extent)
        a.set_editor_property("text",body)

    def pickup(id,item,p,model,name):
        a=interactable("WCPickup",id,p,"Take "+name.lower(),(12,10,7),model)
        a.set_editor_property("item_id",u.Name(item))
        a.set_editor_property("display_name",name)

    def top(a):
        o,e=a.get_actor_bounds(False)
        return o.z+e.z+.35

    # Living room entrance through the TV wall's return. The mantel, TV and
    # chimney stay in place. The second doorway replaces the sitting-room window.
    sub.destroy_actor(by_name["LivingExtensionRearWall"])
    sub.destroy_actor(by_name["LivingExtensionRearSiding"])
    portal("MusicFromLiving","y",827.,-750.,-600.,-676.,0.,84.)
    relocate_window(1000,-600,1000,-1015,"W_G_sitting")
    portal("MusicToSitting","x",-617.,800.,1205.,1000.,0.,55.)
    door("music_sitting","x",-617.,1000.,0.,locked=True)
    for label,x0,x1,y0,y1 in (("West",550,800,-1015,-750),("East",800,1205,-1015,-600)):
        solid("MusicFloor"+label,(x0,x1,y0,y1,-20,0),"MI_FloorBoards").tags=[u.Name("Floor_Wood")]
        solid("MusicFoundation"+label,(x0-8,x1+8,y0-8,y1+8,-40,-20),"MI_CellarStone",EXTERIOR)
        solid("MusicCeiling"+label,(x0,x1,y0,y1,278,284),"MI_PlasterCeiling")
        solid("MusicRoof"+label,(x0-22,x1+22,y0-18,y1+18,300,317),"MI_RoofTin",EXTERIOR)
    solid("MusicWestWall",(532,558,-1015,-750,0,300),"MI_SidingPaint",EXTERIOR)
    solid("MusicEastWall",(1196,1225,-1015,-600,0,300),"MI_SidingPaint",EXTERIOR)
    solid("MusicBackWall",(532,800,-1038,-999,0,331),"MI_SidingPaint",EXTERIOR)
    solid("MusicReturnWood",(550,1205,-1026,-1015,270,282),WM,EXTERIOR,False)
    solid("MusicEastLining",(1186,1197,-1015,-600,0,278),PLASTER)
    solid("MusicWestLining",(556,567,-1015,-750,0,278),PLASTER)
    solid("MusicBackLining",(556,800,-1015,-1000,0,278),PLASTER)

    # The pantry's boarded window is reused at the scullery's exterior.
    relocate_window(1800,600,1890,892,"W_G_pantry")
    portal("SculleryFromPantry","x",617.,1600.,2000.,1800.,0.,55.)
    sub.destroy_actor(match("Wall_Peeling",2200,600,0))
    sub.destroy_actor(match("Wall_Exterior_Siding_Broken",2200,636,0))
    portal("SculleryFromSickroom","x",617.,2000.,2400.,2230.,0.,55.)
    door("scullery_pantry","x",617.,1800.,0.,locked=True,key="key_scullery")
    door("scullery_sickroom","x",617.,2230.,0.,locked=True,key="key_scullery")
    solid("SculleryFloor",(1690,2510,600,892,-16,0),"MI_MegaTilesOld").tags=[u.Name("Floor_Stone")]
    solid("SculleryFoundation",(1682,2518,619,902,-40,-16),"MI_CellarStone",EXTERIOR)
    solid("SculleryCeiling",(1690,2510,600,892,280,286),"MI_PlasterCeiling")
    solid("SculleryRoof",(1669,2531,615,925,307,329),"MI_RoofTin",EXTERIOR,pitch=-3.)
    solid("SculleryWestWall",(1668,1695,618,910,0,312),"MI_SidingPaint",EXTERIOR)
    solid("SculleryEastWall",(2502,2530,618,910,0,312),"MI_SidingPaint",EXTERIOR)
    solid("SculleryBackWall",(2090,2530,883,928,0,330),"MI_SidingPaint",EXTERIOR)
    solid("SculleryBackLining",(2090,2510,870,885,0,280),"MI_MegaMuddyPlaster")
    for x in (1695,2493):
        solid(f"SculleryLining_{x}",(x,x+9,630,893,0,280),PLASTER)

    # The two upper passages cut only their respective shared walls.
    sub.destroy_actor(match("Wall_Peeling",2400,400,350))
    portal("AideLinen","y",2400.,200.,600.,443.,350.)
    door("aide_linen","y",2400.,443.,350.)
    sub.destroy_actor(by_name["RearWing_Divider_-1"])
    portal("BoxesSewing","y",3020.,-600.,-200.,-343.,350.)
    door("boxes_sewing","y",3020.,-343.,350.)
    by_name["RearWing_LinenCupboard"].set_actor_location(V(2635,544,350),False,True)
    by_name["RearWing_BoxRoomCrates"].set_actor_location(V(2800,-548,350),False,True)
    for a in actors:
        p=a.get_actor_location()
        if a.get_actor_label()=="Box_Cardboard_Open" and str(a.get_folder_path()).endswith("/Sewing") and p.x>3000:
            a.set_actor_location(V(3095,-239,350),False,True)
        if a.get_actor_label()=="Chair_Dining_HighBack" and str(a.get_folder_path()).endswith("/Sewing") and p.x>3000:
            a.set_actor_location(V(3210,-306,350),False,True)

    music = prop("MusicConsole",oldwest+"/SM_Table_Small_01a",(1055,-946,0),"Music",180)
    mt=top(music)
    prop("Metronome",polish+"/SM_AlcoveMetronomeSet",(1041,-943,mt),"Music",0,False)
    note("music_lesson",(1069,-925,mt+1),20)
    look("alcove_metronome",(1041,-943,mt+14),"the metronome",
         "The pendulum has rusted in place. Ruth drew a tiny crescent beside the slowest mark.",(11,10,15))
    prop("MusicSideChair","Armchair_Wingback_Torn",(639,-939,0),"Music",55,height=104)
    prop("MusicRecords","Bookshelf_Tall",(1172,-791,0),"Music",90,height=151)
    prop("MusicRug","Rug_Persian_Worn",(932,-839,.5),"Music",90,False)
    prop("MusicCase","Suitcase_Old",(770,-948,0),"Music",20,True,height=25)
    prop("MusicLamp","Candle_Wall_Sconce",(1171,-917,154),"Music",270,False,snap=False)
    ceiling("MusicLampLight",(1155,-917,177),185.,(1.,.71,.41),430.)

    wash=prop("SculleryWashBench",oldwest+"/SM_Table_Small_01a",(2358,816,0),"Scullery",180)
    st=top(wash)
    prop("Washboard",polish+"/SM_SculleryWashSet",(2358,824,st),"Scullery",15,False)
    prop("WashBasin","/Game/Fab/Urban_Australian_Desolation_Basin_Metal_Rusty/SM_yjrfbep_tier_2/StaticMeshes/SM_yjrfbep_tier_2",(1747,829,0),"Scullery",0,height=49)
    prop("WashBucket","/Game/Fab/Urban_Australian_Desolation_Bucket_Metal_Weathered/SM_yjrefhg_tier_2/StaticMeshes/SM_yjrefhg_tier_2",(2425,816,0),"Scullery",30,height=32)
    prop("SculleryShelves",polish+"/SM_PolishCellarShelves",(2010,847,0),"Scullery",180,height=140)
    prop("SculleryJugs","Bottles_Empty_Group",(1935,820,0),"Scullery",45,False)
    note("scullery_service",(2333,795,st+1),-14)
    look("scullery_washboard",(2360,816,st+18),"the washboard",
         "Rust in the zinc ribs. A ring of black grime marks the waterline.",(27,22,22))
    pickup("pick_ammo_scullery","ammo_scullery",(2391,797,st+1),"/Game/WC/Props/SM_Item_AmmoBox","Box of cartridges")
    solid("SculleryKeyPeg",(1629,1650,502,510,122,132),WM,PROPS+"/Scullery",False)
    pickup("pick_key_scullery","key_scullery",(1650,506,132),"/Game/WC/Props/SM_Item_KeyDesk","Scullery key")
    prop("SculleryLamp","Oil_Lamp_Wall_Bracket",(2484,791,166),"Scullery",270,False,snap=False)
    ceiling("SculleryLampLight",(2460,780,196),210.,(1.,.73,.48),460.)

    linen=prop("LinenSortingTable",oldwest+"/SM_Table_Small_01a",(2840,515,350),"Linen",180)
    lt=top(linen)
    prop("FoldedLinen",polish+"/SM_LinenStackSet",(2820,518,lt),"Linen",185,False)
    prop("LinenBlanket","/Game/Fab/Urban_Shanty_Town_Blanket_Fabric_Worn/SM_ycblbew_tier_2/StaticMeshes/SM_ycblbew_tier_2",
         (2445,555,350),"Linen",30,False,height=7)
    note("linen_checkout",(2858,496,lt+1),9)
    look("linen_stack",(2820,518,lt+7),"the folded linen",
         "The outer sheets are yellow with age. One towel in the middle is wet.",(17,12,9))
    ceiling("LinenLampLight",(2698,452,608),96.,(1.,.72,.49),400.)

    boxes=prop("BoxRoomWorkTable",oldwest+"/SM_Table_Small_01a",(2670,-537,350),"BoxRoom",0)
    bt=top(boxes)
    prop("ParcelPatterns",polish+"/SM_BoxRoomPatternSet",(2662,-538,bt),"BoxRoom",0,False)
    prop("BoxRoomCase","/Game/Fab/Urban_Australian_Desolation_Suitcase_Leather_Worn/SM_yjxdddq_tier_2/StaticMeshes/SM_yjxdddq_tier_2",
         (2455,-293,350),"BoxRoom",35,True,height=29)
    note("boxroom_patterns",(2693,-518,bt+1),-7)
    look("boxroom_pattern_stack",(2662,-538,bt+5),"the dress patterns",
         "Three packets tied with string. Edith has written names on them instead of sizes.",(17,14,10))
    ceiling("BoxRoomLampLight",(2720,-458,607),93.,(1.,.67,.40),400.)
    u.log_warning("WC_CONNECTIONS six thresholds and four dressed rooms")
