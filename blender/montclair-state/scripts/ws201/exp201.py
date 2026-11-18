import bpy, numpy as np, os
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws201/fix201.py').read())
U=[o for o in bpy.data.objects if o.name.startswith('WS81_lot_seam_underlay')][0]
a=np.empty(len(U.data.vertices)*3,dtype=np.float32); U.data.vertices.foreach_get('co',a); np.save(os.environ['OUT'],a); print('F201 exported',len(a)//3,flush=True)
