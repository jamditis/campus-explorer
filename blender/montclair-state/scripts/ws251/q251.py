# ws251 read-only (Q6): evaluated Footpaths_OSM vs evaluated Terrain_LiDAR_DTM_1m (incl. joined patches) on a 0.5 m grid in the W63b box
import bpy, os, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
F='/workspace/nj-scenes/montclair-state/'+os.environ.get('F','montclair_state_ws251b.blend')
with bpy.data.libraries.load(F) as (a,b): b.objects=['Terrain_LiDAR_DTM_1m','Footpaths_OSM']
for o in b.objects: bpy.context.scene.collection.objects.link(o)
dg=bpy.context.evaluated_depsgraph_get(); box=(-195,-163,139,179); T={}
for o in b.objects:
    me=o.evaluated_get(dg).to_mesh(); M=o.matrix_world; vs=[M@v.co for v in me.vertices]
    ps=[p.vertices[:] for p in me.polygons if any(box[0]-3<vs[i].x<box[1]+3 and box[2]-3<vs[i].y<box[3]+3 for i in p.vertices)]
    T[o.name]=BVHTree.FromPolygons(vs,ps); print('Q251',o.name,len(ps),flush=True)
d=[];hole=0
for y in np.arange(box[2],box[3],0.5):
    for x in np.arange(box[0],box[1],0.5):
        hp=T['Footpaths_OSM'].ray_cast(Vector((x,y,300)),Vector((0,0,-1)),400)
        ht=T['Terrain_LiDAR_DTM_1m'].ray_cast(Vector((x,y,300)),Vector((0,0,-1)),400)
        if ht[0] is None: hole+=1; continue
        if hp[0] is not None: d.append((hp[0].z-ht[0].z,x,y))
a=np.array([v[0] for v in d]); print('Q251 path samples',len(a),'path-ground min %.3f p5 %.3f median %.3f max %.3f; under ground %d; terrain holes %d'%(a.min(),np.percentile(a,5),np.median(a),a.max(),(a<0).sum(),hole),flush=True)
print('Q251 worst',sorted(d)[:5],flush=True); os._exit(0)
