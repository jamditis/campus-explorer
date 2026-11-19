# W53d follow-up (ws228, runs AFTER fix228a): snapping apices A1 (246.29,-248.74) and A2 (245.97,-33.5) to dtm_1m dragged
# the remaining long fan slivers incident to them (up to 199 m long, pre-ws227 base triangulation) down to 1.4 m UNDER the
# DTM along their length (and the south boundary sliver from A1). Region = every face incident to A1/A2 plus every face
# sharing an edge with those (so no outline edge touches an apex); mesh-boundary outline edges > 4 m get boundary verts every
# 2 m at dtm_1m (with the same split applied to the coincident WS60 apron edges); CDT re-triangulate with a 2 m interior grid
# at dtm_1m, blended back to the old surface within 4 m of the INTERIOR (non-boundary) outline edges.
import bpy, bmesh, json
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
def segd(q,a,b):
    ab=b-a; L2=ab.length_squared; tt=0 if L2==0 else max(0,min(1,(q-a).dot(ab)/L2)); return (q-(a+ab*tt)).length
rep={}
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=t.data
bm=bmesh.new(); bm.from_mesh(me); uvl=list(bm.loops.layers.uv.items())
AP=[[v for v in bm.verts if (v.co.to_2d()-Vector(P)).length<0.05][0] for P in [(246.29,-248.74),(245.97,-33.5)]]
F0=set(f for V in AP for f in V.link_faces)
F=set(F0)
for f in F0:
    for e in f.edges:
        for g in e.link_faces: F.add(g)
F=[f for f in F if f.calc_area()<15000]; Fs=set(F)
rep['faces']=len(F); rep['area']=round(sum(f.calc_area() for f in F)); rep['maxarea']=round(max(f.calc_area() for f in F),1)
be=[e for f in F for e in f.edges if sum(1 for g in e.link_faces if g in Fs)==1]
assert not any(V in e.verts for e in be for V in AP if not e.is_boundary), 'apex on interior outline'
mi=max(F,key=lambda f:f.calc_area()).material_index; sm=F[0].smooth
bm.verts.index_update()
VV=[v.co.copy() for v in bm.verts]; BT=BVHTree.FromPolygons(VV,[[v.index for v in f.verts] for f in F])
big=max(F,key=lambda f:f.calc_area()); L3=list(big.loops)[:3]
M=np.array([[l.vert.co.x,l.vert.co.y,1] for l in L3])
UVA={nm:(np.linalg.solve(M,[l[L].uv.x for l in L3]),np.linalg.solve(M,[l[L].uv.y for l in L3])) for nm,L in uvl}
BVs=list({v for e in be for v in e.verts}); vid={v:i for i,v in enumerate(BVs)}
P2=[v.co.to_2d() for v in BVs]; n0=len(P2); CE=[]; SPL=[]; INNER=[]; killE=[]
for e in be:
    a,b=e.verts; pa=a.co.to_2d(); pb=b.co.to_2d(); L=(pb-pa).length
    if e.is_boundary and L>4.0:
        k=int(round(L/2.0)); ids=[vid[a]]
        for j in range(1,k):
            q=pa.lerp(pb,j/k); P2.append(q); ids.append(len(P2)-1)
        ids.append(vid[b]); CE+=[(ids[j],ids[j+1]) for j in range(len(ids)-1)]; SPL.append((pa,pb)); killE.append(e)
    else:
        CE.append((vid[a],vid[b]))
        if not e.is_boundary: INNER.append((pa,pb))
n=len(P2)
SEG=[(P2[i],P2[j]) for i,j in CE]
def edist(q): return min(segd(q,a,b) for a,b in SEG)
def idist(q): return min([segd(q,a,b) for a,b in INNER] or [1e9])
def inreg(x,y): return BT.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0] is not None
xs=np.array([p.x for p in P2]); ys=np.array([p.y for p in P2]); pts=[]
for x in range(int(xs.min()),int(xs.max())+2,2):
    for y in range(int(ys.min()),int(ys.max())+2,2):
        q=Vector((x,y))
        if inreg(x,y) and edist(q)>=1.0: pts.append(q)
