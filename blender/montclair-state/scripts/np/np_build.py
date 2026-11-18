# np (Oct 30 2026 ~3:40 PM ET, MAIN): CCOM interior life-safety + wayfinding detail per no 'Next' — ALL UNVERIFIED (code-typical, no photos):
# (a) fire alarm horn/strobes (red, ~2.03 m AFF lens) in the atrium, 1F/2F hallways; manual pull station by the front doors (1.2 m AFF);
# (b) pendent sprinkler heads (chrome escutcheon + deflector) on the atrium / hallway / double-height / room ceilings (~3 m grid);
# (c) room-number plaques (charcoal, white numerals + braille dots) beside the 4 hallway door pairs — NUMBERS UNVERIFIED;
# (d) fix: no PIR sensors floated ~13 cm off the hallway walls -> moved onto the wall face (state recorded for REVERT).
# cutaway aerial: np_render.py also hides the studio rigging grid + hung items and the new atrium sprinklers for 'cutaway' cams.
import bpy, bmesh, os, json, mathutils, math
SAVE=os.environ.get('SAVE')=='1'; REVERT=os.environ.get('REVERT')=='1'
CN='NP_CCOM_life_safety_wayfinding_20261030np'
sc=bpy.context.scene
def revert():
    st=json.loads(sc.get('np_state','{}'))
    for n,m in st.get('mats',{}).items():
        o=bpy.data.objects.get(n)
        if o: o.matrix_world=mathutils.Matrix([m[i*4:(i+1)*4] for i in range(4)])
    for n,h in st.get('hide',{}).items():
        o=bpy.data.objects.get(n)
        if o: o.hide_render,o.hide_viewport=h
    for n,(link,objmat) in st.get('slots',{}).items():
        o=bpy.data.objects.get(n)
        if o: s=o.material_slots[0]; s.link='OBJECT'; s.material=bpy.data.materials.get(objmat) if objmat else None; s.link=link
    c=bpy.data.collections.get(CN)
    if c:
        for o in list(c.objects):
            d=o.data; bpy.data.objects.remove(o)
            if d and d.users==0:
                for coll in (bpy.data.meshes,bpy.data.cameras,bpy.data.lights,bpy.data.curves):
                    if d.name in coll and coll[d.name]==d: coll.remove(d); break
        bpy.data.collections.remove(c)
    for me in list(bpy.data.meshes):
        if me.name.startswith('NP_') and me.users==0: bpy.data.meshes.remove(me)
    for m in list(bpy.data.materials):
        if m.name.startswith('NP_') and m.users==0: bpy.data.materials.remove(m)
    for k in ('np_state','np_note'):
        if k in sc: del sc[k]
    bpy.context.view_layer.update()
if REVERT:
    revert(); bpy.ops.wm.save_mainfile(); raise SystemExit
revert()
state={'mats':{},'hide':{},'slots':{}}
col=bpy.data.collections.new(CN); sc.collection.children.link(col)
def tag(o,layer):
    o['msu_building']='School of Communication and Media'; o['msu_area']='ccom'; o['msu_layer']=layer
    o['msu_merge_role']='live'; o['msu_target_collection']='MSU_CCOM'; o['msu_tag_session']='np'
def mat(name,c,rough=0.6,emit=0.0,metal=0.0):
    m=bpy.data.materials.new(name); m.use_nodes=True; p=m.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value=c; p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal
    if emit: p.inputs['Emission Color'].default_value=c; p.inputs['Emission Strength'].default_value=emit
    return m
def boxbm(bm,x0,x1,y0,y1,z0,z1):
    r=bmesh.ops.create_cube(bm,size=1.0)
    for v in r['verts']: v.co=mathutils.Vector(((x0+x1)/2+v.co.x*(x1-x0),(y0+y1)/2+v.co.y*(y1-y0),(z0+z1)/2+v.co.z*(z1-z0)))
def cylbm(bm,x,y,z0,z1,r,seg=16):
    res=bmesh.ops.create_cone(bm,cap_ends=True,segments=seg,radius1=r,radius2=r,depth=z1-z0)
    bmesh.ops.translate(bm,verts=res['verts'],vec=(x,y,(z0+z1)/2))
