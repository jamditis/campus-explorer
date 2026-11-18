# ws132: UNIFY #40 = Russ Hall (1915 Spanish Mission women's dorm, white stucco + red tile hip roofs; between Chapin and
# Freeman per MSU self-guided tour map + jamesbetelle.com). Not in the OSM extract. Footprint = LiDAR 2023 class-6 in a frame
# rotated to the building axis (u=(1,-0.24), v=(0.24,1), origin (-150,-242)): H-plan of a centre block (s -10..12, t -7.2..7.3)
# and two hipped cross-wings (s -23.8..-10.3 / 12..25.5, t -11.6..11.8), plus flat-roofed one-storey additions (W s -31..-24,
# t -6.1..6.6; S porches s -23..-11.5 / 13..24, t -14.5..-11.4) at z~130.2. Roof outlines include a ~0.6 m eave. Also fixes
# NaN verts in two ws131 meshes (drive E end beyond the LiDAR extract, W-foot bed).
import bpy, bmesh, math, os, numpy as np
from mathutils import Vector
SAVE=os.environ.get('SAVE','0')=='1'
D='/workspace/nj-scenes/montclair-state/scripts/'
P=np.load(D+'ws132/las132.npy'); B6=P[P[:,3]==6]; G2=P[P[:,3]==2]
c=math.hypot(1,0.24); U=np.array([1,-0.24])/c; V=np.array([0.24,1])/c; O=np.array([-150.,-242.])
def W(s,t,z): p=O+s*U+t*V; return Vector((float(p[0]),float(p[1]),float(z)))
def loc(A): d=A[:,:2]-O; return np.c_[d@U,d@V,A[:,2]]
L6=loc(B6)
# ---- NaN fix (ws131) ----
for n in ('WS131_E_building_W_foot_mulch_bed_tree0001_UNVERIFIED','WS131_lot_E_drive_S_of_E_building_LiDAR2023_UNVERIFIEDend_x-170'):
    o=bpy.data.objects.get(n)
    if not o: continue
    me=o.data; good=[v for v in me.vertices if not any(math.isnan(q) for q in v.co)]
    bad=[v for v in me.vertices if any(math.isnan(q) for q in v.co)]
    xy_bad=0
    for v in bad:
        if math.isnan(v.co.x) or math.isnan(v.co.y): xy_bad+=1; continue
        nb=sorted(good,key=lambda g:(g.co.x-v.co.x)**2+(g.co.y-v.co.y)**2)[:3]
        v.co.z=sum(g.co.z for g in nb)/3
    if xy_bad:
        bm=bmesh.new(); bm.from_mesh(me)
        bmesh.ops.delete(bm,geom=[v for v in bm.verts if any(math.isnan(q) for q in v.co)],context='VERTS'); bm.to_mesh(me); bm.free()
    me.update(); print('NANFIX',n,len(bad),'xy_bad',xy_bad)
# ---- materials ----
st=bpy.data.materials['COLE_stucco_plain_bq']; tl=bpy.data.materials['bx2_rhd_tile_roof_darker']
fm=bpy.data.materials['WS107_Chapin_flat_roof_membrane_UNVERIFIED.001']; so=bpy.data.materials['WS108_Chapin_eave_soffit_fascia_dark_brown_wood']
gl=bpy.data.materials['COLE_win_glass_bq']; tr=bpy.data.materials['COLE_win_trim_white_br']
col=bpy.data.collections.get('WS132_Russ_Hall') or bpy.data.collections.new('WS132_Russ_Hall')
if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
for o in [o for o in bpy.data.objects if o.name.startswith('WS132_')]: bpy.data.objects.remove(o)
def gz(s,t,r=2.0):
    p=O+s*U+t*V; d2=(G2[:,0]-p[0])**2+(G2[:,1]-p[1])**2; m=d2<r*r
    if m.sum()<3: m=d2<(3*r)**2
    return float(np.median(G2[m,2])) if m.sum() else 123.5
