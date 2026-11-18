import bpy
from mathutils import Vector
c=bpy.data.objects['QR_CAM_eye_richardson_NE_door']; print('CAM',tuple(round(v,2) for v in c.location),tuple(round(v,3) for v in c.rotation_euler),c.data.lens)
dg=bpy.context.evaluated_depsgraph_get()
for n in ('Footpaths_OSM','Roads_OSM'):
    o=bpy.data.objects.get(n)
    if not o: print('no',n); continue
    e=o.evaluated_get(dg); me=e.to_mesh(); mw=o.matrix_world
    pts=[mw@v.co for v in me.vertices]
    near=[p for p in pts if 70<p.x<95 and 280<p.y<312]
    print(n,len(pts),'near',len(near),[tuple(round(a,2) for a in p) for p in near[:30]])
    e.to_mesh_clear()
# ground objects ray down
for nm in ('Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km'):
    o=bpy.data.objects.get(nm); 
    if not o: print('no',nm); continue
    e=o.evaluated_get(dg); inv=o.matrix_world.inverted()
    for xy in ((80.3,291.5),(82.6,297.4),(84.8,302.7),(78,288),(90,295)):
        ok,loc,nor,i=e.ray_cast(inv@Vector((xy[0],xy[1],300)),Vector((0,0,-1)))
        print(nm,xy,ok,round((o.matrix_world@loc).z,2) if ok else None)
# objects whose bbox covers region
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    bb=[o.matrix_world@Vector(b) for b in o.bound_box]
    if min(b.x for b in bb)<84<max(b.x for b in bb) and min(b.y for b in bb)<297<max(b.y for b in bb) and (max(b.x for b in bb)-min(b.x for b in bb))<400:
        print('COVER',o.name,round(min(b.z for b in bb),2),round(max(b.z for b in bb),2))
