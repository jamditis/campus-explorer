# qa wrapper (session qa, Nov 2 2026). REVERT=1 -> exact pz state. ALL UNVERIFIED.
import bpy, os
REV=os.environ.get('REVERT')=='1'
def run(p): exec(compile(open(p).read(),p,'exec'),{'__name__':'__main__'})
SC=[s for s in os.environ.get('QA_SCRIPTS','qa_gaps,qa_cam').split(',') if s]
for s in (reversed(SC) if REV else SC): run('scripts/qa/%s.py'%s)
print('QA_MAIN done REV',REV,'objects',len(bpy.data.objects))
exec(open('scripts/pn/pn_sig.py').read())
if os.environ.get('QASAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
if os.environ.get('QASAVEAS'): bpy.ops.wm.save_as_mainfile(filepath=os.environ['QASAVEAS'],copy=True); print('SAVEDAS')