out=delaunay_2d_cdt(P2+pts,CE,[],0,1e-5,True)
ov,of,oo=out[0],out[2],out[3]
of=[tri for tri in of if inreg(sum(ov[i].x for i in tri)/3,sum(ov[i].y for i in tri)/3)]
FV=set(v for f in F for v in f.verts); FE=set(e for f in F for e in f.edges)
bmesh.ops.delete(bm,geom=F,context='FACES_ONLY')
for e in killE:
    if e.is_valid and not e.link_faces: bm.edges.remove(e)
for e in [e for e in FE if e.is_valid and not e.link_faces and e not in be]: bm.edges.remove(e)
for v in [v for v in FV if v.is_valid and not v.link_edges]: bm.verts.remove(v)
BV=[]; dz=[]; EP=[]
for k,v in enumerate(ov):
    s=oo[k]; q=Vector((v.x,v.y))
    if s and s[0]<n0: BV.append(BVs[s[0]]); continue
    if s and s[0]<n:
        z=dtm(v.x,v.y); EP.append(Vector((v.x,v.y,z))); BV.append(bm.verts.new(Vector((v.x,v.y,z)))); continue
    h=BT.ray_cast(Vector((v.x,v.y,400)),Vector((0,0,-1))); z0=h[0].z if h[0] else dtm(v.x,v.y)
    w=ss(idist(q)/4.0); z=z0*(1-w)+dtm(v.x,v.y)*w; dz.append(z-z0)
    BV.append(bm.verts.new(Vector((v.x,v.y,z))))
nf=0; areas=[]
for tri in of:
    try: f=bm.faces.new([BV[i] for i in tri])
    except ValueError: continue
    f.material_index=mi; f.smooth=sm; nf+=1; areas.append(f.calc_area())
    if f.normal.z<0: f.normal_flip()
    for l in f.loops:
        c=l.vert.co
        for nm,L in uvl:
            ax,ay=UVA[nm]; l[L].uv=(ax[0]*c.x+ax[1]*c.y+ax[2],ay[0]*c.x+ay[1]*c.y+ay[2])
rep.update(boundary_split_edges=len(SPL),edgepts=len(EP),interior=len(pts),tris=nf,big_tris_gt20=sum(1 for a in areas if a>20),maxtri=round(max(areas),1),
  dz=[round(min(dz or [0]),2),round(sum(dz)/max(1,len(dz)),2),round(max(dz or [0]),2)])
bm.to_mesh(me); bm.free(); me.update()
o=bpy.data.objects['WS60_terrain_edge_apron_LiDAR_to_skirt']; ab=bmesh.new(); ab.from_mesh(o.data)
na=0; touched=set(); NV=[]
for pa,pb in SPL:
    on=lambda c: segd(c.to_2d(),pa,pb)<0.03
    ins=[p for p in EP if segd(p.to_2d(),pa,pb)<0.01]
    for e in [e for e in ab.edges if e.link_faces and on(e.verts[0].co) and on(e.verts[1].co)]:  # skip the apron's pre-existing loose edges
        a0,b0=e.verts; d=(b0.co.to_2d()-a0.co.to_2d()); L=d.length
        if L<0.1: continue
        tl=sorted([( (p.to_2d()-a0.co.to_2d()).dot(d)/L/L, p) for p in ins],key=lambda r:r[0])
        tl=[r for r in tl if 0.002<r[0]<0.998]
        if not tl: continue
        touched.update(e.link_faces); va=a0; cur=e; t0=0.0
        for tt,p in tl:
            fac=(tt-t0)/(1-t0); ne,nv=bmesh.utils.edge_split(cur,va,fac); nv.co=p.copy(); na+=1; NV.append(nv)
            cur=[g for g in nv.link_edges if b0 in g.verts][0]; va=nv; t0=tt
touched=list({f for v in NV if v.is_valid for f in v.link_faces})
if touched: bmesh.ops.triangulate(ab,faces=touched,quad_method='BEAUTY',ngon_method='BEAUTY')
ab.to_mesh(o.data); ab.free(); o.data.update()
rep['apron_split_verts']=na; rep['apron_faces_triangulated']=len(touched)
print('F228C',json.dumps(rep),flush=True)
json.dump(rep,open('/workspace/nj-scenes/montclair-state/scripts/ws228/fix228c_report.json','w'))
