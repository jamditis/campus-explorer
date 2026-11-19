import bpy
for o in bpy.data.objects:
    if o.name.startswith(('KY_college_ave_carriageway','WS67_CollegeAve_gap_asphalt','WS214_N_berm','WS214_berm','WS27_')) and o.type=='MESH':
        print('P219B',o.name[:50],[s.material.name if s.material else None for s in o.material_slots],len(o.data.vertices),'uv',[u.name for u in o.data.uv_layers],[m.type for m in o.modifiers],flush=True)
for mn in set(s.material.name for o in bpy.data.objects if o.name.startswith(('KY_college_ave_carriageway','WS67_CollegeAve_gap_asphalt')) for s in o.material_slots if s.material):
    m=bpy.data.materials[mn]
    print('P219B mat',mn,[(n.type,n.label or n.name) for n in m.node_tree.nodes][:14] if m.node_tree else None,flush=True)
