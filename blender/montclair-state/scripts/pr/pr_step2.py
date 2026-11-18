import bpy,os
exec(open('scripts/pr/pr_calcia_brick.py').read())
exec(open('scripts/pn/pn_sig.py').read())
bpy.ops.wm.save_mainfile(); print('SAVED')
