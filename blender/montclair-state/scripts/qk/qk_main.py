# qk wrapper (Nov 2 2026). REVERT=1 -> exact pre-qk (qj final).
import bpy, os
R=os.environ.get('REVERT')=='1'
parts=[p for p in ['scripts/qk/qk_roads.py','scripts/qk/qk_tower_fix.py','scripts/qk/qk_cams.py'] if os.path.exists(p)]
for p in (reversed(parts) if R else parts): exec(compile(open(p).read(),p,'exec'),{'__name__':'__main__'})
if os.environ.get('QKPROBE'): exec(open(os.environ['QKPROBE']).read())
exec(open('scripts/pn/pn_sig.py').read())
if os.environ.get('QKSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
if os.environ.get('QKSAVEAS'): bpy.ops.wm.save_as_mainfile(filepath=os.environ['QKSAVEAS'],copy=True); print('SAVEDAS')
