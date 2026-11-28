# ws270 probe: police south walk S edge vs the College Ave paving 0.5 m south of it (no save)
import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OB=bpy.data.objects; pav=OB['WS268_W72_CollegeAve_Lot33_paving_UNVERIFIED']
bm=bmesh.new(); bm.from_mesh(pav.data); bm.transform(pav.matrix_world); TP=BVHTree.FromBMesh(bm); bm.free()
wk=OB['ge_police_south_walk']; W=[wk.matrix_world@v.co for v in wk.data.vertices]; ymin=min(w.y for w in W)
dd=[]
for w in [w for w in W if w.y<ymin+1.0]:
    r=TP.ray_cast(Vector((w.x,w.y-0.5,200)),Vector((0,0,-1)))
    if r[0] is not None: dd.append((round(w.x,1),round(w.z-r[0].z,3)))
print('P270B walk x-range',min(w.x for w in W),max(w.x for w in W),'ymin',round(ymin,2),flush=True)
print('P270B walk-minus-paving',sorted(dd)[::5],flush=True)
raise SystemExit(0)
