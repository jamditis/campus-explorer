# qc wrapper (session qc, Nov 2 2026). REVERT=1 -> exact qb state. ALL UNVERIFIED.
import bpy, os
REV=os.environ.get('REVERT')=='1'
def run(p): exec(compile(open(p).read(),p,'exec'),{'__name__':'__main__'})
SC=[s for s in os.environ.get('QC_SCRIPTS','qc_cornerbay,qc_stepfill,qc_cam').split(',') if s]
for s in (reversed(SC) if REV else SC): run('scripts/qc/%s.py'%s)
print('QC_MAIN done REV',REV,'objects',len(bpy.data.objects))
exec(open('scripts/pn/pn_sig.py').read())
if os.environ.get('QCSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
if os.environ.get('QCSAVEAS'): bpy.ops.wm.save_as_mainfile(filepath=os.environ['QCSAVEAS'],copy=True); print('SAVEDAS')
