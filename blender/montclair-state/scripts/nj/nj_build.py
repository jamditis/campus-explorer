# nj (Oct 30 2026, MAIN): CCOM interior polish per ni 'Next': (1) interior materials/lights less white/flat (terrazzo, red wall, wood stair, maroon frames read);
# (2) unsourced black 'bin' inside the right door pair = a 3g downspout boot + grate left inside the atrium after nh moved the glazing -> removed (mesh copy);
# (3) ceiling LED strip reflections in the arch glass seen from inside -> arch glass copy goes mostly transparent for rays from the interior side;
# (4) real openings behind the 2 maroon door pairs on the atrium red wall + a simple blocked-out vestibule behind them (UNVERIFIED);
# (5) recessed entrance walk-off mat inside the doors (UNVERIFIED). All sizes/tones UNVERIFIED.
import bpy, bmesh, os, json, mathutils
SAVE=os.environ.get('SAVE')=='1'; REVERT=os.environ.get('REVERT')=='1'
CN='NJ_CCOM_interior_tone_rooms_20261030nj'
sc=bpy.context.scene
A,B=-22.930214,0.238365
def L(y,off=0.0): return A+B*y+off
def P(m): return bpy.data.materials[m].node_tree.nodes['Principled BSDF']
def revert():
    st=json.loads(sc.get('nj_state','{}'))
    for mn,nn,inp,v in st.get('inputs',[]):
        m=bpy.data.materials.get(mn)
        if m: m.node_tree.nodes[nn].inputs[inp].default_value=v
    for mn,nn,els in st.get('ramps',[]):
        m=bpy.data.materials.get(mn)
        if m:
            for e,c in zip(m.node_tree.nodes[nn].color_ramp.elements,els): e.color=c
    for n,e in st.get('light_energy',{}).items():
        o=bpy.data.objects.get(n)
        if o: o.data.energy=e
    for n,(orig,fu) in st.get('mesh_swap',{}).items():
        o=bpy.data.objects.get(n); om=bpy.data.meshes.get(orig)
        if o and om:
            cp=o.data; o.data=om; om.use_fake_user=fu
            if cp!=om and cp.users==0: bpy.data.meshes.remove(cp)
    for n,slots in st.get('slots',{}).items():
        o=bpy.data.objects.get(n)
        if o:
            for i,(link,objmat) in enumerate(slots):
                s=o.material_slots[i]; s.link='OBJECT'; s.material=bpy.data.materials.get(objmat) if objmat else None; s.link=link
    for mn in st.get('fake_mats',[]):
        m=bpy.data.materials.get(mn)
        if m: m.use_fake_user=False
    for n in st.get('mods',[]):
        o=bpy.data.objects.get(n)
        if o:
            for md in list(o.modifiers):
                if md.name.startswith('NJ_'): o.modifiers.remove(md)
    c=bpy.data.collections.get(CN)
    if c:
        for o in list(c.objects):
            d=o.data; bpy.data.objects.remove(o)
            if d and d.users==0:
                if isinstance(d,bpy.types.Mesh): bpy.data.meshes.remove(d)
                elif isinstance(d,bpy.types.Camera): bpy.data.cameras.remove(d)
                elif isinstance(d,bpy.types.Light): bpy.data.lights.remove(d)
        bpy.data.collections.remove(c)
    for m in list(bpy.data.materials):
        if m.name.startswith('NJ_') and m.users==0: bpy.data.materials.remove(m)
    for k in ('nj_state','nj_note'):
        if k in sc: del sc[k]
    bpy.context.view_layer.update()
if REVERT:
    revert(); bpy.ops.wm.save_mainfile(); raise SystemExit
revert()
state={'inputs':[],'ramps':[],'light_energy':{},'mesh_swap':{},'slots':{},'mods':[]}
col=bpy.data.collections.new(CN); sc.collection.children.link(col)
def tag(o,layer):
    o['msu_building']='School of Communication and Media'; o['msu_area']='ccom'; o['msu_layer']=layer
    o['msu_merge_role']='live'; o['msu_target_collection']='MSU_CCOM'; o['msu_tag_session']='nj'
