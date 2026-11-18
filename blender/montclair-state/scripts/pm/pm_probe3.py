import bpy, numpy as np
from mathutils.bvhtree import BVHTree
from mathutils import Vector
r=bpy.data.objects['Feliciano School of Business roof (LiDAR)']; w=bpy.data.objects['Feliciano School of Business walls']
mw=r.matrix_world; bv=BVHTree.FromPolygons([mw@v.co for v in r.data.vertices],[p.vertices for p in r.data.polygons])
def rz(x,y):
    h=bv.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))
    return h[0].z if h[0] else None
ww=w.matrix_world; V=[ww@v.co for v in w.data.vertices]
segs=[]
for p in w.data.polygons:
    vs=[V[i] for i in p.vertices]; zt=max(v.z for v in vs)
    top=[v for v in vs if abs(v.z-zt)<0.05]
    if len(top)!=2: continue
    a,b=top; d=(b-a); d.z=0; L=d.length
    if L<0.5: continue
    nrm=Vector((-d.y,d.x,0)).normalized(); mid=(a+b)/2
    s1=[rz(*(mid+nrm*t).xy) for t in (2.5,4,6)]; s2=[rz(*(mid-nrm*t).xy) for t in (2.5,4,6)]
    segs.append((round(zt,2),round(L,1),[None if z is None else round(z,1) for z in s1],[None if z is None else round(z,1) for z in s2],tuple(round(c,1) for c in a.xy)))
for s in sorted(segs,key=lambda s:(s[0],s[4])): print(s)
