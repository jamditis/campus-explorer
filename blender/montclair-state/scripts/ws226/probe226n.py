# hole check: 2 m grid over the east, count points where NOTHING of the terrain object (evaluated) is hit
import bpy, sys, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']
for m in t.modifiers: m.show_viewport=m.show_render
dg=bpy.context.evaluated_depsgraph_get(); e=t.evaluated_get(dg); me=e.to_mesh()
B=BVHTree.FromPolygons([v.co.copy() for v in me.vertices],[p.vertices[:] for p in me.polygons]); e.to_mesh_clear()
miss=0; n=0; pts=[]
for x in range(60,248,2):
    for y in range(-248,248,2):
        n+=1
        if B.ray_cast(Vector((x+.3,y+.3,400)),Vector((0,0,-1)))[0] is None: miss+=1; pts.append((x,y))
print('P226N',os.path.basename(os.environ.get('INF','')),'samples',n,'miss',miss,flush=True)
import json; json.dump(pts,open('/tmp/p226n_%s.json'%os.path.basename(os.environ.get('INF','x')),'w'))
sys.stdout.flush(); os._exit(0)
