import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
def bvh(o,ev=True):
    if ev: e=o.evaluated_get(dg); m=e.to_mesh()
    else: m=o.data
    bm=bmesh.new(); bm.from_mesh(m); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free()
    if ev: e.to_mesh_clear()
    return t
S=bvh(bpy.data.objects['Context_skirt_3DEP_ortho_4km'])
for l in open('/proc/self/status'):
    if l.startswith('VmHWM'): print('MEM189',l.strip(),flush=True)
P=[bvh(o,False) for o in bpy.data.objects if o.name.startswith(('WS181_Lot36_asphalt','WS163_ground_patch_W','WS185_Lot36_N_grass','WS169c_','WS167_ground_W_of_Lot3'))]
bad=[]
for x in np.arange(-340,-322,0.2):
    for y in np.arange(-236,-224,0.2):
        hs=S.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))[0]
        tops=[t.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))[0] for t in P]; tops=[h.z for h in tops if h]
        if hs and tops and hs.z>max(tops)-0.01: bad.append((round(x,1),round(y,1),round(hs.z-max(tops),3)))
print('BAD189',len(bad),flush=True)
for b in bad[:400]: print('B',*b)
