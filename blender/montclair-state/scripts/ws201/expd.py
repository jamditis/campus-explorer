import bpy, numpy as np, os
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws201/fix201d.py').read())
a=np.empty(len(U.data.vertices)*3,dtype=np.float32); U.data.vertices.foreach_get('co',a); np.savez(os.environ['OUT'],**{U.name:a}); print('F201 exported',flush=True)
