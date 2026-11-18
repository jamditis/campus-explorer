# ob (Oct 31 2026 ~3:30 AM ET, MAIN, CCOM 2F student area polish from oa 'Not fixed'): (1) the oa bar stools read like pendant lamps from
# above (black disc on a pole) -> oak dished seats with a low curved backrest (oa seats hidden, not deleted); (2) the terrazzo on the 1F/2F
# open floors was mirror-glossy (roughness 0.16) -> honed look: noise-varied roughness 0.24-0.36 (material shared by 10 objects; REVERT
# restores); (3) two floor planters with leafy plants in the lounge. OB cameras. ALL UNVERIFIED. SAVE=1 saves, REVERT=1 removes all.
import bpy, os, json, sys, math, mathutils, bmesh, random
SAVE=os.environ.get('SAVE')=='1'; REVERT=os.environ.get('REVERT')=='1'
sys.path.insert(0,os.path.abspath('scripts/oa')); import importlib, oa_geo; importlib.reload(oa_geo); G=oa_geo; V=mathutils.Vector
CN='OB_CCOM_2F_stools_planters_floor_sheen_20261031ob'; sc=bpy.context.scene; assert len(CN)<=63
TZ='NG_terrazzo_1F_open_floor'
def revert():
    st=json.loads(sc.get('ob_state','{}'))
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
    m=bpy.data.materials.get(TZ)
    if m:
        nt=m.node_tree
        for nd in [n for n in nt.nodes if n.name.startswith('OB ')]: nt.nodes.remove(nd)
        b=[n for n in nt.nodes if n.type=='BSDF_PRINCIPLED'][0]; b.inputs['Roughness'].default_value=st.get('rough',0.16)
    for mm in list(bpy.data.materials):
        if mm.name.startswith('OB_') and mm.users==0: bpy.data.materials.remove(mm)
    for k in ('ob_state',):
        if k in sc: del sc[k]
    bpy.context.view_layer.update()
if REVERT:
    revert(); bpy.ops.wm.save_mainfile(); raise SystemExit
revert()
col=bpy.data.collections.new(CN); sc.collection.children.link(col)
def tag(o,layer):
    o['msu_building']='School of Communication and Media'; o['msu_area']='ccom'; o['msu_layer']=layer
    o['msu_merge_role']='live'; o['msu_target_collection']='MSU_CCOM'; o['msu_tag_session']='ob'; o['msu_verified']='UNVERIFIED'
def link(nm,me,mat,loc=(0,0,0),rot=0.0,layer='furniture',bevel=None):
    nmo='OB 2F %s (UNVERIFIED)'%nm; assert len(nmo)<=63,nmo
    o=bpy.data.objects.new(nmo,me); o.location=loc; o.rotation_euler=(0,0,rot); col.objects.link(o); tag(o,layer)
    if isinstance(mat,(list,tuple)):
        for mm in mat: me.materials.append(mm)
    else: me.materials.append(mat)
    if bevel:
        b=o.modifiers.new('OB bevel','BEVEL'); b.width=bevel; b.segments=2; b.limit_method='ANGLE'
    return o
