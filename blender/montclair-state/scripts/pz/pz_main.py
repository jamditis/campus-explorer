# pz wrapper (session pz, Nov 2 2026). REVERT=1 -> exact py state. ALL UNVERIFIED.
import bpy, os
REV=os.environ.get('REVERT')=='1'
def run(p): exec(compile(open(p).read(),p,'exec'),{'__name__':'__main__'})
SC=[s for s in os.environ.get('PZ_SCRIPTS','pz_parapet,pz_swfeather,pz_cam').split(',') if s]
for s in (reversed(SC) if REV else SC): run('scripts/pz/%s.py'%s)
print('PZ_MAIN done REV',REV,'objects',len(bpy.data.objects))
exec(open('scripts/pn/pn_sig.py').read())
if os.environ.get('PZSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
if os.environ.get('PZSAVEAS'): bpy.ops.wm.save_as_mainfile(filepath=os.environ['PZSAVEAS'],copy=True); print('SAVEDAS')