def setin(mn,inp,v,nn='Principled BSDF'):
    m=bpy.data.materials.get(mn)
    if not m: return
    i=m.node_tree.nodes[nn].inputs[inp]; old=i.default_value
    state['inputs'].append((mn,nn,inp,tuple(old) if hasattr(old,'__len__') else old)); i.default_value=v
def ramp(mn,nn,f):
    m=bpy.data.materials.get(mn)
    if not m: return
    els=m.node_tree.nodes[nn].color_ramp.elements
    state['ramps'].append((mn,nn,[tuple(e.color) for e in els]))
    for e in els: e.color=f(tuple(e.color))
# ---- (1) materials: less white/flat (refs epic_28, Joe 1F photos). Tones UNVERIFIED.
setin('NG_wall_white','Base Color',(0.74,0.72,0.68,1))
setin('NG_ceiling_white','Base Color',(0.78,0.78,0.77,1))
setin('NG_red_wall','Base Color',(0.30,0.014,0.019,1)); setin('NG_red_wall','Roughness',0.5)
setin('NG_maroon_frame','Base Color',(0.15,0.017,0.021,1)); setin('NG_maroon_frame','Roughness',0.3)
for mn in ('NG_terrazzo_1F_open_floor','NH_terrazzo_1F_tone_variation_UNVERIFIED'):
    ramp(mn,'Color Ramp',lambda c:(c[0]*0.80,c[1]*0.79,c[2]*0.76,1))
setin('NG_terrazzo_1F_open_floor','Roughness',0.16); setin('NH_terrazzo_1F_tone_variation_UNVERIFIED','Roughness',0.2)
ramp('NG_wood_cladding','Color Ramp',lambda c:(c[0]*0.62,c[1]*0.50,c[2]*0.38,1))
for o in bpy.data.objects:
    if o.type=='LIGHT' and o.name.startswith('NG '):
        state['light_energy'][o.name]=o.data.energy; o.data.energy=round(o.data.energy*0.8,2)
setin('NG_led_strip','Emission Strength',2.6)
# ---- (2) unsourced black box inside the right door pair = 3g downspout boot (+cap) and its grate/cleanout at y~10.3 (no downspout there any more) -> removed in a mesh copy
CEN=mathutils.Vector((-21.0,10.3))
for n in ('Downspout boots + drain grates (3g, CCOM)','Downspout cleanout plugs brass (3h, CCOM)'):
    o=bpy.data.objects.get(n)
    if not o: continue
    om=o.data; cp=om.copy(); cp.name=om.name+'_nj'
    bm=bmesh.new(); bm.from_mesh(cp); M=o.matrix_world; seen=set(); kill=[]
    for v in bm.verts:
        if v in seen: continue
        st=[v]; isl=[]; seen.add(v)
        while st:
            x=st.pop(); isl.append(x)
            for e in x.link_edges:
                y=e.other_vert(x)
                if y not in seen: seen.add(y); st.append(y)
        c=sum((M@x.co for x in isl),mathutils.Vector())/len(isl)
        if (c.xy-CEN).length<0.75: kill+=isl
    if kill:
        bmesh.ops.delete(bm,geom=kill,context='VERTS'); bm.to_mesh(cp)
        state['mesh_swap'][n]=(om.name,om.use_fake_user); om.use_fake_user=True; o.data=cp
        print('NJ removed',len(kill),'verts from',n)
    bm.free()
    if not kill: bpy.data.meshes.remove(cp)
def setslots(o,mats):
    state['slots'][o.name]=[(s.link,(s.material.name if (s.link=='OBJECT' and s.material) else None)) for s in o.material_slots]
    for s in o.material_slots:
        if s.link=='OBJECT' and s.material and not s.material.use_fake_user:
            s.material.use_fake_user=True; state.setdefault('fake_mats',[]).append(s.material.name)   # keep the replaced object-level material alive in the file (REVERT needs it)
    for s,m in zip(o.material_slots,mats): s.link='OBJECT'; s.material=m
