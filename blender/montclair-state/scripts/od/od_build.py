# od (Oct 31 2026 ~5:25 AM ET, MAIN, CCOM 1F open floor EAST END, follow-up to oc after Joe's photo refs/joe/ccom_interior_east_1f_joe_20261020_01):
# the photo shows the grey side chairs with a WRAPPED, TAPERED shell back (wider at the top, sides curving forward, mid-grey) over a
# lighter warm-grey seat cushion on splayed wooden legs, and slim chrome floor-standing power poles (disc base, small module on top)
# at the table ends. The 24 oc box chair shells are HIDDEN (not deleted; oc legs kept) and replaced by shaped backs + seat cushions;
# 4 power poles added. Rug edges checked vs the photo: plain cut edge, no visible binding -> nothing added.
# Types from the photo; exact shape/positions approximated -> UNVERIFIED. SAVE=1 saves, REVERT=1 removes all and unhides.
import bpy, os, json, sys, math, mathutils, bmesh, random
SAVE=os.environ.get('SAVE')=='1'; REVERT=os.environ.get('REVERT')=='1'
sys.path.insert(0,os.path.abspath('scripts/oa')); import importlib, oa_geo; importlib.reload(oa_geo); G=oa_geo; V=mathutils.Vector
CN='OD_CCOM_1F_east_shaped_chairs_power_poles_20261031od'; sc=bpy.context.scene; assert len(CN)<=63
def revert():
    st=json.loads(sc.get('od_state','{}'))
    for n in st.get('hidden',[]):
        o=bpy.data.objects.get(n)
        if o: o.hide_render=False; o.hide_viewport=False
    c=bpy.data.collections.get(CN)
    if c:
        for o in list(c.objects):
            d=o.data; bpy.data.objects.remove(o)
            if d and d.users==0:
                if d.name in bpy.data.cameras: bpy.data.cameras.remove(d)
                elif d.name in bpy.data.meshes: bpy.data.meshes.remove(d)
        bpy.data.collections.remove(c)
    for mm in list(bpy.data.materials):
        if mm.name.startswith('OD_') and mm.users==0: bpy.data.materials.remove(mm)
    if 'od_state' in sc: del sc['od_state']
    bpy.context.view_layer.update()
if REVERT:
    revert(); bpy.ops.wm.save_mainfile(); raise SystemExit
revert()
col=bpy.data.collections.new(CN); sc.collection.children.link(col)
def tag(o,layer):
    o['msu_building']='School of Communication and Media'; o['msu_area']='ccom'; o['msu_layer']=layer
    o['msu_merge_role']='live'; o['msu_target_collection']='MSU_CCOM'; o['msu_tag_session']='od'; o['msu_verified']='UNVERIFIED (photo-based type, approx. shape/layout)'
def link(nm,me,mat,mw=None,loc=(0,0,0),rot=0.0,layer='furniture'):
    nmo='OD 1F %s (UNVERIFIED)'%nm; assert len(nmo)<=63,nmo
    o=bpy.data.objects.new(nmo,me); col.objects.link(o); tag(o,layer)
    if mw is not None: o.matrix_world=mw
    else: o.location=loc; o.rotation_euler=(0,0,rot)
    for mm in (mat if isinstance(mat,(list,tuple)) else [mat]): me.materials.append(mm)
    return o
F=137.70
BACKF=G.fabric('OD_chair_back_fabric_mid_grey_UNVERIFIED',(0.30,0.31,0.33))
SEATF=G.fabric('OD_chair_seat_fabric_warm_grey_UNVERIFIED',(0.44,0.43,0.39))
CHROME=bpy.data.materials['OC_table_base_polished_chrome_UNVERIFIED']
MOD=G.pm('OD_power_pole_module_black_UNVERIFIED',(0.02,0.02,0.022),0.45)
FACE=G.pm('OD_power_outlet_face_white_UNVERIFIED',(0.75,0.75,0.72),0.4)
# 1) shaped chairs replacing the oc box shells (legs kept)
hidden=[]
shells=[o for o in bpy.data.objects if o.name.startswith('OC 1F table ') and ' chair ' in o.name and ' legs' not in o.name]
def back_mesh():
    bm=bmesh.new(); NU,NV=15,9; rows=[]
    for j in range(NV):
        v=j/(NV-1); hw=0.15+0.10*v**0.8; R=0.25-0.06*v; yb=-0.19-0.075*v; row=[]
        for i in range(NU):
            u=-1+2*i/(NU-1); a=u*hw/R
            z=0.47+0.40*v-0.035*u*u*v   # top edge dips at the sides
            row.append(bm.verts.new((R*math.sin(a), yb+R*(1-math.cos(a)), z)))
        rows.append(row)
    for j in range(NV-1):
        for i in range(NU-1): bm.faces.new((rows[j][i],rows[j][i+1],rows[j+1][i+1],rows[j+1][i]))
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    me=G.mesh('OD chair shaped back',bm,True); return me
def seat_mesh():
    bm=bmesh.new(); G.box(bm,-0.225,0.225,-0.20,0.235,0.405,0.47); return G.mesh('OD chair seat cushion',bm,True)
