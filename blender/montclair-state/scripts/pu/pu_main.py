# pu wrapper (session pu, Nov 1 2026). REVERT=1 -> exact pt state. ALL UNVERIFIED.
import bpy, os
REV=os.environ.get('REVERT')=='1'
def run(p): exec(compile(open(p).read(),p,'exec'),{'__name__':'__main__'})
SC=[s for s in os.environ.get('PU_SCRIPTS','pu_dickson_frames,pu_cam,pu_dickson_topstrip,pu_coping,pu_calcia_heads,pu_mortar,pu_dickson_midcoping').split(',') if s]
for s in (reversed(SC) if REV else SC): run('scripts/pu/%s.py'%s)
print('PU_MAIN done REV',REV,'objects',len(bpy.data.objects))
exec(open('scripts/pn/pn_sig.py').read())
exec(open('scripts/pt/pt_cohash.py').read())
import hashlib as _h
for _on in ('Roof_coping',):
    _me=bpy.data.objects[_on].data; _x=_h.sha1()
    for _v in _me.vertices: _x.update(('%.5f %.5f %.5f'%tuple(_v.co)).encode())
    print('COHASH',_on,_x.hexdigest()[:12],len(_me.vertices),[m.name for m in _me.materials])
_r=bpy.data.objects['Dickson Hall roof (LiDAR)']; print('ROOFUV',[u.name for u in _r.data.uv_layers],sorted(_r.keys()))
_w=bpy.data.objects['Dickson Hall walls']; print('WINTOP',_w['win_top'],sorted(_w.keys()))
if os.environ.get('PUSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
