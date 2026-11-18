import bpy
im=sorted([(i.size[0]*i.size[1]*i.channels*(4 if i.is_float else 1)/1e6,i.name,tuple(i.size),i.users) for i in bpy.data.images],reverse=True)
print('IMG total MB',round(sum(x[0] for x in im)),len(im)); [print('IMG',x) for x in im[:12]]
ms=sorted([(len(o.data.vertices),o.name) for o in bpy.context.scene.objects if o.type=='MESH' and not o.hide_render],reverse=True)
print('VERTS total',sum(x[0] for x in ms)); [print('ME',x) for x in ms[:10]]
gn=[(o.name,m.name) for o in bpy.context.scene.objects for m in o.modifiers if m.type=='NODES' and not o.hide_render]; print('GN',len(gn),gn[:20])
