# Session mw (Oct 29 2026): CCOM west bay south of the entrance = ONE double-height NJ PBS newsroom studio (Joe 10:45 PM).
# Mode env MW_MODE=SAVE (live) | TEST (write to data/mw/test.blend)
import bpy, bmesh, math, os
from mathutils import Vector
MODE=os.environ.get('MW_MODE','TEST')
SES='mw'; COLN='MS_CCOM_newsroom_studio_20261029mw'
L=math.hypot(0.238,0.9713); d=Vector((0.238/L,0.9713/L,0)); n=Vector((-0.9713/L,0.238/L,0)); C0=20.36; T0=0.012
def P(u,t,z): return d*u+n*(C0+T0+t)+Vector((0,0,z))
U0,U1=-18.04,2.83; ZB,ZT=135.3,147.61
SILL,SPR,R=137.85,144.75,1.05
mats=bpy.data.materials
def mat(name,col,rough=0.6,emit=None,metal=0.0):
    m=mats.get(name)
    if m: return m
    m=mats.new(name); m.use_nodes=True; b=m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=(*col,1); b.inputs['Roughness'].default_value=rough; b.inputs['Metallic'].default_value=metal
    if emit: b.inputs['Emission Color'].default_value=(*emit,1); b.inputs['Emission Strength'].default_value=6.0
    m['msu_tag_session']=SES; return m
M_WALL=mats['Wall_SCM_precast']; M_FR=mats['Mullion_mahogany']; M_GL=mats['CCOM_atrium_glass_interior']
M_IW=mats['CCOM_int_wall_white_20261014v']; M_DESK=mats['CCOM_dc_table_white']; M_MON=mats['Dark_glass']
M_REV=mats.get('CCOM_win_reveal_stucco') or M_WALL; M_SILL=mats.get('CCOM_win_sill_cast_stone') or M_WALL
M_FLOOR=mat('MW_studio_raised_floor_grey_UNVERIFIED',(0.42,0.43,0.43),0.5)
M_CEIL=mat('MW_studio_open_ceiling_dark_UNVERIFIED',(0.06,0.06,0.065),0.8)
M_LED=mat('MW_studio_light_panel_emit_UNVERIFIED',(0.9,0.9,0.9),0.5,emit=(1.0,0.97,0.92))
M_SET=mat('MW_studio_set_backdrop_blue_UNVERIFIED',(0.03,0.09,0.25),0.4,emit=(0.05,0.15,0.5))
M_ANCH=mat('MW_anchor_desk_gloss_white_UNVERIFIED',(0.85,0.86,0.88),0.15)
M_PART=mat('MW_cubicle_partition_white_UNVERIFIED',(0.82,0.83,0.82),0.7)
M_TRUSS=mat('MW_lighting_grid_black_UNVERIFIED',(0.02,0.02,0.02),0.5,metal=0.6)
M_CARP=mat('MW_ccm_office_carpet_UNVERIFIED',(0.25,0.22,0.24),0.9)

col=bpy.data.collections.get(COLN)
if col is None:
    col=bpy.data.collections.new(COLN); bpy.context.scene.collection.children.link(col)
col['msu_tag_session']=SES
def newobj(name,bm,mlist,status='UNVERIFIED'):
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for m in mlist: me.materials.append(m)
    o=bpy.data.objects.new(name,me); col.objects.link(o)
    o['msu_tag_session']=SES; o['status']=status; o['source']="Joe correction Oct 29 10:45 PM + refs ccom_usgbc_exterior_03 / ccom_njpbs_newsroom_21 / ccom_nv5_classroom_10"
    return o
