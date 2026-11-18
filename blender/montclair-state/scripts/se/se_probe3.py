import bpy
for mn in ('MH_Annex_CMU_painted_photo2016','North_wall_StudentCenterAnnex_plain_UNVERIFIED'):
    m=bpy.data.materials.get(mn); print('SE_M',mn,m and m.users,[n.type for n in m.node_tree.nodes] if m else '')
    print('SE_U',[o.name[:50] for o in bpy.data.objects if o.type=='MESH' and any(s.material==m for s in o.material_slots)])
