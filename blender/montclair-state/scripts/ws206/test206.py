import bpy,os
M='/workspace/nj-scenes/montclair-state/montclair_state.blend'
PF=('WS98_','WS76_accessible_lot_asphalt','WS27_CollegeAve','WS205_','WS75_sprague_lot_asphalt','WS79_lot_E_patch','WS80_','WS81_','WS96_lot_E_edge_gap','WS94_lot_slit','WS99_lotE_padS_bed','Footpaths_OSM','WS77_lot_median_island_MULCH','WS76_lot_stall_paint_blue')
with bpy.data.libraries.load(M) as (a,b):
    b.objects=[n for n in a.objects if n.startswith(PF)]
for o in b.objects: bpy.context.scene.collection.objects.link(o)
for f in os.environ['CH'].split(): exec(open('/workspace/nj-scenes/montclair-state/scripts/'+f).read())
