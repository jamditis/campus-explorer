# qe wrapper (session qe, Nov 2 2026). REVERT=1 -> exact qd state. ALL UNVERIFIED.
import bpy, os
def run(p): exec(compile(open(p).read(),p,'exec'),{'__name__':'__main__'})
if os.environ.get('REVERT')=='1': run('scripts/qe/qe_doorclear.py'); run('scripts/qe/qe_ccis.py')
else: run('scripts/qe/qe_ccis.py'); run('scripts/qe/qe_doorclear.py')

print('QE_MAIN done objects',len(bpy.data.objects))
exec(open('scripts/pn/pn_sig.py').read())
if os.environ.get('QESAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
if os.environ.get('QESAVEAS'): bpy.ops.wm.save_as_mainfile(filepath=os.environ['QESAVEAS'],copy=True); print('SAVEDAS')
