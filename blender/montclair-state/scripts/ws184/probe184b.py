# ws184 probe B: what is under / W of the S-drive W-edge flap (x -314..-309, y -240..-234), per-object z stack at 0.5 m
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get(); T=[]
for o in bpy.data.objects:
    if o.type!='MESH': continue
    W=[o.matrix_world@Vector(c) for c in o.bound_box]
    if max(w.x for w in W)<-316 or min(w.x for w in W)>-307 or max(w.y for w in W)<-242 or min(w.y for w in W)>-232: continue
    bm=bmesh.new(); bm.from_object(o,dg); bm.transform(o.matrix_world); T.append((o.name[:22],BVHTree.FromBMesh(bm))); bm.free()
print('P184B objs',[n for n,_ in T],flush=True)
import numpy as np
for y in np.arange(-234.5,-240.6,-0.5):
    row=[]
    for x in np.arange(-314.0,-308.9,0.5):
        hs=[]
        for n,t in T:
            h=t.ray_cast(Vector((x,y,130)),Vector((0,0,-1)))
            if h[0] is not None: hs.append((h[0].z,n))
        hs.sort(reverse=True)
        row.append('%s%.2f/%s'%(hs[0][1][:6],hs[0][0],(hs[1][1][:6]+'%.2f'%hs[1][0]) if len(hs)>1 else '-') if hs else 'VOID')
    print('P184B y %.1f | '%y+' | '.join(row),flush=True)
