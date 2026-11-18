import os
for f in ('main129c.py','main129e.py'):
    os.environ['SAVE']='0'
    exec(compile(open('/workspace/nj-scenes/montclair-state/scripts/ws129/'+f).read(),f,'exec'),{'__name__':'__main__'})
import bpy; bpy.ops.wm.save_mainfile(); print('M129 CE SAVED')
