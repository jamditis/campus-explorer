import bpy,json
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
names=['WS27_CollegeAve_carriageway_2020ortho','WS27_CollegeAve_curb_right_UNVERIFIED','WS27_CollegeAve_curb_left_UNVERIFIED','WS76_accessible_lot_asphalt_ortho2020_UNVERIFIED_edges','WS79_lot_E_patch_asphalt_ortho2020_UNVERIFIED_edges','WS96_lot_E_edge_gap_filler_asphalt_UNVERIFIED','WS75_sprague_lot_asphalt_ortho2020_UNVERIFIED_edges','WS80_sprague_lot_fill_asphalt_ortho2020_UNVERIFIED_edges','WS77_lot_median_island_MULCH_JOEphoto20261112_curb_ortho2020','Terrain_LiDAR_DTM_1m','Footpaths_OSM','WS89_CollegeAve_lot_median_CURB_concrete_UNVERIFIED','WS73_curb_back_lawn_verge_UNVERIFIED']
with bpy.data.libraries.load(p) as (s,d): d.objects=[n for n in names if n in s.objects]
X0,X1,Y0,Y1=-226,-196,-96,-60
D={}
for o in d.objects:
    mw=o.matrix_world; me=o.data
    V=[tuple(mw@v.co) for v in me.vertices]
    F=[]
    for f in me.polygons:
        c=mw@f.center
        if X0<c.x<X1 and Y0<c.y<Y1: F.append(list(f.vertices))
    used=sorted({i for f in F for i in f}); m={i:k for k,i in enumerate(used)}
    D[o.name]={'v':[V[i] for i in used],'f':[[m[i] for i in f] for f in F],'idx':used,'mats':[sl.name for sl in o.material_slots],'fm':[me.polygons[0].material_index]*0}
    print("D98",o.name,len(F),len(me.vertices), 'mods',[x.type for x in o.modifiers])
json.dump(D,open('/workspace/nj-scenes/montclair-state/scripts/ws98/dump98.json','w'))