def box(bm,u0,u1,t0,t1,z0,z1,mi=0):
    vs=[bm.verts.new(P(u,t,z)) for z in (z0,z1) for t in (t0,t1) for u in (u0,u1)]
    # idx: z0: (t0u0,t0u1,t1u0,t1u1)=0..3, z1 4..7
    for f in [(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]:
        try: bm.faces.new([vs[i] for i in f]).material_index=mi
        except ValueError: pass
# ---------- 1. hide old 2-row windows + dd rooms inside the studio ----------
hidden=[]
centers=[]
for i in range(82,92):
    for nm in [o.name for o in bpy.data.objects if o.name.startswith('CCOM_win_%03d_'%i)]:
        o=bpy.data.objects[nm]
        if nm.endswith('_r0'): centers.append(d.dot(o.matrix_world.translation))
        o.hide_render=True; o.hide_viewport=True; hidden.append(nm)
centers=sorted(centers); print("CENTERS",centers)
UMAX_ST=1.8; TBACK=-14.3
def inside(o):
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; c=sum(bb,Vector())/8
    u=d.dot(c); t=n.dot(c)-C0-T0
    return (U0-0.2)<u<UMAX_ST+0.6 and TBACK-0.5<t<0.1 and 137.0<c.z<147
for o in bpy.data.objects:
    if o.name.startswith(('dd_WEST0','dd_SOUTH1')) and not o.hide_render and inside(o):
        o.hide_render=True; o.hide_viewport=True; hidden.append(o.name)
print("HIDDEN",len(hidden))
# ---------- 2. wall: delete old bay faces, rebuild with 5 tall arched openings ----------
w=bpy.data.objects['School of Communication and Media walls']; Mw=w.matrix_world
bm=bmesh.new(); bm.from_mesh(w.data); kill=[]
for f in bm.faces:
    ok=True
    for v in f.verts:
        p=Mw@v.co; u=d.dot(p); t=n.dot(p)-C0
        if not (U0-0.01<=u<=U1+0.01 and abs(t-T0)<0.03 and 134.5<=p.z<=ZT+0.01): ok=False; break
    if ok: kill.append(f)
print("KILL faces",len(kill)); bmesh.ops.delete(bm,geom=kill,context='FACES'); bm.to_mesh(w.data); bm.free()
w['mw_note']="mw: %d west-bay faces (u %.2f..%.2f) removed; replaced by '%s' (single-height arched studio glazing)"%(len(kill),U0,U1,'CCOM newsroom bay wall (mw)')
NA=12
def arch_pts(uc): return [(uc+R*math.cos(math.pi*k/NA), SPR+R*math.sin(math.pi*k/NA)) for k in range(NA+1)]  # right->left
def wall_face(bm,t,flip=False):
    def q(a): 
        f=bm.faces.new([bm.verts.new(P(u,t,z)) for u,z in (a[::-1] if flip else a)]); return f
    edges=[U0]+[x for uc in centers for x in (uc-R,uc+R)]+[U1]
    for i in range(0,len(edges),2): q([(edges[i],ZB),(edges[i+1],ZB),(edges[i+1],ZT),(edges[i],ZT)])  # piers
    for uc in centers:
        q([(uc-R,ZB),(uc+R,ZB),(uc+R,SILL),(uc-R,SILL)])
        ap=arch_pts(uc)
        for k in range(NA):
            (ua,za),(ub,zb)=ap[k],ap[k+1]
            q([(ub,zb),(ua,za),(ua,ZT),(ub,ZT)])
        q([(uc+R,SILL),(uc+R,SPR),(uc+R,SPR)]) if False else None
        q([(uc+R,SPR),(uc+R,SPR+0.0001),(uc+R,ZT),(uc+R,ZT-0.0001)]) if False else None
DEP=0.30
bm=bmesh.new(); wall_face(bm,0.0,True); wall_face(bm,-DEP,False)
# reveals: jambs below spring + arch soffit + sill
for uc in centers:
    for us in (uc-R,uc+R):
        vs=[bm.verts.new(P(us,t,z)) for t,z in ((0,SILL),(-DEP,SILL),(-DEP,SPR),(0,SPR))]; bm.faces.new(vs).material_index=1
    ap=arch_pts(uc)
    for k in range(NA):
        (ua,za),(ub,zb)=ap[k],ap[k+1]
        bm.faces.new([bm.verts.new(P(ua,0,za)),bm.verts.new(P(ub,0,zb)),bm.verts.new(P(ub,-DEP,zb)),bm.verts.new(P(ua,-DEP,za))]).material_index=1
bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=0.0005)
newobj('CCOM newsroom bay wall (mw)',bm,[M_WALL,M_REV],'shape from ccom_usgbc_exterior_03 (5 tall arched single-height windows); sizes UNVERIFIED')
# sills (proud 6 cm, under the opening, 10 cm wider)
bm=bmesh.new()
for uc in centers: box(bm,uc-R-0.10,uc+R+0.10,0.06,-DEP+0.02,SILL-0.09,SILL-0.005)
newobj('CCOM newsroom bay sills (mw)',bm,[M_SILL])
# glass + mullion grid (maroon)
TG=-0.16
bm=bmesh.new()
for uc in centers:
    pts=[(uc-R,SILL),(uc+R,SILL)]+arch_pts(uc)
    bm.faces.new([bm.verts.new(P(u,TG,z)) for u,z in pts])
