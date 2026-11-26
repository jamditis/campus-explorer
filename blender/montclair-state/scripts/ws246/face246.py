import bpy, collections, os
S='/workspace/nj-scenes/montclair-state/'
N=['Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km','WS60_terrain_edge_apron_LiDAR_to_skirt']
with bpy.data.libraries.load(S+'montclair_state.blend') as (a,b): b.objects=N
for o in b.objects:
    M=o.matrix_world; me=o.data
    for nm,box in [('bank',(-232,-212,118,150)),('lawnW',(-270,-240,160,190)),('lawnN',(-240,-200,150,175)),('Eback',(-224,-205,60,118))]:
        c=collections.Counter()
        for p in me.polygons:
            v=M@p.center
            if box[0]<v.x<box[1] and box[2]<v.y<box[3]: c[me.materials[p.material_index].name if me.materials else None]+=1
        print('F246',o.name[:20],nm,dict(c),flush=True)
os._exit(0)
