import bpy,os
exec(open('scripts/pq/pq_snap.py').read())
exec(open('scripts/pq/pq_probe.py').read())
exec(open('scripts/pn/pn_sig.py').read())
if os.environ.get('PQSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
