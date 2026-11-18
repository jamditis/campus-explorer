import bpy
from mathutils import Vector
from collections import defaultdict
dg=bpy.context.evaluated_depsgraph_get()
def bins(n):
    o=bpy.data.objects[n]; oe=o.evaluated_get(dg); m=oe.to_mesh(); d=defaultdict(list)
    for v in m.vertices:
        w=o.matrix_world@v.co
        if -250<w.x<-200 and -70<w.y<-50: d[int(w.x//3)*3].append(w)
    for k in sorted(d): vs=d[k]; print('P71',n[:30],k,'y',round(min(v.y for v in vs),2),round(max(v.y for v in vs),2),'z',round(min(v.z for v in vs),2),round(max(v.z for v in vs),2))
    oe.to_mesh_clear()
for n in ('WS27_CollegeAve_curb_left_UNVERIFIED','WS27_CollegeAve_carriageway_2020ortho'): bins(n)
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    x0,x1=min(v.x for v in bb),max(v.x for v in bb); y0,y1=min(v.y for v in bb),max(v.y for v in bb)
    if x1<-246 or x0>-205 or y1<-59.8 or y0>-50 or x1-x0>300: continue
    print('O71',o.name[:50],round(x0,1),round(x1,1),round(y0,1),round(y1,1),round(min(v.z for v in bb),1))
