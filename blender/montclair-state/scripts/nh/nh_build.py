# nh (Oct 30 2026): CCOM west (front) entrance glazing made see-through and lined up with the ng atrium. ALL UNVERIFIED.
import bpy, bmesh, os, math, mathutils, json
SAVE=os.environ.get('SAVE')=='1'; REVERT=os.environ.get('REVERT')=='1'
CN='NH_CCOM_front_entrance_glazing_20261030nh'
sc=bpy.context.scene
A,B=-22.930214,0.238365   # facade glass plane fitted to the existing arched glass verts: x = A + B*y (resid +-5 mm)
def L(y,off=0.0): return A+B*y+off
WALLS='School of Communication and Media walls'; WBK='nh_backup_SCM_walls_mesh_pre_nh'
GLASS='CCOM atrium glass (arched, 7x10 grid)'
def revert():
    st=json.loads(sc.get('nh_state','{}'))
    for n,(hr,hv) in st.get('hidden',{}).items():
        o=bpy.data.objects.get(n)
        if o: o.hide_render=hr; o.hide_viewport=hv
    for n,cos in st.get('verts',{}).items():
        o=bpy.data.objects.get(n)
        if o:
            for i,c in cos: o.data.vertices[i].co=c
            o.data.update()
    for n,(link,mn) in st.get('slots',{}).items():
        o=bpy.data.objects.get(n)
        if o:
            s=o.material_slots[0]; s.link='OBJECT'; s.material=None; s.link=link
    c=bpy.data.collections.get(CN)
    if c:
        for o in list(c.objects):
            d=o.data; bpy.data.objects.remove(o)
            if d and d.users==0:
                (bpy.data.meshes if isinstance(d,bpy.types.Mesh) else bpy.data.lights if isinstance(d,bpy.types.Light) else bpy.data.cameras).remove(d)
        bpy.data.collections.remove(c)
    for m in list(bpy.data.materials):
        if m.name.startswith('NH_') and m.users==0: bpy.data.materials.remove(m)
    wo=bpy.data.objects.get(WALLS); bk=bpy.data.meshes.get(WBK)
    if wo and bk:
        cur=wo.data; nm=st.get('walls_mesh',cur.name); wo.data=bk
        if cur.users==0: bpy.data.meshes.remove(cur)
        bk.use_fake_user=False; bk.name=nm
    for k in ('nh_state','nh_note'):
        if k in sc: del sc[k]
    bpy.context.view_layer.update()
if REVERT:
    revert(); bpy.ops.wm.save_mainfile(); raise SystemExit
revert()
state={'hidden':{},'verts':{},'slots':{}}
col=bpy.data.collections.new(CN); sc.collection.children.link(col)
def tag(o,layer):
    o['msu_building']='School of Communication and Media'; o['msu_area']='ccom'; o['msu_layer']=layer
    o['msu_merge_role']='live'; o['msu_target_collection']='MSU_CCOM'; o['msu_tag_session']='nh'
def simple(n,c,rough=0.5):
    m=bpy.data.materials.new('NH_'+n); m.use_nodes=True; p=m.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value=(*c,1); p.inputs['Roughness'].default_value=rough; return m
