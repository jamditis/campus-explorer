import bpy, json
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
names=['Terrain_LiDAR_DTM_1m','WS27_CollegeAve_carriageway_2020ortho','WS27_CollegeAve_curb_right','WS27_CollegeAve_curb_left','WS89_CollegeAve_lot_median_MULCH_JOEcatwalk20261112_BVH_UNVERIFIED_edges','WS89_CollegeAve_lot_median_CURB_concrete_UNVERIFIED','WS98_CollegeAve_bend_teardrop_island_MULCH_LiDAR_ortho2020_UNVERIFIED','WS75_sprague_lot_asphalt_ortho2020_UNVERIFIED_edges','WS76_accessible_lot_asphalt_ortho2020_UNVERIFIED_edges']
with bpy.data.libraries.load(p) as (s,d):
    have=[n for n in s.objects if n.startswith(tuple(names))]
    d.objects=have
sc=bpy.context.scene
for o in d.objects: sc.collection.objects.link(o)
dg=bpy.context.evaluated_depsgraph_get()
out={}
for o in d.objects:
    e=o.evaluated_get(dg); m=e.to_mesh(); mw=o.matrix_world
    vs=[(round(w.x,3),round(w.y,3),round(w.z,3)) for w in (mw@v.co for v in m.vertices) if -240<w.x<-175 and -105<w.y<-35]
    out[o.name]=vs; print('D99',o.name,len(vs)); e.to_mesh_clear()
json.dump(out,open('/workspace/nj-scenes/montclair-state/scripts/ws99/bend99.json','w'))
