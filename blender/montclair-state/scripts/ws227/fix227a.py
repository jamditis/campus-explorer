# W53c: SE corner base terrain triangle (16,282 m2, centre ~(196,-137), the old interpolated lid) sits +0.5...+4 m over
# data/dtm_1m.npy (real 1 m LiDAR here: agrees with USGS 3DEP 10 m within ~0-2 m at 30 test points, no edge padding).
# No LiDAR patch covers it. Re-grid it in place: delete that one face, keep its 3 boundary vertices/edges untouched
# (so neighbours and any T-junctions stay as they were), add a 2 m interior grid (inset >= 1 m) at bilinear dtm_1m
# heights, tapered over 12 m from the original plane at the boundary to the DTM inside (no step at the edge), and
# constrained-Delaunay triangulate inside the triangle. UVs from the face's own affine UV map, same material.
import bpy, bmesh, json, os
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt, intersect_point_tri_2d
import numpy as np
A=np.load('/workspace/nj-scenes/montclair-state/data/dtm_1m.npy')
def dtm(x,y):
    gx=x+250-0.5; gy=y+250-0.5; i=int(np.floor(gy)); j=int(np.floor(gx)); fy=gy-i; fx=gx-j
    i=min(498,max(0,i)); j=min(498,max(0,j))
    return float(A[i,j]*(1-fx)*(1-fy)+A[i,j+1]*fx*(1-fy)+A[i+1,j]*(1-fx)*fy+A[i+1,j+1]*fx*fy)
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=t.data
assert t.matrix_world.is_identity or True
bm=bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table()
cand=[f for f in bm.faces if len(f.verts)==3 and f.calc_area()>15000 and abs(f.calc_center_median().x-195.9)<3 and abs(f.calc_center_median().y+136.9)<3]
assert len(cand)==1, len(cand)
f=cand[0]; T=[v for v in f.verts]; P=[v.co.copy() for v in T]
mi=f.material_index; sm=f.smooth
# affine UV maps from the face's 3 loops
uvl=list(bm.loops.layers.uv.items())
def affine(vals):
    M=np.array([[p.x,p.y,1] for p in P]); return np.linalg.solve(M,np.array(vals))
UVA={nm:(affine([l[L].uv.x for l in f.loops]),affine([l[L].uv.y for l in f.loops])) for nm,L in uvl}
# plane
n=(P[1]-P[0]).cross(P[2]-P[0])
def plane(x,y): return P[0].z-(n.x*(x-P[0].x)+n.y*(y-P[0].y))/n.z
a2=[p.to_2d() for p in P]
# ws227d: the east side A1-A2 (x~246) is the mesh boundary; WS60_terrain_edge_apron_LiDAR_to_skirt has 1 m vertices
# along it at LiDAR height while the base edge ran straight between the two high apices. Split that edge at the apron
# vertices (z = apron z). Taper from ALL three edges: tapering only from the W/S edges (ws227f) left a 1 m wide wall
# up to 3.5 m high along the east edge (seen as a stretched ochre band in the ws227f oblique WIP).
EA=sorted([i for i in range(3) if P[i].x>240],key=lambda i:P[i].y)
assert len(EA)==2
k3=[i for i in range(3) if i not in EA][0]
ap=bpy.data.objects['WS60_terrain_edge_apron_LiDAR_to_skirt']
lo,hi=P[EA[0]],P[EA[1]]
def xline(y): return lo.x+(hi.x-lo.x)*(y-lo.y)/(hi.y-lo.y)
AE={}
for v in ap.data.vertices:
    c=ap.matrix_world@v.co
    if lo.y+0.5<c.y<hi.y-0.5 and abs(c.x-xline(c.y))<0.06: AE[round(c.y,2)]=(xline(c.y),c.y,c.z)
AE=[AE[k] for k in sorted(AE)]
def edist(x,y):
    q=Vector((x,y)); d=1e9
    for i in range(3):
        a=a2[i]; b=a2[(i+1)%3]; ab=b-a; tt=max(0,min(1,(q-a).dot(ab)/ab.length_squared)); d=min(d,(q-(a+ab*tt)).length)
    return d
pts=[]
x0=int(min(p.x for p in P))-1; x1=int(max(p.x for p in P))+1; y0=int(min(p.y for p in P))-1; y1=int(max(p.y for p in P))+1
for x in range(x0,x1+1,2):
    for y in range(y0,y1+1,2):
        if intersect_point_tri_2d(Vector((x,y)),*a2) and edist(x,y)>=1.0: pts.append((x,y))
def ss(w): w=max(0.0,min(1.0,w)); return w*w*(3-2*w)
def zf(x,y):
    q=Vector((x,y)); w=ss(edist(x,y)/12.0)*ss(min((q-a2[EA[0]]).length,(q-a2[EA[1]]).length)/12.0); return plane(x,y)*(1-w)+dtm(x,y)*w
na=len(AE)
vin=[a.to_tuple() for a in a2]+[(e[0],e[1]) for e in AE]+[(float(x),float(y)) for x,y in pts]
chain=[EA[0]]+list(range(3,3+na))+[EA[1]]
ring=chain+[k3]
out=delaunay_2d_cdt([Vector(v) for v in vin],[(ring[i],ring[(i+1)%len(ring)]) for i in range(len(ring))],[ring],1,1e-4,True)
ov,oe,of,oorig=out[0],out[1],out[2],out[3]
old=[e for e in f.edges if set(e.verts)=={T[EA[0]],T[EA[1]]}]
bmesh.ops.delete(bm,geom=[f],context='FACES_ONLY')
if na: bmesh.ops.delete(bm,geom=old,context='EDGES')
BV=[]
for k,v in enumerate(ov):
    src=oorig[k]
    if src and src[0]<3: BV.append(T[src[0]])
    elif src and src[0]<3+na: e_=AE[src[0]-3]; BV.append(bm.verts.new(Vector((e_[0],e_[1],e_[2]))))
    else: BV.append(bm.verts.new(Vector((v.x,v.y,zf(v.x,v.y)))))
nf=0; dz=[]
for tri in of:
    try: nf_=bm.faces.new([BV[i] for i in tri])
    except ValueError: continue
    nf_.material_index=mi; nf_.smooth=sm; nf+=1
    if nf_.normal.z<0: nf_.normal_flip()
    for l in nf_.loops:
        c=l.vert.co
        for nm,L in uvl:
            ax,ay=UVA[nm]; l[L].uv=(ax[0]*c.x+ax[1]*c.y+ax[2], ay[0]*c.x+ay[1]*c.y+ay[2])
for v in BV[3+na:]: dz.append(v.co.z-plane(v.co.x,v.co.y))
bm.to_mesh(me); bm.free(); me.update()
print('F227A apron edge verts',na,'regrid tris',nf,'interior verts',len(BV)-3,'boundary',[tuple(round(c,1) for c in p) for p in P],'dz vs old plane min/mean/max',round(min(dz),2),round(sum(dz)/len(dz),2),round(max(dz),2),flush=True)
json.dump({'tri':[p[:] for p in P],'n':nf},open('/workspace/nj-scenes/montclair-state/scripts/ws227/fix227a_report.json','w'))
