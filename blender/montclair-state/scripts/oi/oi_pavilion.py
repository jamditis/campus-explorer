# oi (Oct 31 2026): Schmitt Hall entrance pavilion per env-team photos schmitt_01/03 (CONRAD J. SCHMITT HALL, 2011).
# The photographed pavilion = the existing 7.3 m projecting bay on the long ESE facade where og/oh put the entrance
# (bay along -3.63..3.66 m, 5 m proud of the wing facade; wing runs both ways = arches both sides in schmitt_03).
# Builds a raised stucco pavilion shell around the bay (sides 0.17 m / front 0.18 m outside the bay walls -> no coplanar faces),
# arched recess with radial-mullion window + 2 pairs of red doors, lettering band, top window grid, deep red overhang + brackets,
# low hip roof, grey block plinths on the piers. Hides (not deletes) og door/glass/vestibule, bay windows; removes bay eave/roof faces
# poking through (original meshes kept with fake users). State -> data/oi/oi_state.json. REVERT=1 restores the oh state.
import bpy, bmesh, json, math, os, sys
from mathutils import Vector, Matrix
REV=os.environ.get('REVERT')=='1'; SAVE='--save' in sys.argv
ROOT=os.path.dirname(bpy.data.filepath); SJ=os.path.join(ROOT,'data/oi/oi_state.json')
CN='OI_Schmitt_entrance_pavilion_20261031oi'
EAVE='Schmitt Hall eave soffit + fascia + rafter tails'; ROOF='Schmitt Hall roof (LiDAR)'
def restore_mesh(objname, key):
    o=bpy.data.objects[objname]; orig=bpy.data.meshes.get(key)
    if orig:
        cur=o.data; nm=cur.name; o.data=orig; bpy.data.meshes.remove(cur); orig.name=nm; orig.use_fake_user=False
# ---- undo (always, idempotent) ----
st=json.load(open(SJ)) if os.path.exists(SJ) else {}
c=bpy.data.collections.get(CN)
if c:
    for ob in list(c.objects):
        me=ob.data; bpy.data.objects.remove(ob)
        if me and me.users==0 and isinstance(me,bpy.types.Mesh): bpy.data.meshes.remove(me)
    bpy.data.collections.remove(c)
for n,v in st.get('hidden',{}).items():
    o=bpy.data.objects.get(n)
    if o: o.hide_render=v[0]; o.hide_viewport=v[1]
for n,v in st.get('moved',{}).items():
    o=bpy.data.objects.get(n)
    if o: o.matrix_world=Matrix(v)
restore_mesh(EAVE,'OI_eave_orig_pre_oi'); restore_mesh(ROOF,'OI_roof_orig_pre_oi')
for on,key in st.get('trimmed',{}).items():
    if bpy.data.objects.get(on): restore_mesh(on,key)
if bpy.data.objects.get('OH_Schmitt_downspouts_UNVERIFIED'): restore_mesh('OH_Schmitt_downspouts_UNVERIFIED','OI_downspouts_orig_pre_oi')
for n in [m.name for m in bpy.data.materials if m.name.startswith('OI_Schmitt_')]: bpy.data.materials.remove(bpy.data.materials[n])
for t in [t for t in bpy.data.curves if t.name.startswith('OI_')]: bpy.data.curves.remove(t)
if os.path.exists(SJ): os.remove(SJ)
if REV:
    print('REVERTED')
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit(0)
# ---- frame of reference from the oh entrance ----
fr=bpy.data.objects['OG_Schmitt_E_entrance_storefront_frame']; la=bpy.data.objects['OG_Schmitt_E_entrance_landing']
fv=[fr.matrix_world@v.co for v in fr.data.vertices]; lb=[la.matrix_world@v.co for v in la.data.vertices]
cen=sum(fv,Vector())/len(fv); lc=sum(lb,Vector())/len(lb)
OUT=Vector(((lc-cen).x,(lc-cen).y,0)).normalized(); AL=Vector((-OUT.y,OUT.x,0)); cen.z=0
def P(a,o,z): return cen+AL*a+OUT*o+Vector((0,0,z))
def loc(v): d=v-cen; return d.dot(AL), d.dot(OUT)
Z0=138.30; ZD=138.79; ZTOP=150.55
HA=3.80; OF=0.67; OB=-5.30          # pavilion half-width, front, back (bay: +-3.63/3.66, front 0.12, wing facade -4.9)
st={'hidden':{},'moved':{},'trimmed':{},'note':'oi pavilion'}
# materials
def mat(n,col,rough=0.6,metal=0.0,emc=None,ems=0.0,trans=0.0):
    m=bpy.data.materials.new(n); m.use_nodes=True; p=m.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value=(*col,1); p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal
    if emc: p.inputs['Emission Color'].default_value=(*emc,1); p.inputs['Emission Strength'].default_value=ems
    if trans: p.inputs['Transmission Weight'].default_value=trans; p.inputs['IOR'].default_value=1.5
    return m
