import bpy, numpy as np
cap=bpy.data.objects['OL_Schmitt_walk_island_lawn_caps']; me=cap.data; ul=me.uv_layers['ortho']
m=bpy.data.materials['Ground_ortho_grass']
imgs=[n.image for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image]
print('IMGS',[(i.name,i.size[:]) for i in imgs])
img=max(imgs,key=lambda i:i.size[0]*i.size[1]); W,H=img.size; px=np.array(img.pixels[:]).reshape(H,W,4)
from collections import defaultdict
for lab,(cx,cy) in (('small',(21.6,136.5)),('big',(47.8,150.2))):
    vals=[]
    for p in me.polygons:
        c=p.center
        if (c.x-cx)**2+(c.y-cy)**2<200:
            uv=sum((ul.data[li].uv for li in p.loop_indices),__import__('mathutils').Vector((0,0)))/len(p.loop_indices)
            vals.append(px[min(H-1,int(uv.y*H)),min(W-1,int(uv.x*W)),:3])
    print('ORTHO',lab,img.name,np.round(np.mean(vals,axis=0),3) if vals else None,len(vals))
