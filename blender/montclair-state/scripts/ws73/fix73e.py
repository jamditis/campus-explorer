# ws73e: verge strip tone mismatch -> give WS73 verge the terrain's own material + a world-linear UV fit from nearby terrain loops
import bpy,os
import numpy as np
from mathutils.bvhtree import BVHTree
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; tm=t.data; uvl=tm.uv_layers.active
vg=bpy.data.objects['WS73_curb_back_lawn_verge_UNVERIFIED']; vm=vg.data
# material of terrain faces near the verge
from collections import Counter
cx=sum(v.co.x for v in vm.vertices)/len(vm.vertices); cy=sum(v.co.y for v in vm.vertices)/len(vm.vertices)
cnt=Counter(); A=[];U=[]
for p in tm.polygons:
    c=t.matrix_world@p.center
    if abs(c.x-cx)<8 and abs(c.y-cy)<8:
        cnt[p.material_index]+=1
        for li in p.loop_indices:
            co=t.matrix_world@tm.vertices[tm.loops[li].vertex_index].co; A.append((co.x,co.y,1)); U.append(tuple(uvl.data[li].uv))
mi=cnt.most_common(1)[0][0]; mat=t.material_slots[mi].material
A=np.array(A);U=np.array(U); coef,res,_,_=np.linalg.lstsq(A,U,rcond=None)
print('W73e terrain mat',mat.name,cnt.most_common(3),'uv fit resid',res,'uvlayer',uvl.name,flush=True)
vm.materials.clear(); vm.materials.append(mat)
uv=vm.uv_layers[0]; uv.name=uvl.name
for l in vm.loops:
    c=vg.matrix_world@vm.vertices[l.vertex_index].co; uv.data[l.index].uv=tuple(np.array((c.x,c.y,1))@coef)
vm.update()
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('W73e SAVED',flush=True)