M_st=mat('OI_Schmitt_pavilion_stucco_grey',(0.50,0.50,0.47),0.85)
nt=M_st.node_tree; tx=nt.nodes.new('ShaderNodeTexNoise'); tx.inputs['Scale'].default_value=60; bp=nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value=0.08
nt.links.new(tx.outputs['Fac'],bp.inputs['Height']); nt.links.new(bp.outputs['Normal'],nt.nodes['Principled BSDF'].inputs['Normal'])
M_red=bpy.data.materials['OH_Schmitt_win_frame_red_brown']
M_soff=mat('OI_Schmitt_overhang_red_UNVERIFIED',(0.24,0.035,0.03),0.55)
M_tile=mat('OI_Schmitt_pavilion_roof_tile_UNVERIFIED',(0.45,0.12,0.05),0.8)
M_txt=mat('OI_Schmitt_lettering_dark_bronze',(0.025,0.025,0.03),0.35,0.6)
M_back=mat('OI_Schmitt_pavilion_interior_warm_UNVERIFIED',(0.16,0.12,0.09),0.7,emc=(1.0,0.70,0.42),ems=0.45)
M_glass=bpy.data.materials['OH_Schmitt_door_glass_clear_UNVERIFIED']
_n=M_back.node_tree.nodes; _l=M_back.node_tree.links; _g=_n.new('ShaderNodeNewGeometry'); _sx=_n.new('ShaderNodeSeparateXYZ'); _l.new(_g.outputs['Position'],_sx.inputs[0])
_mr=_n.new('ShaderNodeMapRange'); _mr.inputs['From Min'].default_value=139.0; _mr.inputs['From Max'].default_value=146.5; _mr.inputs['To Min'].default_value=0.28; _mr.inputs['To Max'].default_value=0.03
_l.new(_sx.outputs['Z'],_mr.inputs['Value']); _l.new(_mr.outputs['Result'],_n['Principled BSDF'].inputs['Emission Strength'])
_n['Principled BSDF'].inputs['Base Color'].default_value=(0.06,0.05,0.045,1)
blk=bpy.data.materials['OH_Schmitt_stucco_block_base_UNVERIFIED'].copy(); blk.name='OI_Schmitt_pier_block_plinth_UNVERIFIED'
for n in blk.node_tree.nodes:
    if n.type=='MATH' and n.operation=='LESS_THAN': n.inputs[1].default_value=139.95
    if n.type=='MATH' and n.operation=='COMPARE': n.inputs[1].default_value=140.01
col=bpy.data.collections.new(CN); bpy.context.scene.collection.children.link(col)
def newobj(name,bm,m):
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(m)
    for p in me.polygons: p.use_smooth=False
    o=bpy.data.objects.new(name,me); col.objects.link(o); o['UNVERIFIED']='oi: from photos schmitt_01/03; sizes estimated'; return o
def box(bm,a0,a1,o0,o1,z0,z1,taper=None):
    vs=[]
    for z in (z0,z1):
        for a,o in ((a0,o0),(a1,o0),(a1,o1),(a0,o1)):
            if taper and z==z0: o=o0+(o-o0)*taper
            vs.append(bm.verts.new(P(a,o,z)))
    for f in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)): bm.faces.new([vs[i] for i in f])
