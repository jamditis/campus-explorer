# ws248g: instead of dropping patch faces (partial drops left holes), sink each patch vertex that the dense snapped terrain
# covers to 4 cm under the terrain -> no holes, no pokes. Writes k248g.json {vertex index: new z}.
import bpy, os, sys, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
F='/workspace/nj-scenes/montclair-state/'+os.environ.get('F','montclair_state_ws248f2.blend'); PN='WS248_E_stand_LiDAR2023_ground_patch_1m'
with bpy.data.libraries.load(F) as (a,b): b.objects=['Terrain_LiDAR_DTM_1m',PN]
for o in b.objects: bpy.context.scene.collection.objects.link(o)
T,P=b.objects
for m in T.modifiers:
    if 'skirt_under' in m.name.lower(): m.show_viewport=False
dg=bpy.context.evaluated_depsgraph_get(); e=T.evaluated_get(dg); me=e.to_mesh(); M=T.matrix_world
vs=[M@v.co for v in me.vertices]; box=(-230,-182,38,140)
t=BVHTree.FromPolygons(vs,[p.vertices[:] for p in me.polygons if any(box[0]<vs[i].x<box[1] and box[2]<vs[i].y<box[3] for i in p.vertices)])
out={}; dmax=0
for v in P.data.vertices:
    h=t.ray_cast(Vector((v.co.x,v.co.y,300)),Vector((0,0,-1)),400)
    if h[0] is not None and h[0].z>v.co.z-0.03:
        nz=h[0].z-0.04; dmax=max(dmax,v.co.z-nz); out[v.index]=nz
print('K248G sink verts',len(out),'max sink',round(dmax,2),flush=True)
json.dump(out,open('/workspace/nj-scenes/montclair-state/scripts/ws248/k248g.json','w'))
sys.stdout.flush(); os._exit(0)
