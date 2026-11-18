# pv wrapper (session pv, Nov 1 2026). REVERT=1 -> exact pu state. ALL UNVERIFIED.
import bpy, os
REV=os.environ.get('REVERT')=='1'
def run(p): exec(compile(open(p).read(),p,'exec'),{'__name__':'__main__'})
SC=[s for s in os.environ.get('PV_SCRIPTS','pv_accents,pv_clipped,pv_cam,pv_pent').split(',') if s]
for s in (reversed(SC) if REV else SC): run('scripts/pv/%s.py'%s)
print('PV_MAIN done REV',REV,'objects',len(bpy.data.objects))
exec(open('scripts/pn/pn_sig.py').read())
_a=[o for o in bpy.data.collections['DK_pier_accents_20261015aq'].objects][0]; print('ACC',_a.hide_render,_a.hide_viewport,sorted(_a.keys()))
print('MESHN',len(bpy.data.meshes),'CAMN',len(bpy.data.cameras))
if os.environ.get('PVSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
