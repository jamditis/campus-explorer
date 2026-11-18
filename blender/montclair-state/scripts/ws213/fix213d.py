# ws213d W36: WS70 gap-strip berm W tip (x<-252) crumpled against the lot-entrance asphalt.
# Boundary verts of the tip -> flush on the asphalt below (WS204/KY/WS67/WS27, base mesh) +1 cm; interior tip verts -> Laplacian-smoothed
# heights (boundary fixed), clamped >= asphalt+1 cm. No curb added at the tip (curbs WS69 end at x -255.5 N / -252.5 S; tip edge UNVERIFIED).
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
o=bpy.data.objects.get('WS70_gap_strip_grass_berms')
if o is None: print('F213 d WS70 missing',flush=True)
else:
    pav=[p for p in bpy.data.objects if p.type=='MESH' and p.name.startswith(('WS204_CollegeAve_lot_entrance_asphalt','KY_college_ave_carriageway','WS67_CollegeAve_gap_asphalt','WS27_CollegeAve_carriageway'))]
    T=[BVHTree.FromPolygons([p.matrix_world@v.co for v in p.data.vertices],[f.vertices[:] for f in p.data.polygons]) for p in pav]
    def az(x,y):
        best=None
        for t in T:
            h=t.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),300)
            if h[0] is not None and (best is None or h[0].z>best): best=h[0].z
        return best
    me=o.data; M=o.matrix_world; Mi=M.inverted()
    W=[M@v.co for v in me.vertices]
    ec={}
    for p in me.polygons:
        for e in p.edge_keys: ec[e]=ec.get(e,0)+1
    bnd=set(); nb={i:set() for i in range(len(W))}
    for (a,b),c in ec.items():
        nb[a].add(b); nb[b].add(a)
        if c==1: bnd.add(a); bnd.add(b)
    tip=[i for i,w in enumerate(W) if w.x<-252.0]
    Z={i:W[i].z for i in range(len(W))}; A={}
    nfl=0
    for i in tip:
        a=az(W[i].x,W[i].y); A[i]=a
        if i in bnd and a is not None: Z[i]=a+0.01; nfl+=1
    inner=[i for i in tip if i not in bnd]
    for it in range(30):
        for i in inner:
            Z[i]=0.5*Z[i]+0.5*sum(Z[j] for j in nb[i])/len(nb[i])
    for i in inner:
        if A[i] is not None: Z[i]=max(Z[i],A[i]+0.01)
    for i in tip:
        w=W[i].copy(); w.z=Z[i]; me.vertices[i].co=Mi@w
    me.update()
    print('F213 d WS70 tip verts',len(tip),'flushed boundary',nfl,'smoothed',len(inner),'pav',[p.name[:20] for p in pav],flush=True)
