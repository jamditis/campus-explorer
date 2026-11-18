"""Session 20261016bq: Susan A. Cole Hall (= historic College Hall) first real pass in montclair_state.blend.
- 3 roof towers at LiDAR-MEASURED positions/tops (grid_1m bld >151 m clusters): central cupola (-113.4,-95.4) top 157.96;
  flanking belvederes (-137.0,-89.4) top 155.72 and (-89.1,-101.6) top 155.76. Stage splits/forms UNVERIFIED (Commons photos:
  Daniel Case 2015 CC BY-SA 3.0 cupola; Freeholdman12 2023 CC BY-SA 4.0 front; Academic Banana 5 2024 CC0 wide).
- Punched windows on north- and west-facing walls only (faces shown in photos). Rhythm pitch 2.0 m / 1.3 x 2.0 m, 3 rows
  (UNVERIFIED generalisation of PD west-wing photo + 2023 front photo; scaled to LiDAR wall height).
Idempotent: rebuilds collection COLE_hero_20261016bq. SAVE=1 to save.
"""
import bpy, bmesh, json, math, os
import numpy as np
from mathutils import Vector, Matrix
ROOT='/workspace/nj-scenes/montclair-state'
COLN='COLE_hero_20261016bq'
ring=json.load(open(ROOT+'/north/data/day_heroes/day9_cole_hall_levels_prep_20261016be.json'))['footprint']['ring_scene_xy_m']
g=np.load(ROOT+'/north/data/grid_1m.npz'); dtm=g['dtm_filled']
def ground(x,y):
    c=int(math.floor(x+600)); r=int(math.floor(y+260)); return float(dtm[r,c])
sc=bpy.context.scene
if COLN in bpy.data.collections:
    c=bpy.data.collections[COLN]
    for o in list(c.objects): bpy.data.objects.remove(o,do_unlink=True)
else:
    c=bpy.data.collections.new(COLN); sc.collection.children.link(c)
def mat(name,col,rough=0.6,metal=0.0,spec=0.5):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes=True; b=m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value=(*col,1); b.inputs['Roughness'].default_value=rough; b.inputs['Metallic'].default_value=metal
    return m
walls=bpy.data.objects['Susan A. Cole Hall walls']; tiles=bpy.data.objects['Susan A. Cole Hall hip + ridge cap tiles']
M_tex=walls.material_slots[0].material   # Wall_stucco_mission: image facade WITH generic (not photo-matched) windows
M_st=mat('COLE_stucco_plain_bq',(0.80,0.785,0.74),0.85)
# 4a doubled-window fix: plain stucco on the wall faces that now carry photo-backed geometric windows (S + W-wing W faces).
# Material-slot assignment only; walls geometry untouched. North/east faces keep the old generic texture.
me=walls.data
if 'COLE_stucco_plain_bq' not in [m.name for m in me.materials if m]: me.materials.append(M_st)
si=[m.name if m else '' for m in me.materials].index('COLE_stucco_plain_bq')
nfix=0
for poly in me.polygons:
    if poly.material_index==si: poly.material_index=0   # reset (idempotent)
for poly in me.polygons:
    nw=-(walls.matrix_world.to_3x3()@poly.normal).normalized(); cw=walls.matrix_world@poly.center   # wall normals point INWARD in this mesh
    if abs(nw.z)>0.5: continue
    if nw.y<-0.6 or (nw.x<-0.6 and cw.x<-155 and cw.y>-110):
        poly.material_index=si; nfix+=1
print('BQ_WALLFIX faces',nfix)
M_tile=mat('COLE_tower_tile_bq',(0.40,0.13,0.07),0.7)  # own flat terracotta (hip-tile mat is UV/coord-driven and read slate on small caps)
M_fr=mat('COLE_win_frame_bq',(0.035,0.045,0.04),0.5)
M_gl=mat('COLE_win_glass_bq',(0.015,0.018,0.022),0.35)
M_ox=mat('COLE_oxblood_wood_bq',(0.28,0.06,0.045),0.65)
M_cu=mat('COLE_copper_verdigris_bq',(0.30,0.52,0.44),0.45,0.3)
M_dk=mat('COLE_loggia_shadow_bq',(0.02,0.018,0.016),0.9)
M_br=mat('COLE_dark_brown_wood_bq',(0.10,0.05,0.035),0.6)
M_door=mat('COLE_maroon_door_bq',(0.11,0.025,0.02),0.5)
def new_obj(name,mats):
    me=bpy.data.meshes.new(name); o=bpy.data.objects.new(name,me); c.objects.link(o)
    for m in mats: me.materials.append(m)
    o['bq_source']='20261016bq'; return o
