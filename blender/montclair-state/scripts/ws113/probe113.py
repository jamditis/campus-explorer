import bpy, random
from mathutils import Vector
from collections import Counter
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
O=lambda p: next(o for o in bpy.data.objects if o.name.startswith(p))
random.seed(1)
for p in ['WS112_CollegeAve_S_E_walk_N_brick','WS112_W_branch_walk','WS111_CollegeAve_S_E_walk_gap','WS111_CollegeAve_S_W_walk_gap']:
    o=O(p); me=o.data; mw=o.matrix_world; C=Counter(); n=0
    for f in me.polygons:
        if f.normal.z<0.5: continue
        for k in range(3):
            vs=[mw@me.vertices[i].co for i in f.vertices]; a=[random.random() for _ in vs]; s=sum(a)
            q=sum((v*(ai/s) for v,ai in zip(vs,a)),Vector())
            h=sc.ray_cast(dg,q+Vector((0,0,3)),Vector((0,0,-1)),distance=3.05)
            n+=1
            if h[0]:
                nm=h[4].name
                if not (nm==o.name or nm.startswith('T_')): C[nm]+=1
    print('P113',p[:30],'samples',n,'pokes',dict(C))