for s in shells:
    if not s.hide_render:
        s.hide_render=True; s.hide_viewport=True; hidden.append(s.name)
    short=s.name.replace('OC 1F ','').replace(' (UNVERIFIED)','')
    b=link(short+' back',back_mesh(),BACKF,mw=s.matrix_world.copy())
    m=b.modifiers.new('OD shell','SOLIDIFY'); m.thickness=0.028; m.offset=-1.0
    m=b.modifiers.new('OD smooth','SUBSURF'); m.levels=1; m.render_levels=2
    c=link(short+' seat',seat_mesh(),SEATF,mw=s.matrix_world.copy())
    m=c.modifiers.new('OD bevel','BEVEL'); m.width=0.022; m.segments=3; m.limit_method='ANGLE'; m.harden_normals=True
# 2) floor-standing power poles at table ends (photo 01 foreground + right)
def pole(nm,x,y):
    z0=F+0.008
    bm=bmesh.new(); G.cyl(bm,(0,0),0.15,0.0,0.012,40); G.cyl(bm,(0,0),0.02,0.012,0.86,20)
    o=link(nm+' base+tube',G.mesh('OD power pole tube',bm,True),CHROME,loc=(x,y,z0)); bv=o.modifiers.new('OD bevel','BEVEL'); bv.width=0.004; bv.segments=2; bv.limit_method='ANGLE'
    bm=bmesh.new(); G.box(bm,-0.045,0.045,-0.045,0.045,0.86,1.06); G.cyl(bm,(0,0),0.04,1.06,1.07,24)
    o=link(nm+' module',G.mesh('OD power pole module',bm),MOD,loc=(x,y,z0)); bv=o.modifiers.new('OD bevel','BEVEL'); bv.width=0.006; bv.segments=2
    bm=bmesh.new()
    for sy in (-1,1):   # duplex outlet + USB faces on two opposite sides
        yy=sy*0.0455; G.box(bm,-0.022,0.022,yy-0.002,yy+0.002,0.955,1.035)   # duplex plate (review fix: smaller, read as a sign)
        G.box(bm,-0.012,0.012,yy-0.002,yy+0.002,0.905,0.925)                     # USB plate
    link(nm+' outlet faces',G.mesh('OD power pole faces',bm),FACE,loc=(x,y,z0))
for i,(x,y) in enumerate(((1.55,10.5),(6.65,10.5),(10.98,8.9),(8.92,11.1))):
    pole('power pole %d'%i,x,y)
# 3) atrium stair S glass guard + handrails after refs/ccom_google/ccom_epic_interior_28 (glass panels between round stainless posts,
#    round top rail, inner handrail on brackets; wall-side round handrail) + aluminium tread nosings. The NG slab rails are HIDDEN.
for n in ('NG stair S glass rail','NG stair S handrail','NG stair N wall handrail'):
    o=bpy.data.objects.get(n)
    if o and not o.hide_render: o.hide_render=True; o.hide_viewport=True; hidden.append(n)
SS=G.pm('OD_stair_rail_satin_stainless_UNVERIFIED',(0.78,0.78,0.79),0.22,metal=1.0)
NOS=G.pm('OD_stair_nosing_aluminium_UNVERIFIED',(0.55,0.56,0.57),0.38,metal=0.8)
GL=bpy.data.materials['NH_stair_rail_glass_low_reflection_UNVERIFIED']
R0=0.15958; zn=lambda x: 137.7+R0+(x+15.0)/0.3*R0   # nosing line (25 risers 0.1596, 0.30 goings, from the NG stair mesh)
def tube(bm,p0,p1,r,seg=16):
    p0=V(p0); p1=V(p1); d=p1-p0; q=bmesh.ops.create_cone(bm,cap_ends=True,segments=seg,radius1=r,radius2=r,depth=d.length)
    M=mathutils.Matrix.Translation((p0+p1)/2)@d.to_track_quat('Z','Y').to_matrix().to_4x4()
    bmesh.ops.transform(bm,matrix=M,verts=q['verts'])