def bar(bm,p0,p1,w,o0,o1):
    # bar in facade plane from (a,z) p0 to p1, width w, depth o0..o1
    a0,z0=p0; a1,z1=p1; d=Vector((a1-a0,z1-z0)); L=d.length; d/=L; n=Vector((-d.y,d.x))*w/2
    q=[(a0+n.x-d.x*w/2,z0+n.y-d.y*w/2),(a1+n.x+d.x*w/2,z1+n.y+d.y*w/2),(a1-n.x+d.x*w/2,z1-n.y+d.y*w/2),(a0-n.x-d.x*w/2,z0-n.y-d.y*w/2)]
    vs=[bm.verts.new(P(a,o,z)) for o in (o0,o1) for a,z in q]
    for f in ((0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)): bm.faces.new([vs[i] for i in f])
# ---- pavilion shell with arch + top-window recesses ----
AW=2.30; ZS=144.30; ZC=ZS+AW         # arch half-width, spring, crown 146.60
RD=0.40                               # recess depth
bm=bmesh.new(); box(bm,-HA,HA,OB,OF,Z0,ZTOP); shell=newobj('OI_Schmitt_pavilion_shell_stucco',bm,M_st)
cb=bmesh.new()
N=24; prof=[(-AW,ZD-0.05),(AW,ZD-0.05)]+[(AW*math.cos(math.pi*i/N),ZS+AW*math.sin(math.pi*i/N)) for i in range(N+1)]
vs0=[cb.verts.new(P(a,OF-RD,z)) for a,z in prof]; vs1=[cb.verts.new(P(a,OF+0.5,z)) for a,z in prof]
cb.faces.new(vs0); cb.faces.new(vs1[::-1])
for i in range(len(prof)):
    j=(i+1)%len(prof); cb.faces.new([vs0[i],vs0[j],vs1[j],vs1[i]])
TW=2.60; TZ0=148.05; TZ1=150.00
box(cb,-TW,TW,OF-0.22,OF+0.5,TZ0,TZ1)
bmesh.ops.recalc_face_normals(cb,faces=cb.faces)
cme=bpy.data.meshes.new('OI_cut_tmp'); cb.to_mesh(cme); cb.free(); cut=bpy.data.objects.new('OI_cut_tmp',cme); col.objects.link(cut)
md=shell.modifiers.new('cut','BOOLEAN'); md.operation='DIFFERENCE'; md.solver='EXACT'; md.object=cut
dg=bpy.context.evaluated_depsgraph_get(); nm=bpy.data.meshes.new_from_object(shell.evaluated_get(dg)); shell.modifiers.remove(md)
old=shell.data; shell.data=nm; bpy.data.meshes.remove(old); nm.name='OI_Schmitt_pavilion_shell_stucco'
bpy.data.objects.remove(cut); bpy.data.meshes.remove(cme)
_b=bmesh.new(); _b.from_mesh(shell.data); print('shell faces',len(shell.data.polygons),'nonmanifold edges',sum(1 for e in _b.edges if not e.is_manifold)); _b.free()
# ---- arch window + doors ----
FO0=OF-RD+0.10; FO1=FO0+0.14; GO=FO0+0.06    # frame depth band, glass plane
bm=bmesh.new(); W=0.10
# outer arch ring + jambs
for i in range(N):
    t0=math.pi*i/N; t1=math.pi*(i+1)/N; r=AW-W/2
    bar(bm,(r*math.cos(t0),ZS+r*math.sin(t0)),(r*math.cos(t1),ZS+r*math.sin(t1)),W,FO0,FO1)
for s in (-1,1): bar(bm,(s*(AW-W/2),ZD),(s*(AW-W/2),ZS),W,FO0,FO1)
# inner arch ring r=1.15
RI=1.15; M2=12
for i in range(M2):
    t0=math.pi*i/M2; t1=math.pi*(i+1)/M2
    bar(bm,(RI*math.cos(t0),ZS+RI*math.sin(t0)),(RI*math.cos(t1),ZS+RI*math.sin(t1)),0.08,FO0,FO1)
# radial spokes (diamond-like as in schmitt_03): inner ring 30/150 deg -> outer 60/120 deg, inner 90 -> outer 90
for ti,to in ((30,60),(150,120),(60,30),(120,150)):
    a=math.radians(ti); b=math.radians(to); ro=AW-W
    bar(bm,(RI*math.cos(a),ZS+RI*math.sin(a)),(ro*math.cos(b),ZS+ro*math.sin(b)),0.07,FO0,FO1)
