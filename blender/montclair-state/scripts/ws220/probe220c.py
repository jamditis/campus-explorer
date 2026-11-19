import bpy
for o in bpy.data.objects:
    if o.type!='MESH': continue
    if not (o.name.startswith('WS69') or o.name.startswith('WS27_CollegeAve_curb_left') or o.name.startswith('WS72_Kasser_SW') or o.name.startswith('WS70_gap')): continue
    M=o.matrix_world
    V=[M@v.co for v in o.data.vertices]
    sel=[(round(v.x,2),round(v.y,2),round(v.z,2)) for v in V if -252<=v.x<=-245 and -57.5<=v.y<=-52.5]
    print('P220C',o.name,len(V),[m.type+':'+m.name for m in o.modifiers],[s.material.name if s.material else None for s in o.material_slots],flush=True)
    for s in sorted(sel)[:80]: print('P220V',o.name[:12],s)
