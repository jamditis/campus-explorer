import bpy,hashlib
h=hashlib.sha1()
for n in ('Feliciano School of Business roof (LiDAR)','Feliciano School of Business walls'):
    o=bpy.data.objects[n]; h.update(bytes([p.material_index for p in o.data.polygons])); h.update(str([s.material.name for s in o.material_slots]).encode()); h.update(str(sorted(o.keys())).encode())
print('SIG',len(bpy.data.objects),len(bpy.data.materials),h.hexdigest()[:12])
