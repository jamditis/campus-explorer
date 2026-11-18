import bpy,hashlib
h=hashlib.sha1()
for o in sorted(bpy.data.objects,key=lambda o:o.name):
    h.update(o.name.encode()); h.update(str([m.name for m in o.modifiers]).encode()); h.update(str([s.material.name if s.material else None for s in o.material_slots]).encode())
    if o.type=='MESH' and o.name.startswith('Feliciano'):
        h.update(bytes(str([p.material_index for p in o.data.polygons]),'ascii'))
print('SIG',len(bpy.data.objects),len(bpy.data.collections),len(bpy.data.materials),len(bpy.data.node_groups),h.hexdigest()[:12])
