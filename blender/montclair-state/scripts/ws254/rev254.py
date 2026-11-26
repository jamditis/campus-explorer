# ws254 read-only M2c review: north-file walk/plaza items vs main's evaluated terrain (float/bury) and main meshes overlapping them
import bpy, os, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
MS='/workspace/nj-scenes/montclair-state/'
ITEMS=['North_NEWalkCurveS_gk','North_NEPlaza_gi','ge_police_south_walk']
with bpy.data.libraries.load(MS+'north/montclair_north.blend') as (a,b): b.objects=[n for n in a.objects if n in ITEMS]
nobj=list(b.objects)
with bpy.data.libraries.load(MS+'montclair_state.blend') as (a,b): b.objects=[n for n in a.objects if n.startswith(('Terrain_LiDAR_DTM_1m','Footpaths_OSM','Roads_OSM'))]
for o in list(b.objects)+nobj: bpy.context.scene.collection.objects.link(o)
dg=bpy.context.evaluated_depsgraph_get()
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; em=T.evaluated_get(dg).to_mesh(); M=T.matrix_world; vs=[M@v.co for v in em.vertices]
bt=BVHTree.FromPolygons(vs,[p.vertices[:] for p in em.polygons])
fp=[BVHTree.FromObject(bpy.data.objects[n],dg) for n in ('Footpaths_OSM','Roads_OSM') if n in bpy.data.objects]
for o in nobj:
    bo=BVHTree.FromObject(o,dg); bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    x0,x1=min(v.x for v in bb),max(v.x for v in bb); y0,y1=min(v.y for v in bb),max(v.y for v in bb)
    d=[]; ov=0; hole=0
    for x in np.arange(x0+0.1,x1,0.5):
        for y in np.arange(y0+0.1,y1,0.5):
            h=bo.ray_cast(Vector((x,y,400)),Vector((0,0,-1)),600)
            if not h[0]: continue
            g=bt.ray_cast(Vector((x,y,400)),Vector((0,0,-1)),600)
            if not g[0]: hole+=1; continue
            d.append(h[0].z-g[0].z)
            if any(f.ray_cast(Vector((x,y,400)),Vector((0,0,-1)),600)[0] and abs(f.ray_cast(Vector((x,y,400)),Vector((0,0,-1)),600)[0].z-h[0].z)<0.4 for f in fp): ov+=1
    d=np.array(d) if d else np.array([np.nan])
    print('REV254',o.name,'bbox x %.1f..%.1f y %.1f..%.1f'%(x0,x1,y0,y1),'n',len(d),'top-ground p5 %.2f p50 %.2f p95 %.2f'%(np.nanpercentile(d,5),np.nanmedian(d),np.nanpercentile(d,95)),'buried(<0) %d float(>0.3) %d'%((d<0).sum(),(d>0.3).sum()),'OSM-walk/road overlap samples',ov,'terrain holes',hole,flush=True)
os._exit(0)
