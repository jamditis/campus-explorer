import bpy
for o in bpy.data.objects:
    if o.type=='MESH' and o.name.startswith(('WS191c_Lot3_S_strip_back_lawn','WS170b_Lot3_S_end_curb')):
        sm=sum(p.use_smooth for p in o.data.polygons); print('F202n',o.name[:30],'smooth',sm,'/',len(o.data.polygons),[m.type for m in o.modifiers],[s.material.name if s.material else None for s in o.material_slots],flush=True)
        o.hide_render=True
