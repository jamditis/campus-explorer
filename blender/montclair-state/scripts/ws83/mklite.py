import bpy
M='/workspace/nj-scenes/montclair-state/montclair_state.blend'
want=['Footpaths_OSM','WS82_sprague_lane_onesurface_asphalt_ortho2020_UNVERIFIED_edges','WS75_sprague_lot_asphalt_ortho2020_UNVERIFIED_edges','WS80_sprague_lot_fill_asphalt_ortho2020_UNVERIFIED_edges']
with bpy.data.libraries.load(M,link=False) as (src,dst):
    allc=[n for n in src.objects if 'curb' in n.lower()]
    print('P83 curbobs',allc[:60])
    dst.objects=[n for n in want if n in src.objects]
for o in dst.objects:
    if o: bpy.context.scene.collection.objects.link(o)
print('P83 loaded',[o.name for o in dst.objects if o])
bpy.ops.wm.save_as_mainfile(filepath='/workspace/nj-scenes/montclair-state/scripts/ws83/lite83.blend')
