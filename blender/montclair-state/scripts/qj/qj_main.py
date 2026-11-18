# qj wrapper (Nov 2 2026). REVERT=1 -> exact pre-qj (qi final).
import bpy, os
R=os.environ.get('REVERT')=='1'
parts=['scripts/qj/qj_seam.py','scripts/qj/qj_farfield.py']+(['scripts/qj/qj_cams.py'] if os.path.exists('scripts/qj/qj_cams.py') else [])
for p in (reversed(parts) if R else parts): exec(compile(open(p).read(),p,'exec'),{'__name__':'__main__'})
exec(open('scripts/pn/pn_sig.py').read())
if os.environ.get('QJSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
if os.environ.get('QJSAVEAS'): bpy.ops.wm.save_as_mainfile(filepath=os.environ['QJSAVEAS'],copy=True); print('SAVEDAS')
