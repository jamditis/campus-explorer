import bpy,hashlib
me=bpy.data.objects['Calcia Hall walls'].data; h=hashlib.sha1()
for v in me.vertices: h.update(('%.5f %.5f %.5f'%tuple(v.co)).encode())
for p in me.polygons: h.update(str(tuple(p.vertices)).encode())
for l in me.uv_layers['facade'].data: h.update(('%.4f %.4f'%tuple(l.uv)).encode())
print('COHASH',h.hexdigest()[:12],len(me.vertices),len(me.polygons),bpy.data.meshes.get('PS_backup_Calcia_walls') is not None)
