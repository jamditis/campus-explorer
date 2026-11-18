# wa: drop the tree-occluded WA eye cam (TK_CAM_eye_Bohn_from_W used as the 2nd eye WIP instead)
import bpy
o = bpy.data.objects.get('WA_CAM_eye_Bohn_S_wing_from_SW')
if o:
    cd = o.data; bpy.data.objects.remove(o, do_unlink=True)
    if cd.users == 0: bpy.data.cameras.remove(cd)
print('WADROP objs', len(bpy.data.objects))
bpy.ops.wm.save_mainfile(); print('SAVED')
