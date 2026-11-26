import bpy, os
for n in ('Lamp_acorn_031','WS252_W63c_Lamp_acorn_ortho2020_UNVERIFIED'):
    o=bpy.data.objects.get(n)
    print('L252',n,o.type,o.data.name if o.data else None,'dims',tuple(round(a,2) for a in o.dimensions),'loc',tuple(round(a,2) for a in o.matrix_world.translation),'hr',o.hide_render,'hv',o.hide_viewport,'cols',[c.name for c in o.users_collection],'mods',[m.name for m in o.modifiers],'inst',o.instance_type,flush=True)
os._exit(0)
