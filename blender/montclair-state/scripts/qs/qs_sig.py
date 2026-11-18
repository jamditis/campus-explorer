import bpy,hashlib
h=hashlib.sha1(''.join(sorted(o.name for o in bpy.data.objects)).encode()).hexdigest()[:12]
print('QS_SIG',len(bpy.data.objects),len(bpy.data.materials),len(bpy.data.meshes),h)
