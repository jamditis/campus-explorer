# W53d (ws228): the SE terrain's east mesh boundary (x~246) was ONE 214 m edge from apex A1 (246.29,-248.74, +3.57 m over
# dtm_1m) to B (245.97,-35.0, ~0), plus apex A2 (245.97,-33.5, +1.75 m); fix227x/a tapered the re-grid back to that edge,
# so a ~12 m strip stayed up to 3.7 m high. Welded-by-position partner: WS60_terrain_edge_apron_LiDAR_to_skirt (long quads).
# Fix: (1) delete the terrain faces with all verts in x>=230, -249<y<-34.9 (the east strip of the fix227x/a re-grid, all
# small), drop the long boundary edge, insert boundary verts every 2 m at dtm_1m heights, snap A1/A2 (+ coincident apron
# verts) to dtm_1m, and CDT re-triangulate the outline with a 2 m interior grid at dtm_1m, blended to the old surface only
# within 4 m of the WEST/inner part of the outline. (2) split the apron's coincident inner edges at the same points (same
# z) and triangulate those apron faces, so no crack opens between terrain and apron. Raise/lower: terrain only (no paving).
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
rep={}
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=t.data
bm=bmesh.new(); bm.from_mesh(me); uvl=list(bm.loops.layers.uv.items())
A1=[v for v in bm.verts if (v.co.to_2d()-Vector((246.29,-248.74))).length<0.05][0]
Bv=[v for v in bm.verts if (v.co.to_2d()-Vector((245.97,-35.0))).length<0.05][0]
A2=[v for v in bm.verts if (v.co.to_2d()-Vector((245.97,-33.5))).length<0.05][0]
LE=[e for e in A1.link_edges if Bv in e.verts]; assert len(LE)==1 and LE[0].is_boundary
F=[f for f in bm.faces if all(v.co.x>=230 and -249<v.co.y<-34.9 for v in f.verts)]
assert LE[0].link_faces[0] in F
rep['faces']=len(F); rep['maxarea']=round(max(f.calc_area() for f in F),2)
Fs=set(F)
be=[e for f in F for e in f.edges if sum(1 for g in e.link_faces if g in Fs)==1 and e is not LE[0]]
BVs=list({v for e in be for v in e.verts}); BVset=set(BVs); vid={v:i for i,v in enumerate(BVs)}
mi=F[0].material_index; sm=F[0].smooth
bm.verts.index_update()
VV=[v.co.copy() for v in bm.verts]; BT=BVHTree.FromPolygons(VV,[[v.index for v in f.verts] for f in F])
big=max(F,key=lambda f:f.calc_area()); L3=list(big.loops)[:3]
M=np.array([[l.vert.co.x,l.vert.co.y,1] for l in L3])
UVA={nm:(np.linalg.solve(M,[l[L].uv.x for l in L3]),np.linalg.solve(M,[l[L].uv.y for l in L3])) for nm,L in uvl}
p0=Bv.co.to_2d(); p1=A1.co.to_2d(); Ltot=(p1-p0).length; nseg=int(round(Ltot/2.0))
edgepts=[p0.lerp(p1,k/nseg) for k in range(1,nseg)]
n0=len(BVs); P2=[v.co.to_2d() for v in BVs]+edgepts; n=len(P2)
CE=[(vid[e.verts[0]],vid[e.verts[1]]) for e in be]
chain=[vid[Bv]]+list(range(n0,n))+[vid[A1]]
CE+= [(chain[i],chain[i+1]) for i in range(len(chain)-1)]
def segd(q,a,b):
    ab=b-a; L2=ab.length_squared; tt=0 if L2==0 else max(0,min(1,(q-a).dot(ab)/L2)); return (q-(a+ab*tt)).length
SEG=[(P2[i],P2[j]) for i,j in CE]
def edist(q): return min(segd(q,a,b) for a,b in SEG)
INNER=[(a,b) for a,b in SEG if min(a.x,b.x)<244.0]
def idist(q): return min(segd(q,a,b) for a,b in INNER)
def inreg(x,y): return BT.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))[0] is not None
xs=np.array([p.x for p in P2]); ys=np.array([p.y for p in P2]); pts=[]
for x in range(int(xs.min()),int(xs.max())+2,2):
    for y in range(int(ys.min()),int(ys.max())+2,2):
        q=Vector((x,y))
        if inreg(x,y) and edist(q)>=1.0: pts.append(q)
