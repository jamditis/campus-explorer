import bpy,os
M='/workspace/nj-scenes/montclair-state/montclair_state.blend'
PF=('WS98_','WS99_lotE_padS_bed','WS27_CollegeAve','Terrain_LiDAR_DTM_1m','Footpaths_OSM')
with bpy.data.libraries.load(M) as (a,b):
    b.objects=[n for n in a.objects if n.startswith(PF)]
for o in b.objects: bpy.context.scene.collection.objects.link(o)
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws205/fix205a.py').read())