# ---- (3) arch glass: rays arriving from the interior side see mostly transparent glass (low-e look), so the ceiling LED strips no longer mirror in it from inside
g=bpy.data.objects['CCOM atrium glass (arched, 7x10 grid)']
gm=g.material_slots[0].material.copy(); gm.name='NJ_entrance_glass_inside_low_reflection_UNVERIFIED'
nt=gm.node_tree; out=[n for n in nt.nodes if n.type=='OUTPUT_MATERIAL'][0]; src=out.inputs['Surface'].links[0].from_socket
geo=nt.nodes.new('ShaderNodeNewGeometry'); dot=nt.nodes.new('ShaderNodeVectorMath'); dot.operation='DOT_PRODUCT'
nin=mathutils.Vector((1,-B,0)).normalized(); dot.inputs[1].default_value=nin
nt.links.new(geo.outputs['Incoming'],dot.inputs[0])
gt=nt.nodes.new('ShaderNodeMath'); gt.operation='GREATER_THAN'; gt.inputs[1].default_value=0.0; nt.links.new(dot.outputs['Value'],gt.inputs[0])
mul=nt.nodes.new('ShaderNodeMath'); mul.operation='MULTIPLY'; mul.inputs[1].default_value=0.85; nt.links.new(gt.outputs[0],mul.inputs[0])
tr=nt.nodes.new('ShaderNodeBsdfTransparent'); mx=nt.nodes.new('ShaderNodeMixShader')
nt.links.new(mul.outputs[0],mx.inputs[0]); nt.links.new(src,mx.inputs[1]); nt.links.new(tr.outputs[0],mx.inputs[2]); nt.links.new(mx.outputs[0],out.inputs['Surface'])
setslots(g,[gm])
# ---- (4) real openings behind the 2 maroon door pairs on the atrium red wall + blocked-out vestibule (UNVERIFIED: nothing shows what is behind these doors)
def box(name,x0,x1,y0,y1,z0,z1,m,layer,inward=False):
    me=bpy.data.meshes.new(name); bm=bmesh.new(); bmesh.ops.create_cube(bm,size=1.0)
    for v in bm.verts: v.co=mathutils.Vector(((x0+x1)/2+v.co.x*(x1-x0),(y0+y1)/2+v.co.y*(y1-y0),(z0+z1)/2+v.co.z*(z1-z0)))
    if inward: bmesh.ops.reverse_faces(bm,faces=bm.faces)
    bm.to_mesh(me); bm.free(); me.materials.append(m); ob=bpy.data.objects.new(name,me); col.objects.link(ob); tag(ob,layer); return ob
def mat(name,col_,rough=0.6,emit=0.0,trans=0.0):
    m=bpy.data.materials.new(name); m.use_nodes=True; p=m.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value=col_; p.inputs['Roughness'].default_value=rough
    if emit: p.inputs['Emission Color'].default_value=col_; p.inputs['Emission Strength'].default_value=emit
    if trans: p.inputs['Transmission Weight'].default_value=trans
    return m
DOORS=[(-13.48,-11.52),(-8.98,-7.02)]
wall_names=['NG atrium S wall red panel','CCOM_int_lounge_wall_S_20261014v']
for i,(x0,x1) in enumerate(DOORS):
    c=box('NJ door opening cutter %d (hidden)'%i,x0+0.14,x1-0.14,5.95,6.45,137.80,140.04,bpy.data.materials['NG_wall_white'],'cutter')
    c.hide_render=True; c.display_type='BOUNDS'
    for wn in wall_names+['NG atrium red wall maroon doors %d frame'%i]:
        w=bpy.data.objects.get(wn)
        if w:
            md=w.modifiers.new('NJ_door_opening_%d'%i,'BOOLEAN'); md.object=c; md.operation='DIFFERENCE'; md.solver='EXACT'
            if wn not in state['mods']: state['mods'].append(wn)
