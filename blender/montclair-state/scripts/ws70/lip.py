import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    x0,x1=min(v.x for v in bb),max(v.x for v in bb); y0,y1=min(v.y for v in bb),max(v.y for v in bb)
    if x1<-246 or x0>-205 or y1<-64 or y0>-58: continue
    if x1-x0>300: tag='BIG'
    else: tag=''
    oe=o.evaluated_get(dg); m=oe.to_mesh(); bm=bmesh.new(); bm.from_mesh(m); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm)
    hs=[]
    for x in range(-244,-206,4):
        for y in (-63,-61.5,-60.2):
            h=t.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))[0]
            if h: hs.append((x,y,round(h.z,2)))
    bm.free(); oe.to_mesh_clear()
    if hs: print('L70',o.name[:60],tag,[s.material.name[:28] for s in o.material_slots if s.material][:2],len(hs),hs[:12])
