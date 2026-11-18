import bpy, resource
P='/workspace/nj-scenes/montclair-state/montclair_state.blend'
want=['T_RedMaple_L1_0158','Footpaths_OSM','Roads_OSM','Terrain_LiDAR_DTM_1m','WS142_Lot9_asphalt_OSM312845867_LiDAR2023int_ortho2020_UNVERIFI','WS145_walk_nose_lot_asphalt_LiDAR2023int','WS135a_Skyline_Way_asphalt_y-190_-284_ortho2020_edges_LiDAR2023']
with bpy.data.libraries.load(P, link=False) as (src,dst): dst.objects=list(want)
for o in dst.objects:
    for m in list(o.modifiers): o.modifiers.remove(m)
    bpy.context.scene.collection.objects.link(o)
print("RSS load",resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024)
S='/workspace/nj-scenes/montclair-state/scripts/ws148/'
exec(open(S+'fix148_53.py').read()); exec(open(S+'fix148_54.py').read()); exec(open(S+'dbg148.py').read())
print("RSS end",resource.getrusage(resource.RUSAGE_SELF).ru_maxrss//1024)
