import bpy
from mathutils import Vector
OB=bpy.data.objects
def wbox(o):
    c=[o.matrix_world@Vector(v) for v in o.bound_box]; return min(v.x for v in c),max(v.x for v in c),min(v.y for v in c),max(v.y for v in c),min(v.z for v in c),max(v.z for v in c)
for o in OB:
    if o.type!='MESH' or o.hide_render: continue
    n=o.name.lower()
    if not any(k in n for k in ('curb','gutter','median','edge','walk','sidewalk','collegeave','road')): continue
    try: b=wbox(o)
    except: continue
    if b[1]<-300 or b[0]>-150 or b[3]<-140 or b[2]>-40: continue
    print('P90',o.name,len(o.data.vertices),len(o.data.polygons),[m.type for m in o.modifiers],tuple(round(v,1) for v in b),o.parent.name if o.parent else '')
