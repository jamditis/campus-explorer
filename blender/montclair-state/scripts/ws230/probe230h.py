# ws230 probe h: paving near the x~220 low strip (y 170..215): which object, its z vs 3DEP, and width
import bpy,sys,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
M='/workspace/nj-scenes/montclair-state/'
P=np.load(M+'scripts/ws230/dep1m_full_x-280_280_y-280_280_rowS.npy')
def p3(x,y): return float(P[int(y+280),int(x+280)])
with bpy.data.libraries.load(M+'montclair_state_ws230b.blend',link=False) as (src,dst): dst.objects=['Roads_OSM','Footpaths_OSM','Terrain_LiDAR_DTM_1m']
for o in dst.objects: bpy.context.scene.collection.objects.link(o)
B={}
for o in dst.objects[:2]:
    W=o.matrix_world; B[o.name]=BVHTree.FromPolygons([W@v.co for v in o.data.vertices],[p.vertices[:] for p in o.data.polygons])
t=dst.objects[2]; dg=bpy.context.evaluated_depsgraph_get(); e=t.evaluated_get(dg); mm=e.to_mesh()
BT=BVHTree.FromPolygons([v.co.copy() for v in mm.vertices],[p.vertices[:] for p in mm.polygons])
for y in (176.5,190.5,204.5):
    row=[]
    for x in np.arange(212.5,230,1.0):
        g=p3(x,y); r=[]
        for k,b in B.items():
            h=b.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
            if h[0] is not None: r.append((k[:4],round(h[0].z-g,2)))
        h=BT.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
        row.append((x,None if h[0] is None else round(h[0].z-g,2),r))
    print('P230H',y,row,flush=True)
sys.stdout.flush(); os=__import__('os'); os._exit(0)
