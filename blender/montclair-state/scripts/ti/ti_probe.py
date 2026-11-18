import bpy
for m in bpy.data.materials:
    n=m.name.lower()
    if any(k in n for k in ('grid','mass','facade','stucco','brick','window','context')): print('MAT',m.name,m.users)
for o in bpy.data.objects:
    if any(k in o.name for k in ('Blanton','Stone','Bohn','Context_bld','context_b','Massing','massing')): print('OBJ',o.name,o.hide_render)