out=delaunay_2d_cdt(P2+pts,CE,[],0,1e-5,True)
ov,of,oo=out[0],out[2],out[3]
of=[tri for tri in of if inreg(sum(ov[i].x for i in tri)/3,sum(ov[i].y for i in tri)/3)]
loop=BVs
FV=set(v for f in F for v in f.verts); FE=set(e for f in F for e in f.edges)
bmesh.ops.delete(bm,geom=F,context='FACES_ONLY')
bm.edges.remove(LE[0]); FE.discard(LE[0])
# drop the old interior edges/verts left loose by the face delete (only this region's own geometry)
for e in [e for e in FE if e.is_valid and not e.link_faces and not (e.verts[0] in BVset and e.verts[1] in BVset)]: bm.edges.remove(e)
for v in [v for v in FV if v.is_valid and not v.link_edges]: bm.verts.remove(v)
snap={}
for V in (A1,A2):
    z=dtm(V.co.x,V.co.y); snap[(round(V.co.x,2),round(V.co.y,2))]=(V.co.z,z); V.co.z=z
BV=[]; dz=[]; EZ={}
for k,v in enumerate(ov):
    s=oo[k]
    if s and s[0]<n0: BV.append(loop[s[0]]); continue
    q=Vector((v.x,v.y))
    if s and s[0]<n:
        z=dtm(v.x,v.y); EZ[round(v.y,3)]=(v.x,z); BV.append(bm.verts.new(Vector((v.x,v.y,z)))); continue
    h=BT.ray_cast(Vector((v.x,v.y,400)),Vector((0,0,-1))); z0=h[0].z if h[0] else dtm(v.x,v.y)
    w=ss(idist(q)/4.0); z=z0*(1-w)+dtm(v.x,v.y)*w; dz.append(z-z0)
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
rep.update(outline=n0,edgepts=len(edgepts),interior=len(pts),tris=nf,snap={str(k):[round(a,2),round(b,2)] for k,(a,b) in snap.items()},
  dz=[round(min(dz or [0]),2),round(sum(dz)/max(1,len(dz)),2),round(max(dz or [0]),2)])
A2xy=A2.co.to_2d(); Bxyz=Bv.co.copy()
bm.to_mesh(me); bm.free(); me.update()
# apron
o=bpy.data.objects['WS60_terrain_edge_apron_LiDAR_to_skirt']; ab=bmesh.new(); ab.from_mesh(o.data)
for V in ab.verts:
    for (sx,sy),(z0,z1) in snap.items():
        if abs(V.co.x-sx)<0.02 and abs(V.co.y-sy)<0.02: V.co.z=z1
na=0; touched=set()
pA2=A2xy; EZ[round(Bxyz.y,3)]=(Bxyz.x,Bxyz.z)
def online(c): return abs(segd(c.to_2d(),pA2,p1))<0.03  # apron inner edge runs A1->A2 directly (B is on it within 3 mm)
for e in [e for e in ab.edges if online(e.verts[0].co) and online(e.verts[1].co)]:
    ya,yb=sorted([e.verts[0].co.y,e.verts[1].co.y])
    ins=sorted([yy for yy in EZ if ya+0.05<yy<yb-0.05])
    if not ins: continue
    touched.update(e.link_faces)
    va=e.verts[0] if e.verts[0].co.y<e.verts[1].co.y else e.verts[1]; cur=e
    for yy in ins:
        x,z=EZ[yy]; other=cur.other_vert(va)
        fac=(yy-va.co.y)/(other.co.y-va.co.y)
        ne,nv=bmesh.utils.edge_split(cur,va,fac); nv.co=Vector((x,yy,z)); na+=1
        cur=[g for g in nv.link_edges if other in g.verts][0]; va=nv
touched=[f for f in touched if f.is_valid]
if touched: bmesh.ops.triangulate(ab,faces=touched,quad_method='BEAUTY',ngon_method='BEAUTY')
ab.to_mesh(o.data); ab.free(); o.data.update()
rep['apron_split_verts']=na; rep['apron_faces_triangulated']=len(touched)
print('F228A',json.dumps(rep),flush=True)
json.dump(rep,open('/workspace/nj-scenes/montclair-state/scripts/ws228/fix228a_report.json','w'))
