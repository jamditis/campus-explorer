import bpy,hashlib
h=hashlib.sha1(''.join(sorted(o.name for o in bpy.data.objects)).encode()).hexdigest()[:12]
print('QY_SIG',len(bpy.data.objects),len(bpy.data.materials),len(bpy.data.meshes),h)
