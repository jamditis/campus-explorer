# read-only: objects' verts buried by the feathered target grounds (before vs after)
import bpy, mathutils, os, collections
from mathutils.bvhtree import BVHTree
TG=['PK_Feliciano_west_DTM_fill_UNVERIFIED','WS60_terrain_edge_apron_LiDAR_to_skirt','WS68_RHD_ground_northDTM']
TERR=('Terrain','M3','PK_Feliciano','WS60_terrain','WS68_RHD_ground','Skirt','skirt','BD_','DTM','Lawn','lawn','Grass_','grass')
for F in os.environ['FILES'].split():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    with bpy.data.libraries.load(F) as (a,b): b.objects=[n for n in a.objects if any(n.startswith(t) for t in TG)]
    T=[]
    for o in b.objects:
        m=o.data; T.append(BVHTree.FromPolygons([(o.matrix_world@v.co)[:] for v in m.vertices],[p.vertices[:] for p in m.polygons]))
    # reuse same names for comparison objects
    with bpy.data.libraries.load(F) as (a,b2): b2.objects=[n for n in a.objects if not any(t in n for t in TERR)]
    cnt=collections.Counter(); tot=0
    for o in b2.objects:
        if o is None or o.type!='MESH': continue
        bb=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]
        if max(p.x for p in bb)<-450 or min(p.x for p in bb)>-200 or max(p.y for p in bb)<-140 or min(p.y for p in bb)>290: continue
        for v in list(o.data.vertices)[::2]:
            w=o.matrix_world@v.co
            if not (-450<w.x<-200 and -140<w.y<290): continue
            tot+=1
            for t in T:
                h=t.ray_cast(mathutils.Vector((w.x,w.y,w.z+40)),mathutils.Vector((0,0,-1)),60)
                if h[0] is not None and h[0].z>w.z+0.05: cnt[o.name[:40]]+=1; break
    print('P236C',os.path.basename(F),'tot',tot,'buried',sum(cnt.values()),cnt.most_common(10),flush=True)
