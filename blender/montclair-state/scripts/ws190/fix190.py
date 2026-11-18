# ws190 UNIFY #92: Lot 3 S ramp (aisle S drive) — straight edges + flush edge feather + retire the overlapping S-end apron feather.
# Evidence: NJOGIS Natural2020 ortho prep/ws181_lot36/ortho181.jpg (0.1 m/px): W edge = dark curb-shadow line, brightness minima
# x -310.8 (y-234), -311.1 (-236), -312.0 (-238), -312.7 (-240), -313.1 (-242) -> straight x=-310.75+0.29(y+234) (+-0.3 m);
# E edge = asphalt/vegetation brightness drop at x -305.4..-305.6 for y -236..-242 -> near-N-S straight x=-305.45+0.045(y+236);
# below y -243 the E edge is under WS165 canopy shadow (UNVERIFIED, line extrapolated, matches the old model -306.0 at y -245).
# Old model edges were LiDAR-intensity polylines (0.8 m jog on the W side at y -239, E flare to x -303 at y -235.5).
# The E top flare is kept as a smooth curb-return arc into Lot 3 (blend y -235.2 -> -238.0). Edge verts drape 1.5 cm over the lawn
# (old edges stood 3-10 cm proud = dark wavy lip in the E eye view), feathered over 1.0 m back to the LiDAR surface.
import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def _o190(p): return [o for o in bpy.data.objects if o.name.startswith(p)][0]
DR190=_o190('WS163_Lot3_aisle_S_drive_to_NormalAve_OSM232846667')
FE190=_o190('WS162_Lot3_S_end_apron_feather')
LAWN190=[_o190(p) for p in ('WS163_ground_patch_W_of_WS110','WS186_Lot3_S_bank_lawn','WS187_Lot3_W_shoulder_toe','WS169c_Lot3_S_end_lawn','WS162_Lot3_W_shoulder_lawn')]
def _bvh190(o):
    M=o.matrix_world; return BVHTree.FromPolygons([M@v.co for v in o.data.vertices],[p.vertices[:] for p in o.data.polygons])
LB190=[_bvh190(o) for o in LAWN190]; OB190=_bvh190(DR190)
def lawnz190(x,y):
    zs=[h[0].z for t in LB190 for h in [t.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))] if h[0]]
    return max(zs) if zs else None
me=DR190.data; M=DR190.matrix_world; Mi=M.inverted()
W=np.array([tuple(M@v.co) for v in me.vertices])
# boundary loop
import bmesh
bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
bidx=sorted({v.index for e in bm.edges if e.is_boundary for v in e.verts}); bm.free()
B=W[bidx]
ybot190=lambda x: -248.66+(x+315.2)*(-2.27/9.6)   # S joint edge (-315.2,-248.66)->(-305.6,-250.93), untouched
keepB=B[:,1]>ybot190(B[:,0])+0.05
wch=B[(B[:,0]<-309.4)&(B[:,1]<=-234.55)&keepB]; wch=wch[np.argsort(wch[:,1])]
ech=B[(B[:,0]>-306.3)&(B[:,1]<=-235.1)&(B[:,0]<-302.9)&keepB]; ech=ech[np.argsort(ech[:,1])]
Wo=lambda y: np.interp(y,wch[:,1],wch[:,0]); Eo=lambda y: np.interp(y,ech[:,1],ech[:,0])
Wn=lambda y: -310.75+0.3035*(y+234.0); En=lambda y: -305.45+0.0114*(y+236.0)  # both lines end on the existing S-joint corners
def ss(a,b,y):
    t=np.clip((y-a)/(b-a),0,1); return t*t*(3-2*t)
wW=lambda y: ss(-234.55,-235.6,y)
wE=lambda y: ss(-235.2,-238.0,y)
N=W.copy(); moved=0; mx=0
for i,(x,y,z) in enumerate(W):
    if y>-234.55 or y<ybot190(x)+0.05: continue
    wo,eo=Wo(y),Eo(y)
    if eo-wo<1.0: continue
    t=np.clip((x-wo)/(eo-wo),0,1)
    w1=wo+wW(y)*(Wn(y)-wo); e1=eo+wE(y)*(En(y)-eo)
    nx=w1+t*(e1-w1)
    if abs(nx-x)>1e-4: moved+=1; mx=max(mx,abs(nx-x))
    N[i,0]=nx
# z: resample original drive surface at the new xy, feather edges onto the lawn
NB=N[bidx]; nz=0; up=0
for i in range(len(N)):
    x,y,_=N[i]
    if y>-234.9: continue   # top joint with Lot 3 asphalt stays
    h=OB190.ray_cast(Vector((x,y,200)),Vector((0,0,-1))); lz=lawnz190(x,y)
    zs=h[0].z if h[0] else (lz+0.015 if lz is not None else W[i,2])
    d=np.min(np.hypot(NB[:,0]-x,NB[:,1]-y)) if i not in bidx else 0.0
    if lz is not None:
        zf=lz+0.015; zn=zf+(zs-zf)*min(d/1.0,1.0); zn=max(zn,lz+0.016)
        if zn>zs+1e-4: up+=1
    else: zn=zs
    N[i,2]=zn; nz+=1
# smooth edge-chain z (2 passes, 3-pt) so the drape follows a calm line, then keep >= lawn+8 mm
bset=set(bidx)
for ch in (wch,ech):
    ids=[bidx[int(np.argmin(np.hypot(B[:,0]-p[0],B[:,1]-p[1])))] for p in ch]
    for _ in range(2):
        zz=N[ids,2].copy(); zz[1:-1]=(zz[:-2]+zz[1:-1]+zz[2:])/3; 
        for k,j in enumerate(ids):
            if N[j,1]<=-234.9:
                lz=lawnz190(N[j,0],N[j,1]); N[j,2]=max(zz[k],lz+0.008) if lz is not None else zz[k]
for i,v in enumerate(me.vertices): v.co=Mi@Vector(N[i])
me.update()
# S-end apron feather: keep it as the filler at the Lot 3 S-end corner, but 2.5 cm BELOW the drive (was z-fighting it, +-3 mm)
# -> subdivide it (0.94 m grid -> ~0.24 m) and tuck every vertex 2 cm under the drive or under the lawn wherever either
# covers it; it stays on top only in the two small true gaps (drive top edge / WS170b curb strip corner).
bmf=bmesh.new(); bmf.from_mesh(FE190.data); bmesh.ops.subdivide_edges(bmf,edges=bmf.edges[:],cuts=3,use_grid_fill=True); bmf.to_mesh(FE190.data); bmf.free()
MF=FE190.matrix_world; MFi=MF.inverted(); OB190b=_bvh190(DR190); tk=[0,0,0]
for v in FE190.data.vertices:
    p=MF@v.co; h=OB190b.ray_cast(Vector((p.x,p.y,200)),Vector((0,0,-1))); lz=lawnz190(p.x,p.y)
    if h[0]: p.z=min(p.z,h[0].z-0.02); tk[0]+=1
    elif lz is not None: p.z=min(p.z,lz-0.02); tk[1]+=1
    else: tk[2]+=1
    v.co=MFi@p
FE190.data.update(); print('FIX190 feather verts under drive/lawn/kept',tk,flush=True)
print('FIX190 moved',moved,'maxdx %.2f'%mx,'z set',nz,'raised',up,'Wchain',len(wch),'Echain',len(ech),'lowered',FE190.name,flush=True)
