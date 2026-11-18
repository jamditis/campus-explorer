import bpy,json,numpy as np
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
N=['WS102_CollegeAve_S_curb_W_LiDARstep12-20cm_UNVERIFIED','WS102_CollegeAve_S_curb_E_LiDARstep12-20cm_UNVERIFIED','WS102_CollegeAve_S_carriageway_brickband_table_ortho2020_LiDAR_UNVERIFIED','Footpaths_OSM','Terrain_LiDAR_DTM_1m']
with bpy.data.libraries.load(p) as (s,d): d.objects=N
out={}
dg=bpy.context.evaluated_depsgraph_get()
for o in d.objects:
    bpy.context.scene.collection.objects.link(o)
dg.update()
for o in d.objects:
    me=o.evaluated_get(dg).to_mesh(); mw=np.array(o.matrix_world)
    V=np.empty(len(me.vertices)*3); me.vertices.foreach_get('co',V); V=V.reshape(-1,3)@mw[:3,:3].T+mw[:3,3]
    m=(V[:,0]>-245)&(V[:,0]<-205)&(V[:,1]>-250)&(V[:,1]<-155)
    idx=np.where(m)[0]; S=set(idx.tolist())
    F=[list(p.vertices) for p in me.polygons if all(k in S for k in p.vertices)]
    out[o.name]={'v':{int(i):V[i].round(3).tolist() for i in idx},'f':F}
    print('D103',o.name,len(idx),len(F))
json.dump(out,open('scripts/ws103/dump103b.json','w'))