def mkmesh(name,bm,mats):
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for m in mats: me.materials.append(m)
    return me
def inst(name,me,loc,rotz,layer,shadow=True):
    ob=bpy.data.objects.new(name[:63],me); ob.location=loc; ob.rotation_euler=(0,0,rotz); col.objects.link(ob); tag(ob,layer)
    if not shadow: ob.visible_shadow=False
    return ob
red=mat('NP_fire_alarm_red_UNVERIFIED',(0.55,0.02,0.02,1),0.35)
lensm=mat('NP_strobe_lens_clear_UNVERIFIED',(0.95,0.95,0.95,1),0.1); lensm.node_tree.nodes['Principled BSDF'].inputs['Transmission Weight'].default_value=0.6
whitep=mat('NP_fire_label_white_UNVERIFIED',(0.85,0.85,0.83,1),0.4)
chrome=mat('NP_sprinkler_chrome_UNVERIFIED',(0.8,0.8,0.8,1),0.18,metal=1.0)
brass=mat('NP_sprinkler_bulb_red_glass_UNVERIFIED',(0.8,0.05,0.03,1),0.1)
char=mat('NP_room_plaque_charcoal_UNVERIFIED',(0.05,0.05,0.055,1),0.45)
num=mat('NP_room_plaque_numeral_white_UNVERIFIED',(0.88,0.88,0.86,1),0.4)
# ---- (a) horn/strobe: local frame = mounted on a wall facing local -Y (back at y=0)
bm=bmesh.new()
boxbm(bm,-0.065,0.065,-0.045,0.0,-0.11,0.065)       # red body (mat 0)
n0=len(bm.faces)
boxbm(bm,-0.035,0.035,-0.062,-0.045,0.0,0.045)      # strobe lens on top part (mat 1)
n1=len(bm.faces)
boxbm(bm,-0.045,0.045,-0.049,-0.045,-0.085,-0.06)   # white 'FIRE' label band (mat 2)
for i,f in enumerate(bm.faces): f.material_index=0 if i<n0 else (1 if i<n1 else 2)
for v in bm.verts: pass
HS=mkmesh('NP_horn_strobe_UNVERIFIED',bm,[red,lensm,whitep])
# wall face lists: (name, x, y_face, z_centre, facing) facing '-y' means the device faces -y (wall behind at larger y)
STROBES=[('1F hallway N wall',3.0,13.93,139.85,'-y'),('1F hallway S wall',3.75,7.07,139.85,'+y'),
         ('atrium red wall between door pairs',-10.25,6.25,139.85,'+y'),('atrium N wall W of stair',-17.4,16.52,139.85,'-y'),
         ('2F hallway S wall',3.0,7.07,143.90,'+y'),('2F back hallway W wall',5.57,18.0,143.90,'+x')]
for nm,x,yf,z,f in STROBES:
    if f=='-y': inst('NP horn-strobe '+nm+' (UNVERIFIED)',HS,(x,yf+0.002,z),0,'life_safety')
    elif f=='+y': inst('NP horn-strobe '+nm+' (UNVERIFIED)',HS,(x,yf-0.002,z),math.pi,'life_safety')
    else: inst('NP horn-strobe '+nm+' (UNVERIFIED)',HS,(x-0.002,yf,z),math.pi/2,'life_safety')
