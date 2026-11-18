import bpy, json
F='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(F) as (a,b):
    b.objects=[n for n in a.objects if n.startswith(('WS67_CollegeAve_gap','WS69','WS70','WS204','KY_college_ave_carriageway','WS27_CollegeAve_carr','WS205'))]
out={}
for o in b.objects:
    M=o.matrix_world; W=[M@v.co for v in o.data.vertices]; P=[]
    for p in o.data.polygons:
        c=[W[i] for i in p.vertices]
        if all(-264<w.x<-246 and -66<w.y<-48 for w in c[:1]): P.append([[round(w.x,3),round(w.y,3),round(w.z,3)] for w in c])
    out[o.name]=P
json.dump(out,open('/tmp/plot214.json','w'))
print('DONE',{k:len(v) for k,v in out.items()})
