# ws216 W35c part 3: the WS215 walk's W edge beside the KX deck drive apron stands up to ~0.3 m above the apron near the road
# (a 30 cm vertical face; a standard NJ curb reveal is 15 cm) with a 0.3-1.0 m gap to the apron (y -50..-47).
# Design (rev 2, AGENTS.md rule 6: raise paving, never lower it): close the gap by moving the walk's W-edge column to the apron edge
# (walk grade unchanged), then RAISE the apron's E-edge strip so the walk stands a standard 15 cm curb above it, tapering to the
# apron's own plane over 1.0 m. Rev 1 (eased the walk DOWN onto the apron) is fix216b_lower_REJECTED.py.
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def ob(p): return next((o for o in bpy.data.objects if o.name.startswith(p)),None)
SL=ob('WS215_RHD_SE_core_street_level_sidewalk'); AP=ob('KX_drive_apron'); KY=ob('KY_college_ave_carriageway_asphalt (')
def bvh(o,top=False):
    M=o.matrix_world; P=[p for p in o.data.polygons if (not top) or (M.to_3x3()@p.normal).z>0.7]
    return BVHTree.FromPolygons([M@v.co for v in o.data.vertices],[p.vertices[:] for p in P])
def ray(t,x,y):
    h=t.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),300); return h[0].z if h[0] is not None else None
ta=bvh(AP,top=True); tk=bvh(KY)
M=SL.matrix_world; Mi=M.inverted(); W=[M@v.co for v in SL.data.vertices]
top=[w for w in W if w.z>124.2]
zmax=max(w.z for w in W); 
# W edge per 0.25 m y-bin (top verts only: z within 0.2 of local max -> use per-bin max z cluster)
bins={}
for w in W:
    k=round(w.y*4)/4
    if k not in bins or w.x<bins[k][0]: bins[k]=(w.x,)
def xedge(y):
    k=min(bins,key=lambda b:abs(b-y)); return bins[k][0]
# S edge (southmost per 0.5 m x-bin)
sb={}
for w in W:
    k=int((w.x+300)/0.5)
    if k not in sb or w.y<sb[k]: sb[k]=w.y
def sedge(x): return sb[min(sb,key=lambda k:abs(k-int((x+300)/0.5)))]
# top z per (x,y) column = max z of verts at that xy
col={}
for i,w in enumerate(W):
    key=(round(w.x,3),round(w.y,3)); col.setdefault(key,[]).append(i)
for yy in (-52.5,-51.5,-50.5,-49.5,-48.5,-47.5,-46.5):
    xe=xedge(yy); print('F216b dbg y',yy,'xe',round(xe,2),'walk',[round(ray(bvh(SL,top=True),xe+dd,yy) or 0,3) for dd in (0.05,0.5,1.0)],'apron',[round(ray(ta,xe-dd,yy) or 0,3) for dd in (0.05,0.12,0.3,0.6,1.0)],flush=True)
# W edge: close the 0.3-1.0 m gap to the apron (y -50..-47) by moving the W-edge column to the apron E edge (+2 cm under it),
# then ease the walk to apron + 3 cm at that edge, tapering back to its own grade over 1.5 m (driveway-side flare).
TS=bvh(SL,top=True); n=0; mv=0
def xapron(y,xe):
    for i in range(0,61):
        x=xe-0.02*i
        if ray(ta,x,y) is not None: return x
    return None
EDGE={}
for key,idx in col.items():
    x,y=key
    if y>-46.6 or y<-50.6: continue
    xe=xedge(y)
    if abs(x-xe)>0.01: continue
    xa=xapron(y,xe)
    if xa is None or xe-xa<0.03: continue
    for i in idx: SL.data.vertices[i].co=Mi@Vector((xa-0.04,W[i].y,W[i].z)); W[i]=Vector((xa-0.04,W[i].y,W[i].z))
    EDGE[round(y,3)]=(xa-0.04,ray(ta,xa+0.0,y)); mv+=1
print('F216b W-edge columns moved to apron edge',mv,flush=True)
# AGENTS.md rule 6 (raise paving, never lower it; Codex review on PR #7): the walk keeps its grade. Instead the apron's E-edge strip is
# raised so the walk stands a standard 15 cm curb above it, tapering back to the apron's own plane over 1.0 m.
ys=sorted(EDGE)
TS=bvh(SL,top=True)
Ma=AP.matrix_world; Mai=Ma.inverted(); na=0; mx_=0
for v in AP.data.vertices:
    w=Ma@v.co
    if w.z<123.0 or not (-50.6<=w.y<=-46.6): continue
    k=min(ys,key=lambda b:abs(b-w.y)) if ys else None
    xe=EDGE[k][0] if k is not None and abs(k-w.y)<0.6 else xedge(w.y)
    d=xe-w.x
    if d<-0.1 or d>1.0: continue
    zw=ray(TS,xe+0.1,w.y)
    if zw is None: continue
    dz=((zw-0.15)-w.z)*(1-max(0.0,d)/1.0)
    if dz>0.002: v.co=Mai@Vector((w.x,w.y,w.z+dz)); na+=1; mx_=max(mx_,dz)
AP.data.update()
print('F216b apron E-edge verts raised',na,'max',round(mx_,3),flush=True)
