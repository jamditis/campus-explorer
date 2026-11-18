import bpy, os
R=os.environ.get('REVERT')=='1'
parts=['scripts/ql/ql_fix.py','scripts/ql/ql_drape.py','scripts/ql/ql_column.py']+(['scripts/ql/ql_cams.py'] if os.path.exists('scripts/ql/ql_cams.py') else [])
for p in (reversed(parts) if R else parts): exec(compile(open(p).read(),p,'exec'),{'__name__':'__main__'})
exec(open('scripts/pn/pn_sig.py').read())
if os.environ.get('QLSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
