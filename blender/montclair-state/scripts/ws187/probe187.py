import numpy as np, bpy, math
from mathutils import Vector
G=np.vstack([np.load('/workspace/nj-scenes/montclair-state/prep/ws175_scurb/las175_2023.npy'),np.load('/workspace/nj-scenes/montclair-state/prep/ws174_scurb/las174.npy')]); G=G[G[:,3]==2]
def gz2(x,y):
    k=(abs(G[:,0]-x)<2)&(abs(G[:,1]-y)<2); return float(np.median(G[k,2])) if k.any() else 118.0
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
sc.render.resolution_x=1280; sc.render.resolution_y=720
import os
cx,cy,ch,tx,ty,th,fl=[float(a) for a in os.environ.get('PCAM','-336,-231,1.7,-312,-236,1.0,26').split(',')]
cz=gz2(cx,cy)+ch; tz=gz2(tx,ty)+th
cam=bpy.data.objects.new('C',bpy.data.cameras.new('C')); sc.collection.objects.link(cam); cam.data.lens=fl
cam.location=(cx,cy,cz); d=Vector((tx,ty,tz))-Vector((cx,cy,cz)); cam.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
bpy.context.view_layer.update()
fr=[cam.matrix_world@v for v in cam.data.view_frame(scene=sc)]  # tr,br,bl,tl
tr,br,bl,tl=fr
W,H=896,504
for (px,py) in [tuple(int(b) for b in a.split(':')) for a in os.environ['PPIX'].split()]:
    u=px/W; v=py/H
    top=tl.lerp(tr,u); bot=bl.lerp(br,u); p=top.lerp(bot,v)
    dirn=(p-cam.location).normalized()
    hit,loc,nor,fi,ob,_=sc.ray_cast(dg,cam.location,dirn)
    print('PROBE187',px,py,hit and ob.name,tuple(round(c,2) for c in loc),tuple(round(c,2) for c in nor),'dtm',round(gz2(loc.x,loc.y),2),flush=True)
# steep / near-vertical lawn faces in the toe box
import bmesh
for ob in sc.objects:
    if ob.type!='MESH': continue
    me=ob.data; mw=ob.matrix_world; n=0; ex=[]
    for f in me.polygons:
        c=mw@f.center
        if -322<c.x<-305 and -240<c.y<-226 and ob.name.startswith(('WS187','WS186','WS162_Lot3_W_sh','WS169c','WS163_ground','WS167_ground')):
            nz=(mw.to_3x3()@f.normal).normalized().z
            if nz<0.5 and f.area>0.002: n+=1; ex.append((round(c.x,1),round(c.y,1),round(c.z,2),round(nz,2),round(f.area,3)))
    if n: print('STEEP187',ob.name,n,ex[:8],flush=True)
