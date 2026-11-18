import bpy,json
P='/workspace/nj-scenes/montclair-state/scripts/ws127/cut127.blend'
pre=('WS112','WS111','WS102_CollegeAve_S_curb_E','WS127_CollegeAve_E_curbside_bed','WS115','WS116','WS27','WS110_ground','Footpaths_OSM','WS85','WS103')
with bpy.data.libraries.load(P) as (df,dt):
    dt.objects=[n for n in df.objects if n.startswith(pre)]
X0,X1,Y0,Y1=-256,-216,-256,-224
out={}
for o in dt.objects:
    if o is None or o.type!='MESH': continue
    mw=o.matrix_world; V=[mw@v.co for v in o.data.vertices]; L=[]
    for p in o.data.polygons:
        if p.normal.z<0.5: continue
        c=[V[i] for i in p.vertices]
        if any(X0<v.x<X1 and Y0<v.y<Y1 for v in c): L.append([(round(v.x,3),round(v.y,3),round(v.z,3)) for v in c])
    if L: out[o.name]=L; print('PL',o.name,len(L))
json.dump(out,open('/workspace/nj-scenes/montclair-state/scripts/ws128/plan128.json','w'))