satin=mat('NJ_door_glass_satin_UNVERIFIED',(0.92,0.92,0.93,1),rough=0.22,trans=1.0)
for i in range(2):
    o=bpy.data.objects.get('NG atrium red wall maroon doors %d frosted glass'%i)
    if o: setslots(o,[satin])
vw=mat('NJ_vestibule_wall_white_UNVERIFIED',(0.70,0.69,0.66,1),0.75)
vf=bpy.data.materials['NG_terrazzo_1F_open_floor']
box('NJ vestibule behind red-wall doors (room shell, inward, UNVERIFIED)',-14.2,-6.3,4.62,6.08,137.69,140.62,vw,'room',inward=True)
box('NJ vestibule floor terrazzo (UNVERIFIED)',-14.18,-6.32,4.64,6.08,137.66,137.70,vf,'floor')
box('NJ vestibule cove base (UNVERIFIED)',-14.18,-6.32,4.64,4.66,137.70,137.80,bpy.data.materials.get('MY_rubber_cove_base_dark_grey_UNVERIFIED') or vw,'trim')
led=bpy.data.materials['NG_led_strip']
for k,xc in enumerate((-12.5,-8.0)):
    box('NJ vestibule ceiling LED panel %d (UNVERIFIED)'%k,xc-0.6,xc+0.6,5.05,5.65,140.585,140.60,led,'light')
    ld=bpy.data.lights.new('NJ vestibule light %d'%k,'AREA'); ld.energy=60; ld.size=1.0; ld.color=(1,0.96,0.9)
    lo=bpy.data.objects.new('NJ vestibule light %d'%k,ld); lo.location=(xc,5.35,140.55); col.objects.link(lo); tag(lo,'light')
# ---- (5) recessed walk-off mat inside the entrance doors (UNVERIFIED; common in entries, not in a photo)
mm=mat('NJ_entrance_mat_charcoal_UNVERIFIED',(0.035,0.035,0.038,1),0.95)
y0,y1=9.70,13.90
me=bpy.data.meshes.new('NJ entrance walk-off mat'); bm=bmesh.new()
pts=[(L(y0,0.16),y0),(L(y1,0.16),y1),(L(y1,1.95),y1),(L(y0,1.95),y0)]
lo_=[bm.verts.new((x,y,137.695)) for x,y in pts]; hi_=[bm.verts.new((x,y,137.709)) for x,y in pts]
bm.faces.new(lo_[::-1]); bm.faces.new(hi_)
for i in range(4): bm.faces.new([lo_[i],lo_[(i+1)%4],hi_[(i+1)%4],hi_[i]])
bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(me); bm.free(); me.materials.append(mm)
ob=bpy.data.objects.new('NJ entrance walk-off mat (UNVERIFIED)',me); col.objects.link(ob); tag(ob,'floor')
# ---- cameras
def cam(n,loc,tgt,lens):
    c=bpy.data.cameras.new(n); c.lens=lens; c.clip_start=0.05; o=bpy.data.objects.new(n,c); o.location=loc
    o.rotation_euler=(mathutils.Vector(tgt)-mathutils.Vector(loc)).to_track_quat('-Z','Y').to_euler(); col.objects.link(o); tag(o,'camera')
cam('NJ_CAM_aerial_cutaway_atrium_oblique',(-38,-14,170),(-6,10,138),30)
cam('NJ_CAM_eye_atrium_looking_east',(-18.4,11.0,139.3),(5,9.6,139.0),20)
cam('NJ_CAM_eye_1F_open_floor_looking_west',(6.0,10.0,139.2),(-20,11.6,139.9),22)
cam('NJ_CAM_closeup_red_wall_door_openings',(-10.3,10.8,139.0),(-10.3,5.6,138.8),22)
sc['nj_state']=json.dumps(state)
sc['nj_note']='nj: CCOM interior tones/lights, downspout boot removed from inside the doors, arch glass low reflection from inside, real openings + blocked vestibule behind the red-wall maroon doors, entrance mat; ALL UNVERIFIED'
print('NJ objects',len(col.objects),'total',len(bpy.data.objects))
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
