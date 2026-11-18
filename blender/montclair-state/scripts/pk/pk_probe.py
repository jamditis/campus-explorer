import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
w=bpy.data.objects['Feliciano School of Business walls']; mw=w.matrix_world; R=mw.to_3x3()
ws=[mw@v.co for v in w.data.vertices]
X0=min(v.x for v in ws)-10; X1=max(v.x for v in ws)+10; Y0=min(v.y for v in ws)-10; Y1=max(v.y for v in ws)+10
C=Vector(((X0+X1)/2,(Y0+Y1)/2,0)); print('BOX',round(X0),round(X1),round(Y0),round(Y1))
def mk(name):
    T=bpy.data.objects[name]; tm=T.matrix_world; tv=[tm@v.co for v in T.data.vertices]
    ins=[X0<=v.x<=X1 and Y0<=v.y<=Y1 for v in tv]
    polys=[list(p.vertices) for p in T.data.polygons if any(ins[i] for i in p.vertices)]
    used=sorted({i for p in polys for i in p}); rm={o:n for n,o in enumerate(used)}
    print(name,len(polys))
    return BVHTree.FromPolygons([tv[i] for i in used],[[rm[i] for i in p] for p in polys]) if polys else None
bt=mk('Terrain_LiDAR_DTM_1m'); 
dg=bpy.context.evaluated_depsgraph_get(); s=bpy.context.scene
cnt={}
for p in w.data.polygons:
    n=(R@p.normal).normalized(); pc=mw@p.center
    if abs(n.z)>0.2: continue
    if Vector((n.x,n.y,0)).dot(Vector((pc.x-C.x,pc.y-C.y,0)))<0: n=-n
    nh=Vector((n.x,n.y,0)).normalized()
    a,b=sorted([mw@w.data.vertices[v].co for v in p.vertices],key=lambda v:v.z)[:2]
    if (a-b).length<0.2: continue
    m=(a+b)/2
    q=m+nh*0.8
    h=bt.ray_cast(Vector((q.x,q.y,q.z+6)),Vector((0,0,-1)),40)
    hs=s.ray_cast(dg,Vector((q.x,q.y,q.z+6)),Vector((0,0,-1)),distance=40)
    tz=round(h[0].z-m.z,2) if h[0] is not None else None
    sz=(round(hs[1].z-m.z,2),hs[4].name[:28]) if hs[0] else None
    if sz and sz[0]<-0.1: print('GAP',p.index,round(m.x,1),round(m.y,1),round(m.z,2),'nh',round(nh.x,2),round(nh.y,2),'T',tz,'S',sz)
