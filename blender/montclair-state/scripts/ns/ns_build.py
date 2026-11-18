# ns (Oct 30 2026 ~6:30 PM ET, MAIN): CCOM front-door entry zone detail (inside the doors; NO vestibule enclosure invented: the doors open straight into the atrium per Joe) — ALL UNVERIFIED:
# (a) brushed-aluminium recessed edge trim around the NJ walk-off mat (E/N/S sides) + ribbed charcoal mat material (slot override, revertable);
# (b) overhead door closers (body + arm + shoe) on the inside top of the 4 front-door leaves, dark bronze;
# (c) atrium ottoman piping (darker top-edge welt) + recessed black plinth shadow gap;
# (d) strobe lens glint: NP_strobe_lens_clear_UNVERIFIED roughness 0.1 -> 0.03 + coat (values stored, revertable);
# (e) NS_CAM_* cameras.
import bpy, bmesh, os, json, mathutils, math
SAVE=os.environ.get('SAVE')=='1'; REVERT=os.environ.get('REVERT')=='1'
CN='NS_CCOM_entry_zone_closers_ottomans_20261030ns'
sc=bpy.context.scene
def _keep_nj():
    if 'NJ_entrance_mat_charcoal_UNVERIFIED' not in bpy.data.materials:
        with bpy.data.libraries.load(os.path.abspath('montclair_state_pre_20261030ns.blend'),link=False) as (src,dst): dst.materials=['NJ_entrance_mat_charcoal_UNVERIFIED']
        print('NS re-appended NJ_entrance_mat_charcoal_UNVERIFIED from backup')
    bpy.data.materials['NJ_entrance_mat_charcoal_UNVERIFIED'].use_fake_user=True
def revert():
    _keep_nj()
    st=json.loads(sc.get('ns_state','{}'))
    for n,mn in st.get('matslot',{}).items():
        o=bpy.data.objects.get(n); m=bpy.data.materials.get(mn)
        if o and m: o.material_slots[0].material=m
    mo_=bpy.data.objects.get('NJ entrance walk-off mat (UNVERIFIED)'); nj_=bpy.data.materials.get('NJ_entrance_mat_charcoal_UNVERIFIED')
    if mo_ and nj_ and mo_.material_slots and (mo_.material_slots[0].material is None or mo_.material_slots[0].material.name.startswith('NS_')):
        mo_.material_slots[0].material=nj_; print('NS revert: mat slot fallback ->',nj_.name, mo_.material_slots[0].link)
    for mn,vals in st.get('matvals',{}).items():
        m=bpy.data.materials.get(mn)
        if m:
            p=m.node_tree.nodes['Principled BSDF']
            for k,v in vals.items(): p.inputs[k].default_value=v
    c=bpy.data.collections.get(CN)
    if c:
        for o in list(c.objects):
            d=o.data; bpy.data.objects.remove(o)
            if d and d.users==0:
                for coll in (bpy.data.meshes,bpy.data.cameras):
                    if d.name in coll and coll[d.name]==d: coll.remove(d); break
        bpy.data.collections.remove(c)
    for me in list(bpy.data.meshes):
        if me.name.startswith('NS_') and me.users==0: bpy.data.meshes.remove(me)
    for m in list(bpy.data.materials):
        if m.name.startswith('NS_') and m.users==0: bpy.data.materials.remove(m)
    for k in ('ns_state','ns_note'):
        if k in sc: del sc[k]
    bpy.context.view_layer.update()
if REVERT:
    revert(); bpy.ops.wm.save_mainfile(); raise SystemExit
revert()
state={'matslot':{},'matvals':{}}
col=bpy.data.collections.new(CN); sc.collection.children.link(col)
def tag(o,layer):
    o['msu_building']='School of Communication and Media'; o['msu_area']='ccom'; o['msu_layer']=layer
    o['msu_merge_role']='live'; o['msu_target_collection']='MSU_CCOM'; o['msu_tag_session']='ns'; o['msu_verified']='UNVERIFIED'
def mat(name,c,rough=0.6,metal=0.0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes=True; p=m.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value=c; p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal
    return m
def bb(o):
    cs=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]
    return mathutils.Vector([min(c[i] for c in cs) for i in range(3)]),mathutils.Vector([max(c[i] for c in cs) for i in range(3)])
def box(name,lo,hi,m,layer,rotz=0.0,pivot=None):
    bm=bmesh.new(); bmesh.ops.create_cube(bm,size=1.0)
    for v in bm.verts: v.co=mathutils.Vector((v.co.x*(hi[0]-lo[0]),v.co.y*(hi[1]-lo[1]),v.co.z*(hi[2]-lo[2])))
    me=bpy.data.meshes.new('NS_'+name[:55]); bm.to_mesh(me); bm.free(); me.materials.append(m)
    o=bpy.data.objects.new(name,me); c=[(lo[i]+hi[i])/2 for i in range(3)]
    o.location=c; o.rotation_euler=(0,0,rotz); col.objects.link(o); tag(o,layer); return o
