import bpy, json, math
from mathutils import Vector
CN='Center for Computing and Information Science'
P=json.load(open('north/data/day_heroes/day7_geom.json'))['buildings'][CN]['poly_m'][:-1]
n=len(P); area=sum(P[i][0]*P[(i+1)%n][1]-P[(i+1)%n][0]*P[i][1] for i in range(n))/2
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
def hits(x,y):
    out=[]; o=Vector((x,y,200)); 
    for _ in range(6):
        ok,loc,nn,i,ob,m=sc.ray_cast(dg,o,Vector((0,0,-1)))
        if not ok: break
        out.append((ob.name[:40],round(loc.z,2))); o=loc-Vector((0,0,0.01))
    return out
for i in (0,2,4,8,12,15):
    a,b=P[i],P[(i+1)%n]; ex_=b[0]-a[0]; ey=b[1]-a[1]; L=math.hypot(ex_,ey); tx,ty=ex_/L,ey/L
    nx,ny=(ty,-tx) if area>0 else (-ty,tx); m=((a[0]+b[0])/2,(a[1]+b[1])/2)
    for k in (0.5,2,6,15):
        print('E',i,k,hits(m[0]+nx*k,m[1]+ny*k))
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    if min(v.x for v in bb)<10 and max(v.x for v in bb)>-5 and min(v.y for v in bb)<230 and max(v.y for v in bb)>195 and min(v.z for v in bb)<136 and max(v.z for v in bb)>128 and (max(v.x for v in bb)-min(v.x for v in bb))<200:
        print('LOW',o.name,round(min(v.z for v in bb),1),round(max(v.z for v in bb),1),[s.material.name if s.material else None for s in o.material_slots][:4])
