import bpy, hashlib
s=[len(bpy.data.objects),len(bpy.data.materials),len(bpy.data.meshes),len(bpy.data.collections),len(bpy.data.cameras)]
st=sorted((o.name,[x.material.name if x.material else '' for x in o.material_slots]) for o in bpy.data.objects if any(k in o.name for k in ('Stone','Blanton','TR_')))
h=hashlib.sha1(repr(st).encode()+repr(sorted(o.name for o in bpy.data.objects)).encode()+repr(sorted(m.name for m in bpy.data.materials)).encode()).hexdigest()[:12]
print('TRSIG',*s,h)
