import bpy,json
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(p) as (s,d): d.objects=['Terrain_LiDAR_DTM_1m','Footpaths_OSM']
T=d.objects[0]; mw=T.matrix_world
out=[(i,*(mw@v.co)) for i,v in enumerate(T.data.vertices) if -235<(mw@v.co).x<-185 and -125<(mw@v.co).y<-60]
json.dump(out,open('/workspace/nj-scenes/montclair-state/scripts/ws98/terr98.json','w'))
F=d.objects[1]; print("FP mods",[(m.name,m.node_group.name if m.node_group else None) for m in F.modifiers])
print("T mods",[(m.name,m.node_group.name if m.node_group else None) for m in T.modifiers]); print("TD",len(out))
