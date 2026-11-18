# ws193: Lot 3 S ramp (WS163_Lot3_aisle_S_drive) — wavy dark seams in the E eye view.
# probe193.out: faces along the W edge tilt 25-37 deg, creases up to 34 deg at x -311.1..-312.1 (y -234.6..-239.4):
# the fix190 edge drape pulled the W edge 0.2-0.4 m down onto the bank lawn over the last 0.3-0.6 m -> a rolled, wavy dark lip.
# probe193b.out: interior cross-slope is a steady ~8 %/m falling W; bank lawn W of the edge sits 0.35-0.4 m below.
# Evidence: NJOGIS 2020 ortho shows a dark curb-SHADOW line exactly on the W edge (fix190 research), i.e. a curb holds the
# asphalt and the bank drops behind it. Build: (1) asphalt W feather re-graded to the local interior plane (no roll-down),
# light Laplacian smoothing of interior z (1 pass, 0.5 weight) to calm LiDAR ripples; E edge drape kept;
# (2) WS193 W-edge curb: 0.15 m wide, 0.10 m reveal (UNVERIFIED height/type), back face to below the bank lawn, tapered to flush
# over the last 1.2 m at the Normal Ave end (into the depressed curb) and at the Lot 3 end.
import bpy, bmesh, math
from mathutils import Vector
D=[o for o in bpy.data.objects if o.name.startswith('WS163_Lot3_aisle_S_drive')][0]
M=D.matrix_world; Mi=M.inverted(); me=D.data
bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
W=[M@v.co for v in bm.verts]
bnd=set(v.index for v in bm.verts if v.is_boundary)
xs=[w.x for w in W]; ys=[w.y for w in W]
# W boundary chain = boundary verts left of the drive centre at their y
def xmid(y):
    row=[w.x for w in W if abs(w.y-y)<0.6]; return (min(row)+max(row))/2 if row else -308.5
Wb=sorted([i for i in bnd if W[i].x<xmid(W[i].y)-0.5 and -247.5<W[i].y<-234.3],key=lambda i:-W[i].y)
def xW(y):
    best=min(Wb,key=lambda i:abs(W[i].y-y)); return W[best].x
def dW(i): return W[i].x-xW(W[i].y)
interior=[i for i in range(len(W)) if i not in bnd and dW(i)>1.1]
import numpy as np
P=np.array([[W[i].x,W[i].y,W[i].z] for i in interior])
def plane_z(x,y,r=2.5):
    d=np.hypot(P[:,0]-x,P[:,1]-y); m=d<r
    if m.sum()<6: m=np.argsort(d)[:12]
    A=np.c_[np.ones(len(P[m])),P[m][:,0],P[m][:,1]]; c=np.linalg.lstsq(A,P[m][:,2],rcond=None)[0]
    return c[0]+c[1]*x+c[2]*y
nW=0; newz={}
for i in range(len(W)):
    d=dW(i)
    if d<=1.1 and W[i].x<xmid(W[i].y):
        pz=plane_z(W[i].x,W[i].y)
        t=max(0.0,min(1.0,d/1.1)); t=t*t*(3-2*t)
        newz[i]=(1-t)*pz+t*W[i].z; nW+=1
for i,z in newz.items(): W[i].z=z
# one light Laplacian pass on non-boundary verts
nb=0; sm={}
for v in bm.verts:
    if v.index in bnd: continue
    ns=[e.other_vert(v).index for e in v.link_edges]
    if ns: sm[v.index]=0.5*W[v.index].z+0.5*sum(W[n].z for n in ns)/len(ns); nb+=1
for i,z in sm.items(): W[i].z=z
for v in bm.verts: v.co=Mi@W[v.index]
bm.to_mesh(me); me.update(); bm.free()
print('FIX193 drive Wfeather regraded',nW,'smoothed',nb,'Wchain',len(Wb),flush=True)
# --- curb along the W edge ---
ch=[W[i] for i in Wb]
# resample every 0.4 m along y
y0,y1=ch[0].y,ch[-1].y; n=max(2,int((y0-y1)/0.4)+1)
def at(y):
    for a,b in zip(ch,ch[1:]):
        if b.y<=y<=a.y:
            t=(a.y-y)/max(1e-6,a.y-b.y); return a.lerp(b,t)
    return ch[-1] if y<y1 else ch[0]
pts=[at(y0-(y0-y1)*k/(n-1)) for k in range(n)]
vs=[];fs=[];WID=0.15;REV=0.10
L=(y0-y1)
for k,p in enumerate(pts):
    q=pts[min(k+1,n-1)]-pts[max(k-1,0)]; q.z=0; q.normalize()
    out=Vector((q.y,-q.x,0))  # pick the side pointing -x
    if out.x>0: out=-out
    s=(y0-p.y); taper=min(1.0,s/1.2,(L-s)/1.2)
    rv=REV*max(0.0,taper)
    zi=p.z-0.004
    a=Vector((p.x+0.01*out.x,p.y+0.01*out.y,zi-0.05))
    b=Vector((p.x+0.01*out.x,p.y+0.01*out.y,zi+rv))
    c=Vector((p.x+(WID+0.01)*out.x,p.y+(WID+0.01)*out.y,zi+rv-0.005))
    d=Vector((c.x,c.y,zi-0.85))
    vs+= [a,b,c,d]
for k in range(n-1):
    o=4*k
    for j in range(3): fs.append((o+j,o+j+1,o+4+j+1,o+4+j))
fs.append((0,1,2,3)); o=4*(n-1); fs.append((o+3,o+2,o+1,o))
cm=bpy.data.meshes.new('WS193_Lot3_S_ramp_W_curb'); cm.from_pydata([tuple(v) for v in vs],[],fs); cm.update()
for p in cm.polygons: p.use_smooth=False
mat=bpy.data.materials.get('WS27_curb_concrete_UNVERIFIED')
if mat: cm.materials.append(mat)
cob=bpy.data.objects.new('WS193_Lot3_S_ramp_W_curb_ortho2020_shadow_UNVERIFIEDheight',cm)
for c in D.users_collection: c.objects.link(cob)
uv=cm.uv_layers.new()
for l in cm.loops: co=cm.vertices[l.vertex_index].co; uv.data[l.index].uv=(co.x/2+co.z, co.y/2)
print('FIX193 curb pts',n,'len %.1f'%L,'y',round(y0,2),round(y1,2),flush=True)
