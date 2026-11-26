# ws248: patch faces where the evaluated terrain (dense, snapped) is above the patch -> drop them (terrain shows there)
import bpy, os, sys, json, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
F='/workspace/nj-scenes/montclair-state/'+__import__('os').environ.get('F','montclair_state_ws248d.blend')+''; PN='WS248_E_stand_LiDAR2023_ground_patch_1m'
with bpy.data.libraries.load(F) as (a,b): b.objects=['Terrain_LiDAR_DTM_1m',PN]
for o in b.objects: bpy.context.scene.collection.objects.link(o)
T,P=b.objects
for m in T.modifiers:
    if 'skirt_under' in m.name.lower(): m.show_viewport=False
dg=bpy.context.evaluated_depsgraph_get(); e=T.evaluated_get(dg); me=e.to_mesh(); M=T.matrix_world
vs=[M@v.co for v in me.vertices]; box=(-230,-182,38,140)
ps=[p.vertices[:] for p in me.polygons if any(box[0]<vs[i].x<box[1] and box[2]<vs[i].y<box[3] for i in p.vertices)]
t=BVHTree.FromPolygons(vs,ps)
pm=P.data; drop=[]
for p in pm.polygons:
    if abs(p.normal.z)<0.5: continue
    pts=[pm.vertices[i].co for i in p.vertices]+[p.center]
    ok=0
    for q in pts:
        h=t.ray_cast(Vector((q.x,q.y,300)),Vector((0,0,-1)),400)
        if h[0] is not None and h[0].z>q.z+0.005: ok+=1
    if ok==len(pts): drop.append(p.index)   # ws248f: only faces the terrain covers completely (partial drops left holes)
print('K248E drop',len(drop),'of',len(pm.polygons),flush=True)
json.dump(drop,open('/workspace/nj-scenes/montclair-state/scripts/ws248/k248e.json','w'))
sys.stdout.flush(); os._exit(0)