newobj('CCOM newsroom bay glass (mw)',bm,[M_GL])
bm=bmesh.new(); FW=0.06
for uc in centers:
    # outer frame jambs + sill rail
    box(bm,uc-R,uc-R+0.08,TG+0.05,TG-0.05,SILL,SPR); box(bm,uc+R-0.08,uc+R,TG+0.05,TG-0.05,SILL,SPR)
    box(bm,uc-R,uc+R,TG+0.05,TG-0.05,SILL,SILL+0.10)
    # arch frame
    ap=[(uc+(R-0.04)*math.cos(math.pi*k/NA),SPR+(R-0.04)*math.sin(math.pi*k/NA)) for k in range(NA+1)]
    for k in range(NA):
        (ua,za),(ub,zb)=ap[k],ap[k+1]
        q=[P(ua,TG+0.05,za-0.0),P(ub,TG+0.05,zb),P(ub,TG-0.05,zb),P(ua,TG-0.05,za)]
        vs=[bm.verts.new(x) for x in q]; bm.faces.new(vs)
    # 3 verticals (4 lights wide), transoms every ~0.86 m up to the spring
    for j in (1,2,3):
        uj=uc-R+2*R*j/4; zt=SPR+math.sqrt(max(0,(R-0.04)**2-(uj-uc)**2))
        box(bm,uj-FW/2,uj+FW/2,TG+0.04,TG-0.04,SILL+0.10,zt)
    for z in [SILL+0.10+k*((SPR-SILL-0.10)/8) for k in range(1,9)]:
        box(bm,uc-R+0.08,uc+R-0.08,TG+0.04,TG-0.04,z-0.03,z+0.03)
newobj('CCOM newsroom bay mullion grid (mw, maroon)',bm,[M_FR],'maroon grid per photos; 4x9 lights UNVERIFIED')
# ---------- 3. studio interior blocking ----------
UA,UB=U0+0.35,UMAX_ST; TF=-DEP-0.02; ZF=137.41; ZC=146.4
bm=bmesh.new(); box(bm,UA,UB,TF,TBACK,ZF-0.25,ZF)
newobj('CCOM newsroom studio floor (raised access, mw)',bm,[M_FLOOR])
bm=bmesh.new(); box(bm,UA,UB,TF,TBACK,ZC,ZC+0.15)
newobj('CCOM newsroom studio ceiling (open, dark, mw)',bm,[M_CEIL])
bm=bmesh.new()
box(bm,UA-0.2,UA,TF,TBACK,ZF,ZC); box(bm,UB,UB+0.2,TF,TBACK,ZF,ZC); box(bm,UA-0.2,UB+0.2,TBACK,TBACK-0.2,ZF,ZC)
newobj('CCOM newsroom studio side + back walls (mw)',bm,[M_IW])
# lighting grid + light panels
bm=bmesh.new()
for t in (-2.5,-5.0,-7.5):
    box(bm,UA+0.5,UB-0.5,t+0.04,t-0.04,ZC-0.9,ZC-0.84)
