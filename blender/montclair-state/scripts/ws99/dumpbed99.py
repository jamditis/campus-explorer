import bpy, json
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
pre=('Footpaths_OSM','WS98_lotE_raised','WS77_lot_median','WS75_sprague','WS80_sprague','WS76_access','WS79_lot','WS40_CollegeAve_east','WS27_CollegeAve_curb_left','WS27_CollegeAve_carriageway','WS73_curb_back_lawn')
with bpy.data.libraries.load(p) as (s,d):
    d.objects=[n for n in s.objects if n.startswith(pre)]
sc=bpy.context.scene
for o in d.objects: sc.collection.objects.link(o)
dg=bpy.context.evaluated_depsgraph_get(); out={}
for o in d.objects:
    e=o.evaluated_get(dg); m=e.to_mesh(); mw=o.matrix_world; V=[mw@v.co for v in m.vertices]; F=[]
    for f in m.polygons:
        pts=[V[i] for i in f.vertices]
        if any(-222<q.x<-200 and -100<q.y<-84 for q in pts): F.append([[round(q.x,3),round(q.y,3),round(q.z,3)] for q in pts])
    out[o.name]=F; print('B99',o.name,len(F)); e.to_mesh_clear()
json.dump(out,open('/workspace/nj-scenes/montclair-state/scripts/ws99/bedctx99.json','w'))
