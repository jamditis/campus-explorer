import bpy, sys, math
exec(open('scripts/og/og_cam.py').read().split("CAMS={}")[0])
CAMS={}
exec("def cam" + open('scripts/og/og_cam.py').read().split("def cam",1)[1].split("for nm,n,s in")[0])
o=bpy.data.objects.get('OG_CAM_eye_schmitt_N_end_lower_storey')
if o: bpy.data.objects.remove(o, do_unlink=True)
w,ob=wallpt(n1,22,140.5); print('wall',w,ob)
p=w+n1*20+u*7; p.z=gz(p)+1.7
cam('OG_CAM_eye_schmitt_ESE_north_lower_storey',p,w-u*3+Vector((0,0,0.3)),24)
bpy.ops.wm.save_mainfile(); print('SAVED')
