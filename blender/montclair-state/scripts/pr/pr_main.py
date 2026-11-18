# pr wrapper (session pr, Nov 1 2026): tier sliver snap, old-wall stub tops, downpipe brackets + splash blocks.
# + Calcia brick course size (pr_calcia_brick) + 3D slot surrounds (pr_calcia_slots). REVERT=1 -> exact pq state. ALL UNVERIFIED.
import bpy, os
REV=os.environ.get('REVERT')=='1'
def run(p):
    exec(compile(open(p).read(),p,'exec'),{'__name__':'__main__'})
if REV:
    for s in ('pr_calcia_slots','pr_calcia_brick','pr_brackets','pr_oldtop','pr_tiersnap'): run('scripts/pr/%s.py'%s)
    m=bpy.data.materials.get('PR_precast_concrete_splash_UNVERIFIED')
    if m and m.users==0: bpy.data.materials.remove(m)
else:
    for s in ('pr_tiersnap','pr_oldtop','pr_brackets','pr_calcia_brick','pr_calcia_slots'): run('scripts/pr/%s.py'%s)
print('PR_MAIN done REV',REV,'objects',len(bpy.data.objects))
exec(open('scripts/pn/pn_sig.py').read())
if os.environ.get('PRSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
