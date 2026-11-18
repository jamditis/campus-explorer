import bpy
P='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(P) as (df,dt):
    names=list(df.objects)
    dt.objects=[n for n in names if not n.startswith(('T_','Tree','ShrubLeaf','WS126','WS125','WS127_CollegeAve_E_curbside_pach','Context','Terrain','Footpaths','Building','OSM_b','bld','CAM','WS1','WS2','WS3','WS4','WS5','WS6','WS7','WS8','WS9'))] + [n for n in names if n.startswith(('WS9','WS8','WS10','WS11','WS12'))]
X0,X1,Y0,Y1=-236,-188,-256,-236
for o in dt.objects:
    if o is None or o.type!='MESH' or len(o.data.vertices)>200000: continue
    mw=o.matrix_world
    vs=[mw@v.co for v in o.data.vertices]; vs=[v for v in vs if X0<v.x<X1 and Y0<v.y<Y1]
    if len(vs)<3: continue
    print('OBJ',o.name,len(vs),'x',round(min(v.x for v in vs),1),round(max(v.x for v in vs),1),'y',round(min(v.y for v in vs),1),round(max(v.y for v in vs),1),'z',round(min(v.z for v in vs),2),round(max(v.z for v in vs),2),[m.name for m in o.data.materials if m][:3])
