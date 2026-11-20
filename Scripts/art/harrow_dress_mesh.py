"""Build closed, folded garment meshes from the silhouettes and front UVs of the four approved dresses."""
from pathlib import Path
import math
import bpy
import numpy as np
from harrow_mesh import finish, xyz, brass
from harrow_mesh import path

def garment(name,back,cy,hem,top,width,angle,index):
    root=Path(__file__).resolve().parents[2]/'SourceArt/Textures/Harrow'
    picture=bpy.data.images.load(str(root/('Shape_'+name+'.png')),check_existing=True)
    w,h=picture.size
    pixels=np.empty(w*h*4,np.float32)
    picture.pixels.foreach_get(pixels);pixels=pixels.reshape(h,w,4)
    alpha=pixels[:,:,3]
    theta=math.radians(angle)
    def local(x,y,z):
        return (4+x*math.cos(theta)-y*math.sin(theta),cy+x*math.sin(theta)+y*math.cos(theta),z)
    def pixel(u,v):
        return pixels[min(h-1,max(0,round(v*(h-1)))),min(w-1,max(0,round(u*(w-1))))]
    # Scan each row separately; the waistband and the skirt have different cross-sections.
    spans=[]
    for row in alpha:
        inside=np.where(row>.5)[0]
        spans.append((inside[0]/w,inside[-1]/w) if len(inside) else (.47,.53))
    points=[];coords=[];faces=[];slots=[];lookup={};border={}
    def vertex(u,v):
        key=(round(u,6),round(v,6))
        if key in lookup:return lookup[key]
        l,r=spans[min(h-1,round(v*(h-1)))];side=np.clip((2*u-l-r)/max(.04,r-l),-1,1)
        roundness=math.sqrt(max(0,1-side*side));sag=1-v
        # Folds round the hanger at the shoulders, gather beneath the waist, and open at the hem.
        pleat=math.sin((u-.5)*(35+index*2)+math.sin(v*5+index)*.75)
        fold=(.20+1.2*sag*sag)*pleat*roundness
        forward=1.1*math.sin(4*v+.75*index)+.78*math.sin(u*11+index)
        sleeve=math.exp(-((abs(side)-.81)/.10)**2)*max(0,min(1,(v-.43)*5))
        face=forward+(1.35+4.4*roundness)+fold+1.9*sleeve
        # Puckered light stitching and lace sit just proud of the cloth beneath them.
        rgb=pixel(u,v)[:3];face+=.43*math.sqrt(float(rgb.mean()))
        y=(.5-u)*width+.8*sag*sag*math.sin(index+v*4)
        z=hem+v*(top-hem)
        back_x=forward-(.85+3.35*roundness)-.38*fold
        k=len(points);lookup[key]=k
        points.extend((xyz(local(face,y,z)),xyz(local(back_x,y,z))));coords.extend(((u,v),(1-u,v)))
        return k
    def emit(poly):
        ids=[vertex(a,b) for a,b,_ in poly]
        ids=list(dict.fromkeys(ids))
        if len(ids)<3:return
        faces.append(tuple(ids));slots.append(0);faces.append(tuple(i+1 for i in reversed(ids)));slots.append(1)
        for a,b in zip(ids,ids[1:]+ids[:1]):
            if (b,a) in border:del border[b,a]
            else:border[a,b]=True
    def cut(tri):
        polygon=[]
        for i,p in enumerate(tri):
            prev=tri[i-1]
            if (p[2]>.5)!=(prev[2]>.5):
                f=(.5-prev[2])/(p[2]-prev[2]);polygon.append((prev[0]+f*(p[0]-prev[0]),prev[1]+f*(p[1]-prev[1]),.5))
            if p[2]>.5:polygon.append(p)
        if len(polygon)>=3:emit(polygon)
    nx,ny=55,115
    grid=[[(i/nx,j/ny,float(pixel(i/nx,j/ny)[3])) for i in range(nx+1)] for j in range(ny+1)]
    for j in range(ny):
        for i in range(nx):
            a,b,c,d=grid[j][i],grid[j][i+1],grid[j+1][i+1],grid[j+1][i]
            cut((a,b,c));cut((a,c,d))
    for a,b in border:
        faces.append((b,a,a+1,b+1));slots.append(1)
    mesh=bpy.data.meshes.new(name+' tailored shell');mesh.from_pydata(points,[],faces);mesh.update()
    layer=mesh.uv_layers.new(name='UVMap')
    obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj);finish(obj,'M_Dress'+name)
    obj.data.materials.append(bpy.data.materials.get(back) or bpy.data.materials.new(back))
    for poly,slot in zip(mesh.polygons,slots):
        poly.material_index=slot;poly.use_smooth=True
        for li in poly.loop_indices:
            u,v=coords[mesh.loops[li].vertex_index]
            layer.data[li].uv=(u,v) if slot==0 else (u*1.25,v*3)
    # Each garment has an independently positioned hardwood hanger and a turned wire hook.
    def seam(ps,r,m):path([local(*p) for p in ps],r,m)
    for side in (-1,1):
        seam([(0,0,top+.5),(0,side*4,top+.3),(0,side*width*.29,top-3.9),(.2,side*width*.32,top-5.1)],.78,'MI_WoodTrim')
    seam([(0,-width*.3,top-5),(0,0,top-6),(0,width*.3,top-5)],.38,'MI_WoodTrim')
    seam([(0,0,top+.6),(0,0,172.5),(.3,0,174.2),(1,0,176.1),(2.3,0,176.7),(3.5,0,176.1),(3.8,0,174.7)],.30,brass)
