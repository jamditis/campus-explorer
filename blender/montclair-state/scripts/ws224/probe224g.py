import bpy
for o in bpy.data.objects:
    if o.name.startswith(('WS222_CollegeAve_retur','WS27_CollegeAve_carria','WS220_CollegeAve_curb','WS27_CollegeAve_curb_left')):
        print('P224',o.name,[s.material.name if s.material else None for s in o.material_slots],[m.type for m in o.modifiers],'uv',[u.name for u in o.data.uv_layers], 'attrs',[a.name for a in o.data.attributes if not a.name.startswith('.')][:12])