def add_box(bm,cx,cy,z0,z1,hx,hy,rot,mi):
    R=Matrix.Rotation(rot,4,'Z')
    vs=[bm.verts.new(Vector((cx,cy,0))+(R@Vector((sx*hx,sy*hy,0))).to_3d()+Vector((0,0,z))) for z in (z0,z1) for sx,sy in ((-1,-1),(1,-1),(1,1),(-1,1))]
    for f in ((0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)):
        bm.faces.new([vs[i] for i in f]).material_index=mi
def add_pyr(bm,cx,cy,z0,z1,h,rot,mi,apex_h=0.0):
    R=Matrix.Rotation(rot,4,'Z')
    b=[bm.verts.new(Vector((cx,cy,z0))+(R@Vector((sx*h,sy*h,0))).to_3d()) for sx,sy in ((-1,-1),(1,-1),(1,1),(-1,1))]
    if apex_h>0:
        t=[bm.verts.new(Vector((cx,cy,z1))+(R@Vector((sx*apex_h,sy*apex_h,0))).to_3d()) for sx,sy in ((-1,-1),(1,-1),(1,1),(-1,1))]
        for i in range(4): bm.faces.new([b[i],b[(i+1)%4],t[(i+1)%4],t[i]]).material_index=mi
        bm.faces.new(t).material_index=mi
    else:
        a=bm.verts.new((cx,cy,z1))
        for i in range(4): bm.faces.new([b[i],b[(i+1)%4],a]).material_index=mi
    bm.faces.new(b[::-1]).material_index=mi
def add_dome(bm,cx,cy,z0,z1,r,mi,seg=12,rings=5):
    prev=None
    for k in range(rings+1):
        t=k/rings; zz=z0+(z1-z0)*t
        rr=r*(1.0-t**1.6)*(1+0.18*math.sin(math.pi*t))  # bell/ogee-ish profile UNVERIFIED
        cur=[bm.verts.new((cx+rr*math.cos(2*math.pi*j/seg),cy+rr*math.sin(2*math.pi*j/seg),zz)) for j in range(seg)]
        if prev:
            for j in range(seg): bm.faces.new([prev[j],prev[(j+1)%seg],cur[(j+1)%seg],cur[j]]).material_index=mi
        prev=cur
def posts(bm,cx,cy,z0,z1,h,rot,mi,per_side=3,pw=0.22):
    R=Matrix.Rotation(rot,4,'Z')
    for s in range(4):
        for k in range(per_side):
            u=-1+2*k/(per_side-1) if per_side>1 else 0
            loc=[(u*h,-h),(h,u*h),(-u*h,h),(-h,-u*h)][s]
            p=R@Vector((loc[0],loc[1],0)); add_box(bm,cx+p.x,cy+p.y,z0,z1,pw/2,pw/2,rot,mi)
# building rotation from long wall (-152.0,-98.2)->(-126.3,-104.2)
rot=math.atan2(-104.247+98.217,-126.347+151.955)
# --- towers
tw=new_obj('Cole Hall roof towers (LiDAR xy/top MEASURED; forms UNVERIFIED) bq',[M_st,M_tile,M_ox,M_cu,M_dk,M_fr,M_br])
bm=bmesh.new()
# central cupola, stages per bk dims (UNVERIFIED splits; top MEASURED 157.96)
cx,cy=-113.21,-95.5
add_box(bm,cx,cy,146.0,150.6,1.5,1.5,rot,2)           # red/oxblood base box from inside roof
add_box(bm,cx,cy,150.6,150.75,1.62,1.62,rot,2)        # sill/cornice lip
add_box(bm,cx,cy,150.75,153.6,1.25,1.25,rot,4)        # dark open-arcade core (shadow)
posts(bm,cx,cy,150.75,153.6,1.38,rot,2,per_side=3,pw=0.26)
add_box(bm,cx,cy,150.75,151.55,1.42,1.42,rot,2)       # panelled balustrade band
add_box(bm,cx,cy,153.6,154.0,1.7,1.7,rot,2)           # deep bracketed cornice
add_box(bm,cx,cy,154.0,155.85,0.85,0.85,rot,4)        # upper lantern core
posts(bm,cx,cy,154.0,155.85,1.02,rot,2,per_side=2,pw=0.22)
add_box(bm,cx,cy,155.85,156.2,1.2,1.2,rot,2)          # upper cornice
add_dome(bm,cx,cy,156.2,157.55,0.95,3)                # copper bell dome
add_box(bm,cx,cy,157.5,157.96,0.05,0.05,rot,3)       # spire finial to MEASURED top
for sx,sy in ((-1,-1),(1,-1),(1,1),(-1,1)):           # corner ball finials (approx as small cubes)
    p=Matrix.Rotation(rot,4,'Z')@Vector((sx*1.1,sy*1.1,0)); add_box(bm,cx+p.x,cy+p.y,156.2,156.45,0.11,0.11,rot,3)
