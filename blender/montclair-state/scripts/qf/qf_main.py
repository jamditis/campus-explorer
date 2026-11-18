# qf wrapper (session qf, Nov 2 2026). REVERT=1 -> exact qe state. Photo-based kind, positions approximate / UNVERIFIED.
import bpy, os
exec(compile(open('scripts/qf/qf_ccis.py').read(),'scripts/qf/qf_ccis.py','exec'),{'__name__':'__main__'})
print('QF_MAIN done objects',len(bpy.data.objects))
exec(open('scripts/pn/pn_sig.py').read())
if os.environ.get('QFSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
if os.environ.get('QFSAVEAS'): bpy.ops.wm.save_as_mainfile(filepath=os.environ['QFSAVEAS'],copy=True); print('SAVEDAS')
