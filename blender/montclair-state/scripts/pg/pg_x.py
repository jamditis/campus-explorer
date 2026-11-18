import bpy,hashlib
r=bpy.data.objects['Feliciano School of Business roof (LiDAR)']; w=bpy.data.objects['Feliciano School of Business walls']; W=bpy.data.objects['Feliciano windows over the entrance pavilion (photo 08/09)']
h=hashlib.sha1(); h.update(str(len(r.data.polygons)).encode()); h.update(bytes(str([round(v.co.z,3) for v in r.data.vertices]),'ascii')); h.update(str([p.material_index for p in w.data.polygons]).encode()); h.update(str(tuple(round(c,4) for c in W.location)).encode()); h.update(str(sorted(m.name for m in bpy.data.materials)).encode())
print('XCHK',h.hexdigest()[:12])
