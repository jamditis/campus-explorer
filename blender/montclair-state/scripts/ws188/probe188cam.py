import bpy
bpy.data.objects['Context_skirt_3DEP_ortho_4km'].hide_viewport=True
import numpy as np, bpy, math
from mathutils import Vector
D181=np.load('/workspace/nj-scenes/montclair-state/prep/ws181_lot36/dtm181_0p5m.npy')
def gz2(x,y):
    r=int((-200-y)/0.5); c=int((x+355)/0.5)
    r=min(max(r,0),D181.shape[0]-1); c=min(max(c,0),D181.shape[1]-1); v=D181[r,c]
    return float(v) if v==v else 116.0
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
    print('PROBE188',px,py,hit and ob.name,tuple(round(c,2) for c in loc),tuple(round(c,2) for c in nor),'dtm',round(gz2(loc.x,loc.y),2),flush=True)
