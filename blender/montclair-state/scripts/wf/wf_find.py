import bpy,numpy as np
from mathutils import Vector
O=bpy.data.objects
for o in O:
    if o.type!='MESH': continue
    c=np.array([o.matrix_world@Vector(b) for b in o.bound_box])
    if c[:,0].min()<88 and c[:,0].max()>80 and c[:,1].min()<300 and c[:,1].max()>293 and (c[:,0].max()-c[:,0].min())<60:
        print('OBJ',o.name,[m.name for m in o.data.materials][:3],len(o.data.vertices),flush=True)
