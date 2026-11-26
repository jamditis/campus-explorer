import bpy, os
for o in bpy.context.scene.objects:
    k=[m.name for m in o.modifiers if m.show_render]
    ps=[p.name for p in getattr(o,'particle_systems',[])]
    if k or ps: print('P246K',o.name[:40],o.type,len(o.data.vertices) if o.type=='MESH' else '',k[:6],len(k),ps,flush=True)
big=sorted([(len(o.data.vertices),o.name) for o in bpy.context.scene.objects if o.type=='MESH'],reverse=True)[:15]
print('P246K big',big,flush=True)
os._exit(0)
