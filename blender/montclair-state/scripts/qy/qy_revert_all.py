# qy: full revert -> pre-qy SIG 8101 842 4033 62c241145c19 (run: blender -b main --python this; QYSAVE=1 to save)
import os,runpy
os.environ['REVERT']='1'; sv=os.environ.pop('QYSAVE',None)
for s in ('qy_ptone','qy_cams','qy_wear','qy_rim'):
    try: runpy.run_path('scripts/qy/%s.py'%s)
    except SystemExit: pass
import bpy
if sv=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