alu=mat('NS_mat_trim_brushed_aluminium',(0.62,0.62,0.6,1),0.32,1.0)
bronze=mat('NS_closer_dark_bronze',(0.07,0.05,0.04,1),0.35,0.85)
black=mat('NS_plinth_black',(0.015,0.015,0.015,1),0.6)
# (a) mat
mo=bpy.data.objects.get('NJ entrance walk-off mat (UNVERIFIED)')
if mo:
    lo,hi=bb(mo); t=0.035; z0=137.695; z1=hi[2]+0.004
    box('NS walk-off mat edge trim E (alu, UNVERIFIED)',(hi[0],lo[1]-t,z0),(hi[0]+t,hi[1]+t,z1),alu,'floor_trim')
    box('NS walk-off mat edge trim N (alu, UNVERIFIED)',(-19.50,hi[1],z0),(hi[0],hi[1]+t,z1),alu,'floor_trim')
    box('NS walk-off mat edge trim S (alu, UNVERIFIED)',(-20.40,lo[1]-t,z0),(hi[0],lo[1],z1),alu,'floor_trim')
    old=mo.material_slots[0].material if mo.material_slots else None
    rib=bpy.data.materials.new('NS_walkoff_mat_ribbed_UNVERIFIED'); rib.use_nodes=True; nt=rib.node_tree; p=nt.nodes['Principled BSDF']
    p.inputs['Roughness'].default_value=0.92
    tc=nt.nodes.new('ShaderNodeTexCoord'); wv=nt.nodes.new('ShaderNodeTexWave'); wv.wave_type='BANDS'; wv.bands_direction='X'
    wv.inputs['Scale'].default_value=0.0; 
    mp=nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value=(22,22,22)
    nt.links.new(tc.outputs['Object'],mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'],wv.inputs['Vector']); wv.inputs['Scale'].default_value=1.0
    wv.inputs['Distortion'].default_value=0.0; wv.inputs['Detail'].default_value=0.0
    ns=nt.nodes.new('ShaderNodeTexNoise'); ns.inputs['Scale'].default_value=60.0
    nt.links.new(tc.outputs['Object'],ns.inputs['Vector'])
    cr=nt.nodes.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].color=(0.014,0.014,0.016,1); cr.color_ramp.elements[1].color=(0.10,0.097,0.092,1)
    mx=nt.nodes.new('ShaderNodeMath'); mx.operation='MULTIPLY_ADD'; mx.inputs[1].default_value=0.8
    ns2=nt.nodes.new('ShaderNodeMath'); ns2.operation='MULTIPLY'; ns2.inputs[1].default_value=0.2
    nt.links.new(ns.outputs['Fac'],ns2.inputs[0]); nt.links.new(wv.outputs['Fac'],mx.inputs[0]); nt.links.new(ns2.outputs[0],mx.inputs[2])
    nt.links.new(mx.outputs[0],cr.inputs[0]); nt.links.new(cr.outputs['Color'],p.inputs['Base Color'])
    bp=nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value=1.0; bp.inputs['Distance'].default_value=0.004
    nt.links.new(wv.outputs['Fac'],bp.inputs['Height']); nt.links.new(bp.outputs['Normal'],p.inputs['Normal'])
    if old: state['matslot'][mo.name]='NJ_entrance_mat_charcoal_UNVERIFIED' if old.name.startswith('NS_') else old.name; mo.material_slots[0].material=rib
    else: mo.data.materials.append(rib)
# (b) closers: facade line through door stile centres; inside normal
A=mathutils.Vector((-20.695,9.665)); Bp=mathutils.Vector((-19.675,13.945)); d=(Bp-A).normalized(); n=mathutils.Vector((d.y,-d.x))
if n.x<0: n=-n
ang=math.atan2(d.y,d.x)
leaves=[(9.73,10.52,'lo'),(10.65,11.45,'hi'),(12.16,12.96,'lo'),(13.09,13.88,'hi')]  # hinge at the outer stile of each pair
for i,(y0,y1,h) in enumerate(leaves):
    def P(y,off):
        t=(y-A.y)/d.y; q=A+d*t+n*off; return q
    yh=y0+0.12 if h=='lo' else y1-0.12; ym=(y0+y1)/2
    q=P((yh+ym)/2,0.075); L=abs(ym-yh)/abs(d.y)
    o=box(f'NS front door leaf {i} overhead closer body (UNVERIFIED)',(q.x-L/2,q.y-0.028,140.06),(q.x+L/2,q.y+0.028,140.135),bronze,'door_hardware',ang)
    o.location=(q.x,q.y,140.0975)
    # arm from body to the head frame (track)
    q2=P(ym+(0.1 if h=='lo' else -0.1),0.10); L2=0.30
    a=box(f'NS front door leaf {i} closer arm (UNVERIFIED)',(0,0,0),(L2,0.018,0.012),bronze,'door_hardware',ang+(0.5 if h=='lo' else -0.5))
    a.location=(q2.x,q2.y,140.145)
    s=P(ym+(0.22 if h=='lo' else -0.22),0.06)
    sh=box(f'NS front door leaf {i} closer track shoe (UNVERIFIED)',(0,0,0),(0.09,0.03,0.025),bronze,'door_hardware',ang)
    sh.location=(s.x,s.y,140.148)
