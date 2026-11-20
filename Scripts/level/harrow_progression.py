"""Dress the puzzle route. Safe to apply to the existing map or the level build."""
import unreal as u
V=u.Vector
def dress():
    actors=u.get_editor_subsystem(u.EditorActorSubsystem)
    all_actors=actors.get_all_level_actors()
    def found(label,folder=None):
        return [a for a in all_actors if a.get_actor_label()==label and (not folder or str(a.get_folder_path()).endswith(folder))]
    def get(label):
        matches=found(label)
        assert len(matches)==1,(label,len(matches))
        return matches[0]
    def pose(a,pos=None,yaw=None):
        a.modify()
        if pos is not None:a.set_actor_location(V(*pos),False,True)
        if yaw is not None:a.set_actor_rotation(u.Rotator(0,0,yaw),False)
        return a
    def mesh(a,name):
        m=a.get_component_by_class(u.StaticMeshComponent)
        asset=u.EditorAssetLibrary.load_asset('/Game/WC/Props/HouseDetails/SM_'+name)
        assert asset,name
        m.modify();m.set_static_mesh(asset);m.set_editor_property('override_materials',[])
        a.set_actor_scale3d(V(1,1,1))
        return m
    def trigger(id,pos,extent,prompt,model=None,yaw=0,offset=(0,0,0),item=None):
        lab='Harrow_'+id
        a=(found(lab) or [None])[0]
        if not a:
            cls='WCPickup' if item else 'WCUsable'
            a=actors.spawn_actor_from_class(u.load_class(None,'/Script/WellnessCheck.'+cls),V(*pos))
            a.set_actor_label(lab);a.set_folder_path('House/Interact/Harrow')
        pose(a,pos,yaw)
        for k,v in [('wc_id',id),('grab_extent',V(*extent)),('grab_offset',V(*offset)),('prompt',prompt)]:
            a.set_editor_property(k,v)
        if item:
            a.set_editor_property('item_id',item);a.set_editor_property('display_name','Loose ivory piano key')
        if model:
            m=mesh(a,model);m.set_mobility(u.ComponentMobility.MOVABLE)
            m.set_collision_profile_name('NoCollision')
        return a
    def slip(id,pos,yaw,title,body):
        lab='Harrow_'+id
        a=(found(lab) or [None])[0] or actors.spawn_actor_from_class(u.load_class(None,'/Script/WellnessCheck.WCNote'),V(*pos))
        a.set_actor_label(lab);a.set_folder_path('House/Interact/Harrow');pose(a,pos,yaw)
        a.set_editor_property('wc_id',id);a.set_editor_property('title',title);a.set_editor_property('body',body)
        a.set_editor_property('prompt','Read '+title.lower());a.set_editor_property('grab_extent',V(8,5,2))
        m=a.get_component_by_class(u.StaticMeshComponent)
        m.set_static_mesh(u.EditorAssetLibrary.load_asset('/Game/HorrorHouseKit/Meshes/Clutter_Debris/SM_Letters_Scattered'))
        m.set_relative_scale3d(V(.30,.30,.25));m.set_collision_profile_name('NoCollision')
    def look(label,xyz,text,extent):
        a=pose(get('Look_'+label),xyz)
        a.set_editor_property('text',text);a.set_editor_property('grab_extent',V(*extent))
    def pickup(label,xyz,tag,extent,title):
        a=pose(get('Pickup_pick_'+label),xyz)
        a.set_editor_property('tags',[t for t in a.tags if str(t) not in ('Show_drawer','Show_desk',tag)]+[tag])
        a.set_editor_property('grab_extent',V(*extent));a.set_editor_property('display_name',title)
    can=get('TrashCanDown');can.set_editor_property('tags',[t for t in can.tags if str(t)!='BinBody']+['BinBody'])
    mesh(pose(get('Piano_Upright'),yaw=0),'HarrowUpright')
    pose(get('Piano_Stool'),(190,-363,0))
    pose(get('Sofa_Sagging_Broken'),yaw=0)
    pose(found('Armchair_Wingback_Torn','/Living')[0],(129,-544,0),-135)
    look('living_shelf',(145,-526,55),"Ruth's lesson card is tucked into the arm of the chair. She hid the ivory piano key in her mother's sitting-room desk.",(21,24,18))
    look('piano',(129,-420,89),"One ivory key is missing. The little drawer underneath has no keyhole.",(12,57,7))
    trigger('piano_drawer',(102,-420,64),(3,20,5),'Inspect the piano drawer','PianoDrawer',offset=(14,0,4))
    trigger('ivory_fitted',(122,-421.27,84),(0,0,0),'','LoosePianoKey').set_editor_property('enabled',False)
    trigger('pick_ivory',(1440,-420,62),(11,5,4),'Take the loose piano key','LoosePianoKey',yaw=25,item='piano_ivory')
    pickup('key_prayer',(138,-420,66),'PianoReward',(9,8,5),'Upstairs prayer-room key')
    mesh(pose(get('Desk_Writing'),yaw=180),'HarrowDesk')
    for chair in found('Chair_Dining_HighBack','/Sitting'):pose(chair,(1400,-515,0),140)
    trigger('sitting_drawer',(1478,-420,60),(3,21,5),'Open the writing-desk drawer','PianoDrawer',180,(14,0,4))
    den=pose(get('Usable_desk'),yaw=180)
    mesh(den,'HarrowDesk');den.set_actor_scale3d(V(1,1,1.36))
    den.set_editor_property('grab_extent',V(4,64,10));den.set_editor_property('grab_offset',V(34,0,66))
    trigger('walter_drawer',(2318,-330,82),(3,21,5),"Try Walter's locked drawer",'PianoDrawer',180,(14,0,4))
    pickup('key_ell',(2280,-336,84),'Show_desk',(8,7,4),"Walter's upstairs rear-hall keys")
    mesh(pose(get('DanielDesk'),yaw=0),'HarrowDesk')
    get('DanielDesk').set_actor_scale3d(V(1,1,1.36))
    trigger('daniel_drawer',(1682,-400,432),(3,21,5),"Open Daniel's desk drawer",'PianoDrawer',0,(14,0,4))
    shelves=sorted(found('Bookshelf_Tall','/Den'),key=lambda a:a.get_actor_location().y)
    assert len(shelves)==2
    for i,a in enumerate(shelves):mesh(pose(a,yaw=0),'DenBooks'+str(i+1))
    look('den_books',(1663,-396,108),"A gap in the county histories. Walter's pencilled shelf card: FIRST SETTLERS moved to the living room, beside the stair wall. Desk key inside.",(7,112,73))
    for lab,pos in [('Desk_Lamp_Green',(2320,-384,103.4)),('Typewriter_Old',(2340,-307,103.4)),('Book_Stack_Old',(2343,-270,103.4))]:
        for a in found(lab,'/Den'):pose(a,pos)
    look('den_typewriter',(2330,-310,121),"Walter typed one line until the ribbon gave out. On the margin he pencilled: desk key in the settlers' book, front living room.",(12,15,7))
    mesh(pose(found('Wardrobe_Open_Clothes','/Master')[0],yaw=0),'EdithWardrobe')
    look('master_wardrobe',(88,500,470),"Four dresses on wire hangers. The seams have been let out again and again. A laundry ticket in the pocket reads: Mrs Pruitt, rear upstairs room. Return her videotape.",(12,52,44))
    fridge=pose(get('Fridge'),yaw=180);mesh(fridge,'HarrowFridge').set_collision_profile_name('InvisibleWall')
    # Front faces west. The door hinge is the southern corner in fridge-local coordinates.
    trigger('fridge_door',(1512,479,2),(6,37,44),'Open the refrigerator','HarrowFridgeDoor',180,(4,-42,92))
    look('fridge',(1550,526,86),"Three jars and one empty shelf. A strip of masking tape reads: RUTH, STAY OUT OF MY DESK.",(9,20,13))
    tubs=[a for a in found('Urban_Australian_Desolation_Bathtub_Meta') if a.get_actor_location().x<1500]
    assert len(tubs)==1
    mesh(pose(tubs[0],yaw=0),'HarrowBath')
    # Keep the tub physically solid for movement but let the use ray reach into the hollow bowl.
    tubs[0].static_mesh_component.set_collision_profile_name('InvisibleWall')
    trigger('bath_water',(1000,-520,402),(0,0,0),'','BathWater').set_editor_property('enabled',False)
    look('upbath_tub',(1000,-483,404),"A plug chain hangs over the chipped rim.",(66,7,15))
    pickup('key_sitting',(980,-514,369),'BathReward',(12,7,5),'Downstairs sitting-room key')
    slip('note_tape_receipt',(1714,-399,433.5),15,'Cassette loan slip',"RECORDING II. Borrower: Mrs Pruitt, live-in aide. If she is gone, check the suitcase in her room beyond the upstairs rear-hall lock.")
    slip('note_fridge',(1524,516,40.4),-75,'Grease-stained kitchen note',"Ruth, I found another piano key in the butter dish. If you must hide things, use the drawer in my sitting-room desk. Leave the icebox shut. Mother.")
    # A pull on the bathroom dresser reads as a clue after the call.
    trigger('bath_dresser',(1380,-277,440),(29,9,10),'Inspect the open bathroom drawer')
    get('Usable_book_settlers').set_editor_property('prompt',"Pull out Customs of the First Settlers")
    for id,coords in [('company_foyer',(1510,60,0)),('company_landing',(900,55,350))]:
        lab='Watcher_'+id
        a=(found(lab) or [None])[0] or actors.spawn_actor_from_class(u.load_class(None,'/Script/WellnessCheck.WCWatcher'),V(*coords))
        a.set_actor_label(lab);a.set_folder_path('House/Watchers');pose(a,coords,180)
        a.set_editor_property('wc_id',id);a.set_editor_property('kind',2);a.set_editor_property('radius',4.15)
