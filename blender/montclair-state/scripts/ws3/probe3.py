import bpy
from mathutils import Vector
c=Vector((-140,-40,134))
for o in bpy.context.scene.objects:
  if o.type not in('MESH','CURVE') or o.hide_render: continue
  bb=[o.matrix_world@Vector(k) for k in o.bound_box]
  mn=Vector((min(p.x for p in bb),min(p.y for p in bb),min(p.z for p in bb))); mx=Vector((max(p.x for p in bb),max(p.y for p in bb),max(p.z for p in bb)))
  d=mx-mn; ctr=(mn+mx)/2
  if (ctr-c).length>45: continue
  if mn.z>c.z+2.5 and mx.z<c.z+9 and max(d.x,d.y)>3 and d.z<1.0:
    print('THIN',o.name,[round(v,1) for v in mn],[round(v,1) for v in mx],o.type,len(o.data.vertices) if o.type=='MESH' else '',[x.name for x in o.users_collection][:1])
