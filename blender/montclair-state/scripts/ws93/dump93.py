import bpy,json
names=[o.name for o in bpy.data.objects if o.type=='MESH' and any(o.name.startswith(p) for p in ('WS74_cogen_lot_asphalt','WS75_sprague_lot_asphalt','WS76_accessible_lot_asphalt','WS80_sprague_lot_fill','WS79_lot_E_patch','WS81_lot_seam_underlay'))]
D={}
for n in names:
    o=bpy.data.objects[n]; mw=o.matrix_world
    D[n]={'v':[list(mw@v.co) for v in o.data.vertices],'f':[list(p.vertices) for p in o.data.polygons],'mat':[p.material_index for p in o.data.polygons],'mats':[m.name if m else None for m in o.data.materials]}
json.dump(D,open('scripts/ws93/dump93.json','w')); print('D93',len(D))
