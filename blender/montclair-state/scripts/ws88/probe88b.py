import bpy
from mathutils import Vector
W=[o for o in bpy.data.objects if o.name.startswith('Plaza long arched wall')][0]
print('P88 shapekeys',W.data.shape_keys and [k.name for k in W.data.shape_keys.key_blocks])
dg=bpy.context.evaluated_depsgraph_get(); sc=bpy.context.scene
A=Vector((-182.8,-73.9)); B=Vector((-173.1,-95.2))
for t in (0.3,0.5,0.7):
  p=A+(B-A)*t
  for dx in (-0.6,-0.3,0,0.3,0.6):
    q=p+Vector((dx,0))
    ok,loc,n,i,o,_=sc.ray_cast(dg,Vector((q.x,q.y,140)),Vector((0,0,-1)))
    print('P88',t,dx,round(loc.z,2) if ok else None,o.name[:40] if ok else '', i)
E=W.evaluated_get(dg); me=E.to_mesh(); import statistics
zs=[ (E.matrix_world@v.co) for v in me.vertices]
print('P88 eval verts',len(zs),'orig',len(W.data.vertices))
hi=[v for v in zs if v.z>133.5]; print('P88 top verts sample',[tuple(round(c,1) for c in v) for v in hi[::max(1,len(hi)//12)]])
