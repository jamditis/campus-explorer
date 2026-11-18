import bpy
from mathutils import Vector
out=Vector((0.2249,0.9744,0)); c0=Vector((-105.2351,-62.9952,0))
pl=bpy.data.objects['WS5_Cole_plaza_circle_quatrefoil_20261109']; mi=pl.matrix_world.inverted()
zs=[]
for k in (0.4,0.8,1.5):
  for s in (-1.5,0,1.5):
    xy=c0+out*k+Vector((0.9744,-0.2249,0))*s
    ok,loc,n,i=pl.ray_cast(mi@Vector((xy.x,xy.y,300)),(mi.to_3x3()@Vector((0,0,-1))).normalized())
    zs.append(round((pl.matrix_world@loc).z,3) if ok else None)
print('APRON Z',zs)
v=[z for z in zs if z]; za=min(v) if v else None
w=bpy.data.objects['WS6_Cole_gable_arched_window_UNVERIFIED']
if za:
  dz=(za+0.02)-133.434
  w.location.z=dz; print('DZ',dz)
bpy.ops.wm.save_mainfile(); print('SAVED')
