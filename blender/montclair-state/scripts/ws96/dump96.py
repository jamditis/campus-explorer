import bpy,json
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
names=['WS75_sprague_lot_asphalt_ortho2020_UNVERIFIED_edges','WS76_accessible_lot_asphalt_ortho2020_UNVERIFIED_edges','WS79_lot_E_patch_asphalt_ortho2020_UNVERIFIED_edges','WS80_sprague_lot_fill_asphalt_ortho2020_UNVERIFIED_edges','WS94_lot_slit_filler_asphalt_UNVERIFIED','WS77_lot_median_island_MULCH_JOEphoto20261112_curb_ortho2020','Terrain_LiDAR_DTM_1m']
with bpy.data.libraries.load(p) as (s,d): d.objects=[n for n in names if n in s.objects]
X0,X1,Y0,Y1=-228,-208,-104,-72
D={}
for o in d.objects:
    if o is None: continue
    mw=o.matrix_world; me=o.data
    V=[tuple(mw@v.co) for v in me.vertices]
    F=[]
    for f in me.polygons:
        c=mw@f.center
        if X0<c.x<X1 and Y0<c.y<Y1: F.append(list(f.vertices))
    used=sorted({i for f in F for i in f})
    m={i:k for k,i in enumerate(used)}
    D[o.name]={'v':[V[i] for i in used],'f':[[m[i] for i in f] for f in F],'idx':used,'mats':[s.name for s in o.material_slots]}
    print("D96",o.name,len(F))
json.dump(D,open('/workspace/nj-scenes/montclair-state/scripts/ws96/dump96.json','w'))