# two ridge cupolas (LiDAR >151 clusters, tops MEASURED); form = oxblood belfry + verdigris dome per MSU 2020 aerial
# (X @MontclairStateU 2020-10-30 tour-map post, eye reference only) -- stage splits UNVERIFIED (scaled from central cupola)
for (bx,by,top) in ((-137.0,-89.4,155.72),(-89.1,-101.6,155.76)):
    zb=146.5; k=(top-149.0)/(157.96-149.0)
    Z=lambda z: zb+(z-149.0)*k*(top-zb)/(top-149.0)/k if False else 149.0+(z-149.0)*k
    add_box(bm,bx,by,zb,Z(150.6),1.35,1.35,rot,2)
    add_box(bm,bx,by,Z(150.6),Z(150.75),1.47,1.47,rot,2)
    add_box(bm,bx,by,Z(150.75),Z(154.0),1.1,1.1,rot,4)
    posts(bm,bx,by,Z(150.75),Z(154.0),1.22,rot,2,per_side=3,pw=0.22)
    add_box(bm,bx,by,Z(150.75),Z(151.55),1.26,1.26,rot,2)
    add_box(bm,bx,by,Z(154.0),Z(154.4),1.5,1.5,rot,2)
    add_dome(bm,bx,by,Z(154.4),top-0.35,1.05,3)
    add_box(bm,bx,by,top-0.4,top,0.05,0.05,rot,3)
# two south belvederes flanking the gable (2021 CC BY-SA photo + 2023 photo): LiDAR raised pads 149.5-150.0 MEASURED at
# (-124,-106.5) and (-108.5,-108.5); white shaft, open loggia w/ dark-brown posts, red-brown tile hip -- splits UNVERIFIED
for (bx,by,top) in ((-124.0,-106.5,150.0),(-108.5,-108.5,150.0)):
    h=2.2
    add_box(bm,bx,by,141.0,146.6,h,h,rot,0)
    add_box(bm,bx,by,146.6,146.75,h+0.1,h+0.1,rot,0)
    add_box(bm,bx,by,146.75,149.15,h-0.45,h-0.45,rot,4)
    posts(bm,bx,by,146.75,149.15,h-0.14,rot,6,per_side=4,pw=0.26)
    add_box(bm,bx,by,146.75,147.6,h-0.1,h-0.1,rot,0)
    add_box(bm,bx,by,149.15,149.38,h+0.55,h+0.55,rot,6)
    add_pyr(bm,bx,by,149.38,top,h+0.55,rot,1)
