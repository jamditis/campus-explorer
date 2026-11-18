import bpy
exec(open('scripts/pr/pr_oldtop.py').read())
exec(open('scripts/pn/pn_sig.py').read())
bpy.ops.wm.save_mainfile(); print('SAVED')
