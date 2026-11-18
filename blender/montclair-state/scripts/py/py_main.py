# py wrapper (session py, Nov 2 2026). REVERT=1 -> exact px state. ALL UNVERIFIED.
import bpy, os
REV=os.environ.get('REVERT')=='1'
def run(p): exec(compile(open(p).read(),p,'exec'),{'__name__':'__main__'})
SC=[s for s in os.environ.get('PY_SCRIPTS','py_parapet,py_cam').split(',') if s]
for s in (reversed(SC) if REV else SC): run('scripts/py/%s.py'%s)
print('PY_MAIN done REV',REV,'objects',len(bpy.data.objects))
exec(open('scripts/pn/pn_sig.py').read())
if os.environ.get('PYSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
if os.environ.get('PYSAVEAS'): bpy.ops.wm.save_as_mainfile(filepath=os.environ['PYSAVEAS'],copy=True); print('SAVEDAS')
