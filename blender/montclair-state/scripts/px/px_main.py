# px wrapper (session px, Nov 2 2026). REVERT=1 -> exact pw state. ALL UNVERIFIED.
import bpy, os
REV=os.environ.get('REVERT')=='1'
def run(p): exec(compile(open(p).read(),p,'exec'),{'__name__':'__main__'})
SC=[s for s in os.environ.get('PX_SCRIPTS','px_parapet,px_clipped,px_blinds').split(',') if s]
for s in (reversed(SC) if REV else SC): run('scripts/px/%s.py'%s)
print('PX_MAIN done REV',REV,'objects',len(bpy.data.objects))
exec(open('scripts/pn/pn_sig.py').read())
if os.environ.get('PXSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
