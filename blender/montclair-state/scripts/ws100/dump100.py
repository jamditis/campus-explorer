import bpy, json
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
pre=('WS35_Kasser','WS35_Cole_steps','WS27_','WS40_','WS73_curb_back_lawn','WS89_Kasser','WS89_Cole_curved','COLE_plaza','WS98_','WS92_','WS72b_Kasser','Cole Hall plaza pavilion','Cole Hall west portico')
with bpy.data.libraries.load(p) as (s,d): d.objects=[n for n in s.objects if n.startswith(pre) and 'helper' not in n]
dg=bpy.context.evaluated_depsgraph_get()
out={}
X0,X1,Y0,Y1=-218,-180,-112,-60
for o in d.objects:
    if o.type!='MESH': continue
    bpy.context.scene.collection.objects.link(o)
dg.update()
for o in d.objects:
    if o.type!='MESH': continue
    e=o.evaluated_get(dg); m=e.to_mesh(); mw=o.matrix_world
    V=[mw@v.co for v in m.vertices]; fs=[]
    for f in m.polygons:
        P=[V[j] for j in f.vertices]
        cx=sum(q.x for q in P)/len(P); cy=sum(q.y for q in P)/len(P)
        if X0<cx<X1 and Y0<cy<Y1: fs.append([[round(q.x,2),round(q.y,2),round(q.z,2)] for q in P])
    out[o.name]=fs; print('D100',o.name[:50],len(fs))
    e.to_mesh_clear()
json.dump(out,open('/workspace/nj-scenes/montclair-state/scripts/ws100/dump100.json','w'))
