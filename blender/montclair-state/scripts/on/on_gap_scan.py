import bpy
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
w=bpy.data.objects['Schmitt Hall walls']; me=w.data; M=w.matrix_world
for f in me.polygons:
    if abs(f.normal.z)>0.1 or f.area<1: continue
    vs=[M@me.vertices[i].co for i in f.vertices]; zt=max(v.z for v in vs)
    top=[v for v in vs if v.z>zt-0.3]; m=sum(top,Vector())/len(top)
    n=(M.to_3x3()@f.normal).normalized()
    for s in (1,-1):
        p=Vector((m.x,m.y,zt+0.02))-Vector((n.x,n.y,0))*0.15*s
        h,l,nn,i,ob,mx=sc.ray_cast(dg,p,Vector((0,0,1)))
        if h and ob.name.startswith('Schmitt Hall roof') and l.z-zt>0.8:
            print('GAP',f.index,round(m.x,2),round(m.y,2),round(zt,2),'roof',round(l.z,2),'side',s)
