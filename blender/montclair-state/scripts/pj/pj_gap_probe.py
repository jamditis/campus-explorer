import bpy
from mathutils import Vector
s=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
w=bpy.data.objects['Feliciano School of Business walls']; mw=w.matrix_world; R=mw.to_3x3()
ws=[mw@v.co for v in w.data.vertices]; C=Vector(((min(v.x for v in ws)+max(v.x for v in ws))/2,(min(v.y for v in ws)+max(v.y for v in ws))/2,0))
out=[]
for p in w.data.polygons:
    n=(R@p.normal).normalized(); pc=mw@p.center
    if abs(n.z)>0.2: continue
    if Vector((n.x,n.y,0)).dot(Vector((pc.x-C.x,pc.y-C.y,0)))<0: n=-n
    nh=Vector((n.x,n.y,0)).normalized()
    vs=sorted([mw@w.data.vertices[v].co for v in p.vertices],key=lambda v:v.z)[:2]
    gs=[]
    for v in vs:
        h=s.ray_cast(dg,v+nh*0.8+Vector((0,0,4)),Vector((0,0,-1)),distance=30)
        gs.append((round(h[1].z-v.z,2),h[4].name[:25]) if h[0] else None)
    out.append((p.index,round(nh.x,2),round(nh.y,2),[round(v.z,2) for v in vs],gs))
for o in out:
    if any(g and g[0]< -0.1 for g in o[4]): print('GAP',o)
print('N',len(out))
