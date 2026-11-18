import bpy,hashlib
L=[]
for o in sorted(bpy.data.objects,key=lambda o:o.name):
    L.append((o.name,tuple(round(x,4) for x in o.location),o.data.name if o.data else ''))
L.append(len(bpy.data.meshes)); L.append(len(bpy.data.materials))
print('TUSIG',hashlib.md5(repr(L).encode()).hexdigest(),len(bpy.data.objects))