# eave edge z from class-6 points within 0.8 m inside the main roof outlines
def edge_z(s0,s1,t0,t1):
    q=L6[(L6[:,0]>s0)&(L6[:,0]<s1)&(L6[:,1]>t0)&(L6[:,1]<t1)&(L6[:,2]>133)]
    dd=np.minimum.reduce([q[:,0]-s0,s1-q[:,0],q[:,1]-t0,t1-q[:,1]]); e=q[dd<0.8]
    return float(np.median(e[:,2])) if len(e)>5 else 135.0
PIT=math.tan(math.radians(26)); EAVE=0.6
blocks=[('centre',-17.0,19.0,-7.25,7.3,'s'),('W_wing',-23.8,-10.3,-11.55,11.8,'t'),('E_wing',12.0,25.5,-11.65,11.75,'t')]
ze=np.median([edge_z(b[1],b[2],b[3],b[4]) for b in blocks[1:]]+[edge_z(-10,12,-7.25,7.3)])
print('EAVE edge z',ze)
zw=ze+EAVE*PIT   # wall top at the wall line
base=min(gz(s,t) for s in (-31,-24,-10,12,25.5) for t in (-14.5,0,11.8))-0.6
print('wall top %.2f base %.2f'%(zw,base))
def box(bm,s0,s1,t0,t1,z0,z1):
    vs=[bm.verts.new(W(s,t,z)) for z in (z0,z1) for (s,t) in ((s0,t0),(s1,t0),(s1,t1),(s0,t1))]
    for f in ((0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)): bm.faces.new([vs[i] for i in f])
def hip(bm,s0,s1,t0,t1,z0,ax):
    # ridge along the longer axis given by ax
    if ax=='s':
        h=(t1-t0)/2; r=z0+h*PIT; tm=(t0+t1)/2
        a=[bm.verts.new(W(s,t,z0)) for (s,t) in ((s0,t0),(s1,t0),(s1,t1),(s0,t1))]
        r0=bm.verts.new(W(s0+h,tm,r)); r1=bm.verts.new(W(s1-h,tm,r))
        fs=[(a[0],a[1],r1,r0),(a[1],a[2],r1),(a[2],a[3],r0,r1),(a[3],a[0],r0)]
    else:
        h=(s1-s0)/2; r=z0+h*PIT; sm=(s0+s1)/2
        a=[bm.verts.new(W(s,t,z0)) for (s,t) in ((s0,t0),(s1,t0),(s1,t1),(s0,t1))]
        r0=bm.verts.new(W(sm,t0+h,r)); r1=bm.verts.new(W(sm,t1-h,r))
        fs=[(a[0],a[1],r0),(a[1],a[2],r1,r0),(a[2],a[3],r1),(a[3],a[0],r0,r1)]
    for f in fs: bm.faces.new(f)
    sof=bm.faces.new(list(reversed(a))); return r,sof
def mk(name,bm,mats):
    me=bpy.data.meshes.new(name); bm.normal_update(); bm.to_mesh(me); bm.free()
    for m in mats: me.materials.append(m)
    o=bpy.data.objects.new(name,me); col.objects.link(o); return o
# walls (stucco), roofs (tile + soffit)
bw=bmesh.new()
for n,s0,s1,t0,t1,ax in blocks:
    i0,i1=(s0+EAVE,s1-EAVE) if n!='centre' else (-10.3,12.0)
    j0,j1=t0+EAVE,t1-EAVE
    box(bw,i0,i1,j0,j1,base,zw)
mk('WS132_Russ_Hall_walls_white_stucco_LiDAR2023_class6_UNVERIFIEDopenings',bw,[st])
br=bmesh.new(); soff=[]
for n,s0,s1,t0,t1,ax in blocks:
    r,sf=hip(br,s0,s1,t0,t1,ze,ax); soff.append(sf); print('RIDGE',n,'%.2f'%r)
for f in br.faces: f.material_index=1 if f in soff else 0
# fascia: thin vertical band at the eave edge
mk('WS132_Russ_Hall_hip_roofs_red_tile_26deg_eave0p6_LiDAR2023_UNVERIFIEDpitch',br,[tl,so])
# one-storey flat-roofed additions + parapets
lows=[('W_addition',-31.0,-23.0,-6.1,6.6),('S_porch_W',-23.0,-11.5,-14.5,-11.0),('S_porch_E',13.0,24.1,-14.6,-11.0)]
zl=float(np.median(L6[(L6[:,2]>126)&(L6[:,2]<=133)][:,2])); print('low roof z',zl)
bl=bmesh.new(); bf=bmesh.new()
for n,s0,s1,t0,t1 in lows:
    box(bl,s0,s1,t0,t1,base,zl+0.35)
    box(bf,s0+0.25,s1-0.25,t0+0.25,t1-0.25,zl+0.02,zl+0.06)
