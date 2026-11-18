import bpy
F='/workspace/nj-scenes/montclair-state/montclair_state.blend'
names=None
with bpy.data.libraries.load(F) as (a,b):
    b.objects=[n for n in a.objects if n.startswith(('WS67','WS69','WS70','WS204','KY_college_ave_carriageway','WS68_RHD'))]
for o in b.objects:
    me=o.data; M=o.matrix_world
    W=[M@v.co for v in me.vertices]
    near=[w for w in W if -262<w.x<-250 and -62<w.y<-52]
    print('OBJ',o.name,len(W),len(me.polygons),[m.type+':'+m.name for m in o.modifiers],[m.name for m in me.materials],'near',len(near))
    if o.name.startswith(('WS67','WS69','WS70')) and near:
        for w in sorted(near,key=lambda w:(round(w.x,1),w.y))[:80]: print('  V',o.name[:6],round(w.x,2),round(w.y,2),round(w.z,3))