bar(bm,(0,ZS),(0,ZS+RI),0.07,FO0,FO1)
# transoms + mullions below spring
for z in (141.45,142.45,143.40,ZS): bar(bm,(-AW+W,z),(AW-W,z),0.09,FO0,FO1)
for a in (-1.15,0.0,1.15): bar(bm,(a,141.45),(a,ZS),0.08,FO0,FO1)
# doors: 2 pairs (4 leaves) under the transom, centre post
DT=141.45
for a in (-AW+W,-1.15,0.0,1.15,AW-W):
    bar(bm,(a,ZD),(a,DT),0.14 if a==0.0 else 0.10,FO0,FO1+0.02)
for a0,a1 in ((-AW+W,-1.15),(-1.15,0.0),(0.0,1.15),(1.15,AW-W)):
    m=(a0+a1)/2
    bar(bm,(a0+0.05,ZD+0.12),(a1-0.05,ZD+0.12),0.24,FO0,FO1+0.02)   # kick rail
    bar(bm,(m-0.02,ZD+0.06),(m-0.02,DT-0.05),0.13,FO0,FO1+0.02)       # meeting stiles
    bar(bm,(a0+0.05,DT-0.06),(a1-0.05,DT-0.06),0.12,FO0,FO1+0.02)    # top rail
frames=newobj('OI_Schmitt_pavilion_arch_window_doors_frame',bm,M_red)
# pulls (vertical bars proud)
bm=bmesh.new()
for a in (-1.15,1.15):
    for s in (-0.10,0.10): bar(bm,(a/2+s*0+ (0.0),0),(0,0),0.01,0,0.001) if False else None
for m in (-1.725,-0.575,0.575,1.725):
    for s in (-0.07,0.07): bar(bm,(m+s,ZD+0.95),(m+s,ZD+1.85),0.03,FO1+0.03,FO1+0.08)
newobj('OI_Schmitt_pavilion_door_pulls',bm,bpy.data.materials.get('Steel_brushed') or M_txt)
# glass + interior backing in the arch
bm=bmesh.new()
gp=[(-AW+0.02,ZD+0.01),(AW-0.02,ZD+0.01)]+[((AW-0.02)*math.cos(math.pi*i/N),ZS+(AW-0.02)*math.sin(math.pi*i/N)) for i in range(N+1)]
for oo,(mm) in ((GO,'g'),):
    v0=[bm.verts.new(P(a,oo-0.006,z)) for a,z in gp]; v1=[bm.verts.new(P(a,oo+0.006,z)) for a,z in gp]
    bm.faces.new(v0); bm.faces.new(v1[::-1])
    for i in range(len(gp)): j=(i+1)%len(gp); bm.faces.new([v0[i],v0[j],v1[j],v1[i]])
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
newobj('OI_Schmitt_pavilion_arch_glass',bm,M_glass)
bm=bmesh.new()
bp_=[(a*0.995,max(z,ZD+0.005)) for a,z in gp]
v0=[bm.verts.new(P(a,OF-RD+0.02,z)) for a,z in bp_]; v1=[bm.verts.new(P(a,OF-RD+0.035,z)) for a,z in bp_]
bm.faces.new(v0); bm.faces.new(v1[::-1])
for i in range(len(bp_)): j=(i+1)%len(bp_); bm.faces.new([v0[i],v0[j],v1[j],v1[i]])
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
newobj('OI_Schmitt_pavilion_vestibule_warm_backing',bm,M_back)
# ---- top window grid (8 cols x 3 rows, top row short) ----
bm=bmesh.new(); TO0=OF-0.22+0.04; TO1=TO0+0.10
box(bm,-TW,TW,TO0,TO1,TZ0,TZ0+0.09); box(bm,-TW,TW,TO0,TO1,TZ1-0.09,TZ1)
for z in (149.45,148.95): bar(bm,(-TW,z),(TW,z),0.07,TO0,TO1)
for k in range(9):
    a=-TW+0.045+k*(2*TW-0.09)/8; bar(bm,(a,TZ0),(a,TZ1),0.09 if k in (0,4,8) else 0.06,TO0,TO1)
