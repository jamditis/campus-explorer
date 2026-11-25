import bpy
for n in ['WS226_CCOM_dock_apron_lawn_shoulder_UNVERIFIED','WS240_CCOM_apron_S_corner_lawn_bank_UNVERIFIED','Terrain_LiDAR_DTM_1m','WS224_verge' ]:
    o=bpy.data.objects.get(n)
    if o: print('P240C',n,'uv',[u.name for u in o.data.uv_layers],'mats',[m.name for m in o.data.materials if m],'attrs',[a.name for a in o.data.attributes][:12],flush=True)
m=bpy.data.materials['WS70_berm_lawn_ortho_matched']
for nd in m.node_tree.nodes:
    print('P240C node',nd.type,nd.name,getattr(nd,'uv_map',''),getattr(nd,'attribute_name',''),(nd.image.name if getattr(nd,'image',None) else ''),flush=True)
us=[o.name for o in bpy.data.objects if o.type=='MESH' and any(s.material==m for s in o.material_slots)]
print('P240C users',us[:20],flush=True)