for u in [UA+1+k*2.5 for k in range(int((UB-UA-2)/2.5)+1)]:
    for t in (-2.5,-5.0,-7.5): box(bm,u-0.02,u+0.02,t+0.02,t-0.02,ZC-0.84,ZC)
newobj('CCOM newsroom studio lighting grid (mw)',bm,[M_TRUSS])
bm=bmesh.new()
for u in [UA+1.5+k*3.0 for k in range(int((UB-UA-3)/3.0)+1)]:
    for t in (-1.6,-4.2,-6.8,-9.4): box(bm,u-0.6,u+0.6,t+0.3,t-0.3,ZC-0.03,ZC-0.005)
newobj('CCOM newsroom studio ceiling light panels (mw)',bm,[M_LED])
# back 2-floor split: mezzanine
TM=-9.8; ZM0,ZM1=141.55,141.85
bm=bmesh.new(); box(bm,UA,UB,TM,TBACK,ZM0,ZM1); box(bm,UA,UB,TM,TM-0.05,140.55,ZM0)  # slab + white fascia band (TVs)
newobj('CCOM newsroom back mezzanine slab + fascia (mw)',bm,[M_IW])
# room dividers + glass fronts, lower (NJ PBS mgmt offices) and upper (glass conference rooms; far-LEFT = CCM)
NR=5; edges=[UA+(UB-UA)*k/NR for k in range(NR+1)]
bm=bmesh.new()
for lvl,(z0,z1) in enumerate(((ZF,140.55),(ZM1,144.9))):
    box(bm,UA,UB,TM+0.04,TM-0.04,z0,z0+0.08); box(bm,UA,UB,TM+0.04,TM-0.04,z1-0.08,z1)
    for e in edges:
        box(bm,e-0.04,e+0.04,TM+0.04,TM-0.04,z0,z1)
        box(bm,e-0.05,e+0.05,TM-0.05,TBACK,z0,z1)   # partition walls (white) - frame material OK
    for k in range(NR):
        for j in (1,2): 
            e=edges[k]+(edges[k+1]-edges[k])*j/3; box(bm,e-0.025,e+0.025,TM+0.03,TM-0.03,z0,z1)
newobj('CCOM newsroom back offices frames (mw, maroon)',bm,[M_FR])
bm=bmesh.new()
for z0,z1 in ((ZF,140.55),(ZM1,144.9)):
    vs=[bm.verts.new(P(u,TM,z)) for u,z in ((UA,z0),(UB,z0),(UB,z1),(UA,z1))]; bm.faces.new(vs)
newobj('CCOM newsroom back offices glass fronts (mw)',bm,[M_GL])
bm=bmesh.new(); box(bm,UA,UB,TM-0.06,TM-0.1,144.9,ZC)
newobj('CCOM newsroom upper white band (mw)',bm,[M_IW])
# TVs on the fascia band (ref newsroom_21)
bm=bmesh.new()
for k in range(7):
    u=UA+1.4+k*(UB-UA-2.8)/6; box(bm,u-0.62,u+0.62,TM+0.06,TM+0.01,140.72,141.42)
newobj('CCOM newsroom fascia TV row (mw)',bm,[M_MON])
# CCM office (far-left upper room = highest u) carpet + 3 desks
bm=bmesh.new(); e0,e1=edges[-2],edges[-1]
box(bm,e0+0.05,e1-0.05,TM-0.1,TBACK,ZM1,ZM1+0.01)
for t in (-11.2,-12.8):
    box(bm,e0+0.4,e1-0.4,t+0.35,t-0.35,ZM1+0.72,ZM1+0.75)
