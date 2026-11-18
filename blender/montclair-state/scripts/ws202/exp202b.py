import bpy, numpy as np, os
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws202/fix202b.py').read())
out={}
for n in SH:
    o=bpy.data.objects[n]; a=np.empty(len(o.data.vertices)*3,dtype=np.float32); o.data.vertices.foreach_get('co',a); out[n]=a
np.savez(os.environ['OUT'],**out); print('F201 exported',len(out),flush=True)
