# qg wrapper: terrain north-strip LiDAR patch, then re-run qf (CCIS plinth/cams depend on the ground). REVERT=1 reverts qg then re-runs qf.
import bpy, os
exec(compile(open('scripts/qg/qg_terrain.py').read(),'scripts/qg/qg_terrain.py','exec'),{'__name__':'__main__'})
if os.environ.get('NOQF')!='1':
    os.environ.pop('REVERT',None) if os.environ.get('REVERT')=='1' and False else None
    _rev=os.environ.pop('REVERT',None)
    exec(compile(open('scripts/qf/qf_ccis.py').read(),'scripts/qf/qf_ccis.py','exec'),{'__name__':'__main__'})
    if _rev: os.environ['REVERT']=_rev
exec(compile(open('scripts/qg/qg_details.py').read(),'scripts/qg/qg_details.py','exec'),{'__name__':'__main__'})
print('QG_MAIN done objects',len(bpy.data.objects))
exec(open('scripts/pn/pn_sig.py').read())
if os.environ.get('QGSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
if os.environ.get('QGSAVEAS'): bpy.ops.wm.save_as_mainfile(filepath=os.environ['QGSAVEAS'],copy=True); print('SAVEDAS')
