import bpy, hashlib
def mh(me):
    h=hashlib.sha1()
    for v in me.vertices: h.update(('%.4f,%.4f,%.4f;'%tuple(v.co)).encode())
    h.update(str(len(me.polygons)).encode()); return h.hexdigest()[:12]
ob=bpy.data.objects
hid=hashlib.sha1(); tr=hashlib.sha1()
for o in sorted(ob,key=lambda o:o.name):
    hid.update(f'{o.name}{o.hide_render}{o.hide_viewport}'.encode())
    tr.update((o.name+' '.join('%.4f'%x for r in o.matrix_world for x in r)).encode())
print('SIG objs',len(bpy.context.scene.objects),len(ob),'walls',mh(ob['Schmitt Hall walls'].data),'eave',mh(ob['Schmitt Hall eave soffit + fascia + rafter tails'].data),
 'roof',mh(ob['Schmitt Hall roof (LiDAR)'].data),'ds',mh(ob['OH_Schmitt_downspouts_UNVERIFIED'].data),'tiles',mh(ob['Schmitt Hall barrel tile eave course'].data),'caps',mh(ob['Schmitt Hall hip + ridge cap tiles'].data),'hide',hid.hexdigest()[:12],'xf',tr.hexdigest()[:12],
 'OImats',sorted(m.name for m in bpy.data.materials if m.name.startswith('OI_')),'OImeshes',sorted(m.name for m in bpy.data.meshes if m.name.startswith('OI_')),
 'roofattrs',sorted(a.name for a in ob['Schmitt Hall roof (LiDAR)'].data.attributes if not a.name.startswith('.')))
