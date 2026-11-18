import bpy
src='/workspace/nj-scenes/montclair-state/montclair_state.blend'
P=('Terrain_LiDAR_DTM_1m','WS60_terrain_edge_apron','WS27_CollegeAve','KY_','LF_','ey_','KX_','LH_college','WS67_')
with bpy.data.libraries.load(src) as (fr,to): N=[n for n in fr.objects if n.startswith(P)]
with bpy.data.libraries.load(src,link=False) as (fr,to): to.objects=N
for o in to.objects: bpy.context.scene.collection.objects.link(o)
exec(compile(open('/workspace/nj-scenes/montclair-state/scripts/ws67/fix67b.py').read(),'b67','exec'))
