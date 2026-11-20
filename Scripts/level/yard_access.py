"""Dress the two exterior approaches."""
import math
import unreal as u

LEFT = [(-710,0),(-649,-340),(-536,-654),(-216,-1000),(53,-1184),(463,-1184),(760,-1000),(1410,-845),(2695,-836),(3230,-755),(3556,-745)]
RIGHT = [(-710,0),(-595,400),(-507,685),(-431,911),(-325,993),(825,993),(1100,875),(2610,802),(3130,760),(3335,480),(3345,-482),(3230,-755)]

def build():
    actors=u.get_editor_subsystem(u.EditorActorSubsystem)
    level=actors.get_all_level_actors()
    names={a.get_actor_label():a for a in level}
    # Existing saved maps and fresh map builds go through the same placement pass.
    previously_dressed = 'YardTrail_Left_0' in names
    plane=u.EditorAssetLibrary.load_asset('/Engine/BasicShapes/Plane')
    mat=u.EditorAssetLibrary.load_asset('/Game/WC/Materials/M_YardFootpath')
    if not plane or not mat: raise RuntimeError('Missing footpath material or mesh')
    segments=[]
    for side,path in [('Left',LEFT),('Right',RIGHT)]:
        for i,((x,y),(ex,ey)) in enumerate(zip(path,path[1:])):
            dx,dy=ex-x,ey-y
            length=math.hypot(dx,dy)
            width=146 if side=='Right' and -510 < x < 840 else 184
            # Extend through the bend; the gravel is mapped in world space across joins.
            position=u.Vector((x+ex)/2,(y+ey)/2,-37.75+i*.025+(side=='Right')*.30)
            rotation=u.Rotator(yaw=math.degrees(math.atan2(dy,dx)))
            label=f'YardTrail_{side}_{i}'
            actor=names.get(label) or actors.spawn_actor_from_class(u.StaticMeshActor,position,rotation)
            actor.set_actor_location_and_rotation(position,rotation,False,True)
            actor.set_editor_property('tags',['YardTrail',label])
            actor.set_actor_label(label)
            actor.set_folder_path('House/Shell/Exterior/Footpaths')
            comp=actor.static_mesh_component
            comp.set_static_mesh(plane); comp.set_material(0,mat)
            comp.set_collision_profile_name('NoCollision');comp.set_cast_shadow(False)
            actor.set_actor_scale3d(u.Vector((length+(10 if ex==3556 else 60))/100,width/100,1))
            segments.append((x,y,dx,dy,length))
    def nearest(px,py):
        result=float('inf')
        for x,y,dx,dy,length in segments:
            t=max(0,min(1,((px-x)*dx+(py-y)*dy)/(length*length)))
            result=min(result,math.hypot(px-x-t*dx,py-y-t*dy))
        return result
    trimmed=0
    def fence_y(x):
        # Bow the old fence around the turret where the enlarged living room meets the trail.
        return -1080 - 260*max(0,min(1,(x+800)/570,(1310-x)/590))
    # The original fence has a separate invisible player barrier. Follow the new panels
    # with that barrier too, including at the two ends of the existing yard.
    limit=names['LimLeft']
    src=limit.static_mesh_component
    o,e=names['LimRight'].get_actor_bounds(False)
    corners=[o.x-e.x,-800,-230,720,1310,o.x+e.x]
    for i,(x,ex) in enumerate(zip(corners,corners[1:])):
        y,ey=fence_y(x)-10,fence_y(ex)-10
        pos=u.Vector((x+ex)/2,(y+ey)/2,o.z)
        rot=u.Rotator(yaw=math.degrees(math.atan2(ey-y,ex-x)))
        label='LimLeft' if i==0 else f'LimLeft_Turret_{i}'
        wall=names.get(label) or actors.spawn_actor_from_class(u.StaticMeshActor,pos,rot)
        wall.set_actor_label(label)
        wall.set_actor_location_and_rotation(pos,rot,False,True)
        wall.set_actor_scale3d(u.Vector((math.hypot(ex-x,ey-y)+2)/100,2*e.y/100,2*e.z/100))
        comp=wall.static_mesh_component
        comp.set_static_mesh(src.static_mesh); comp.set_material(0,src.get_material(0))
        comp.set_collision_profile_name(src.get_collision_profile_name())
        comp.set_cast_shadow(False); wall.set_actor_hidden_in_game(True)
        wall.set_folder_path(limit.get_folder_path())
    for a in level:
        folder=str(a.get_folder_path())
        p=a.get_actor_location(); name=a.get_actor_label()
        if 'Exterior' not in folder or p.z>30: continue
        if 'Fence_Wood' in name and abs(p.y+1080)<1 and -900 < p.x < 1410:
            low,high=fence_y(p.x-100),fence_y(p.x+100)
            if low!=high or low!=-1080:
                a.set_actor_location(u.Vector(p.x,(low+high)/2,p.z),False,True)
                a.set_actor_rotation(u.Rotator(yaw=math.degrees(math.atan2(high-low,200))),False)
                scale=a.get_actor_scale3d()
                a.set_actor_scale3d(u.Vector(scale.x*math.hypot(200,high-low)/200,scale.y,scale.z))
            continue
        if p.y < -840 and -425 < p.x < 920 and nearest(p.x,p.y)<143 and any(t in name for t in ('Bramble','Bush_Thorny','Rock_Fog','Rock_Cluster')):
            a.set_actor_location(u.Vector(p.x,fence_y(p.x)-65,p.z),False,True)
            continue
        if 930<p.y<1110 and -520<p.x<850 and any(t in name for t in ('Bramble','Bush_Thorny','Rock_Fog','Rock_Cluster')):
            a.set_actor_location(u.Vector(p.x,1135,p.z),False,True)
            if not previously_dressed: a.set_actor_scale3d(a.get_actor_scale3d()*.42)
            continue
        if previously_dressed: continue
        if ('TreeLine' in folder and abs(p.y)<1380 and -1000<p.x<3560):
            a.set_actor_location(p+u.Vector(0,math.copysign(260,p.y),0),False,True)
            a.set_actor_scale3d(a.get_actor_scale3d()*.81)
        elif any(word in name for word in ('Bramble','Bush_Thorny','Rock_Fog','Rock_Cluster')) and nearest(p.x,p.y)<200:
            # Move low brush to the verge or leave it short where the two paths meet.
            a.set_actor_scale3d(a.get_actor_scale3d()*.29)
            if abs(p.y)>650 and 0<p.x<2700:
                a.set_actor_location(u.Vector(p.x,math.copysign(1030,p.y),p.z),False,True)
            else:
                a.set_actor_location(p-u.Vector(0,0,18),False,True)
            trimmed+=1
        elif nearest(p.x,p.y)<170:
            dest=None
            if 'Woodpile' in name: dest=(-1150,-900) if p.x<0 else (3750,937)
            elif 'Stump_Axe' in name: dest=(-1250,-780) if p.x<0 else (3660,510)
            elif 'Wheelbarrow' in name and p.x>2800: dest=(3520,150)
            if dest: a.set_actor_location(u.Vector(*dest,p.z),False,True)
    print('WC_PATH_READY',len(segments),'segments;',trimmed,'brush clumps')