# pull station (local, faces -y)
bm=bmesh.new(); boxbm(bm,-0.065,0.065,-0.04,0.0,-0.09,0.09); n0=len(bm.faces)
boxbm(bm,-0.04,0.04,-0.058,-0.04,0.0,0.03); n1=len(bm.faces)   # white pull handle
boxbm(bm,-0.05,0.05,-0.043,-0.04,-0.07,-0.03)                  # white label
for i,f in enumerate(bm.faces): f.material_index=0 if i<n0 else 1
PS=mkmesh('NP_pull_station_UNVERIFIED',bm,[red,whitep])
inst('NP manual pull station atrium S wall by front doors (UNVERIFIED)',PS,(-18.9,6.27-0.002,138.92),math.pi,'life_safety')
inst('NP manual pull station 1F hallway N wall east end (UNVERIFIED)',PS,(7.6,13.93+0.002,138.92),0,'life_safety')
# ---- (b) pendent sprinkler (local: ceiling plane at z=0, hangs down)
bm=bmesh.new(); cylbm(bm,0,0,-0.006,0.0,0.036,20); cylbm(bm,0,0,-0.034,-0.006,0.009,10)
boxbm(bm,-0.012,0.012,-0.002,0.002,-0.045,-0.008)   # frame arms
cylbm(bm,0,0,-0.048,-0.044,0.016,14)                # deflector
n0=len(bm.faces); cylbm(bm,0,0,-0.044,-0.030,0.003,8)   # red glass bulb
for i,f in enumerate(bm.faces): f.material_index=0 if i<n0 else 1
SP=mkmesh('NP_pendent_sprinkler_UNVERIFIED',bm,[chrome,brass])
SPR=[]
SPR+= [('atrium',x,y,145.96) for x in (-18.0,-14.5,-11.0,-7.5) for y in (10.0,13.0)]
SPR+= [('1F hallway',x,y,141.44) for x in (0.0,3.0,6.0) for y in (9.5,11.5)]
SPR+= [('2F hallway',x,y,144.90) for x in (0.0,3.0,6.0) for y in (9.5,11.5)]
SPR+= [('2F back hallway',7.0,y,144.90) for y in (16.0,19.5)]
SPR+= [('double-height east',x,y,144.90) for x in (9.6,11.2) for y in (8.5,11.8)]
SPR+= [('N classroom',x,y,140.88) for x,y in ((2.6,15.0),(5.8,15.0),(1.0,17.2),(4.2,17.2))]
SPR+= [('S office',x,y,140.88) for x,y in ((0.8,4.2),(3.8,6.3),(6.8,4.2))]
for i,(nm,x,y,z) in enumerate(SPR): inst('NP sprinkler %s %02d (UNVERIFIED)'%(nm,i),SP,(x,y,z),0,'life_safety',shadow=False)
# ---- (c) room-number plaques (numbers UNVERIFIED)
def txtmesh(body,size,M,mt):
    cu=bpy.data.curves.new('NP_tmp_txt','FONT'); cu.body=body; cu.size=size; cu.align_x='CENTER'; cu.align_y='CENTER'; cu.extrude=0.0012
    t=bpy.data.objects.new('NP_tmp_txt',cu); col.objects.link(t); bpy.context.view_layer.update()
    dg=bpy.context.evaluated_depsgraph_get(); me=bpy.data.meshes.new_from_object(t.evaluated_get(dg))
    bpy.data.objects.remove(t); bpy.data.curves.remove(cu); me.transform(M); me.materials.clear(); me.materials.append(mt); return me
PLAQ=[('N',2.30,13.93,'1012'),('N',6.30,13.93,'1016'),('S',2.80,7.07,'1013'),('S',7.30,7.07,'1017')]
for side,x,yf,lab in PLAQ:
    zc=139.22; d=-1 if side=='N' else 1   # direction into hallway
    y0,y1=(yf-0.012,yf+0.001) if side=='N' else (yf-0.001,yf+0.012)
    bm=bmesh.new(); boxbm(bm,x-0.10,x+0.10,y0,y1,zc-0.10,zc+0.10)
    me=mkmesh('NP_room_plaque_%s'%lab,bm,[char]); o=bpy.data.objects.new('NP room-number plaque %s (number UNVERIFIED)'%lab,me); col.objects.link(o); tag(o,'sign')
    yt=(y0 if side=='N' else y1)
    R=mathutils.Matrix.Rotation(math.pi/2,4,'X') if side=='N' else mathutils.Matrix.Rotation(math.pi,4,'Z')@mathutils.Matrix.Rotation(math.pi/2,4,'X')
    M=mathutils.Matrix.Translation((x,yt+d*0.0006,zc+0.03))@R
    me2=txtmesh(lab,0.075,M,num); o2=bpy.data.objects.new('NP room-number plaque %s numerals'%lab,me2); col.objects.link(o2); tag(o2,'sign'); o2.visible_shadow=False
    bm=bmesh.new()
    for k in range(len(lab)*2):
        cylbm(bm,0,0,0,0.0015,0.0028,8); 
    me3=bpy.data.meshes.new('NP_braille_%s'%lab); 
    bm2=bmesh.new()
    for k in range(4):
        for r in range(3):
            if (k+r)%2==0:
                res=bmesh.ops.create_cone(bm2,cap_ends=True,segments=8,radius1=0.0028,radius2=0.0028,depth=0.003)
                bmesh.ops.rotate(bm2,verts=res['verts'],cent=(0,0,0),matrix=mathutils.Matrix.Rotation(math.pi/2,3,'X'))
                bmesh.ops.translate(bm2,verts=res['verts'],vec=(x-0.045+k*0.03,yt+d*0.001,zc-0.045+r*0.01))
    bm.free(); bm2.to_mesh(me3); bm2.free(); me3.materials.append(num)
    o3=bpy.data.objects.new('NP room-number plaque %s braille'%lab,me3); col.objects.link(o3); tag(o3,'sign'); o3.visible_shadow=False