# clear thin architectural glass: transparent (slight green tint) + fresnel gloss, no refraction offset (single-sided panes)
g=bpy.data.materials.new('NH_entrance_glass_clear_thin_UNVERIFIED'); g.use_nodes=True; nt=g.node_tree; nt.nodes.clear()
out=nt.nodes.new('ShaderNodeOutputMaterial'); mix=nt.nodes.new('ShaderNodeMixShader'); tr=nt.nodes.new('ShaderNodeBsdfTransparent'); gl=nt.nodes.new('ShaderNodeBsdfGlossy')
lw=nt.nodes.new('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value=0.12
mp=nt.nodes.new('ShaderNodeMath'); mp.operation='MULTIPLY_ADD'; mp.inputs[1].default_value=0.5; mp.inputs[2].default_value=0.03
tr.inputs['Color'].default_value=(0.86,0.93,0.91,1); gl.inputs['Roughness'].default_value=0.03; gl.inputs['Color'].default_value=(0.9,0.93,0.93,1)
nt.links.new(lw.outputs['Fresnel'],mp.inputs[0]); nt.links.new(mp.outputs[0],mix.inputs['Fac'])
nt.links.new(tr.outputs[0],mix.inputs[1]); nt.links.new(gl.outputs[0],mix.inputs[2]); nt.links.new(mix.outputs[0],out.inputs['Surface'])
mar=bpy.data.materials.get('Mullion_mahogany'); wall=bpy.data.materials.get('NG_wall_white'); ceil=bpy.data.materials.get('NG_ceiling_white')
saddle=simple('door_threshold_saddle_bronze_UNVERIFIED',(0.22,0.16,0.10),0.35); saddle.node_tree.nodes['Principled BSDF'].inputs['Metallic'].default_value=0.8
# 1) existing arched entrance glass -> clear thin glass (object-level override; the newsroom bay keeps the old tinted material)
o=bpy.data.objects[GLASS]; s=o.material_slots[0]; state['slots'][GLASS]=(s.link,s.material.name); s.link='OBJECT'; s.material=g
# 1b) real opening: delete the SCM walls faces that filled the arch 6 cm behind the glass (mesh backed up for REVERT)
wo=bpy.data.objects[WALLS]; me=wo.data; state['walls_mesh']=me.name
bk=me.copy(); bk.name=WBK; bk.use_fake_user=True
bm=bmesh.new(); bm.from_mesh(me); bm.faces.ensure_lookup_table(); Wm=wo.matrix_world; dels=[]
for f in bm.faces:
    vs=[Wm@v.co for v in f.verts]
    if min(v.y for v in vs)>=9.45 and max(v.y for v in vs)<=14.25 and min(v.z for v in vs)>=136.6 and max(v.z for v in vs)<=147.7 and max(abs(v.x-L(v.y)) for v in vs)<0.3: dels.append(f)
print('NH deleted wall faces',len(dels)); bmesh.ops.delete(bm,geom=dels,context='FACES_ONLY'); bm.to_mesh(me); bm.free(); me.update()
# 2) line the ng atrium up with the skewed facade: floor + N wall west edges moved onto the glass plane (inner face +3 cm)
for n in ('NG 1F open floor atrium terrazzo','NG atrium N wall (tower face)'):
    ob=bpy.data.objects[n]; keep=[]
    for v in ob.data.vertices:
        if abs(v.co.x+19.55)<1e-3:
            keep.append((v.index,tuple(v.co))); v.co.x=L(v.co.y,0.03)
    ob.data.update(); state['verts'][n]=keep
def prism(name,poly,z0,z1,m,layer):
    me=bpy.data.meshes.new(name); bm=bmesh.new()
    lo=[bm.verts.new((x,y,z0)) for x,y in poly]; hi=[bm.verts.new((x,y,z1)) for x,y in poly]
    bm.faces.new(lo[::-1]); bm.faces.new(hi)
    k=len(poly)
    for i in range(k): bm.faces.new([lo[i],lo[(i+1)%k],hi[(i+1)%k],hi[i]])
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(me); bm.free(); me.materials.append(m)
    ob=bpy.data.objects.new(name,me); col.objects.link(ob); tag(ob,layer); return ob
F=137.70; CA=146.0
# 3) inside jamb linings either side of the glazing (close the gaps to the atrium S wall / tower face)
prism('NH entrance S inner jamb lining (white, UNVERIFIED)',[(L(6.30,0.06),6.30),(L(9.0,0.06),9.0),(-19.58,9.0),(-19.58,6.30)],F+0.004,146.12,wall,'wall')
prism('NH entrance N inner jamb lining (white, UNVERIFIED)',[(L(15.40,0.06),15.40),(L(16.48,0.06),16.48),(L(16.48,0.62),16.48),(L(15.40,0.62),15.40)],F+0.004,146.12,wall,'wall')
# 4) entrance soffit over the inner glazing zone (above the 146.16 arch top) + drop fascia to the ng/14v atrium ceiling at x -17.5
prism('NH entrance soffit over front glazing (UNVERIFIED)',[(L(6.30,0.06),6.30),(L(16.48,0.06),16.48),(-17.44,16.48),(-17.44,6.30)],146.19,146.31,ceil,'ceiling')
prism('NH entrance soffit drop fascia (UNVERIFIED)',[(-17.535,6.30),(-17.535,16.48),(-17.465,16.48),(-17.465,6.30)],145.985,146.19,ceil,'ceiling')
# 5) door leaves: maroon bottom rails + bronze saddles where the threshold (137.65) meets the 137.70 floor
legs=[(9.665,10.59),(10.59,11.515),(12.095,13.025),(13.025,13.945)]
def strip(name,y0,y1,o0,o1,z0,z1,m,layer):
    return prism(name,[(L(y0,o0),y0),(L(y1,o0),y1),(L(y1,o1),y1),(L(y0,o1),y0)],z0,z1,m,layer)
for i,(a,b) in enumerate(legs):
    strip('NH door leaf %d bottom rail (maroon)'%i,a+0.065,b-0.065,-0.035,0.035,137.655,137.88,mar,'door')
for j,(a,b) in enumerate([(9.60,11.58),(12.03,14.01)]):
    strip('NH door pair %d inside saddle (bronze)'%j,a,b,0.045,0.30,137.640,137.712,saddle,'door')
# 7) stair glass rail: low-reflection thin glass (its strong mirror reflection showed the LED sign text reversed)
lg=g.copy(); lg.name='NH_stair_rail_glass_low_reflection_UNVERIFIED'
for n in lg.node_tree.nodes:
    if n.bl_idname=='ShaderNodeMath': n.inputs[1].default_value=0.08; n.inputs[2].default_value=0.005
def override(objname,m):
    ob=bpy.data.objects.get(objname)
    if not ob: print('NH missing',objname); return
    sl=ob.material_slots[0]; state['slots'][objname]=(sl.link,sl.material.name if sl.material else ''); sl.link='OBJECT'; sl.material=m
for ob in list(bpy.data.collections['NG_CCOM_1F_open_floor_20261030ng'].objects):
    if ob.type=='MESH' and ob.material_slots and ob.material_slots[0].material and ob.material_slots[0].material.name=='NG_rail_glass':
        bb=[ob.matrix_world@mathutils.Vector(c) for c in ob.bound_box]
        if max(v.x for v in bb)<-1.0: override(ob.name,lg)
# 8) less flat interior: terrazzo with large-scale tone clouds + fine flecks (object-level copy on the 1F floors), skirting, ceiling diffusers
src=bpy.data.materials['NG_terrazzo_1F_open_floor']; tz=src.copy(); tz.name='NH_terrazzo_1F_tone_variation_UNVERIFIED'; t=tz.node_tree; P=t.nodes['Principled BSDF']
tc=t.nodes.new('ShaderNodeTexCoord'); n1=t.nodes.new('ShaderNodeTexNoise'); n1.inputs['Scale'].default_value=0.35; n1.inputs['Detail'].default_value=3
vo=t.nodes.new('ShaderNodeTexVoronoi'); vo.inputs['Scale'].default_value=140
r1=t.nodes.new('ShaderNodeValToRGB'); r1.color_ramp.elements[0].color=(0.42,0.40,0.37,1); r1.color_ramp.elements[1].color=(0.74,0.72,0.68,1)
r2=t.nodes.new('ShaderNodeValToRGB'); r2.color_ramp.elements[0].position=0.80; r2.color_ramp.elements[0].color=(1,1,1,1); r2.color_ramp.elements[1].color=(0.45,0.43,0.40,1)
mx=t.nodes.new('ShaderNodeMix'); mx.data_type='RGBA'; mx.blend_type='MULTIPLY'; mx.inputs['Factor'].default_value=1.0
old=[l.from_socket for l in t.links if l.to_socket==P.inputs['Base Color']]
t.links.new(tc.outputs['Object'],n1.inputs['Vector']); t.links.new(tc.outputs['Object'],vo.inputs['Vector'])
t.links.new(n1.outputs['Fac'],r1.inputs['Fac']); t.links.new(vo.outputs['Distance'],r2.inputs['Fac'])
mx2=t.nodes.new('ShaderNodeMix'); mx2.data_type='RGBA'; mx2.blend_type='MULTIPLY'; mx2.inputs['Factor'].default_value=1.0
if old: t.links.new(old[0],mx2.inputs[6])
t.links.new(r1.outputs['Color'],mx2.inputs[7]); t.links.new(mx2.outputs[2],mx.inputs[6]); t.links.new(r2.outputs['Color'],mx.inputs[7])
t.links.new(mx.outputs[2],P.inputs['Base Color']); P.inputs['Roughness'].default_value=0.32
for n in ('NG 1F open floor atrium terrazzo','NG 1F open floor hallway terrazzo','NG 1F open floor east double-height terrazzo'): override(n,tz)
sk=bpy.data.materials.get('MY_rubber_cove_base_dark_grey_UNVERIFIED') or simple('skirting_dark_grey_UNVERIFIED',(0.08,0.08,0.085),0.6)
def bx(name,x0,x1,y0,y1,z0,z1,m,layer):
    return prism(name,[(x0,y0),(x1,y0),(x1,y1),(x0,y1)],z0,z1,m,layer)
bx('NH atrium N wall skirting',-19.0,-15.02,16.455,16.515,F+0.002,F+0.11,sk,'skirting')
for i,(a,b) in enumerate([(-16.7,-13.6),(-11.4,-9.1),(-6.9,-2.32)]): bx('NH atrium S wall skirting %d'%i,a,b,6.252,6.30,F+0.002,F+0.11,sk,'skirting')
bx('NH hallway N wall skirting',-2.1,8.4,13.865,13.92,F+0.002,F+0.11,sk,'skirting')
df=simple('ceiling_diffuser_grille_UNVERIFIED',(0.70,0.71,0.72),0.5); dfr=simple('ceiling_diffuser_slot_dark',(0.12,0.12,0.13),0.7)
for i,x in enumerate([-0.6,1.8,4.2,6.6]):
    bx('NH 1F hallway ceiling diffuser %d frame'%i,x-0.3,x+0.3,10.2,10.8,141.425,141.442,df,'ceiling'); bx('NH 1F hallway ceiling diffuser %d core'%i,x-0.2,x+0.2,10.3,10.7,141.418,141.426,dfr,'ceiling')
    bx('NH 2F hallway ceiling diffuser %d frame'%i,x-0.3,x+0.3,10.2,10.8,144.885,144.904,df,'ceiling'); bx('NH 2F hallway ceiling diffuser %d core'%i,x-0.2,x+0.2,10.3,10.7,144.868,144.876,dfr,'ceiling')
# 6) cameras
def cam(n,loc,tgt,lens):
    c=bpy.data.cameras.new(n); c.lens=lens; c.clip_start=0.05; ob=bpy.data.objects.new(n,c); ob.location=loc
    ob.rotation_euler=(mathutils.Vector(tgt)-mathutils.Vector(loc)).to_track_quat('-Z','Y').to_euler(); col.objects.link(ob); tag(ob,'camera')
cam('NH_CAM_aerial_front_oblique',(-50,0,160),(-15,11,141),30)
cam('NH_CAM_eye_outside_front_looking_in',(-28.3,13.9,139.1),(-12.0,9.9,140.0),24)
cam('NH_CAM_eye_atrium_looking_west_to_entry',(-8.5,10.2,139.3),(-20.3,11.6,140.8),20)
cam('NH_CAM_closeup_entrance_door_glazing',(-23.4,10.2,138.7),(-20.3,11.0,138.7),30)
sc['nh_state']=json.dumps(state)
sc['nh_note']='nh: CCOM front entrance glazing clear + aligned with the ng atrium (floor/N wall west edges on the glass plane, jamb linings, soffit, door rails/saddles); ALL UNVERIFIED'
print('NH objects',len(col.objects),'total',len(bpy.data.objects))
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