newobj('OI_Schmitt_pavilion_top_window_grid_frame',bm,M_red)
bm=bmesh.new(); box(bm,-TW+0.01,TW-0.01,TO0+0.03,TO0+0.042,TZ0+0.01,TZ1-0.01); newobj('OI_Schmitt_pavilion_top_window_glass',bm,M_glass)
bm=bmesh.new(); box(bm,-TW+0.01,TW-0.01,OF-0.22+0.005,OF-0.22+0.018,TZ0+0.01,TZ1-0.01); newobj('OI_Schmitt_pavilion_top_window_interior',bm,M_back)
# ---- lettering band + text ----
BZ0=146.95; BZ1=147.80
bm=bmesh.new(); box(bm,-HA-0.05,HA+0.05,OF-0.05,OF+0.07,BZ0,BZ1); newobj('OI_Schmitt_pavilion_lettering_band',bm,M_st)
cu=bpy.data.curves.new('OI_lettering_curve','FONT'); cu.body='CONRAD J. SCHMITT HALL'; cu.size=0.58; cu.extrude=0.012; cu.align_x='CENTER'; cu.align_y='CENTER'
fo=bpy.data.fonts.get('Bfont Regular') or bpy.data.fonts[0] if bpy.data.fonts else None
try:
    for p_ in ('/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf','/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf'):
        if os.path.exists(p_): cu.font=bpy.data.fonts.load(p_,check_existing=True); break
except Exception as e: print('font',e)
to=bpy.data.objects.new('OI_txt_tmp',cu); col.objects.link(to)
X=AL; Y=Vector((0,0,1)); Zv=OUT; c0=P(0,OF+0.07+0.012,(BZ0+BZ1)/2)
to.matrix_world=Matrix(((X.x,Y.x,Zv.x,c0.x),(X.y,Y.y,Zv.y,c0.y),(X.z,Y.z,Zv.z,c0.z),(0,0,0,1)))
dg=bpy.context.evaluated_depsgraph_get(); tm=bpy.data.meshes.new_from_object(to.evaluated_get(dg)); tm.name='OI_Schmitt_lettering_CONRAD_J_SCHMITT_HALL'
mw=to.matrix_world.copy(); bpy.data.objects.remove(to); bpy.data.curves.remove(cu)
tm.materials.clear(); tm.materials.append(M_txt)
txo=bpy.data.objects.new('OI_Schmitt_lettering_CONRAD_J_SCHMITT_HALL',tm); txo.matrix_world=mw; col.objects.link(txo)
xs=[(mw@v.co).dot(AL)-cen.dot(AL) for v in tm.vertices]; print('lettering width',round(max(xs)-min(xs),2),'verts',len(tm.vertices))
# ---- overhang + brackets + hip roof ----
OV=1.0; SZ0=ZTOP; SZ1=ZTOP+0.38
bm=bmesh.new(); box(bm,-HA-OV,HA+OV,OB,OF+OV,SZ0,SZ1); newobj('OI_Schmitt_pavilion_overhang_red',bm,M_soff)
bm=bmesh.new()
for a in (-HA+0.55,HA-0.55):
    box(bm,a-0.11,a+0.11,OF-0.02,OF+OV-0.15,SZ0-0.75,SZ0+0.01,taper=0.25)
for s in (-1,1):
    for o in (-0.7,-3.6):
        vs=[]
        for z in (SZ0-0.75,SZ0+0.01):
            a0=s*(HA-0.02); a1=s*(HA+OV-0.15) if z>SZ0 else s*(HA+(OV-0.15)*0.25)
            for a,oo in ((a0,o-0.11),(a1,o-0.11),(a1,o+0.11),(a0,o+0.11)): vs.append(bm.verts.new(P(a,oo,z)))
        for f in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)): bm.faces.new([vs[i] for i in f])
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
newobj('OI_Schmitt_pavilion_eave_brackets',bm,M_soff)
bm=bmesh.new(); h=1.05; ins=0.05
c4=[bm.verts.new(P(a,o,SZ1)) for a,o in ((-HA-OV+ins,OB+ins),(HA+OV-ins,OB+ins),(HA+OV-ins,OF+OV-ins),(-HA-OV+ins,OF+OV-ins))]
hw=HA+OV-ins; r0=bm.verts.new(P(0,OB+ins+hw,SZ1+h)); r1=bm.verts.new(P(0,OF+OV-ins-hw,SZ1+h))
if (OF+OV-ins-hw) < (OB+ins+hw): r0.co=P(0,(OB+OF+OV)/2,SZ1+h); r1.co=r0.co+OUT*0.01
bm.faces.new([c4[3],c4[2],c4[1],c4[0]]); bm.faces.new([c4[0],c4[1],r0]); bm.faces.new([c4[2],c4[3],r1]); bm.faces.new([c4[1],c4[2],r1,r0]); bm.faces.new([c4[3],c4[0],r0,r1])
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
newobj('OI_Schmitt_pavilion_hip_roof_tile',bm,M_tile)
# ---- pier block plinths (wrap front corners) ----
bm=bmesh.new()
for s in (-1,1):
    a0,a1=sorted((s*(AW+0.02),s*(HA+0.08))); box(bm,a0,a1,OF-0.9,OF+0.08,Z0+0.05,139.98)
