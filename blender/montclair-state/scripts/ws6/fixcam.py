import bpy
from mathutils import Vector
cam=bpy.data.objects['WS6_CAM_eye_cole_gable_from_plaza']
out=Vector((0.2249,0.9744,0)); h=Vector((0.9744,-0.2249,0)); c0=Vector((-105.2351,-62.9952,0))
pl=bpy.data.objects['WS5_Cole_plaza_circle_quatrefoil_20261109']
xy=c0+out*17+h*1.2
mi=pl.matrix_world.inverted()
o=mi@Vector((xy.x,xy.y,300)); d=(mi.to_3x3()@Vector((0,0,-1))).normalized()
ok,loc,nrm,idx=pl.ray_cast(o,d)
gz=(pl.matrix_world@loc).z if ok else None
print('GZ',ok,gz)
cam.location=Vector((xy.x,xy.y,gz+1.65))
tgt=c0+Vector((0,0,138.4)); cam.data.lens=26
cam.rotation_euler=(tgt-cam.location).to_track_quat('-Z','Y').to_euler()
print('CAM',cam.location)
bpy.ops.wm.save_mainfile()
print('SAVED')
