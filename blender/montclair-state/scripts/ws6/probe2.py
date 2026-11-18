import bpy, math
from mathutils import Vector
TZ=bpy.data.objects['TZ_Cole_north_addition_UNVERIFIED']; mw=TZ.matrix_world; nm=mw.to_3x3()
mats=[s.material.name[:14] if s.material else None for s in TZ.material_slots]
a=math.radians(-13.5); u=Vector((math.cos(a),math.sin(a),0)); v=Vector((-math.sin(a),math.cos(a),0))
for f in TZ.data.polygons:
  c=mw@f.center; n=(nm@f.normal).normalized()
  pv=c.dot(v)
  if pv>-92:
    ps=[mw@TZ.data.vertices[i].co for i in f.vertices]
    print('F',f.index,mats[f.material_index],'n·v %.2f n·u %.2f nz %.2f'%(n.dot(v),n.dot(u),n.z),'pu %.2f..%.2f'%(min(p.dot(u) for p in ps),max(p.dot(u) for p in ps)),'pv %.2f..%.2f'%(min(p.dot(v) for p in ps),max(p.dot(v) for p in ps)),'z %.2f..%.2f'%(min(p.z for p in ps),max(p.z for p in ps)))
