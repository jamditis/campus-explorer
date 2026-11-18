import bpy, mathutils
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    m=o.matrix_world; cs=[m@mathutils.Vector(c) for c in o.bound_box]
    b=[min(c[i] for c in cs) for i in range(3)]+[max(c[i] for c in cs) for i in range(3)]
    cx,cy=(b[0]+b[3])/2,(b[1]+b[4])/2
    if 15.3<cx<18.2 and -23.5<cy<-16.3 and b[5]-b[2]>1.5 and b[5]<143: print("WREG",o.name,[round(v,2) for v in b])
    if 17<cx<25.5 and -19.3<cy<-16.3 and b[5]-b[2]>1.5 and b[5]<143: print("NREG",o.name,[round(v,2) for v in b])
