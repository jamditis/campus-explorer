import bpy,os,runpy,sys
os.environ['REVERT']='1'
for s in ('scripts/qw/qw_ramp.py','scripts/qw/qw_cams.py','scripts/qw/qw_extend.py'):
    try: runpy.run_path(s,run_name='__main__')
    except SystemExit: pass
import hashlib
h=hashlib.sha1(''.join(sorted(o.name for o in bpy.data.objects)).encode()).hexdigest()[:12]
print('REV_SIG',len(bpy.data.objects),len(bpy.data.materials),len(bpy.data.meshes),h)
import numpy as np
o=bpy.data.objects['QS_footway_313027429_UNVERIFIED']; co=np.zeros(len(o.data.vertices)*3); o.data.vertices.foreach_get('co',co); print('REV_CO',round(float(co.sum()),3))
