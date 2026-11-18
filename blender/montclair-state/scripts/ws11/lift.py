import bpy, bmesh, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
DRY=os.environ.get('DRY')=='1'
dg=bpy.context.evaluated_depsgraph_get()
b=bpy.data.objects['COLE_planting_beds_smooth_bu']
me=b.evaluated_get(dg).to_mesh(); mw=b.matrix_world
T=BVHTree.FromPolygons([mw@v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons])
for name in ('WS3_Cole_plaza_paving_20261109','Footpaths_OSM'):
    o=bpy.data.objects[name]; w=o.matrix_world; wi=w.inverted()
    n=0; mx=0
    for v in o.data.vertices:
        c=w@v.co
        if not(-100<c.x<-68 and -72<c.y<-59.5): continue
        h=T.ray_cast(c+Vector((0,0,0.5)),Vector((0,0,-1)),1.0)
        if h[0] and h[0].z>c.z-0.012:
            d=h[0].z+0.012-c.z
            if d>0.18: continue
            c.z+=d; v.co=wi@c; n+=1; mx=max(mx,d)
    print('LIFT',name,n,'max',round(mx,3))
    o.data.update()
if not DRY: bpy.ops.wm.save_mainfile(); print('SAVED')
