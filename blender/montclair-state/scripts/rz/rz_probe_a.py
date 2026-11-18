import bpy
print('ANX',[(o.name[:50],o.hide_render) for o in bpy.data.objects if 'nnex' in o.name][:15])
