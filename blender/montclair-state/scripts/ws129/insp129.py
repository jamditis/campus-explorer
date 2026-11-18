import bpy
X0,X1,Y0,Y1=-242,-180,-270,-232
for o in bpy.data.objects:
    if o.type!='MESH' or len(o.data.vertices)>400000: continue
    mw=o.matrix_world
    vs=[mw@v.co for v in o.data.vertices]; vs=[v for v in vs if X0<v.x<X1 and Y0<v.y<Y1]
    if len(vs)<3: continue
    print('OBJ',o.name,len(vs),'x',round(min(v.x for v in vs),1),round(max(v.x for v in vs),1),'y',round(min(v.y for v in vs),1),round(max(v.y for v in vs),1),'z',round(min(v.z for v in vs),2),round(max(v.z for v in vs),2),[m.name for m in o.data.materials if m][:2])
