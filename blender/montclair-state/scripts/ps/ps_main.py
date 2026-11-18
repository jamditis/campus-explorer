# ps wrapper (session ps, Nov 1 2026). REVERT=1 -> exact pr state. ALL UNVERIFIED.
import bpy, os
REV=os.environ.get('REVERT')=='1'
def run(p): exec(compile(open(p).read(),p,'exec'),{'__name__':'__main__'})
SC=[s for s in os.environ.get('PS_SCRIPTS','ps_calcia_recess').split(',') if s]
for s in (reversed(SC) if REV else SC): run('scripts/ps/%s.py'%s)
for n in ('PS_precast_reveal_tan_UNVERIFIED','PS_slot_glass_tinted_UNVERIFIED','PS_slot_interior_dark_UNVERIFIED'):
    m=bpy.data.materials.get(n)
    if REV and m and m.users==0: bpy.data.materials.remove(m)
print('PS_MAIN done REV',REV,'objects',len(bpy.data.objects))
exec(open('scripts/pn/pn_sig.py').read())
if os.environ.get('PSSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
