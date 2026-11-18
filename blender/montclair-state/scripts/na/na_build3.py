# Session na pass 3: CCM office desk clutter (laptops, bottles, mice, desk phone, power strip; kinds as in Joe's photo)
# + 2 robotic PTZ camera heads hung from the studio lighting grid aimed at the anchor desk. All UNVERIFIED.
import bpy, bmesh, math, os, random
from mathutils import Vector, Matrix
MODE=os.environ.get('NA_MODE','TEST')
SES='na'
L=math.hypot(0.238,0.9713); d=Vector((0.238/L,0.9713/L,0)); n=Vector((-0.9713/L,0.238/L,0)); C0=20.36; T0=0.012
def P(u,t,z): return d*u+n*(C0+T0+t)+Vector((0,0,z))
U0=-18.04; UA=U0+0.35; UB=1.8; TM=-9.8; TBACK=-14.3; ZF=137.41; ZM1=141.85; ZC=146.4
edges=[UA+(UB-UA)*k/5 for k in range(6)]; IU0,IU1=edges[4]+0.05,edges[5]-0.05; IT0,IT1=TM-0.05,TBACK
ZD=ZM1+0.01+0.74
mats=bpy.data.materials
def mat(name,col,rough=0.6,metal=0.0,emit=None,es=0.0,alpha=1.0):
    m=mats.get(name)
    if m: return m
    m=mats.new(name); m.use_nodes=True; b=m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=(*col,1); b.inputs['Roughness'].default_value=rough; b.inputs['Metallic'].default_value=metal
    if emit: b.inputs['Emission Color'].default_value=(*emit,1); b.inputs['Emission Strength'].default_value=es
    if alpha<1: b.inputs['Transmission Weight'].default_value=0.9
    m['msu_tag_session']=SES; return m
M_LAP=mat('NA_laptop_dark_grey_UNVERIFIED',(0.04,0.04,0.045),0.4,metal=0.4)
M_LSCR=mats.get('MY_desk_monitor_screen_generic_UNVERIFIED')
M_BOT=mat('NA_water_bottle_clear_UNVERIFIED',(0.85,0.9,0.95),0.05,alpha=0.5)
M_CAP=mat('NA_bottle_cap_white_UNVERIFIED',(0.9,0.9,0.9),0.5)
M_BLK=mats['NA_keyboard_black_UNVERIFIED']
M_PTZ=mat('NA_ptz_head_black_UNVERIFIED',(0.02,0.02,0.022),0.35,metal=0.3)
M_GLS=mats.get('Dark_glass') or M_BLK
M_TAL=mat('NA_ptz_tally_red_UNVERIFIED',(0.8,0.02,0.02),0.3,emit=(1,0.05,0.03),es=8)
def newobj(name,bm,mlist,coln):
    col=bpy.data.collections[coln]
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for m in mlist: me.materials.append(m)
    o=bpy.data.objects.new(name,me); col.objects.link(o); o['msu_tag_session']=SES; o['status']='UNVERIFIED'
    o['source']='kinds per Joe photo ccm_current_office_above_newsroom.jpg / typical studio PTZ; positions invented'; return o