PX=[-15.0+1.25*i for i in range(7)]; YG=13.52
bm=bmesh.new()
for x in PX: tube(bm,(x,YG,zn(x)-0.16),(x,YG,zn(x)+1.045),0.021,16)
link('atrium stair S guard posts',G.mesh('OD stair guard posts',bm,True),SS,layer='stair')
bm=bmesh.new()
for a,b in zip(PX[:-1],PX[1:]):
    a+=0.035; b-=0.035; v=[bm.verts.new((x,YG+dy,zn(x)+dz)) for (x,dz) in ((a,-0.12),(b,-0.12),(b,0.99),(a,0.99)) for dy in (-0.006,0.006)]
    for f in ((0,2,4,6),(1,7,5,3),(0,1,3,2),(2,3,5,4),(4,5,7,6),(6,7,1,0)): bm.faces.new([v[i] for i in f])
link('atrium stair S glass guard panels',G.mesh('OD stair glass panels',bm),GL,layer='stair')
bm=bmesh.new(); tube(bm,(-15.0,YG,zn(-15.0)+1.07),(-7.5,YG,zn(-7.5)+1.07),0.025,24)
tube(bm,(-15.0,YG,zn(-15.0)+1.07),(-15.0,YG,zn(-15.0)+1.0),0.025,24)   # down-turned start
link('atrium stair S guard top rail',G.mesh('OD stair top rail',bm,True),SS,layer='stair')
bm=bmesh.new(); YH=13.60; tube(bm,(-15.3,YH,zn(-15.0)+0.88),(-15.0,YH,zn(-15.0)+0.88),0.02,20); tube(bm,(-15.0,YH,zn(-15.0)+0.88),(-7.5,YH,zn(-7.5)+0.88),0.02,20)
for x in PX[:-1]+[-7.62]: tube(bm,(x,YG+0.02,zn(x)+0.86),(x,YH,zn(x)+0.86),0.008,10)   # brackets off the posts
link('atrium stair S inner handrail',G.mesh('OD stair inner handrail',bm,True),SS,layer='stair')
bm=bmesh.new(); YW=16.43; tube(bm,(-15.3,YW,zn(-15.0)+0.88),(-15.0,YW,zn(-15.0)+0.88),0.02,20); tube(bm,(-15.0,YW,zn(-15.0)+0.88),(-7.5,YW,zn(-7.5)+0.88),0.02,20)
for x in PX: tube(bm,(x,YW,zn(x)+0.86),(x,16.5,zn(x)+0.86),0.008,10); tube(bm,(x,16.488,zn(x)+0.86),(x,16.5,zn(x)+0.86),0.032,16)   # wall rosette
link('atrium stair N wall handrail round',G.mesh('OD stair wall handrail',bm,True),SS,layer='stair')
bm=bmesh.new()
for i in range(25):
    x=-15.0+0.3*i; zt=137.7+R0*(i+1); G.box(bm,x,x+0.045,13.56,16.44,zt,zt+0.003)
link('atrium stair aluminium tread nosings',G.mesh('OD stair nosings',bm),NOS,layer='stair')
def cam(nm,loc,tgt,lens_):
    assert len(nm)<=63
    c=bpy.data.cameras.new(nm); c.lens=lens_; c.clip_start=0.05; o=bpy.data.objects.new(nm,c); o.location=loc
    o.rotation_euler=(V(tgt)-V(loc)).to_track_quat('-Z','Y').to_euler(); col.objects.link(o); tag(o,'camera')
f=lambda k,d: tuple(float(x) for x in os.environ.get(k,d).split(','))
cam('OD_CAM_aerial_cutaway_atrium_stair_to_east_from_W',f('AELOC','-26.0,6.0,156'),f('AETGT','-4.0,12.0,138.0'),20)
cam('OD_CAM_eye_atrium_stair_guard_looking_NE',f('E1LOC','-18.6,9.2,139.3'),f('E1TGT','-10.0,15.0,140.0'),20)
cam('OD_CAM_eye_1F_east_end_from_NE_looking_SW',f('E2LOC','11.3,12.3,139.2'),f('E2TGT','2.0,8.6,138.5'),18)
cam('OD_CAM_closeup_1F_shaped_chair_backs_power_pole',f('CLLOC','0.7,9.2,138.85'),f('CLTGT','2.6,10.5,138.15'),float(os.environ.get('CLLENS','28')))
sc['od_state']=json.dumps({'hidden':hidden,'n':len(col.objects)})
print('OD_BUILT',len(col.objects),'hidden',len(hidden),'shells',len(shells))
if SAVE: bpy.ops.wm.save_mainfile(); print('OD_SAVED',len(bpy.data.objects))
