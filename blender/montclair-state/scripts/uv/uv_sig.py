import bpy, hashlib
n=len(bpy.data.objects); nm=len(bpy.data.meshes); nmat=len(bpy.data.materials)
names='|'.join(sorted(o.name for o in bpy.data.objects if o.get('uv_obj')))
h=hashlib.sha256(names.encode()).hexdigest()[:12]
print('SIG', n, nm, nmat, h, 'uv_obj', sum(1 for o in bpy.data.objects if o.get('uv_obj')))
# also dump freeman-related names
print('FREEMAN', sorted(o.name for o in bpy.data.objects if 'freeman' in o.name.lower() or o.name.startswith('UV_')))