def box(bm,u0,u1,t0,t1,z0,z1,mi=0):
    vs=[bm.verts.new(P(u,t,z)) for z in (z0,z1) for t in (t0,t1) for u in (u0,u1)]
    for f in [(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]:
        try: bm.faces.new([vs[i] for i in f]).material_index=mi
        except ValueError: pass
def cyl(bm,c,r,z0,z1,nseg=10,mi=0):
    lo=[bm.verts.new(c+Vector((r*math.cos(2*math.pi*k/nseg),r*math.sin(2*math.pi*k/nseg),z0))) for k in range(nseg)]
    hi=[bm.verts.new(c+Vector((r*math.cos(2*math.pi*k/nseg),r*math.sin(2*math.pi*k/nseg),z1))) for k in range(nseg)]
    bm.faces.new(lo[::-1]).material_index=mi; bm.faces.new(hi).material_index=mi
    for k in range(nseg): bm.faces.new([lo[k],lo[(k+1)%nseg],hi[(k+1)%nseg],hi[k]]).material_index=mi
COL1='MS_CCM_office_interior_20261030na'
# laptops: base + tilted lid (screen faces the user). Desk A users at t<desk, face +t.
bm=bmesh.new(); uvl=bm.loops.layers.uv.verify()
def laptop(u,t,s,ang=105):
    # s=+1 user on -t side (faces +t): hinge at t+0.12*s
    box(bm,u-0.17,u+0.17,t-0.12,t+0.12,ZD,ZD+0.018,0)
    th=math.radians(ang); hz=ZD+0.018; ht=t+0.12*s
    def LP(du,r,off=0.0): return P(u+du, ht - s*math.cos(th)*r*(-1) - s*off*math.sin(th) if False else ht + s*(-math.cos(math.pi-th))*r*0 - s*r*math.cos(th) + s*off, hz + r*math.sin(th))
    corners=[(-0.17,0),(0.17,0),(0.17,0.23),(-0.17,0.23)]
    vb=[bm.verts.new(LP(du,r)) for du,r in corners]; vf=[bm.verts.new(LP(du,r)+ (P(0,-s*0.008,0)-P(0,0,0))) for du,r in corners]
    for f in ([vb[0],vb[1],vb[2],vb[3]],[vf[3],vf[2],vf[1],vf[0]],[vb[0],vf[0],vf[1],vb[1]],[vb[2],vf[2],vf[3],vb[3]],[vb[1],vf[1],vf[2],vb[2]],[vb[3],vf[3],vf[0],vb[0]]):
        bm.faces.new(f).material_index=0
    sc=[(-0.155,0.015),(0.155,0.015),(0.155,0.215),(-0.155,0.215)]
    vs=[bm.verts.new(LP(du,r)+(P(0,-s*0.0095,0)-P(0,0,0))) for du,r in sc]
    f=bm.faces.new(vs if s<0 else vs[::-1]); f.material_index=1
    ox=random.random()*0.5
    uvs=[(ox,0),(ox+0.5,0),(ox+0.5,1),(ox,1)]
    for lp,uv in zip(f.loops,(uvs if s<0 else uvs[::-1])): lp[uvl].uv=uv
random.seed(3)
laptop(IU0+0.95,IT0-0.55,1); laptop(IU1-0.9,-11.75,-1)
newobj('CCM office laptops (na)',bm,[M_LAP,M_LSCR],COL1)
bm=bmesh.new()
for (u,t) in ((IU0+0.55,IT0-0.62),(IU0+2.05,IT0-0.70),(IU1-0.35,-12.6)):
    c=P(u,t,0); cyl(bm,c,0.033,ZD,ZD+0.20,mi=0); cyl(bm,c,0.018,ZD+0.20,ZD+0.235,mi=1)
newobj('CCM office water bottles (na)',bm,[M_BOT,M_CAP],COL1)
bm=bmesh.new()
for (u,t) in ((IU0+1.25,IT0-0.62),(IU0+2.45,IT0-0.62),(IU0+1.05,IT1+0.45)):
    box(bm,u-0.03,u+0.03,t-0.05,t+0.05,ZD,ZD+0.03)
box(bm,IU1-1.45,IU1-1.25,-11.6,-11.82,ZD,ZD+0.07); box(bm,IU1-1.44,IU1-1.26,-11.62,-11.70,ZD+0.07,ZD+0.10)   # desk phone + handset
box(bm,IU0+0.40,IU0+0.85,IT0-0.18,IT0-0.24,ZD,ZD+0.04)    # power strip
newobj('CCM office mice, desk phone, power strip (na)',bm,[M_BLK],COL1)
# ---- PTZ heads ----
COL2='MS_CCOM_back_rooms_furnish_20261030na'
bm=bmesh.new()
tgt=P(UA+2.35,-6.2,ZF+1.3)
for (u,t) in ((UA+6.2,-5.0),(UA+6.2,-7.5)):
    zg=ZC-0.90
    box(bm,u-0.03,u+0.03,t+0.03,t-0.03,zg-0.12,zg,0)               # drop rod from grid bar
    box(bm,u-0.10,u+0.10,t+0.10,t-0.10,zg-0.16,zg-0.12,0)           # mount plate
    cyl(bm,P(u,t,0),0.07,zg-0.22,zg-0.16,mi=0)                      # pan base
    # tilted body aimed at the anchor desk
    o=P(u,t,zg-0.36); v=(tgt-o).normalized()
    side=v.cross(Vector((0,0,1))).normalized(); up=side.cross(v)
    def Q(a,b,c): return o+v*a+side*b+up*c
    ex=[(-0.12,0.13),(-0.075,0.075),(-0.09,0.09)]
    vs=[bm.verts.new(Q(a,b,c)) for a in (-0.12,0.13) for b in (-0.075,0.075) for c in (-0.09,0.09)]
    for f in [(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]: bm.faces.new([vs[i] for i in f]).material_index=0
    for b in (-0.085,0.085):   # yoke arms
        ws=[bm.verts.new(x) for x in (Q(-0.03,b,0.0)+Vector((0,0,0)),Q(0.03,b,0),P(u,t,zg-0.20)+side*b+Vector((0,0,0)))]
        bm.faces.new(ws).material_index=0
    lc=Q(0.13,0,0)
    lens=[bm.verts.new(Q(0.13+0.004,0.045*math.cos(2*math.pi*k/12),0.045*math.sin(2*math.pi*k/12))) for k in range(12)]
    bm.faces.new(lens).material_index=1
    tl=[bm.verts.new(Q(0.131,b2,c2)) for b2,c2 in ((0.055,0.065),(0.07,0.065),(0.07,0.08),(0.055,0.08))]
    bm.faces.new(tl).material_index=2
newobj('CCOM newsroom robotic PTZ camera heads on the grid (na)',bm,[M_PTZ,M_GLS,M_TAL],COL2)
print("PTZ tgt",tuple(round(x,2) for x in tgt), "PTZ1",tuple(round(x,2) for x in P(UA+6.2,-5.0,ZC-1.26)))
out=bpy.data.filepath if MODE=='SAVE' else os.path.abspath('data/na/test.blend')
bpy.ops.wm.save_as_mainfile(filepath=out,copy=(MODE!='SAVE'))
print("SAVED",out,len(bpy.data.objects))
