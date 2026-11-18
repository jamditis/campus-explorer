# REVERT order: cams, sc. Run: REVERT=1 blender -b <copy> --python scripts/rz/rz_revert_all.py
import os; os.environ['REVERT']='1'
exec(open('scripts/rz/rz_cams.py').read().replace('bpy.ops.wm.save_mainfile()','pass'))
exec(open('scripts/rz/rz_sc.py').read())
import bpy
g=sum(len(o.data.vertices) for o in bpy.data.objects if o.type=='MESH' and 'grass_points' in o.name)
print('REV_OBJCOUNT',len(bpy.data.objects),'grasspts',g,'libs',len(bpy.data.libraries),'mats',len(bpy.data.materials))
