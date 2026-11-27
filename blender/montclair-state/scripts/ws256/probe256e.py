# ws256 read-only: walk extension E edge vs evaluated lawn just E of it
import sys; sys.stdout.reconfigure(line_buffering=True)
import bpy, os, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
F=os.environ['F']
with bpy.data.libraries.load(F) as (a,b):
    b.objects=[n for n in a.objects if n.startswith(('Terrain_LiDAR_DTM_1m','WS250_W63','WS251_W63','WS254_W63e_Feliciano_E_walk_N'))]
for o in b.objects: bpy.context.scene.collection.objects.link(o)
dg=bpy.context.evaluated_depsgraph_get()
def bvh(o):
    em=o.evaluated_get(dg).to_mesh(); M=o.matrix_world; vs=[M@v.co for v in em.vertices]
    ps=[p.vertices[:] for p in em.polygons if any(-195<vs[i].x<-184 and 180<vs[i].y<194 for i in p.vertices)]
    return BVHTree.FromPolygons(vs,ps) if ps else None
T=bvh(bpy.data.objects['Terrain_LiDAR_DTM_1m']); E=bvh(bpy.data.objects['WS254_W63e_Feliciano_E_walk_N_extension_to_OSM_walk_UNVERIFIED'])
def top(bt,x,y):
    h=bt.ray_cast(Vector((x,y,400)),Vector((0,0,-1)),600); return h[0].z if h[0] else float('nan')
print('P256E y  edge  | ground at x -189.4 -189.0 -188.5 -188.0 -187.0 (cm below edge)')
for y in np.arange(184.0,190.61,0.5):
    e=top(E,-189.55,y); print('P256E y%.1f %.3f |'%(y,e),' '.join('%4.0f'%((e-top(T,x,y))*100) for x in (-189.4,-189.0,-188.5,-188.0,-187.0)))
os._exit(0)
