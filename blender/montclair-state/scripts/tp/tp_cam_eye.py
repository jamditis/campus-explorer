# tp: eye-level camera on Bohn from the SE (tagged tp_obj, removed by tp_main REVERT)
import bpy,os
from mathutils import Vector
n='TP_CAM_eye_Bohn_from_SE'
o=bpy.data.objects.get(n)
if o: bpy.data.objects.remove(o)
cd=bpy.data.cameras.new(n); cd.lens=24
cam=bpy.data.objects.new(n,cd); cam['tp_obj']=1; bpy.data.collections['TP_Bohn_service_shafts_UNVERIFIED'].objects.link(cam)
x,y=float(os.environ.get('EX',268)),float(os.environ.get('EY',340))
# ground height by ray cast down
dg=bpy.context.evaluated_depsgraph_get()
hit,loc,*_=bpy.context.scene.ray_cast(dg,Vector((x,y,300)),Vector((0,0,-1)))
z=(loc.z if hit else 130.0)+1.7
cam.location=Vector((x,y,z)); t=Vector((float(os.environ.get("TX",236)),float(os.environ.get("TY",378)),z+14)); cam.rotation_euler=(t-cam.location).to_track_quat('-Z','Y').to_euler()
print('TPCAM',n,tuple(round(v,1) for v in cam.location),hit)
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
