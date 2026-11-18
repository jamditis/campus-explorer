import bpy, json
F='/workspace/nj-scenes/montclair-state/montclair_state.blend'
pre=('KX_drive_apron','et_rhd_lower_wearing','eu_rhd_ground_slab','LH_college_ave_gutter','KY_rhd_drive_side_walk','KY_college_ave_carriageway','ce_rhd_retaining','Red Hawk Deck','KY_rhd','KX_')
with bpy.data.libraries.load(F) as (a,b):
    b.objects=[n for n in a.objects if n.startswith(pre)]
out={}
for o in b.objects:
    if o is None or o.type!='MESH': continue
    M=o.matrix_world; W=[M@v.co for v in o.data.vertices]; P=[]
    for p in o.data.polygons:
        c=[W[i] for i in p.vertices]
        if -286<c[0].x<-252 and -60<c[0].y<-28 and (not o.name.startswith(('et_','Red Hawk')) or c[0].z<126.5): P.append([[round(w.x,2),round(w.y,2),round(w.z,2)] for w in c])
    if P: out[o.name]=P
json.dump(out,open('/tmp/plot35.json','w')); print('DONE',{k[:30]:len(v) for k,v in out.items()})
