# pv2 wrapper (session pv pass 2, Nov 1 2026). REVERT=1 -> exact pv state. ALL UNVERIFIED.
import bpy, os
REV=os.environ.get('REVERT')=='1'
def run(p): exec(compile(open(p).read(),p,'exec'),{'__name__':'__main__'})
SC=[s for s in os.environ.get('PV2_SCRIPTS','pv2_dickson_recess,pv2_cam').split(',') if s]
for s in (reversed(SC) if REV else SC): run('scripts/pv/%s.py'%s)
m=bpy.data.materials.get('PV2_reveal_buff_UNVERIFIED')
if REV and m and m.users==0: bpy.data.materials.remove(m)
print('PV2_MAIN done REV',REV,'objects',len(bpy.data.objects))
exec(open('scripts/pn/pn_sig.py').read())
exec(open('scripts/pv/pv2_cohash.py').read())
if os.environ.get('PVSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
