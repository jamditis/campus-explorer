# ws207 W27: wavy dark seams where the traced WS79 lot patch meets WS75/WS76/WS96/WS94 (x -224..-216.5, y -87..-80).
# an207: 1172 overlap cells, 806 with >1 cm between stacked lot sheets; top-object changes with steps up to 5.7 cm.
# All five are the same fn_lot_asphalt surface (one continuous lot in the 2020 ortho), so the fix is one grade:
# target = Gaussian-smoothed (sigma 0.8 m) top-of-lot field; every lot vertex in the zone is moved to target + a tiny
# per-sheet order offset (WS79 -2 mm under, fillers -1 mm, WS75 0, WS76 +1 mm), blended to 0 over 1.5 m outside the core,
# never touching x > -215.6 (ws206 aisle joint). Capped 4 mm under curbs/islands/pad; paint re-seated by the same delta.
import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def obp(p):
    r=[o for o in bpy.data.objects if o.name.startswith(p)]; return r[0] if r else None
def bvh(o):
    mw=o.matrix_world; return BVHTree.FromPolygons([mw@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])
def hz(t,x,y):
    h=t.ray_cast(Vector((x,y,160)),Vector((0,0,-1)),80); return h[0].z if h[0] is not None else None
OFF={'WS75_sprague_lot_asphalt':0.0,'WS76_accessible_lot_asphalt':0.001,'WS79_lot_E_patch':-0.002,'WS96_lot_E_edge_gap':-0.001,'WS94_lot_slit_filler':-0.001}
LOT={p:obp(p) for p in OFF}; LOT={p:o for p,o in LOT.items() if o is not None}
print('F207a lots',[o.name[:28] for o in LOT.values()],flush=True)
CX0,CX1,CY0,CY1,TP=-224.5,-217.2,-86.8,-80.0,1.5
def wgt(x,y):
    if x>-215.6: return 0.0
    dx=max(CX0-x,0,x-CX1); dy=max(CY0-y,0,y-CY1); d=(dx*dx+dy*dy)**0.5
    f=min(max(1-d/TP,0),1); f=f*f*(3-2*f)
    if x>-216.6: f*=min(max((-215.6-x)/1.0,0),1)
    return f
GX0,GX1,GY0,GY1,ST=-228.0,-213.0,-90.5,-76.5,0.1
xs=np.arange(GX0,GX1+1e-6,ST); ys=np.arange(GY0,GY1+1e-6,ST)
TB=[bvh(o) for o in LOT.values()]
Z=np.full((len(ys),len(xs)),np.nan)
for j,y in enumerate(ys):
    for i,x in enumerate(xs):
        zz=[z for z in (hz(t,x,y) for t in TB) if z is not None]
        if zz: Z[j,i]=max(zz)
m=~np.isnan(Z); Zf=np.where(m,Z,0.0)
k=np.arange(-24,25)*ST; g=np.exp(-0.5*(k/0.8)**2)
def conv(A):
    A=np.apply_along_axis(lambda r: np.convolve(r,g,'same'),1,A); return np.apply_along_axis(lambda c: np.convolve(c,g,'same'),0,A)
ZS=conv(Zf)/np.maximum(conv(m.astype(float)),1e-9)
def zs(x,y):
    fx=(x-GX0)/ST; fy=(y-GY0)/ST; i=int(np.floor(fx)); j=int(np.floor(fy)); i=min(max(i,0),len(xs)-2); j=min(max(j,0),len(ys)-2); u=fx-i; v=fy-j
    return (ZS[j,i]*(1-u)*(1-v)+ZS[j,i+1]*u*(1-v)+ZS[j+1,i]*(1-u)*v+ZS[j+1,i+1]*u*v)
OTP=['WS77_lot_median_island','WS98_lotE_raised_concrete_walk_pad','WS206_CollegeAve_bend_teardrop_island','WS98_CollegeAve_bend_teardrop','WS99_lotE_padS_bed']
OT=[bvh(o) for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(tuple(OTP)) and len(o.data.polygons)]
oldT=[bvh(o) for o in LOT.values()]
import bmesh
for p,o in LOT.items():
    mw=o.matrix_world; tot=0
    for it in range(4):
        bm=bmesh.new(); bm.from_mesh(o.data)
        E=[e for e in bm.edges if e.calc_length()>0.45 and all(wgt(*(mw@v.co).xy)>0 for v in e.verts)]
        if not E: bm.free(); break
        r=bmesh.ops.subdivide_edges(bm,edges=E,cuts=1,use_grid_fill=True)
        bmesh.ops.triangulate(bm,faces=[f for f in bm.faces if len(f.verts)>4])
        bm.to_mesh(o.data); bm.free(); tot+=len(E)
    print('F207a subdiv',o.name[:24],'edges split',tot,flush=True)
for p,o in LOT.items():
    mw=o.matrix_world; mi=mw.inverted(); n=0; mx=0; up=0; dn=0
    for v in o.data.vertices:
        gp=mw@v.co; w=wgt(gp.x,gp.y)
        if w<=0: continue
        z=gp.z+w*(zs(gp.x,gp.y)+OFF[p]-gp.z)
        for t in OT:
            zo=hz(t,gp.x,gp.y)
            if zo is not None and zo>gp.z-0.002 and z>zo-0.004: z=min(z,max(zo-0.004,gp.z if zo-0.004<gp.z else zo-0.004))
        d=z-gp.z
        if abs(d)>1e-5:
            n+=1; mx=max(mx,abs(d)); up+=d>0; dn+=d<0; gp.z=z; v.co=mi@gp
    o.data.update(); print('F207a',o.name[:30],'moved',n,'up',up,'down',dn,'max %.3f'%mx,flush=True)
newT=[bvh(o) for o in LOT.values()]
def top(TT,x,y):
    zz=[z for z in (hz(t,x,y) for t in TT) if z is not None]; return max(zz) if zz else None
for o in [o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('WS76_lot_stall_paint','WS196_lot_accessible_ISA'))]:
    mw=o.matrix_world; mi=mw.inverted(); n=0
    for v in o.data.vertices:
        gp=mw@v.co
        if wgt(gp.x,gp.y)<=0: continue
        a=top(oldT,gp.x,gp.y); b=top(newT,gp.x,gp.y)
        if a is not None and b is not None and abs(b-a)>1e-5: gp.z+=b-a; v.co=mi@gp; n+=1
    o.data.update(); print('F207a paint',o.name[:30],'reseated',n,flush=True)