mk('WS132_Russ_Hall_one_storey_additions_stucco_parapet_LiDAR2023_UNVERIFIED',bl,[st])
mk('WS132_Russ_Hall_additions_flat_roof_membrane_UNVERIFIED',bf,[fm])
# windows: white trim panel + dark glass, 3 storeys on the main walls, 1 row on additions
bt=bmesh.new(); bg=bmesh.new()
def face_windows(p0,p1,nrm,zc_list,wid=1.05,hei=1.75,pitch=3.1,margin=1.6):
    p0=np.array(p0); p1=np.array(p1); Lw=np.linalg.norm(p1-p0); d=(p1-p0)/Lw
    n=max(1,int((Lw-2*margin)//pitch)+1); span=(n-1)*pitch; st0=(Lw-span)/2
    nv=np.array(nrm)
    for k in range(n):
        cpt=p0+d*(st0+k*pitch)
        for zc in zc_list:
            for bm,off,ew,eh in ((bt,0.025,wid+0.18,hei+0.18),(bg,0.04,wid,hei)):
                q=[cpt+d*(-ew/2)+nv*off,cpt+d*(ew/2)+nv*off]
                vs=[bm.verts.new((float(q[0][0]),float(q[0][1]),zc-eh/2)),bm.verts.new((float(q[1][0]),float(q[1][1]),zc-eh/2)),
                    bm.verts.new((float(q[1][0]),float(q[1][1]),zc+eh/2)),bm.verts.new((float(q[0][0]),float(q[0][1]),zc+eh/2))]
                bm.faces.new(vs)
            # sill
            a=cpt+d*(-(wid/2+0.12)); b=cpt+d*(wid/2+0.12); z0=zc-hei/2-0.16
            vs=[bt.verts.new((float(x[0]),float(x[1]),z)) for z in (z0,z0+0.07) for x in (a,b,b+nv*0.09,a+nv*0.09)]
            for f in ((0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)): bt.faces.new([vs[i] for i in f])
def P2(s,t): p=O+s*U+t*V; return (p[0],p[1])
U2=tuple(U); V2=tuple(V); mU=tuple(-U); mV=tuple(-V)
zc=[zw-1.55-k*3.45 for k in range(3)]
# wing outer faces (ends) and long faces; centre N/S faces between wings
for (s0,s1,t0,t1) in ((-23.2,-10.9,-10.95,11.2),(12.6,24.9,-11.05,11.15)):
    face_windows(P2(s0,t0),P2(s1,t0),mV,zc); face_windows(P2(s1,t1),P2(s0,t1),V2,zc)
    face_windows(P2(s0,t1),P2(s0,t0),mU,zc,pitch=3.3); face_windows(P2(s1,t0),P2(s1,t1),U2,zc,pitch=3.3)
face_windows(P2(-10.9,-6.65),P2(12.6,-6.65),mV,zc,margin=1.2); face_windows(P2(12.6,6.7),P2(-10.9,6.7),V2,zc,margin=1.2)
zl2=[126.35,129.0]
for n,s0,s1,t0,t1 in lows:
    a0,a1,b0,b1=s0-0.0,s1+0.0,t0,t1
    if n=='W_addition':
        face_windows(P2(s0,t1),P2(s0,t0),mU,zl2,pitch=3.0,margin=1.3); face_windows(P2(s0,t0),P2(s1-0.6,t0),mV,zl2,pitch=3.0,margin=1.3); face_windows(P2(s1-0.6,t1),P2(s0,t1),V2,zl2,pitch=3.0,margin=1.3)
    else:
        face_windows(P2(s0,t0),P2(s1,t0),mV,zl2,pitch=2.6,margin=1.2); face_windows(P2(s0,t1-0.6),P2(s0,t0),mU,zl2,pitch=2.6,margin=1.0); face_windows(P2(s1,t0),P2(s1,t1-0.6),U2,zl2,pitch=2.6,margin=1.0)
mk('WS132_Russ_Hall_window_trim_white_and_sills_UNVERIFIEDrhythm',bt,[tr])
mk('WS132_Russ_Hall_window_glass_dark_UNVERIFIEDrhythm',bg,[gl])
# water-table base band (white concrete, +5 cm proud) and the N-centre entrance (quad plaza axis, ortho 2020)
wt=bpy.data.materials.get('WS105_retaining_wall_white_concrete_ortho2020_UNVERIFIED') or st
bb=bmesh.new()
for n,s0,s1,t0,t1,ax in blocks:
    i0,i1=(s0+EAVE,s1-EAVE) if n!='centre' else (-10.3,12.0); j0,j1=t0+EAVE,t1-EAVE
    top=min(gz(i0,j0),gz(i1,j0),gz(i1,j1),gz(i0,j1))+0.8
    box(bb,i0-0.05,i1+0.05,j0-0.05,j1+0.05,base,top); print('BAND',n,'%.2f'%top)
for n,s0,s1,t0,t1 in lows:
    top=min(gz(s0,t0),gz(s1,t0),gz(s1,t1),gz(s0,t1))+0.6
    box(bb,s0-0.05,s1+0.05,t0-0.05,t1+0.05,base,top)
mk('WS132_Russ_Hall_water_table_base_band_UNVERIFIEDheight',bb,[wt])
ge=gz(0.8,8.5,1.5); dw=bpy.data.materials['WS108_Chapin_eave_soffit_fascia_dark_brown_wood']
be=bmesh.new(); bdoor=bmesh.new(); pc=bpy.data.materials.get('Paving_concrete') or wt
box(be,-0.9,2.5,6.65,6.95,ge+0.15,ge+3.3)     # surround
box(be,-1.2,2.8,6.65,7.1,ge+3.3,ge+3.6)       # cornice
box(bdoor,-0.4,2.0,6.94,6.99,ge+0.2,ge+2.75)
st2=bmesh.new()
for k in range(3): box(st2,-1.6,3.2,6.65,8.6-k*0.4,ge-0.4,ge+0.05+k*0.05)
mk('WS132_Russ_Hall_N_entrance_surround_UNVERIFIED',be,[wt]); mk('WS132_Russ_Hall_N_entrance_doors_dark_wood_UNVERIFIED',bdoor,[dw]); mk('WS132_Russ_Hall_N_entrance_landing_steps_concrete_UNVERIFIED',st2,[pc])
print('ENTRANCE ground %.2f'%ge)
# chimneys / roof penthouses: class-6 points > 1.0 m above the modelled roof, inside the blocks, 0.5 m-grid components
br2=bmesh.new(); bp=bmesh.new(); cnt=0
q=L6[L6[:,2]>133]
def roofz(s,t):
    best=None
    for n,s0,s1,t0,t1,ax in blocks:
        if s0+0.3<=s<=s1-0.3 and t0+0.3<=t<=t1-0.3:
            if ax=='s': h=(t1-t0)/2; dd=min(h-abs(t-(t0+t1)/2), s-s0, s1-s)
            else: h=(s1-s0)/2; dd=min(h-abs(s-(s0+s1)/2), t-t0, t1-t)
            z=ze+dd*PIT; best=z if best is None else max(best,z)
    return best
bd=bmesh.new(); bdr=bmesh.new(); bdg=bmesh.new()
def outward(s,t):
    for n,s0,s1,t0,t1,ax in blocks:
        if s0<=s<=s1 and t0<=t<=t1:
            ds={(-1,0):s-s0,(1,0):s1-s,(0,-1):t-t0,(0,1):t1-t}
            return min(ds,key=ds.get)
    return (0,-1)
def dormer(sm,tm,s0,s1,t0,t1,zt):
    o=outward(sm,tm); W_=0.8; Dp=1.0  # half width, depth inward from the front
    if o[0]==0:
        f=t1 if o[1]>0 else t0; a0,a1=sm-W_,sm+W_
        S=lambda a,d:(a,f-o[1]*d)
    else:
        f=s1 if o[0]>0 else s0; a0,a1=tm-W_,tm+W_
        S=lambda a,d:(f-o[0]*d,a)
    zf=roofz(*S((a0+a1)/2,0)) or ze; zf-=0.15; zr=zt-0.5
    def V3(a,d,z): s,t=S(a,d); return W(s,t,z)
    vs=[bd.verts.new(V3(a,d,z)) for z in (zf,zr) for (a,d) in ((a0,0),(a1,0),(a1,Dp*2),(a0,Dp*2))]
    for fc in ((0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)): bd.faces.new([vs[i] for i in fc])
    e=0.2; rv=[bdr.verts.new(V3(a,d,zr)) for (a,d) in ((a0-e,-e),(a1+e,-e),(a1+e,Dp*2+e),(a0-e,Dp*2+e))]
    ap=bdr.verts.new(V3((a0+a1)/2,Dp*0.9,zt)); ap2=bdr.verts.new(V3((a0+a1)/2,Dp*2+e,zt))
    for fc in ((rv[0],rv[1],ap),(rv[1],rv[2],ap2,ap),(rv[3],rv[0],ap,ap2)): bdr.faces.new(fc)
    gv=[bdg.verts.new(V3(a,-0.02,z)) for (a,z) in ((a0+0.22,zf+0.35),(a1-0.22,zf+0.35),(a1-0.22,zr-0.15),(a0+0.22,zr-0.15))]
    bdg.faces.new(gv)
keep=[(s,t,z) for s,t,z in q if roofz(s,t) is not None and z-roofz(s,t)>1.0]
cand=np.array(keep); print('cand',len(cand))
from collections import defaultdict
cells=defaultdict(list)
for i,(s,t,z) in enumerate(cand): cells[(int(math.floor(s/0.5)),int(math.floor(t/0.5)))].append(i)
seen=set()
for k0 in list(cells):
    if k0 in seen: continue
    comp=[]; st_=[k0]; seen.add(k0)
    while st_:
        k=st_.pop(); comp+=cells[k]
        for di in (-2,-1,0,1,2):
            for dj in (-2,-1,0,1,2):
                kk=(k[0]+di,k[1]+dj)
                if kk in cells and kk not in seen: seen.add(kk); st_.append(kk)
    if len(comp)<8: continue
    C=cand[comp]; s0,s1=np.percentile(C[:,0],[10,90]); t0,t1=np.percentile(C[:,1],[10,90]); zt=float(np.percentile(C[:,2],95))
    if s1-s0<0.9: m=(s0+s1)/2; s0,s1=m-0.45,m+0.45
    if t1-t0<0.7: m=(t0+t1)/2; t0,t1=m-0.35,m+0.35
    sm,tm=(s0+s1)/2,(t0+t1)/2; zb=roofz(sm,tm)-1.0
    area=(s1-s0)*(t1-t0)
    if area>4.0:
        box(bp,s0,s1,t0,t1,zb,zt); box(bp,s0-0.08,s1+0.08,t0-0.08,t1+0.08,zt,zt+0.12); kind='PENTHOUSE'
    elif zt<138.75:
        kind='DORMER'; dormer(sm,tm,s0,s1,t0,t1,zt)
    else:
        box(br2,s0,s1,t0,t1,zb,zt); box(br2,s0-0.1,s1+0.1,t0-0.1,t1+0.1,zt-0.2,zt-0.06); kind='CHIMNEY'
    cnt+=1; print(kind,'s%.1f..%.1f t%.1f..%.1f top %.2f n%d'%(s0,s1,t0,t1,zt,len(comp)))
mk('WS132_Russ_Hall_chimneys_stucco_LiDAR2023_class6_peaks_UNVERIFIED',br2,[st])
mk('WS132_Russ_Hall_hipped_dormers_stucco_LiDAR2023_UNVERIFIEDsize',bd,[st]); mk('WS132_Russ_Hall_dormer_hip_caps_red_tile',bdr,[tl]); mk('WS132_Russ_Hall_dormer_windows_dark_glass',bdg,[gl])
mk('WS132_Russ_Hall_roof_penthouses_stucco_LiDAR2023_class6_UNVERIFIEDuse',bp,[st])
print('M132 done; chimneys',cnt)
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED')
