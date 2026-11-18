import bpy, numpy as np, os
ORIG201={}
for o in bpy.data.objects:
    if o.type=='MESH' and o.name.startswith(('WS81_lot_seam_underlay','WS94_lot_slit_filler')):
        mw=o.matrix_world; ORIG201[o.name]=[(mw@v.co).z for v in o.data.vertices]
for _pass in range(int(os.environ.get('NP','1'))): exec(open('/workspace/nj-scenes/montclair-state/scripts/ws201/fix201b.py').read())
if os.environ.get('FIXC'): exec(open('/workspace/nj-scenes/montclair-state/scripts/ws201/fix201c.py').read())
out={}
for o in SH+PA:
    a=np.empty(len(o.data.vertices)*3,dtype=np.float32); o.data.vertices.foreach_get('co',a); out[o.name]=a
np.savez(os.environ['OUT'],**out); print('F201 exported',len(out),flush=True)
