import bpy
from mathutils.bvhtree import BVHTree
from mathutils import Vector
from collections import Counter
O=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(pre)]
T=[(o.name[:6],BVHTree.FromPolygons([o.matrix_world@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons])) for o in O]
x0,x1,y0,y1=-270,-212,-108,-64; st=0.1; G={}
for i in range(int((x1-x0)/st)):
    for j in range(int((y1-y0)/st)):
        x=x0+i*st; y=y0+j*st; best=None
        for n,t in T:
            h=t.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))
            if h[0] and (best is None or h[0].z>best[1]): best=(n,h[0].z)
        if best: G[(i,j)]=best
diff=0; sw=0
for (i,j),(n,z) in G.items():
    for di,dj in ((1,0),(0,1)):
        q=G.get((i+di,j+dj))
        if q and q[0]!=n:
            sw+=1
            if abs(q[1]-z)>0.02: diff+=1
print("P94S AFTER objswitch",sw,"steps>2cm",diff)
