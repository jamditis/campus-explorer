import bpy
P='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(P) as (df,dt):
    dt.objects=[n for n in df.objects if not n.startswith(('T_','Tree','ShrubLeaf','WS126','WS125','Context','Building','OSM_b','bld','CAM','WS122_Chapin_windows','Grass','Leaf'))and 'CAM' not in n]
X0,X1,Y0,Y1=-242,-180,-270,-232
for o in dt.objects:
    if o is None or o.type!='MESH' or len(o.data.vertices)>600000: continue
    mw=o.matrix_world
    vs=[mw@v.co for v in o.data.vertices]; vs=[v for v in vs if X0<v.x<X1 and Y0<v.y<Y1]
    if len(vs)<3: continue
    print('OBJ',o.name[:70],len(vs),'x',round(min(v.x for v in vs),1),round(max(v.x for v in vs),1),'y',round(min(v.y for v in vs),1),round(max(v.y for v in vs),1),'z',round(min(v.z for v in vs),2),round(max(v.z for v in vs),2),[m.name[:30] for m in o.data.materials if m][:2])
