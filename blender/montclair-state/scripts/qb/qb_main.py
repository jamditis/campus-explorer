# qb wrapper (session qb, Nov 2 2026). REVERT=1 -> exact qa state. ALL UNVERIFIED.
import bpy, os
REV=os.environ.get('REVERT')=='1'
def run(p): exec(compile(open(p).read(),p,'exec'),{'__name__':'__main__'})
SC=[s for s in os.environ.get('QB_SCRIPTS','qb_fade,qb_corner').split(',') if s]
for s in (reversed(SC) if REV else SC): run('scripts/qb/%s.py'%s)
print('QB_MAIN done REV',REV,'objects',len(bpy.data.objects))
exec(open('scripts/pn/pn_sig.py').read())
if os.environ.get('QBSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
if os.environ.get('QBSAVEAS'): bpy.ops.wm.save_as_mainfile(filepath=os.environ['QBSAVEAS'],copy=True); print('SAVEDAS')
