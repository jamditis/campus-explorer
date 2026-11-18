import bpy
from mathutils import Vector
X0,X1,Y0,Y1=-10,40,325,370
dg=bpy.context.evaluated_depsgraph_get()
for o in bpy.data.objects:
    if o.type not in('MESH','CURVE','POINTCLOUD') or o.hide_render: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    xs=[v.x for v in bb]; ys=[v.y for v in bb]
    if max(xs)<X0 or min(xs)>X1 or max(ys)<Y0 or min(ys)>Y1: continue
    if (max(xs)-min(xs))>2000: tag='HUGE'
    else: tag=''
    print('SF_OBJ',o.name,o.type,[round(min(xs)),round(max(xs)),round(min(ys)),round(max(ys))],[c.name for c in o.users_collection][:1],tag)
sc=bpy.context.scene
for x,y in [(5,340),(20,345),(10,362),(30,358),(45,340),(0,330),(25,335),(10,372)]:
    hit,loc,n,i,ob,m=sc.ray_cast(dg,Vector((x,y,400)),Vector((0,0,-1)))
    print('SF_RAY',x,y,hit and round(loc.z,2),ob and ob.name)
