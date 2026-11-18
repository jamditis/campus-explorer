import bpy, hashlib
s=[len(bpy.data.objects),len(bpy.data.materials),len(bpy.data.meshes),len(bpy.data.collections),len(bpy.data.cameras)]
keys=[]
for o in bpy.data.objects:
    n=o.name
    if n.startswith('Cole ') or n.startswith('COLE_') or n.startswith('Susan A. Cole') or n.startswith('TW_') or (o.type=='CAMERA' and ('cole' in n.lower() or n.startswith('TW_'))):
        keys.append((n,[x.material.name if x.material else '' for x in o.material_slots]))
keys.sort()
h=hashlib.sha1(repr(keys).encode()+repr(sorted(o.name for o in bpy.data.objects)).encode()+repr(sorted(m.name for m in bpy.data.materials)).encode()).hexdigest()[:12]
print('TWSIG',*s,h)