F=141.85
OAK=G.pm('OB_stool_seat_oak_UNVERIFIED',(0.50,0.35,0.21),0.42)
STEEL=bpy.data.materials['OA_brushed_steel_UNVERIFIED']
# terrazzo honed: noise-driven roughness
m=bpy.data.materials[TZ]; nt=m.node_tree; b=[n for n in nt.nodes if n.type=='BSDF_PRINCIPLED'][0]
r0=b.inputs['Roughness'].default_value
tc=nt.nodes.new('ShaderNodeTexCoord'); tc.name='OB texcoord'
nz=nt.nodes.new('ShaderNodeTexNoise'); nz.name='OB rough noise'; nz.inputs['Scale'].default_value=0.9; nz.inputs['Detail'].default_value=6.0
mr=nt.nodes.new('ShaderNodeMapRange'); mr.name='OB rough range'; mr.inputs['From Min'].default_value=0.3; mr.inputs['From Max'].default_value=0.7
mr.inputs['To Min'].default_value=0.24; mr.inputs['To Max'].default_value=0.36
nt.links.new(tc.outputs['Object'],nz.inputs['Vector']); nt.links.new(nz.outputs['Fac'],mr.inputs['Value']); nt.links.new(mr.outputs['Result'],b.inputs['Roughness'])
# stools: hide oa seats, add oak dished seat + low curved back on two posts
hidden=[]
stools=sorted({o.name.split(' seat')[0] for o in bpy.data.objects if o.name.startswith('OA 2F stool') and ' seat ' in o.name})
for sname in stools:
    so=bpy.data.objects[sname+' seat (UNVERIFIED)']; so.hide_render=True; hidden.append(so.name)
    loc=so.location.copy(); rot=so.rotation_euler[2]; h=0.76
    # dished seat: 2 rings lathe
    bm=bmesh.new(); seg=40; prof=[(0.0,h-0.015),(0.10,h-0.012),(0.175,h-0.002),(0.195,h),(0.2,h-0.02),(0.19,h-0.045),(0.0,h-0.045)]
    rings=[[bm.verts.new((r*math.cos(2*math.pi*i/seg),r*math.sin(2*math.pi*i/seg),z)) for i in range(seg)] for r,z in prof]
    for a,c in zip(rings,rings[1:]):
        for i in range(seg): bm.faces.new((a[i],a[(i+1)%seg],c[(i+1)%seg],c[i]))
    bm.faces.new(rings[0][::-1]); bm.faces.new(rings[-1])
    me=bpy.data.meshes.new('OB stool seat'); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth=True
    n=sname.replace('OA 2F ','')
    link(n+' oak seat',me,OAK,loc,rot)
    # back: curved band (arc 110 deg at r 0.19, behind = -Y local... face the counter: counter is +Y of stools, so back sits at -Y)
    bm=bmesh.new(); arc=[math.radians(a) for a in range(-145,-34,5)]; R=0.185; z0,z1=h+0.13,h+0.20; t=0.018
    vs=[]
    for a in arc:
        ca,sa=math.cos(a),math.sin(a)
        vs.append([bm.verts.new(((R+dr)*ca,(R+dr)*sa,z)) for dr,z in ((0,z0),(0,z1),(t,z1),(t,z0))])
    for a,c in zip(vs,vs[1:]):
        for i in range(4): bm.faces.new((a[i],a[(i+1)%4],c[(i+1)%4],c[i]))
    bm.faces.new(vs[0][::-1]); bm.faces.new(vs[-1])
    me=bpy.data.meshes.new('OB stool back'); bm.to_mesh(me); bm.free()
    for p in me.polygons: p.use_smooth=True
    link(n+' oak back',me,OAK,loc,0.0)
    bm=bmesh.new()
    for a in (math.radians(-125),math.radians(-55)):
        G.cyl(bm,((R+0.009)*math.cos(a),(R+0.009)*math.sin(a)),0.009,h-0.03,z0+0.02,12)
    link(n+' back posts',G.mesh('OB stool posts',bm,True),STEEL,loc,0.0)
# planters with leafy plants
POT=G.pm('OB_planter_charcoal_fibreglass_UNVERIFIED',(0.035,0.036,0.04),0.55)
SOIL=G.pm('OB_planter_bark_mulch_UNVERIFIED',(0.07,0.045,0.03),0.95)
STEM=G.pm('OB_plant_stem_UNVERIFIED',(0.10,0.16,0.05),0.6)
def leafmat(n,c):
    mm=bpy.data.materials.get(n)
    if mm: return mm
    mm=G.pm(n,c,0.45); bb=mm.node_tree.nodes['Principled BSDF']
    bb.inputs['Subsurface Weight'].default_value=0.15; bb.inputs['Subsurface Radius'].default_value=(0.2,0.4,0.1)
    tc2=mm.node_tree.nodes.new('ShaderNodeTexCoord'); nz2=mm.node_tree.nodes.new('ShaderNodeTexNoise'); nz2.inputs['Scale'].default_value=40
    mx=mm.node_tree.nodes.new('ShaderNodeMix'); mx.data_type='RGBA'; mx.inputs['A'].default_value=(*c,1); mx.inputs['B'].default_value=(c[0]*0.6,c[1]*0.75,c[2]*0.5,1)
    mm.node_tree.links.new(tc2.outputs['Object'],nz2.inputs['Vector']); mm.node_tree.links.new(nz2.outputs['Fac'],mx.inputs['Factor']); mm.node_tree.links.new(mx.outputs['Result'],bb.inputs['Base Color'])
    return mm