# (c) ottomans
for o in [o for o in bpy.data.objects if o.name.startswith('NG atrium ottoman') and o.type=='MESH']:
    lo,hi=bb(o); m0=o.material_slots[0].material if o.material_slots else None
    c=(0.3,0.3,0.3,1)
    if m0 and m0.use_nodes and 'Principled BSDF' in m0.node_tree.nodes:
        bc=m0.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value; c=(bc[0]*0.55,bc[1]*0.55,bc[2]*0.55,1)
    pm=mat('NS_ottoman_welt_'+o.name[-1],c,0.75)
    w=0.012; e=0.006; zt=hi[2]-0.012
    bmw=bmesh.new()
    for (x0,x1,y0,y1) in ((lo[0]-e,hi[0]+e,lo[1]-e,lo[1]-e+w),(lo[0]-e,hi[0]+e,hi[1]+e-w,hi[1]+e),(lo[0]-e,lo[0]-e+w,lo[1]-e,hi[1]+e),(hi[0]+e-w,hi[0]+e,lo[1]-e,hi[1]+e)):
        r=bmesh.ops.create_cube(bmw,size=1.0)
        for v in r['verts']: v.co=mathutils.Vector(((x0+x1)/2+v.co.x*(x1-x0),(y0+y1)/2+v.co.y*(y1-y0),zt+v.co.z*0.014))
    me=bpy.data.meshes.new('NS_ottoman_welt'); bmw.to_mesh(me); bmw.free(); me.materials.append(pm)
    ow=bpy.data.objects.new(o.name.replace('NG','NS')+' top welt (UNVERIFIED)',me); col.objects.link(ow); tag(ow,'furniture')
    box(o.name.replace('NG','NS')+' plinth shadow gap (UNVERIFIED)',(lo[0]+0.03,lo[1]+0.03,lo[2]-0.002),(hi[0]-0.03,hi[1]-0.03,lo[2]+0.02),black,'furniture')
# (d) strobe lens glint
lm=bpy.data.materials.get('NP_strobe_lens_clear_UNVERIFIED')
if lm:
    p=lm.node_tree.nodes['Principled BSDF']; keys=['Roughness','Coat Weight','Coat Roughness','IOR']
    state['matvals'][lm.name]={k:p.inputs[k].default_value for k in keys}
    p.inputs['Roughness'].default_value=0.03; p.inputs['Coat Weight'].default_value=1.0; p.inputs['Coat Roughness'].default_value=0.02; p.inputs['IOR'].default_value=1.58
def cam(nm,loc,tgt,lens_):
    c=bpy.data.cameras.new(nm); c.lens=lens_; c.clip_start=0.05; o=bpy.data.objects.new(nm,c); o.location=loc
    o.rotation_euler=(mathutils.Vector(tgt)-mathutils.Vector(loc)).to_track_quat('-Z','Y').to_euler(); col.objects.link(o); tag(o,'camera')
def camcopy(nm,src):
    s=bpy.data.objects[src]; c=s.data.copy(); c.name=nm; o=bpy.data.objects.new(nm,c); o.matrix_world=s.matrix_world.copy(); col.objects.link(o); tag(o,'camera')
camcopy('NS_CAM_aerial_cutaway_studio_atrium_oblique','NQ_CAM_aerial_cutaway_studio_atrium_oblique')
camcopy('NS_CAM_eye_atrium_looking_west_to_doors','NI_CAM_eye_atrium_looking_west_to_doors')
camcopy('NS_CAM_eye_1F_open_floor_cafe_looking_east','NR_CAM_eye_1F_open_floor_cafe_looking_east')
cam('NS_CAM_closeup_entry_mat_closers_inside',(-15.7,10.9,139.35),(-20.0,11.6,138.75),20)
sc['ns_state']=json.dumps(state)
sc['ns_note']='ns: CCOM entry zone inside the front doors (mat trim + ribbed mat, overhead closers), ottoman welts/plinths, strobe lens glint; ALL UNVERIFIED'
print('NS objects',len(col.objects),'total',len(bpy.data.objects))
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
