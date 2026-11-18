import bpy, numpy as np, os
d=np.load(os.environ['IMP'])
for n in d.files:
    o=bpy.data.objects[n]; o.data.vertices.foreach_set('co',d[n]); o.data.update()
print('F201 imported',len(d.files),flush=True)
