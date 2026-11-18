import bpy,bmesh,os,json
from mathutils import Vector
import numpy as np
img=bpy.data.images['ortho2020.png']; W,H=img.size
px=np.array(img.pixels[:],dtype=np.float32).reshape(H,W,4)
o=bpy.data.objects['QG_north_strip_LiDAR_terrain_patch']; M=o.matrix_world
me=o.data; print('PUV',[u.name for u in me.uv_layers])
uv=me.uv_layers['ortho'].data if 'ortho' in me.uv_layers else None
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
X0,X1,Y0,Y1=-10,66,100,136
res={}
for p in me.polygons:
    c=M@p.center
    if not (X0<=c.x<X1 and Y0<=c.y<Y1): continue
    if uv is None: continue
    u=sum(uv[i].uv.x for i in p.loop_indices)/p.loop_total; v=sum(uv[i].uv.y for i in p.loop_indices)/p.loop_total
    xi=min(W-1,max(0,int(u*W))); yi=min(H-1,max(0,int(v*H)))
    r,g,b,_=px[max(0,yi-1):yi+2,max(0,xi-1):xi+2].reshape(-1,4).mean(0)
    lum=0.3*r+0.59*g+0.11*b; sat=max(r,g,b)-min(r,g,b)
    res[p.index]=(round(c.x,1),round(c.y,1),float(lum),float(sat),float(g-(r+b)/2),p.material_index)
json.dump(res,open('/workspace/nj-scenes/montclair-state/scripts/ws22/classify.json','w'))
print('N',len(res))
