import bpy,numpy as np
from mathutils import Vector
D=np.load('data/dtm_1m.npy')
P=[(150,100),(200,50),(120,30),(180,150),(110,60),(-120,150),(20,135),(-220,-50),(-230,60),(200,-200),(-150,-200)]
cov={p:[] for p in P}
for o in bpy.context.scene.objects:
    if o.type not in('MESH','CURVE') or o.hide_render: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[v.x for v in bb]; ys=[v.y for v in bb]; zs=[v.z for v in bb]
    if max(xs)-min(xs)>900: continue
    for p in P:
        if min(xs)<=p[0]<=max(xs) and min(ys)<=p[1]<=max(ys): cov[p].append('%s[%.0f..%.0f]'%(o.name[:30],min(zs)-D[p[1]+250,p[0]+250],max(zs)-D[p[1]+250,p[0]+250]))
for p in P: print('WH',p,len(cov[p]),cov[p][:10])