newobj('OI_Schmitt_pavilion_pier_block_plinth',bm,blk)
# ---- hide what the pavilion encloses ----
def hide(o):
    st['hidden'][o.name]=[o.hide_render,o.hide_viewport]; o.hide_render=True; o.hide_viewport=True
for n in ('OG_Schmitt_E_entrance_storefront_frame','OG_Schmitt_E_entrance_glass','OG_Schmitt_E_entrance_vestibule_dark'): hide(bpy.data.objects[n])
for o in bpy.data.objects:
    if o.name.startswith('SCH_win_'):
        a,oo=loc(o.matrix_world.translation)
        if abs(a)<HA+0.3 and OB-0.3<oo<OF+0.3: hide(o)
# sconces onto the piers beside the arch (schmitt_03)
for n,s in (('OH_Schmitt_sconce_L',-1),('OH_Schmitt_sconce_R',1)):
    o=bpy.data.objects[n]; st['moved'][n]=[list(r) for r in o.matrix_world]
    a,_=loc(o.location); sg=1 if a>0 else -1
    o.location=P(sg*(AW+0.75),OF+0.08,142.05)
# eave/roof faces of the old bay that poke through the pavilion
for on,key in ((EAVE,'OI_eave_orig_pre_oi'),(ROOF,'OI_roof_orig_pre_oi')):
    o=bpy.data.objects[on]; orig=o.data.copy(); orig.name=key; orig.use_fake_user=True
    bm=bmesh.new(); bm.from_mesh(o.data); M=o.matrix_world; dl=[]
    for f in bm.faces:
        a,oo=loc(M@f.calc_center_median())
        if abs(a)<HA+OV-0.15 and oo>-3.95: dl.append(f)
    bmesh.ops.delete(bm,geom=dl,context='FACES'); bm.to_mesh(o.data); bm.free(); o.data.update(); print(on,'faces removed',len(dl))
# other Schmitt roof-edge meshes (e.g. 'Schmitt Hall barrel tile eave course') crossing the pavilion front/recesses
for o in [o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('Schmitt Hall') and o.name not in ('Schmitt Hall walls',EAVE,ROOF)]:
    M=o.matrix_world; hit=[f.index for f in o.data.polygons if (lambda q:abs(q[0])<HA+OV-0.15 and q[1]>-3.95)(loc(M@f.center))]
    if not hit: continue
    key=('OI_pre_oi_'+o.name)[:60]; orig=o.data.copy(); orig.name=key; orig.use_fake_user=True; st['trimmed'][o.name]=key
    bm=bmesh.new(); bm.from_mesh(o.data); bm.faces.ensure_lookup_table(); bmesh.ops.delete(bm,geom=[bm.faces[i] for i in hit],context='FACES'); bm.to_mesh(o.data); bm.free(); o.data.update()
    print('trimmed',o.name,len(hit))
ds=bpy.data.objects.get('OH_Schmitt_downspouts_UNVERIFIED')
if ds:
    orig=ds.data.copy(); orig.name='OI_downspouts_orig_pre_oi'; orig.use_fake_user=True
    bm=bmesh.new(); bm.from_mesh(ds.data)
    dv=[v for v in bm.verts if (lambda q:abs(q[0])<HA+0.4 and OB<q[1]<OF+0.45)(loc(ds.matrix_world@v.co))]
    bmesh.ops.delete(bm,geom=dv,context='VERTS'); bm.to_mesh(ds.data); bm.free(); ds.data.update(); print('downspout verts removed (bay corners, now inside the pavilion)',len(dv))
json.dump(st,open(SJ,'w'),indent=1)
print('hidden',len(st['hidden']),sorted(st['hidden']))
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
