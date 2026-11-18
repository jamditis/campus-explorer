import bpy, hashlib
o=[x for x in bpy.data.objects if x.name.startswith('MI Annex RED HAWK COUNTRY 3D letters')][0]
b=[x for x in bpy.data.objects if x.name.startswith('MI Annex west wall planted bed')][0]
h=hashlib.sha1(); [h.update(('%.5f%.5f%.5f'%tuple(v.co)).encode()) for v in b.data.vertices]
h2=hashlib.sha1(); [h2.update(('%.5f%.5f%.5f'%tuple(v.co)).encode()) for v in o.data.vertices]
print('SD_SIG',len(bpy.data.objects),len(bpy.data.meshes),len(bpy.data.materials),o.data.name[-6:],len(o.data.polygons),h2.hexdigest()[:12],h.hexdigest()[:12])
