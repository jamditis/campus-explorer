import bpy, os
R=os.environ.get('REVERT')=='1'
parts=[p for p in ['scripts/qm/qm_cels.py','scripts/qm/qm_terrain.py','scripts/qm/qm_fix.py','scripts/qm/qm_cams.py'] if os.path.exists(p)]
for p in (reversed(parts) if R else parts): exec(compile(open(p).read(),p,'exec'),{'__name__':'__main__'})
exec(open('scripts/pn/pn_sig.py').read())
if os.environ.get('QMSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
