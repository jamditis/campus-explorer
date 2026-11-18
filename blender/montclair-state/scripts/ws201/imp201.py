import bpy, numpy as np, os
U=[o for o in bpy.data.objects if o.name.startswith('WS81_lot_seam_underlay')][0]
a=np.load(os.environ['IMP']); U.data.vertices.foreach_set('co',a); U.data.update(); print('F201 imported',len(a)//3,flush=True)
