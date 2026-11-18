import bpy, hashlib, numpy as np
h=hashlib.sha1()
for o in sorted(bpy.data.objects,key=lambda o:o.name):
    h.update((o.name+'%.5f %.5f %.5f'%tuple(o.location)).encode())
    if o.type=='MESH' and o.name in ('Furniture contact darkening (3h)','PC_fillet_grass_points_UNVERIFIED','Terrain_LiDAR_DTM_1m'):
        a=np.zeros(len(o.data.vertices)*3,np.float32); o.data.vertices.foreach_get('co',a); h.update(a.tobytes())
print('LOCSIG',h.hexdigest()[:12])
