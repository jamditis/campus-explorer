# pw wrapper (session pw, Nov 1-2 2026). REVERT=1 -> exact pv2 state. ALL UNVERIFIED.
import bpy, os
REV=os.environ.get('REVERT')=='1'
def run(p): exec(compile(open(p).read(),p,'exec'),{'__name__':'__main__'})
SC=[s for s in os.environ.get('PW_SCRIPTS','pw_blinds,pw_drips,pw_cam').split(',') if s]
for s in (reversed(SC) if REV else SC): run('scripts/pw/%s.py'%s)
print('PW_MAIN done REV',REV,'objects',len(bpy.data.objects))
exec(open('scripts/pn/pn_sig.py').read())
print('MATS',sorted(m.name for m in bpy.data.materials if m.name.startswith(('PW_','PT_','PV2_'))))
if os.environ.get('PWSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
