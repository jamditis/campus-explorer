# pt wrapper (session pt, Nov 1 2026). REVERT=1 -> exact ps state. ALL UNVERIFIED.
import bpy, os
REV=os.environ.get('REVERT')=='1'
def run(p): exec(compile(open(p).read(),p,'exec'),{'__name__':'__main__'})
SC=[s for s in os.environ.get('PT_SCRIPTS','pt_calcia_glazing,pt_feliciano_seam,pt_nw_gutter,pt_calcia_topfill').split(',') if s]
for s in (reversed(SC) if REV else SC): run('scripts/pt/%s.py'%s)
for n in ('PT_blind_slats_offwhite_UNVERIFIED','PT_blind_rail_grey_UNVERIFIED'):
    m=bpy.data.materials.get(n)
    if REV and m and m.users==0: bpy.data.materials.remove(m)
print('PT_MAIN done REV',REV,'objects',len(bpy.data.objects))
exec(open('scripts/pn/pn_sig.py').read())
exec(open('scripts/pt/pt_cohash.py').read())
if os.environ.get('PTSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
