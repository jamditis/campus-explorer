import bpy, hashlib
r=bpy.data.objects['Dickson Hall roof (LiDAR)'].data
print('RMI',hashlib.sha1(bytes(p.material_index for p in r.polygons)).hexdigest()[:12],[a.name for a in r.attributes if not a.name.startswith('.')])
for mn in ('PE_Calcia_brick_slot_windows_UNVERIFIED','PE_Calcia_skirt_brick_UNVERIFIED','PE_Dickson_brick_buff_no_red_spandrel_UNVERIFIED'):
    nt=bpy.data.materials[mn].node_tree; print('MAT',mn[:20],len(nt.nodes),len(nt.links))
print('MESHNAMES',hashlib.sha1(''.join(sorted(m.name for m in bpy.data.meshes)).encode()).hexdigest()[:12], bpy.data.objects['Roof_coping'].data.name)
me=bpy.data.objects['Dickson Hall roof (LiDAR)'].data; h=hashlib.sha1()
for v in me.vertices: h.update(('%.5f %.5f %.5f'%tuple(v.co)).encode())
print('ROOFCO',h.hexdigest()[:12])
