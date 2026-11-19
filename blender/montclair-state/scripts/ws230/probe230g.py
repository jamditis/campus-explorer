# ws230 probe g: which base mesh is on top at the residual spots (evaluated terrain still off 3DEP after fix230c)
import bpy,sys,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
M='/workspace/nj-scenes/montclair-state/'
P=np.load(M+'scripts/ws230/dep1m_full_x-280_280_y-280_280_rowS.npy')
def p3(x,y): return float(P[int(y+280),int(x+280)])
N=['Terrain_LiDAR_DTM_1m','QI_east_edge_LiDAR_terrain_patch','QH_east_fan_LiDAR_terrain_patch','QG_north_strip_LiDAR_terrain_patch','QJ_NE_seam_ramp_field','QJ_NE_seam_fill_UNVERIFIED']
with bpy.data.libraries.load(M+'montclair_state.blend',link=False) as (src,dst): dst.objects=[n for n in src.objects if n in N]
B={}
for o in dst.objects:
    W=o.matrix_world; B[o.name[:6]]=BVHTree.FromPolygons([W@v.co for v in o.data.vertices],[p.vertices[:] for p in o.data.polygons])
for x,y in [(226.5,102.5),(226.5,94.5),(232.5,86.5),(232.5,78.5),(220.5,190.5),(220.5,198.5),(218.5,220.5),(214.5,206.5)]:
    r=[]
    for k,b in B.items():
        h=b.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
        if h[0] is not None: r.append((k,round(h[0].z-p3(x,y),2)))
    print('P230G',x,y,round(p3(x,y),2),r,flush=True)
sys.stdout.flush(); import os; os._exit(0)
