import bpy, numpy as np
with bpy.data.libraries.load('/workspace/nj-scenes/montclair-state/montclair_state.blend') as (a,b): b.objects=['Terrain_LiDAR_DTM_1m','WS27_CollegeAve_curb_right_UNVERIFIED','WS73_curb_back_lawn_verge_UNVERIFIED','Footpaths_OSM','WS27_CollegeAve_carriageway_2020ortho']
for o in b.objects:
    mw=o.matrix_world; V=np.array([tuple(mw@v.co) for v in o.data.vertices])
    k=(V[:,0]>-222)&(V[:,0]<-195)&(V[:,1]>-116)&(V[:,1]<-86)
    print('DT',o.name,len(V),k.sum(),[m.type+':'+m.name for m in o.modifiers][:6], o.data.polygons[0].use_smooth if len(o.data.polygons) else None,flush=True)
    np.save('/workspace/nj-scenes/montclair-state/scripts/ws210/V_%s.npy'%o.name[:12],np.c_[np.nonzero(k)[0],V[k]])
