# ws216 W35c: SE corner of the WS215 RHD SE street-level walk at the College Ave crosswalk.
# Fault (ws215b E5 view): KY_college_ave_carriageway (N edge y -49.0) runs ~1.7-4 m UNDER the walk footprint and stands ~0.15 m
# ABOVE the walk's E end (KY ~125.2 vs walk 125.05) -> dark asphalt plate shows through the walk near the crosswalk.
# Evidence: NJ 2023 LiDAR dtm_1m (data/dtm_1m.npy): ground falls ~0.25 m from the College Ave edge at the crosswalk (y -52..-54)
# to the SE core doors (y -46); i.e. the walk should RISE from the doors to meet the road at the crosswalk (a flush curb ramp),
# not sit below the road. Design: standard perpendicular curb ramp at the crosswalk span (flush, 0 reveal), 1:10 flares
# back to the walk's 15 cm curb reveal either side, regrade decaying linearly to 0 at the door line (y -46.35) so
# thresholds/decals at the doors are untouched. Lift capped at 0.22 m. KY verts that stay inside the walk footprint
# are clamped 2 cm under the walk top (walk wins; road edge hidden under the slab instead of poking through).
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def ob(p): return next((o for o in bpy.data.objects if o.name.startswith(p)),None)
SL=ob('WS215_RHD_SE_core_street_level_sidewalk'); KY=ob('KY_college_ave_carriageway_asphalt (')
assert SL and KY, 'F216 objects missing'
def bvh(o,top=False):
    M=o.matrix_world; P=[p for p in o.data.polygons if (not top) or (M.to_3x3()@p.normal).z>0.7]
    return BVHTree.FromPolygons([M@v.co for v in o.data.vertices],[p.vertices[:] for p in P])
tk=bvh(KY)
def kyz(x,y):
    h=tk.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),300); return h[0].z if h[0] is not None else None
M=SL.matrix_world; Mi=M.inverted()
W=[M@v.co for v in SL.data.vertices]
YD=-46.35; XC0,XC1=-259.4,-255.55   # crosswalk span (old LF landing extent x -259.5..-255.6)
FL=1.5                               # flare length (0.15 m reveal at 1:10)
# S edge = straight fitted line through the southmost slab-top verts per 0.5 m bin
top=[w for w in W if w.z>124.5]
bins={}
for w in top:
    k=int((w.x+300)/0.5)
    if k not in bins or w.y<bins[k].y: bins[k]=w
E=list(bins.values()); n_=len(E); mx=sum(p.x for p in E)/n_; my=sum(p.y for p in E)/n_
kk=sum((p.x-mx)*(p.y-my) for p in E)/sum((p.x-mx)**2 for p in E)
mz=sum(p.z for p in E)/n_; kz=sum((p.x-mx)*(p.z-mz) for p in E)/sum((p.x-mx)**2 for p in E)
sedge=lambda x: my+kk*(x-mx); topz_orig=lambda x: mz+kz*(x-mx)
print('F216 S edge fit n',n_,'y',round(sedge(-265),2),round(sedge(-255.6),2),'z',round(topz_orig(-265),3),round(topz_orig(-255.6),3),flush=True)
def lift_at_edge(x):
    ys=sedge(x); kz_=None
    for d in (0.05,0.15,0.3,0.5):
        kz_=kyz(x,ys-d)
        if kz_ is not None: break
    if kz_ is None: return 0.0
    tz=topz_orig(x)
    if XC0<=x<=XC1: want=kz_+0.005
    else:
        dd=min(abs(x-XC0),abs(x-XC1)); want=kz_+min(0.15,0.15*dd/FL)
    return max(0.0,min(0.22,want-tz))
XS=[-268+i*0.25 for i in range(57)]
LS=[lift_at_edge(x) for x in XS]
print('F216 edge lifts',[(x,round(l,3)) for x,l in zip(XS,LS) if l>0.001],flush=True)
def lift(x):
    if x<=XS[0]: return LS[0]
    if x>=XS[-1]: return LS[-1]
    i=int((x-XS[0])/0.25); u=(x-XS[i])/0.25; return LS[i]*(1-u)+LS[i+1]*u