bm.to_mesh(tw.data); bm.free()
# --- windows on N- and W-facing walls
P=[Vector((x,y)) for x,y in ring]
if P[0]==P[-1]: P=P[:-1]
area=sum(P[i].x*P[(i+1)%len(P)].y-P[(i+1)%len(P)].x*P[i].y for i in range(len(P)))/2
win=new_obj('Cole Hall windows S+W faces (rhythm UNVERIFIED; photos 2023/PD) bq',[M_fr,M_gl,M_st])
bm=bmesh.new(); nwin=0; used=[]
PITCH,W,H=2.0,1.3,2.0
for i in range(len(P)):
    a,b=P[i],P[(i+1)%len(P)]; d=b-a; L=d.length
    if L<4.0: continue
    t=d/L; n=Vector((t.y,-t.x)) if area>0 else Vector((-t.y,t.x))
    # photo-backed faces only: SOUTH front (2021 CC BY-SA photo GPS 40.858722,-74.198564 -> scene (-115.7,-142.9), looking N at the gable)
    # + WEST face of west wing (PD West Wing photo). North side = 2020 modern addition (no photo) -> plain.
    if not (n.y<-0.6 or (n.x<-0.6 and i in (0,1,2))): continue
    if i in (10,11): continue   # gable pavilion: custom photo layout below
    nb=int((L-2.4)//PITCH)+1
    if nb<1: continue
    span=(nb-1)*PITCH; s0=(L-span)/2
    mid=a+d*0.5; gz=ground(mid.x+n.x*3,mid.y+n.y*3); z0=gz; avail=140.65-gz; H=min(2.0,avail*0.22); SILLS=[avail*f for f in (0.09,0.43,0.76)]
    used.append((i,round(L,1),nb,round(gz,2),('S' if n.y<-0.6 else 'W')))
    rr=math.atan2(t.y,t.x)
    for k in range(nb):
        p=a+t*(s0+k*PITCH)
        for row,sill in enumerate(SILLS):
            zc=z0+sill+H/2
            for (dep,hw,hh,mi) in ((0.05,W/2+0.07,H/2+0.07,0),(0.065,W/2-0.04,H/2-0.04,1)):
                q=p+n*(dep/2)
                add_box(bm,q.x,q.y,zc-hh,zc+hh,hw,dep/2,rr,mi)
            q=p+n*0.04; add_box(bm,q.x,q.y,zc-0.05+0.15,zc+0.05+0.15,W/2-0.04,0.04,rr,0)   # meeting rail (2-sash look)
            q=p+n*0.06; add_box(bm,q.x,q.y,z0+sill-0.11,z0+sill-0.02,W/2+0.15,0.06,rr,2)    # stucco sill
            nwin+=1
bm.to_mesh(win.data); bm.free()
# --- south-central Mission gable (2021 photo); top 151.57 MEASURED (LiDAR 2-cell cluster at (-116,-108.5)); outline UNVERIFIED
ga,gb=Vector((-120.568,-107.669)),Vector((-111.355,-109.825))
gd=gb-ga; gL=gd.length; gt=gd/gL; gn=Vector((gt.y,-gt.x)) if area>0 else Vector((-gt.y,gt.x))
Z0,ZT=141.0,151.57; HH=ZT-Z0
half=[(0,0),(0,0.30),(0.03,0.33),(0.08,0.36),(0.14,0.42),(0.20,0.50),(0.25,0.58),(0.29,0.66),(0.32,0.72),(0.34,0.76),(0.36,0.78),(0.36,0.93),(0.40,0.95),(0.5,1.0)]
prof=half+[(1-u,h) for (u,h) in reversed(half[:-1])]
gab=new_obj('Cole Hall south Mission gable (top MEASURED 151.57; outline UNVERIFIED from 2021 photo) bq',[M_st,M_dk,M_fr,M_gl,M_door])
bm=bmesh.new()
def P3(u,h,off): q=ga+gt*(u*gL)-gn*off; return Vector((q.x,q.y,Z0+h*HH))
front=[bm.verts.new(P3(u,h,-0.05)) for u,h in prof]; back=[bm.verts.new(P3(u,h,0.6)) for u,h in prof]
bm.faces.new(front[::-1]); bm.faces.new(back)
for k in range(len(prof)-1): bm.faces.new([front[k],front[k+1],back[k+1],back[k]])
bm.faces.new([front[-1],front[0],back[0],back[-1]])
c0=ga+gt*(gL*0.5)
q=c0+gn*0.07; add_box(bm,q.x,q.y,Z0+0.79*HH,Z0+0.90*HH,0.42,0.06,math.atan2(gt.y,gt.x),1)   # bell niche (dark)
q=c0+gn*0.08; add_box(bm,q.x,q.y,Z0+0.47*HH,Z0+0.47*HH+1.1,0.75,0.06,math.atan2(gt.y,gt.x),2)  # oculus window (as frame block)
q=c0+gn*0.10; add_box(bm,q.x,q.y,Z0+0.47*HH+0.12,Z0+0.47*HH+0.98,0.6,0.06,math.atan2(gt.y,gt.x),1)
# (3 arched gable windows = generic row-3 windows on edges 10/11; not doubled)
# gable pavilion openings per 2021/2023 photos (layout ACCURATE-by-eye, sizes UNVERIFIED): r1 window|arched door|window,
# r2 three windows, r3 three tall arched windows (stair landing in photo is not modelled)
gz=ground(*(c0-gn*3)); rg=math.atan2(gt.y,gt.x)
def win_at(u,zs,w,hh,arch=False):
    p=ga+gt*(gL*u)
    q=p+gn*0.05; add_box(bm,q.x,q.y,zs,zs+hh,w/2+0.08,0.05,rg,2)
    q=p+gn*0.065; add_box(bm,q.x,q.y,zs+0.05,zs+hh-0.05,w/2-0.04,0.05,rg,3)
    if arch:
        for k in range(6):
            a0=math.pi*k/6; a1=math.pi*(k+1)/6; xm=(math.cos(a0)+math.cos(a1))/2*(w/2); hw=abs(math.cos(a0)-math.cos(a1))/2*(w/2)+0.02
            zz=zs+hh+max(math.sin(a0),math.sin(a1))*(w/2); q=p+gt*xm+gn*0.06; add_box(bm,q.x,q.y,zs+hh-0.05,zz,hw,0.05,rg,3 if k else 3)
for u in (0.2,0.8): win_at(u,gz+1.0,1.25,2.0)
p=ga+gt*(gL*0.5); q=p+gn*0.06; add_box(bm,q.x,q.y,gz+0.6,gz+3.4,0.95,0.06,rg,4)          # maroon door (photo) on landing
q=p+gn*0.05; add_box(bm,q.x,q.y,gz+0.5,gz+4.3,1.2,0.05,rg,2)                              # dark door surround / fanlight
for u in (0.2,0.5,0.8): win_at(u,gz+4.9,1.25,2.0)
for u in (0.2,0.5,0.8): win_at(u,gz+8.0,1.1,1.6,arch=True)
bm.to_mesh(gab.data); bm.free()

# --- 2020 north addition (HMR / MSU: 5,000 sf north-side addition, two-storey atrium). Not in OSM ring; footprint = min rotated
# rectangle of 2023 LiDAR bld cells >141.5 outside OSM (396 cells): MEASURED +-1 m; eave 143.2 / ridge 149.3 MEASURED (p10/max);
# gable end faces north (ridge runs N-S in LiDAR). North-end tall arched window + glazed entrance from MSU 2020 aerial (X post,
# eye reference) -- sizes UNVERIFIED. Side walls plain (no clear photo). South end pushed 2.5 m into the old building (4a rule).
A=Vector((-120.51,-77.88)); B=Vector((-98.02,-83.07)); D=Vector((-116.57,-60.79))
uu=(B-A); Lu=uu.length; uu/=Lu; vv=(D-A); Lv=vv.length; vv/=Lv
def Q(u,v,z): p=A+uu*u+vv*v; return Vector((p.x,p.y,z))
EAVE,RIDGE=143.2,149.3
gzN=min(ground(*(A+uu*(Lu/2)+vv*(Lv+2.0))), ground(*(A+vv*(Lv+2.0))), ground(*(B+vv*(Lv+2.0))))
u0,u1,v0,v1=-0.5,Lu+0.5,-2.5,Lv+0.5; um=(u0+u1)/2; Z0=gzN-1.5
nad=new_obj('Cole Hall 2020 north addition (LiDAR footprint/eave/ridge MEASURED; openings UNVERIFIED) bq',[M_st,M_tile,M_fr,M_gl])
bm=bmesh.new()
def face(pts,mi):
    vs=[bm.verts.new(p) for p in pts]; f=bm.faces.new(vs); f.material_index=mi
# walls: two long sides + north gable end (pentagon) + south (hidden) end
face([Q(u0,v0,Z0),Q(u0,v1,Z0),Q(u0,v1,EAVE),Q(u0,v0,EAVE)][::-1],0)
face([Q(u1,v0,Z0),Q(u1,v0,EAVE),Q(u1,v1,EAVE),Q(u1,v1,Z0)][::-1],0)
face([Q(u0,v1,Z0),Q(u1,v1,Z0),Q(u1,v1,EAVE),Q(um,v1,RIDGE),Q(u0,v1,EAVE)],0)
face([Q(u0,v0,Z0),Q(u0,v0,EAVE),Q(um,v0,RIDGE),Q(u1,v0,EAVE),Q(u1,v0,Z0)],0)
# roof slabs w/ 0.6 m overhang, 0.25 thick
ov=0.6; sl=(RIDGE-EAVE)/(um-u0)
for side in (-1,1):
    ue=(u0-ov) if side<0 else (u1+ov); ze=EAVE-ov*sl
    for t,mi in ((0.0,1),(-0.25,1)):
        pass
    top=[Q(ue,v0,ze),Q(ue,v1+ov,ze),Q(um,v1+ov,RIDGE+0.05),Q(um,v0,RIDGE+0.05)]
    if side>0: top=top[::-1]
    add=[bm.verts.new(p) for p in top]; bm.faces.new(add).material_index=1
    bot=[bm.verts.new(p-Vector((0,0,0.25))) for p in top]; bm.faces.new(bot[::-1]).material_index=1
    for k in range(4): bm.faces.new([add[k],bot[k],bot[(k+1)%4],add[(k+1)%4]]).material_index=1
# north-end tall arched window (2-storey) + glazed entrance below
nrm=vv; rr=math.atan2(uu.y,uu.x)
cN=A+uu*um+vv*(v1+0.04)
zb=gzN+4.0; w=7.0; zt=EAVE+1.6
add_box(bm,cN.x,cN.y,zb,zt-w/2,w/2+0.12,0.05,rr,2)
add_box(bm,(cN+nrm*0.02).x,(cN+nrm*0.02).y,zb+0.1,zt-w/2,w/2-0.05,0.05,rr,3)
seg=10
for k in range(seg):     # semicircular head as stepped slices
    a0=math.pi*k/seg; a1=math.pi*(k+1)/seg; xm=(math.cos(a0)+math.cos(a1))/2*(w/2); hw=abs(math.cos(a0)-math.cos(a1))/2*(w/2)
    zz=zt-w/2+max(math.sin(a0),math.sin(a1))*(w/2)
    p=cN+uu*xm; add_box(bm,p.x,p.y,zt-w/2,zz,hw+0.01,0.05,rr,3)
for xm in (-w/3,-w/6,0,w/6,w/3):  # mullions
    p=cN+uu*xm+nrm*0.05; add_box(bm,p.x,p.y,zb+0.1,zt-w/2+math.sqrt(max(0,(w/2)**2-xm**2))-0.05,0.05,0.04,rr,2)
for zm in (zb+2.3,zb+4.6):
    p=cN+nrm*0.05; add_box(bm,p.x,p.y,zm-0.05,zm+0.05,w/2-0.05,0.04,rr,2)
add_box(bm,cN.x,cN.y,gzN-0.2,gzN+3.1,3.2,0.06,rr,2)
p=cN+nrm*0.03; add_box(bm,p.x,p.y,gzN-0.1,gzN+3.0,3.05,0.06,rr,3)
for xo in (-7.5,-5.6,5.6,7.5):          # flanking narrow windows, 3 rows (aerial, UNVERIFIED sizes)
    for zz in (gzN+0.9,gzN+4.4,gzN+7.6):
        p=cN+uu*xo; add_box(bm,p.x,p.y,zz,zz+2.2,0.55,0.05,rr,2); p=p+nrm*0.02; add_box(bm,p.x,p.y,zz+0.06,zz+2.14,0.47,0.05,rr,3)
bm.to_mesh(nad.data); bm.free()
print('BQ_NADD Lu %.1f Lv %.1f groundN %.2f'%(Lu,Lv,gzN))

print('BQ_COLE edges',used,'windows',nwin)
sc['bq_cole_hall']='towers3 windows%d edges%d'%(nwin,len(used))
# --- cameras
def cam(name,loc,tgt,lens):
    o=bpy.data.objects.get(name)
    if not o:
        o=bpy.data.objects.new(name,bpy.data.cameras.new(name)); sc.collection.objects.link(o)
    o.data.lens=lens; o.data.clip_end=60000; o.location=loc
    o.rotation_euler=(Vector(tgt)-Vector(loc)).to_track_quat('-Z','Y').to_euler()
gS=ground(-115.7,-142.9); gW=ground(-205,-100)
for nm in ('CAM_eye_cole_hall_north_bq',):
    if nm in bpy.data.objects: bpy.data.objects.remove(bpy.data.objects[nm],do_unlink=True)
cam('CAM_oblique_cole_hall_bq',(-20,-235,195),(-113,-100,142),30)
cam('CAM_eye_cole_hall_south_bq',(-115.7,-142.9,gS+1.65),(-115.5,-105,146.5),22)
cam('CAM_eye_cole_hall_west_bq',(-205,-118,gW+1.65),(-140,-92,141),30)
cam('CAM_closeup_cole_hall_towers_bq',(-98,-150,151),(-113,-99,151.5),60)
gNa=ground(-96,-30)
cam('CAM_eye_cole_hall_north_addition_bq',(-96,-30,gNa+1.65),(-108,-68,141.5),26)
print('BQ_CAMS ground S %.2f W %.2f'%(gS,gW))
if os.environ.get('SAVE')=='1':
    bpy.ops.wm.save_mainfile(); print('BQ_SAVED')