LEAF=leafmat('OB_plant_leaf_green_UNVERIFIED',(0.05,0.17,0.035))
def planter(nm,c,seed):
    rnd=random.Random(seed); x,y=c
    bm=bmesh.new(); q=bmesh.ops.create_cone(bm,cap_ends=True,segments=36,radius1=0.19,radius2=0.24,depth=0.62)
    for v in q['verts']: v.co=V((x+v.co.x,y+v.co.y,F+0.31+v.co.z))
    link(nm+' pot',G.mesh('OB planter pot',bm,True),POT,layer='furniture',bevel=0.006)
    bm=bmesh.new(); G.cyl(bm,(x,y),0.225,F+0.55,F+0.575,36); link(nm+' mulch',G.mesh('OB planter mulch',bm),SOIL)
    bms=bmesh.new(); bml=bmesh.new()
    for k in range(52):
        az=rnd.uniform(0,2*math.pi); L=rnd.uniform(0.6,1.25); tilt=rnd.uniform(0.15,0.75)
        base=V((x+rnd.uniform(-0.05,0.05),y+rnd.uniform(-0.05,0.05),F+0.57))
        d=V((math.cos(az)*math.sin(tilt),math.sin(az)*math.sin(tilt),math.cos(tilt)))
        tip=base+d*L; tip.z-=0.08*L*tilt
        # stem as thin quad prism
        side=V((-math.sin(az),math.cos(az),0))*0.004
        s=[bms.verts.new(base+side),bms.verts.new(base-side),bms.verts.new(tip-side*0.5),bms.verts.new(tip+side*0.5)]
        bms.faces.new(s)
        # 1-2 leaves near the tip: lanceolate blade, drooping
        for j in range(rnd.choice((1,2,2))):
            p0=base+(tip-base)*rnd.uniform(0.55,1.0); a2=az+rnd.uniform(-0.8,0.8); ln=rnd.uniform(0.24,0.40); w=ln*rnd.uniform(0.22,0.3)
            dirv=V((math.cos(a2),math.sin(a2),rnd.uniform(-0.25,0.35))).normalized(); wv=V((-math.sin(a2),math.cos(a2),0))
            mid=p0+dirv*ln*0.45; mid.z+=0.01; end=p0+dirv*ln; end.z-=ln*rnd.uniform(0.1,0.3)
            vv=[bml.verts.new(p0),bml.verts.new(mid+wv*w/2),bml.verts.new(end),bml.verts.new(mid-wv*w/2)]
            vm=bml.verts.new(mid+V((0,0,0.012)))
            bml.faces.new((vv[0],vv[1],vm)); bml.faces.new((vv[1],vv[2],vm)); bml.faces.new((vv[2],vv[3],vm)); bml.faces.new((vv[3],vv[0],vm))
    link(nm+' stems',G.mesh('OB plant stems',bms),STEM); o=link(nm+' leaves',G.mesh('OB plant leaves',bml,True),LEAF)
planter('planter SE',(7.85,7.55),11); planter('planter NE',(5.35,13.5),23)
def cam(nm,loc,tgt,lens_):
    assert len(nm)<=63
    c=bpy.data.cameras.new(nm); c.lens=lens_; c.clip_start=0.05; o=bpy.data.objects.new(nm,c); o.location=loc
    o.rotation_euler=(V(tgt)-V(loc)).to_track_quat('-Z','Y').to_euler(); col.objects.link(o); tag(o,'camera')
f=lambda k,d: tuple(float(x) for x in os.environ.get(k,d).split(','))
cam('OB_CAM_aerial_cutaway_2F_student_area_from_SW',f('AELOC','-0.5,1.5,158'),f('AETGT','3.2,10.6,141.9'),24)
cam('OB_CAM_eye_2F_student_area_looking_east',f('E1LOC','-1.6,12.4,143.45'),f('E1TGT','8.4,8.6,142.7'),18)
cam('OB_CAM_eye_2F_balcony_looking_west',f('E2LOC','8.1,12.9,143.45'),f('E2TGT','-2.0,8.5,142.6'),18)
cam('OB_CAM_closeup_2F_oak_stools_planter_counter',f('CLLOC','2.6,10.9,142.95'),f('CLTGT','5.3,13.4,142.5'),float(os.environ.get('CLLENS','24')))
sc['ob_state']=json.dumps({'hidden':hidden,'rough':r0,'n':len(col.objects)})
print('OB_BUILT',len(col.objects),'hidden',len(hidden))
if SAVE: bpy.ops.wm.save_mainfile(); print('OB_SAVED',len(bpy.data.objects))
