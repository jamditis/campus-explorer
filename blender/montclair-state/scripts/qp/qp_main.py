import bpy, os
R=os.environ.get('REVERT')=='1'
for p in (['scripts/qp/qp_richardson.py']):
    exec(compile(open(p).read(),p,'exec'),{'__name__':'__main__'})
exec(open('scripts/pn/pn_sig.py').read())
if os.environ.get('QPSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
elif os.environ.get('QPSAVEAS'): bpy.ops.wm.save_as_mainfile(filepath=os.environ['QPSAVEAS'],copy=True); print('SAVED_AS')
