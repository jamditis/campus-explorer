import bpy, hashlib
exec(open('scripts/pn/pn_sig.py').read())
w=bpy.data.objects['Calcia Hall walls']; me=w.data; h=hashlib.sha1()
for v in me.vertices: h.update(('%.5f %.5f %.5f'%tuple(v.co)).encode())
for p in me.polygons: h.update(('%d %d %s'%(p.material_index,len(p.vertices),tuple(p.vertices))).encode())
for l in me.uv_layers['facade'].data: h.update(('%.4f %.4f'%tuple(l.uv)).encode())
print('DEEP calcia',len(me.vertices),len(me.polygons),[m.name for m in me.materials],h.hexdigest()[:12],'win_top',w.get('win_top'),'keys',sorted(k for k in w.keys()))
print('MATNAMES',hashlib.sha1(','.join(sorted(m.name for m in bpy.data.materials)).encode()).hexdigest()[:12],'MESHNAMES',hashlib.sha1(','.join(sorted(m.name for m in bpy.data.meshes)).encode()).hexdigest()[:12])
