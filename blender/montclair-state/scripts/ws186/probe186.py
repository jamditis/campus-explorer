import bpy
from mathutils import Vector
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    M=o.matrix_world; R=M.to_3x3(); st=[]
    for p in o.data.polygons:
        c=M@p.center
        if -337<c.x<-322 and -238<c.y<-224:
            n=(R@p.normal).normalized()
            if abs(n.z)<0.6 and p.area>0.005: st.append((round(c.x,1),round(c.y,1),round(c.z,2),round(n.z,2),round(p.area,2)))
    if st: print('PROBE186W',o.name[:40],len(st),st[:8],flush=True)
