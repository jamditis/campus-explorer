import bpy
for o in bpy.data.objects:
    if o.name.startswith('PJ_Feliciano_'): print('MOD',o.name,o.type,[ (m.type,m.name) for m in getattr(o,'modifiers',[])],o.parent.name if o.parent else None,tuple(round(x,2) for x in o.matrix_world.translation))