# E edge: meet the WS72 Kasser landing (it stands 0.08-0.13 m above the walk's E end at x -255.55)
W72=ob('WS72_Kasser_SW_RHD_core_sidewalk_landing'); t72=bvh(W72) if W72 else None
tsl=bvh(SL,top=True)
XE=max(w.x for w in top)
def ray(t,x,y):
    h=t.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),300); return h[0].z if h[0] is not None else None
YSn=[-46.35-0.25*i for i in range(30)]
EL=[]
for y in YSn:
    a_=ray(t72,XE+0.12,y) if t72 else None; b_=ray(tsl,XE-0.08,y)
    EL.append(max(0.0,min(0.2,(a_-b_))) if (a_ is not None and b_ is not None) else 0.0)
print('F216 E-edge lifts',[(y,round(l,3)) for y,l in zip(YSn,EL) if l>0.001],flush=True)
def elift(y):
    if y>=YSn[0]: return EL[0]
    i=min(len(YSn)-2,int((YSn[0]-y)/0.25)); u=(YSn[i]-y)/0.25; u=min(1,max(0,u)); return EL[i]*(1-u)+EL[i+1]*u
XW0=-259.8
def sm(t): t=max(0.0,min(1.0,t)); return t*t*(3-2*t)
n=0
for v,w in zip(SL.data.vertices,W):
    g=max(0.0,min(1.0,(YD-w.y)/1.5))                 # 0 at the door line, protects thresholds/decals
    ys=sedge(w.x); ty=max(0.0,min(1.0,(YD-w.y)/(YD-ys)))
    dz=elift(w.y)*max(0.0,min(1.0,(w.x-XW0)/(XE-XW0)))*g   # one smooth bilinear-ish ramp (S-edge lift dropped: E-edge lift already makes the SE corner flush with KY)
    if dz>0.0005: v.co=Mi@Vector((w.x,w.y,w.z+dz)); n+=1
# close the 5 cm slot between the walk's E edge (x -255.55) and the WS72 landing W edge (-255.50): push the E-edge column 8 cm E (tucks under WS72)
ne=0
for v in SL.data.vertices:
    w=M@v.co
    if w.x>XE-0.01: v.co=Mi@Vector((XE+0.08,w.y,w.z)); ne+=1
print('F216 E-edge verts pushed under WS72',ne,flush=True)
SL.data.update()
print('F216 slab verts lifted',n,flush=True)
# KY verts inside the walk footprint -> 2 cm under the walk top
ts=bvh(SL,top=True); Mk=KY.matrix_world; Mki=Mk.inverted(); nk=0
for v in KY.data.vertices:
    w=Mk@v.co
    if not (-268<w.x<-254 and -54<w.y<-46): continue
    h=ts.ray_cast(Vector((w.x,w.y,200)),Vector((0,0,-1)),300)
    if h[0] is not None and w.z>h[0].z-0.02: v.co=Mki@Vector((w.x,w.y,h[0].z-0.02)); nk+=1
KY.data.update()
print('F216 KY verts clamped under walk',nk,flush=True)

# WS214 N curb-return nose + WS70 N berm tip overlap the WS72 Kasser landing (x -255.5..-253.5) and stand 0.1-0.15 m above it
# (dark curb-concrete plate in the E5 view). 2020 ortho: grey paving, no lawn W of x ~ -252 at this tip (ws214 evidence) -> the
# landing wins: their verts above WS72 inside x < -253.5 are clamped 1 cm under the WS72 top.
nn=0
for o in [o for o in bpy.data.objects if o.name.startswith(('WS214_WS69_N_berm_tip_curb_return_nose','WS70_gap_strip_grass_berms'))]:
    M2=o.matrix_world; M2i=M2.inverted(); c=0
    for v in o.data.vertices:
        w=M2@v.co
        if not (-255.6<w.x<-253.5 and -55.2<w.y<-46.8): continue
        z72=ray(t72,w.x,w.y)
        if z72 is not None and w.z>z72-0.01: v.co=M2i@Vector((w.x,w.y,z72-0.01)); c+=1
    o.data.update(); nn+=c
    print('F216 clamped under WS72',o.name[:40],c,flush=True)
