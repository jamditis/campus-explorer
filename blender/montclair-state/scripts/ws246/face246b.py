import bpy, collections, os, json
S='/workspace/nj-scenes/montclair-state/'
BB=json.load(open(S+'scripts/ws205/bbox205.json'))
N=[n for n,v in BB.items() if v[0]=='MESH' and n.startswith(('M3a_','M3b_','Terrain','WS6','WS60','PK_','PZ_Fel','Context_skirt')) and not (v[3]<-335 or v[2]>-195 or v[5]<20 or v[4]>95)]
with bpy.data.libraries.load(S+'montclair_state.blend') as (a,b): b.objects=N
for o in b.objects:
    M=o.matrix_world; me=o.data
    for nm,box in [('Send',(-250,-225,40,62)),('Sfield',(-335,-250,20,50)),('W',(-335,-300,50,180))]:
        c=collections.Counter()
        for p in me.polygons:
            v=M@p.center
            if box[0]<v.x<box[1] and box[2]<v.y<box[3]: c[me.materials[p.material_index].name if me.materials else None]+=1
        if c: print('F246',o.name[:30],nm,dict(c),'uv',[u.name for u in me.uv_layers],flush=True)
os._exit(0)
