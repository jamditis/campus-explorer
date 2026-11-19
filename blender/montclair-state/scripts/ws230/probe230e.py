# ws230 W53j probe e: evaluated terrain (all modifiers) over the gap between the QI patch east boundary and the apron (x 214..246, y 28..252), vs 3DEP 1 m
import bpy,sys,numpy as np,json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
M='/workspace/nj-scenes/montclair-state/'
P=np.load(M+'scripts/ws230/dep1m_full_x-280_280_y-280_280_rowS.npy'); A=np.load(M+'data/dtm_1m.npy')
def p3(x,y): return float(P[int(y+280),int(x+280)])
def dt(x,y): return float(A[min(499,int(y+250)),min(499,int(x+250))])
with bpy.data.libraries.load(M+'montclair_state.blend',link=False) as (src,dst): dst.objects=['Terrain_LiDAR_DTM_1m','WS60_terrain_edge_apron_LiDAR_to_skirt']
for o in dst.objects: bpy.context.scene.collection.objects.link(o)
dg=bpy.context.evaluated_depsgraph_get()
B={}
for o in dst.objects:
    e=o.evaluated_get(dg); mm=e.to_mesh(); W=o.matrix_world
    B[o.name[:4]]=BVHTree.FromPolygons([W@v.co for v in mm.vertices],[p.vertices[:] for p in mm.polygons])
    print('P230E',o.name,'eval faces',len(mm.polygons),flush=True); e.to_mesh_clear()
def rz(b,x,y):
    h=b.ray_cast(Vector((x,y,400)),Vector((0,0,-1))); return None if h[0] is None else round(h[0].z,2)
res=[]
for y in range(30,252,8):
    row=[]
    for x in (214,220,226,232,238,242,245,247,250):
        t=rz(B['Terr'],x+0.5,y+0.5); a=rz(B['WS60'],x+0.5,y+0.5); g=p3(x+0.5,y+0.5)
        row.append((x,None if t is None else round(t-g,1),None if a is None else round(a-g,1)))
    print('P230E y',y,row,flush=True); res.append((y,row))
json.dump(res,open(M+'scripts/ws230/probe230e.json','w'))
import resource; print('P230E VmHWM',open('/proc/self/status').read().split('VmHWM:')[1].split('\n')[0],flush=True)
sys.stdout.flush(); import os; os._exit(0)
