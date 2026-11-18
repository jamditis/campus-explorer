import bpy
from mathutils import Vector
X0,X1,Y0,Y1=-244,-232,-248,-232
for o in bpy.data.objects:
    if o.type!='MESH': continue
    mw=o.matrix_world
    vs=[mw@v.co for v in o.data.vertices if X0<(mw@v.co).x<X1 and Y0<(mw@v.co).y<Y1]
    if not vs: continue
    print('OBJ',o.name,len(vs),'z',round(min(v.z for v in vs),2),round(max(v.z for v in vs),2),'x',round(min(v.x for v in vs),2),round(max(v.x for v in vs),2),'y',round(min(v.y for v in vs),2),round(max(v.y for v in vs),2),[m.name for m in o.data.materials][:4], [m.type for m in o.modifiers])
