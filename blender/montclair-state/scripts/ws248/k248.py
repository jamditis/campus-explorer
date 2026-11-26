# ws248 poke probe: first hit from above (terrain eval / patch / walk / pad) over the patch zone, 0.5 m grid
import bpy, os, sys, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
F='/workspace/nj-scenes/montclair-state/'+os.environ.get('F','montclair_state_ws248c.blend')
N=['Terrain_LiDAR_DTM_1m','WS248_E_stand_LiDAR2023_ground_patch_1m','WS247_E_stand_back_walk_ortho2020_UNVERIFIED_level','fse_stand_under_pad','fse_front_walkway','Footpaths_OSM']
with bpy.data.libraries.load(F) as (a,b): b.objects=N
for o in b.objects: bpy.context.scene.collection.objects.link(o)
for m in b.objects[0].modifiers:
    if 'skirt_under' in m.name.lower(): m.show_viewport=False
dg=bpy.context.evaluated_depsgraph_get(); box=(-230,-184,40,140)
def bvh(o):
    e=o.evaluated_get(dg); me=e.to_mesh(); M=o.matrix_world; vs=[M@v.co for v in me.vertices]
    ps=[p.vertices[:] for p in me.polygons if any(box[0]-3<vs[i].x<box[1]+3 and box[2]-3<vs[i].y<box[3]+3 for i in p.vertices)]
    t=BVHTree.FromPolygons(vs,ps) if ps else None; e.to_mesh_clear(); return t
B={o.name:bvh(o) for o in b.objects}
from collections import Counter
first=Counter(); poke=[]
for y in np.arange(box[2]+0.25,box[3],0.5):
    for x in np.arange(box[0]+0.25,box[1],0.5):
        hs=[]
        for n,t in B.items():
            if t is None: continue
            h=t.ray_cast(Vector((x,y,300)),Vector((0,0,-1)),400)
            if h[0] is not None: hs.append((h[0].z,n))
        if not hs: continue
        hs.sort(reverse=True); first[hs[0][1][:22]]+=1
        zt=[z for z,n in hs if n=='Terrain_LiDAR_DTM_1m']; zp=[z for z,n in hs if n.startswith('WS248_E')]
        if zt and zp and zt[0]>zp[0]+0.005: poke.append((round(x,2),round(y,2),round(zt[0]-zp[0],2)))
print('K248 first',dict(first),flush=True)
import collections; print('K248 bins',sorted(collections.Counter((int(p[0]//4*4),int(p[1]//8*8)) for p in poke if p[2]>0.03).items()),flush=True); print('K248 terrain over patch',len(poke),'max',max([p[2] for p in poke]) if poke else 0,sorted(poke,key=lambda p:-p[2])[:12],flush=True)
sys.stdout.flush(); os._exit(0)
