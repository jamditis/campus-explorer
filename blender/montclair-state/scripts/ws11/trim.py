import bpy, bmesh, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
DRY=os.environ.get('DRY')=='1'
dg=bpy.context.evaluated_depsgraph_get()
b=bpy.data.objects['COLE_planting_beds_smooth_bu']
me=b.evaluated_get(dg).to_mesh(); mw=b.matrix_world
T=BVHTree.FromPolygons([mw@v.co for v in me.vertices],[tuple(p.vertices) for p in me.polygons])
tot=0
for name in ('WS3_Cole_plaza_paving_20261109','Footpaths_OSM'):
    o=bpy.data.objects[name]; print('USERS',name,o.data.users)
    bm=bmesh.new(); bm.from_mesh(o.data); w=o.matrix_world
    kill=[]
    for f in bm.faces:
        c=w@f.calc_center_median()
        if not(-140<c.x<-60 and -80<c.y<-59.5): continue
        # inside bed footprint if bed found above or below within 0.6 m
        h=T.ray_cast(c+Vector((0,0,0.6)),Vector((0,0,-1)),1.2)
        if not h[0]: continue
        # require all verts inside footprint too for top faces; side/skirt faces go if centre inside
        inside=all(T.ray_cast(w@v.co+Vector((0,0,0.6)),Vector((0,0,-1)),1.2)[0] for v in f.verts)
        if inside or f.normal.z<0.5: kill.append(f)
    print('KILL',name,len(kill)); tot+=len(kill)
    if not DRY and kill:
        bmesh.ops.delete(bm,geom=kill,context='FACES'); bm.to_mesh(o.data); o.data.update()
    bm.free()
print('TOTAL',tot)
if not DRY: bpy.ops.wm.save_mainfile(); print('SAVED')
