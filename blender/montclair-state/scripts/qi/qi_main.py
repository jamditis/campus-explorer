# qi wrapper (Nov 2 2026). REVERT=1 -> exact pre-qi (qh final).
import bpy, os
R=os.environ.get('REVERT')=='1'
parts=['scripts/qi/qi_east.py','scripts/qi/qi_cams.py']
for p in (reversed(parts) if R else parts): exec(compile(open(p).read(),p,'exec'),{'__name__':'__main__'})
exec(open('scripts/pn/pn_sig.py').read())
if os.environ.get('QISAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
if os.environ.get('QISAVEAS'): bpy.ops.wm.save_as_mainfile(filepath=os.environ['QISAVEAS'],copy=True); print('SAVEDAS')
