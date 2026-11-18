# qx: full revert -> pre-qx SIG 8092 841 4027 4b2679ed8125 (run: blender -b main --python this; QXSAVE=1 to save)
import os,runpy
os.environ['REVERT']='1'; sv=os.environ.pop('QXSAVE',None)
for s in ('qx_cams2','qx_pmat','qx_plaza','qx_cams','qx_grass'):
    try: runpy.run_path('scripts/qx/%s.py'%s)
    except SystemExit: pass
import bpy
for m in [m for m in bpy.data.materials if m.name.startswith('QXP_') and m.users==0]: bpy.data.materials.remove(m)
if sv=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
