import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
for o in bpy.data.objects:
    if o.type=='MESH' and ('planting_beds' in o.name or o.name.startswith(('WS3_Cole_plaza_paving','Footpaths_OSM'))):
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        print('OBJ',o.name,len(o.data.polygons),'x',round(min(v.x for v in bb),1),round(max(v.x for v in bb),1),'y',round(min(v.y for v in bb),1),round(max(v.y for v in bb),1),flush=True)
beds=[o for o in bpy.data.objects if o.type=='MESH' and 'COLE_planting_beds' in o.name]
trees=[]
for b in beds:
    me=b.evaluated_get(dg).to_mesh(); mw=b.matrix_world
    trees.append((b.name,BVHTree.FromPolygons([mw@v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons])))
for name in ('WS3_Cole_plaza_paving_20261109','Footpaths_OSM'):
    o=bpy.data.objects[name]; me=o.data; mw=o.matrix_world
    cov=[]
    for p in me.polygons:
        c=mw@p.center
        if not(-140<c.x<-55 and -110<c.y<-30) or p.normal.z<0.7: continue
        for bn,t in trees:
            h=t.ray_cast(c+Vector((0,0,3)),Vector((0,0,-1)),3.5)
            if h[0] and h[0].z>c.z-0.02:
                cov.append((p.index,round(c.x,1),round(c.y,1),round(h[0].z-c.z,3),bn)); break
    print('COVERED',name,len(cov),flush=True)
    for x in cov: print('  ',x,flush=True)
