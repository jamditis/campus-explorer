# ws230 Q6 check: does any ground changed this session (WS230 fill, WS60 east strip, evaluated terrain) stand above
# Paths_Roads_OSM paving verts in x 150..280, y -40..265?
import bpy,sys,os,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
M='/workspace/nj-scenes/montclair-state/'
G=['Terrain_LiDAR_DTM_1m','WS60_terrain_edge_apron_LiDAR_to_skirt','WS230_NE_east_gap_fill_3DEP_UNVERIFIED']
with bpy.data.libraries.load(M+os.environ.get('PF','montclair_state.blend'),link=False) as (src,dst):
    dst.objects=G+[n for n in src.objects if n in ('Roads_OSM','Footpaths_OSM')]
dst_objects=[o for o in dst.objects if o is not None]
for o in dst_objects: bpy.context.scene.collection.objects.link(o)
dg=bpy.context.evaluated_depsgraph_get(); B=[]
for o in dst_objects:
    if o.name in G:
        e=o.evaluated_get(dg); mm=e.to_mesh(); W=o.matrix_world
        B.append((o.name,BVHTree.FromPolygons([W@v.co for v in mm.vertices],[p.vertices[:] for p in mm.polygons]))); e.to_mesh_clear()
bad={}; n=0
for o in dst_objects:
    if o.name in G: continue
    W=o.matrix_world
    for v in o.data.vertices:
        w=W@v.co
        if not (150<w.x<280 and -40<w.y<265): continue
        n+=1
        for nm,b in B:
            h=b.ray_cast(Vector((w.x,w.y,w.z+30)),Vector((0,0,-1)),30.0)
            if h[0] is not None and h[0].z>w.z+0.02: bad.setdefault((o.name,nm),[]).append((round(w.x),round(w.y),round(h[0].z-w.z,2)))
print('P230I paving verts checked',n,flush=True)
for k,l in bad.items(): print('P230I ABOVE',k,len(l),'max',max(x[2] for x in l),sorted(l,key=lambda t:-t[2])[:12],flush=True)
sys.stdout.flush(); os._exit(0)
