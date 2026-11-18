import bpy, hashlib
h=hashlib.sha1()
for o in sorted(bpy.data.objects,key=lambda o:o.name):
    h.update((o.name+str(o.hide_render)+str(o.hide_viewport)+str(len(o.data.vertices) if o.type=='MESH' else 0)).encode())
print('SIG',len(bpy.data.objects),len(bpy.data.materials),len(bpy.data.meshes),h.hexdigest()[:12])
