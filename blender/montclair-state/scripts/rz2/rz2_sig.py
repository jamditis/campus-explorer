import bpy,hashlib,numpy as np
h=hashlib.sha1(''.join(sorted(o.name for o in bpy.data.objects)).encode()).hexdigest()[:12]
m=hashlib.sha1()
for o in sorted(bpy.data.objects,key=lambda o:o.name):
    if o.type=='MESH' and len(o.data.vertices)<2000000:
        co=np.zeros(len(o.data.vertices)*3,np.float32); o.data.vertices.foreach_get('co',co); m.update(o.name.encode()); m.update(co.tobytes())
print('RZ2_SIG',len(bpy.data.objects),len(bpy.data.materials),len(bpy.data.meshes),h,m.hexdigest()[:16])
