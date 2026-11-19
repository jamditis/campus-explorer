# W53d (SE fan slivers, runs BEFORE fix227a): the residual SE high ground is long sliver fans radiating from two base apex
# vertices on the mesh boundary, A1 (246.3,-248.7) +3.6 m and A2 (246.0,-33.5) +1.5-1.8 m over dtm_1m. Both apices are
# welded to WS60_terrain_edge_apron_LiDAR_to_skirt, so they stay put (snapping them alone, ws227b, left the slivers up to
# 3 m UNDER the DTM; splitting the sliver edges, fix227y, blew up WS63's level-6 subdivision to 8.6 M faces).
# Per apex: take its fan faces (minus the fix227a triangle), delete them, keep the union outline (verts and edges
# untouched), and constrained-Delaunay re-triangulate the outline with a 2 m interior grid (inset >= 1 m) at bilinear
# dtm_1m heights, blended back to the old surface within 6 m of the outline and 12 m of the apex.
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import delaunay_2d_cdt
import numpy as np
A=np.load('/workspace/nj-scenes/montclair-state/data/dtm_1m.npy')
def dtm(x,y):
    gx=x+250-0.5; gy=y+250-0.5; i=int(np.floor(gy)); j=int(np.floor(gx)); fy=gy-i; fx=gx-j
    i=min(498,max(0,i)); j=min(498,max(0,j))
    return float(A[i,j]*(1-fx)*(1-fy)+A[i,j+1]*fx*(1-fy)+A[i+1,j]*(1-fx)*fy+A[i+1,j+1]*fx*fy)
def ss(w): w=max(0.0,min(1.0,w)); return w*w*(3-2*w)
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=t.data
bm=bmesh.new(); bm.from_mesh(me)
uvl=list(bm.loops.layers.uv.items())
rep=[]
for AP in (Vector((246.29,-248.74)),Vector((245.97,-33.5))):
    ap=[v for v in bm.verts if (v.co.to_2d()-AP).length<0.05]; assert len(ap)==1
    ap=ap[0]
    F=[f for f in ap.link_faces if f.calc_area()<15000]
    Fs=set(F)
    be=[e for f in F for e in f.edges if sum(1 for g in e.link_faces if g in Fs)==1]
    adj={}
    for e in be:
        a,b=e.verts; adj.setdefault(a,[]).append(b); adj.setdefault(b,[]).append(a)
    if any(len(n)!=2 for n in adj.values()): rep.append(('skip non-simple outline',AP[:])); continue
    loop=[ap]; prev=None
    while True:
        nx=[n for n in adj[loop[-1]] if n is not prev][0]
        if nx is ap: break
        prev=loop[-1]; loop.append(nx)
    if len(loop)!=len(adj): rep.append(('skip loop',len(loop),len(adj))); continue
    mi=F[0].material_index; sm=F[0].smooth
    B=BVHTree.FromPolygons([v.co.copy() for v in bm.verts],[[v.index for v in f.verts] for f in F]) if False else None
    bm.verts.index_update()
    VV=[v.co.copy() for v in bm.verts]; B=BVHTree.FromPolygons(VV,[[v.index for v in f.verts] for f in F])
    # affine UV from the largest fan face
    big=max(F,key=lambda f:f.calc_area()); L3=list(big.loops)[:3]
    M=np.array([[l.vert.co.x,l.vert.co.y,1] for l in L3])
    UVA={nm:(np.linalg.solve(M,[l[L].uv.x for l in L3]),np.linalg.solve(M,[l[L].uv.y for l in L3])) for nm,L in uvl}
    P2=[v.co.to_2d() for v in loop]; n=len(P2)
    xs=[p.x for p in P2]; ys=[p.y for p in P2]
    PX=np.array([p.x for p in P2]); PY=np.array([p.y for p in P2]); QX=np.roll(PX,-1); QY=np.roll(PY,-1)
    def inside(x,y):
        c=((PY>y)!=(QY>y)); xi=PX+(y-PY)*(QX-PX)/np.where(QY-PY==0,1e-12,QY-PY)
        return bool(np.sum(c&(x<xi))%2)
    def edist(q):
        d=1e9
        for i in range(n):
            a=P2[i]; b=P2[(i+1)%n]; ab=b-a; L2=ab.length_squared
            tt=0 if L2==0 else max(0,min(1,(q-a).dot(ab)/L2)); d=min(d,(q-(a+ab*tt)).length)
        return d
    pts=[]
    for x in range(int(min(xs)),int(max(xs))+2,2):
        for y in range(int(min(ys)),int(max(ys))+2,2):
            q=Vector((x,y))
            if inside(x,y) and edist(q)>=1.0: pts.append(q)
    vin=P2+pts
    out=delaunay_2d_cdt(vin,[(i,(i+1)%n) for i in range(n)],[list(range(n))],1,1e-5,True)
    ov,of,oo=out[0],out[2],out[3]
    bmesh.ops.delete(bm,geom=F,context='FACES_ONLY')
    BV=[]; dz=[]
    for k,v in enumerate(ov):
        s=oo[k]
        if s and s[0]<n: BV.append(loop[s[0]]); continue
        q=Vector((v.x,v.y)); h=B.ray_cast(Vector((v.x,v.y,400)),Vector((0,0,-1)))
        z0=h[0].z if h[0] else dtm(v.x,v.y)
        w=ss(edist(q)/6.0)*ss((q-AP).length/12.0); z=z0*(1-w)+dtm(v.x,v.y)*w; dz.append(z-z0)
        BV.append(bm.verts.new(Vector((v.x,v.y,z))))
    nf=0
    for tri in of:
        try: f=bm.faces.new([BV[i] for i in tri])
        except ValueError: continue
        f.material_index=mi; f.smooth=sm; nf+=1
        if f.normal.z<0: f.normal_flip()
        for l in f.loops:
            c=l.vert.co
            for nm,L in uvl:
                ax,ay=UVA[nm]; l[L].uv=(ax[0]*c.x+ax[1]*c.y+ax[2],ay[0]*c.x+ay[1]*c.y+ay[2])
    rep.append((tuple(round(c,1) for c in AP),'fan faces',len(F),'outline',n,'interior',len(pts),'tris',nf,'dz min/mean/max',round(min(dz or [0]),2),round(sum(dz)/max(1,len(dz)),2),round(max(dz or [0]),2)))
bm.to_mesh(me); bm.free(); me.update()
for r in rep: print('F227X',r,flush=True)
