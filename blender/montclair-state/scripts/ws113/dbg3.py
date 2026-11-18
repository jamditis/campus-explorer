import bpy
px=bpy.data.objects['WS113_paving_tops_proxy']; vs=[v.co for v in px.data.vertices]
print('P113 proxy n',len(vs),'x %.1f..%.1f y %.1f..%.1f z %.1f..%.1f'%(min(v.x for v in vs),max(v.x for v in vs),min(v.y for v in vs),max(v.y for v in vs),min(v.z for v in vs),max(v.z for v in vs)))
b=next(o for o in bpy.data.objects if o.name.startswith('WS112_CollegeAve_S_E_walk_N_brick'))
print('P113 brick faces',len(b.data.polygons),'up',sum(1 for p in b.data.polygons if abs(p.normal.z)>0.5), 'mw',b.matrix_world.to_translation())