# ---- (d) PIR sensor fix: put them on the wall face
for o in bpy.data.objects:
    if o.name.startswith('NO PIR sensor '):
        side=o.name[14]; lo=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]
        state['mats'][o.name]=[v for row in o.matrix_world for v in row]
        if side=='N':
            dy=13.93-max(c.y for c in lo) if o.name.endswith('body') else 13.93-0.05-max(c.y for c in lo)
        else:
            dy=7.07-min(c.y for c in lo) if o.name.endswith('body') else 7.07+0.05-min(c.y for c in lo)
        o.matrix_world=mathutils.Matrix.Translation((0,dy+(0.001 if side=='N' else -0.001),0))@o.matrix_world
# ---- (e) 2F east balcony edge: the 2 cm white slab-edge strip rendered as a black band from the balcony -> walnut fascia like the atrium bridge; balcony rail glass = the low-reflection stair glass
se=bpy.data.objects.get('NG east balcony slab edge')
if se:
    state['hide'][se.name]=(se.hide_render,se.hide_viewport); se.hide_render=True; se.hide_viewport=True
    bm=bmesh.new(); boxbm(bm,8.50,8.53,7.0,14.0,141.40,141.88)
    me=mkmesh('NP_balcony_fascia',bm,[bpy.data.materials.get('NG_wood_cladding') or char]); o=bpy.data.objects.new('NP 2F east balcony walnut fascia (UNVERIFIED)',me); col.objects.link(o); tag(o,'trim')
gr=bpy.data.objects.get('NG east balcony glass rail'); lr=bpy.data.materials.get('NH_stair_rail_glass_low_reflection_UNVERIFIED')
if gr and lr:
    sl=gr.material_slots[0]; state['slots'][gr.name]=(sl.link,sl.material.name if (sl.link=='OBJECT' and sl.material) else None); sl.link='OBJECT'; sl.material=lr
# ---------- cameras
def cam(n,loc,tgt,lens_):
    c=bpy.data.cameras.new(n); c.lens=lens_; c.clip_start=0.05; o=bpy.data.objects.new(n,c); o.location=loc
    o.rotation_euler=(mathutils.Vector(tgt)-mathutils.Vector(loc)).to_track_quat('-Z','Y').to_euler(); col.objects.link(o); tag(o,'camera')
cam('NP_CAM_aerial_cutaway_studio_atrium_oblique',(-3.0,-22.0,178.0),(-9.0,4.0,138.0),28)
cam('NP_CAM_eye_1F_hallway_looking_east_strobes_plaques',(-1.2,10.6,139.3),(10.0,10.4,139.6),18)
cam('NP_CAM_eye_2F_east_balcony_looking_down_east',(8.25,12.4,143.5),(11.2,9.6,138.2),16)
cam('NP_CAM_closeup_hallway_N_wall_strobe_plaque_sprinkler',(2.5,12.2,139.4),(2.85,13.93,139.65),30)
sc['np_state']=json.dumps(state)
sc['np_note']='np: horn/strobes, pull stations, pendent sprinklers, room-number plaques (numbers UNVERIFIED), PIR sensor wall fix; ALL UNVERIFIED'
print('NP objects',len(col.objects),'total',len(bpy.data.objects))
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
