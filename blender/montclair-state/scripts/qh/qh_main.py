# qh wrapper (Nov 2 2026). REVERT=1 runs the parts in reverse order -> exact pre-qh (qg final).
import bpy, os
R=os.environ.get('REVERT')=='1'
parts=['scripts/qh/qh_fixnan.py','scripts/qh/qh_terrain.py','scripts/qh/qh_reseat.py']
if os.path.exists('scripts/qh/qh_east.py'): parts.append('scripts/qh/qh_east.py')
for p in (reversed(parts) if R else parts): exec(compile(open(p).read(),p,'exec'),{'__name__':'__main__'})
exec(open('scripts/pn/pn_sig.py').read())
if os.environ.get('QHSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
if os.environ.get('QHSAVEAS'): bpy.ops.wm.save_as_mainfile(filepath=os.environ['QHSAVEAS'],copy=True); print('SAVEDAS')
