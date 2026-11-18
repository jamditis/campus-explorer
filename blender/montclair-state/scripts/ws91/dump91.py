import bpy,json
names=[o.name for o in bpy.data.objects if o.type=='MESH' and any(o.name.startswith(p) for p in ('WS89_CollegeAve_lot_median','WS77_lot_median','WS74_cogen_lot_asphalt','WS75_sprague','WS76_accessible_lot_asphalt','WS80_sprague_lot_fill','WS71_Kasser_S_sidewalk','WS72_Kasser_SW','WS72b_Kasser_S_sidewalk','WS73_curb_back_lawn','WS83_sprague_lane_walk','WS83_lane_gutter','WS76_lot_stall_paint','WS76_lot_zebra'))]
D={}
for n in names:
    o=bpy.data.objects[n]; mw=o.matrix_world
    D[n]={'v':[list(mw@v.co) for v in o.data.vertices],'f':[list(p.vertices) for p in o.data.polygons],'mat':[p.material_index for p in o.data.polygons],'mats':[m.name if m else None for m in o.data.materials]}
json.dump(D,open('scripts/ws91/dump91.json','w')); print('D91',len(D))
