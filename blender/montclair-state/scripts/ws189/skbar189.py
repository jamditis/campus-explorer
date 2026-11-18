import bpy, bmesh, numpy as np, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
X0,X1,Y0,Y1=[float(v) for v in os.environ.get('BOX','-318,-305,-239,-229').split(',')]
def bvh(o,ev):
    if ev: e=o.evaluated_get(dg); m=e.to_mesh()
    else: m=o.data
    bm=bmesh.new(); bm.from_mesh(m); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free()
    if ev: e.to_mesh_clear()
    return t
S=bvh(bpy.data.objects['Context_skirt_3DEP_ortho_4km'],True)
P=[]
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render or o.name.startswith(('Context_skirt','BD_','Terrain_LiDAR')): continue
    if any(c.hide_render for c in o.users_collection): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    if max(v.x for v in bb)<X0 or min(v.x for v in bb)>X1 or max(v.y for v in bb)<Y0 or min(v.y for v in bb)>Y1: continue
    if max(v.z for v in bb)-min(v.z for v in bb)>8: continue
    P.append((o.name,bvh(o,False)))
print('TOPS189',[n for n,_ in P],flush=True)
bad=[]
for x in np.arange(X0,X1,0.2):
    for y in np.arange(Y0,Y1,0.2):
        hs=S.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))[0]
        tops=[t.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))[0] for _,t in P]; tops=[h.z for h in tops if h]
        if hs and tops and 1.0>hs.z-max(tops)>-0.005: bad.append((round(x,1),round(y,1),round(hs.z-max(tops),3)))
        if False: bad.append((round(x,1),round(y,1),'NOTOP'))
print('BAD189',len(bad),flush=True)
for b in bad[:3000]: print('B',*b)
