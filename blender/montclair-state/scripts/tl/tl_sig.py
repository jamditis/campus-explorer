import bpy
print('TLSIG',len(bpy.data.objects),len(bpy.data.materials),len(bpy.data.meshes),len(bpy.data.collections),sum(len(o.data.vertices) for o in bpy.data.objects if o.type=='MESH' and 'grass' in o.name.lower()),sorted((m.name,m.materials[0].name if m.materials and m.materials[0] else '') for m in bpy.data.meshes if m.name.startswith('TI_'))[:6])
import bpy;print('TLHID',sorted((o.name,o.hide_render,o.hide_viewport) for o in bpy.data.objects if o.name.startswith('TK_Bohn_Hall')))
