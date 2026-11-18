# qd wrapper (session qd, Nov 2 2026). REVERT=1 -> exact qc state. ALL UNVERIFIED.
import bpy, os
REV=os.environ.get('REVERT')=='1'
def run(p): exec(compile(open(p).read(),p,'exec'),{'__name__':'__main__'})
SC=[s for s in os.environ.get('QD_SCRIPTS','qd_skirtdip,qd_sliver').split(',') if s]
for s in (reversed(SC) if REV else SC): run('scripts/qd/%s.py'%s)
print('QD_MAIN done REV',REV,'objects',len(bpy.data.objects),'ngroups',len(bpy.data.node_groups))
exec(open('scripts/pn/pn_sig.py').read())
if os.environ.get('QDSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
if os.environ.get('QDSAVEAS'): bpy.ops.wm.save_as_mainfile(filepath=os.environ['QDSAVEAS'],copy=True); print('SAVEDAS')
