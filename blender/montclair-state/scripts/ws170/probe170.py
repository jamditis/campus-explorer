import bpy
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(p) as (a,b):
    names=[n for n in a.objects if n.startswith(('WS163','WS110','WS162','WS166_','WS84','WS85','NK86'))]
    b.objects=[n for n in names]
print('N',len(names))
for o in b.objects:
    if o is None or o.type!='MESH': continue
    vs=[o.matrix_world@v.co for v in o.data.vertices]
    near=[v for v in vs if -322<v.x<-266 and -280<v.y<-258]
    if near:
        print('OBJ',o.name,len(near),'ymin %.2f ymax %.2f'%(min(v.y for v in near),max(v.y for v in near)),flush=True)