newobj('CCOM CCM office (upper far-left room) carpet + desks (mw)',bm,[M_CARP,M_DESK])
o=bpy.data.objects['CCOM CCM office (upper far-left room) carpet + desks (mw)']; o['note']="Center for Cooperative Media office per Joe; layout UNVERIFIED"
for i,p in enumerate(o.data.polygons): p.material_index=0 if i<6 else 1
# anchor desk + set at far RIGHT (low u)
bm=bmesh.new()
box(bm,UA,UA+4.6,-3.5,-9.0,ZF,ZF+0.25)  # riser
newobj('CCOM newsroom set riser (mw)',bm,[M_FLOOR])
bm=bmesh.new(); box(bm,UA+0.01,UA+0.06,-3.0,-9.4,ZF+0.25,ZF+3.6)
newobj('CCOM newsroom set backdrop video wall (mw)',bm,[M_SET])
bm=bmesh.new()
box(bm,UA+2.0,UA+2.7,-4.8,-7.6,ZF+0.25,ZF+1.05); box(bm,UA+1.9,UA+2.8,-4.7,-7.7,ZF+1.05,ZF+1.1)
newobj('CCOM newsroom anchor desk (mw)',bm,[M_ANCH])
# U of white desks + partitions around central conference table
UC=(UA+4.6+UB)/2+0.5; TCn=-5.2
bm=bmesh.new()
box(bm,UC-2.0,UC+2.0,TCn+0.7,TCn-0.7,ZF+0.72,ZF+0.76)
for du in (-1.8,1.8):
    for dt in (0.55,-0.55): box(bm,UC+du-0.04,UC+du+0.04,TCn+dt-0.04,TCn+dt+0.04,ZF,ZF+0.72)
newobj('CCOM newsroom central conference table (mw)',bm,[M_DESK])
uL,uR=UC-5.0,UC+5.0; tFr,tBk=-1.8,-8.6
bm=bmesh.new(); pm=bmesh.new()
box(bm,uL,uR,tBk+0.8,tBk,ZF+0.72,ZF+0.75); box(pm,uL,uR,tBk+0.05,tBk-0.05,ZF,ZF+1.25)
for uu,s in ((uL,1),(uR,-1)):
    a,b=(uu,uu+0.8) if s>0 else (uu-0.8,uu)
    box(bm,a,b,tFr,tBk+0.8,ZF+0.72,ZF+0.75)
    pa,pb=(uu-0.05,uu+0.05)
    box(pm,pa,pb,tFr,tBk,ZF,ZF+1.25)
for k in range(0,10):  # desk legs/pedestals along runs
    u=uL+0.5+k*(uR-uL-1)/9; box(bm,u-0.2,u+0.2,tBk+0.7,tBk+0.1,ZF,ZF+0.72)
for s in (uL+0.4,uR-0.4):
    for k in range(5):
        t=tFr-0.4-k*(tFr-tBk-1.4)/4; box(bm,s-0.2,s+0.2,t+0.2,t-0.2,ZF,ZF+0.72)
newobj('CCOM newsroom U desks (white, mw)',bm,[M_DESK])
newobj('CCOM newsroom U cubicle partitions (mw)',pm,[M_PART])
bm=bmesh.new()
for k in range(9):
    u=uL+0.8+k*(uR-uL-1.6)/8; box(bm,u-0.27,u+0.27,tBk+0.25,tBk+0.22,ZF+0.80,ZF+1.15)
for s in (uL+0.25,uR-0.25):
    for k in range(4):
        t=tFr-0.6-k*(tFr-tBk-1.8)/3; box(bm,s-0.015,s+0.015,t+0.27,t-0.27,ZF+0.80,ZF+1.15)
newobj('CCOM newsroom desk monitors (mw)',bm,[M_MON])
o=bpy.data.objects.get('CCOM_int_newsroom_G_20261014v')
if o: o['mw_note']="superseded newsroom-location guess (Oct 14); the NJ PBS newsroom is the double-height west-bay studio (mw, Joe Oct 29). Not visible through the mw glazing (behind the studio back wall)."
bpy.context.scene['mw_hidden']=hidden
print("NEWOBJ",len(col.objects))
out=bpy.data.filepath if MODE=='SAVE' else os.path.abspath('data/mw/test.blend')
bpy.ops.wm.save_as_mainfile(filepath=out,copy=(MODE!='SAVE'))
print("SAVED",out,len(bpy.data.objects))
