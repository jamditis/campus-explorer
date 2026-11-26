import bpy, os
for n in ('Lamp_acorn_031','WS252_W63c_Lamp_acorn_ortho2020_UNVERIFIED','Lamp_acorn_074'):
    o=bpy.data.objects.get(n)
    if not o: print('L252B none',n); continue
    print('L252B',n,'cam',o.visible_camera,'diff',o.visible_diffuse,'mats',[m.name if m else None for m in o.data.materials],'lib',o.data.library,'users',o.data.users,flush=True)
os._exit(0)
