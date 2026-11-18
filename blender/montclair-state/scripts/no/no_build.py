# no (Oct 30 2026 ~2:30 PM ET, MAIN): CCOM interior per nk 'Next' — ALL UNVERIFIED:
# (a) red-wall wash: warm ceiling wall-washer spots grazing the atrium crimson wall + stair side (breaks the even daylight look);
# (b) N classroom + S office: 2x2 ft lay-in ceiling grid (tees) + chair variety (small turns/offsets, some charcoal shells);
# (c) PIR motion sensors over the 4 hallway door pairs; lit EXIT sign inside over the front doors (code-typical, UNVERIFIED);
# cutaway aerial: floating LED strips / ceiling cans / 2F diffusers hidden at render time (no_render.py).
import bpy, bmesh, os, json, mathutils, math, random
SAVE=os.environ.get('SAVE')=='1'; REVERT=os.environ.get('REVERT')=='1'
CN='NO_CCOM_interior_wash_grid_signs_20261030no'
sc=bpy.context.scene
def revert():
    st=json.loads(sc.get('no_state','{}'))
    for n,m in st.get('mats',{}).items():
        o=bpy.data.objects.get(n)
        if o: o.matrix_world=mathutils.Matrix([m[i*4:(i+1)*4] for i in range(4)])
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
    for m in list(bpy.data.materials):
        if m.name.startswith('NO_') and m.users==0: bpy.data.materials.remove(m)
    for k in ('no_state','no_note'):
        if k in sc: del sc[k]
    bpy.context.view_layer.update()
if REVERT:
    revert(); bpy.ops.wm.save_mainfile(); raise SystemExit
revert()
state={'mats':{},'slots':{}}
col=bpy.data.collections.new(CN); sc.collection.children.link(col)
def tag(o,layer):
    o['msu_building']='School of Communication and Media'; o['msu_area']='ccom'; o['msu_layer']=layer
    o['msu_merge_role']='live'; o['msu_target_collection']='MSU_CCOM'; o['msu_tag_session']='no'
def mat(name,c,rough=0.6,emit=0.0,metal=0.0):
    m=bpy.data.materials.new(name); m.use_nodes=True; p=m.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value=c; p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal
    if emit: p.inputs['Emission Color'].default_value=c; p.inputs['Emission Strength'].default_value=emit
    return m
def addmesh(name,bm,m,layer,shadow=True):
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(m)
    ob=bpy.data.objects.new(name[:63],me); col.objects.link(ob); tag(ob,layer)
    if not shadow: ob.visible_shadow=False
    return ob
def boxbm(bm,x0,x1,y0,y1,z0,z1):
    r=bmesh.ops.create_cube(bm,size=1.0)
    for v in r['verts']: v.co=mathutils.Vector(((x0+x1)/2+v.co.x*(x1-x0),(y0+y1)/2+v.co.y*(y1-y0),(z0+z1)/2+v.co.z*(z1-z0)))
def box(name,x0,x1,y0,y1,z0,z1,m,layer,shadow=True):
    bm=bmesh.new(); boxbm(bm,x0,x1,y0,y1,z0,z1); return addmesh(name,bm,m,layer,shadow)
def cylo(name,x,y,z0,z1,r,m,layer,seg=16):
    bm=bmesh.new(); bmesh.ops.create_cone(bm,cap_ends=True,segments=seg,radius1=r,radius2=r,depth=z1-z0)
    bmesh.ops.translate(bm,verts=bm.verts,vec=(x,y,(z0+z1)/2)); o=addmesh(name,bm,m,layer); o.visible_shadow=False; return o
# ---------- (a) red-wall wash + stair-side accent (UNVERIFIED)
can=bpy.data.materials.get('NK_downlight_can_trim_UNVERIFIED'); lens=bpy.data.materials.get('NK_downlight_lens_warm_UNVERIFIED')
def wash(name,x,y,zc,energy,tilt_x,ang=44,tilt_y=0.0):
    ld=bpy.data.lights.new(name,'SPOT'); ld.energy=energy; ld.spot_size=math.radians(ang); ld.spot_blend=0.8; ld.color=(1.0,0.82,0.62); ld.shadow_soft_size=0.05
    lo=bpy.data.objects.new(name,ld); lo.location=(x,y,zc-0.04); lo.rotation_euler=(tilt_x,tilt_y,0); col.objects.link(lo); tag(lo,'light')
    if can: cylo(name+' can trim',x,y,zc-0.012,zc,0.09,can,'light')
    if lens: cylo(name+' can lens',x,y,zc-0.016,zc-0.012,0.065,lens,'light')
for i,x in enumerate((-19.0,-15.6,-10.2,-5.6)):
    wash('NO atrium red-wall washer %d'%i,x,8.4,145.96,900,-0.30)
for i,x in enumerate((-13.5,-10.0)):
    wash('NO atrium stair-side accent %d'%i,x,15.4,145.96,420,0.35,ang=40)
# ---------- (b) lay-in ceiling grid + chair variety
tee=mat('NO_ceiling_grid_tee_white_UNVERIFIED',(0.78,0.77,0.74,1),0.45)
def grid(name,x0,x1,y0,y1,zc):
    bm=bmesh.new(); w=0.012; s=0.6096
    x=x0+s/2
    while x<x1-0.05: boxbm(bm,x-w,x+w,y0+0.02,y1-0.02,zc-0.012,zc-0.001); x+=s
    y=y0+s/2
    while y<y1-0.05: boxbm(bm,x0+0.02,x1-0.02,y-w,y+w,zc-0.010,zc-0.002); y+=s
    return addmesh(name,bm,tee,'trim',shadow=False)
grid('NO N classroom lay-in ceiling grid 2x2 ft (UNVERIFIED)',-0.6,6.6,14.08,17.9,140.90)
grid('NO S office lay-in ceiling grid 2x2 ft (UNVERIFIED)',-0.2,7.6,3.40,6.92,140.90)
rng=random.Random(20261030)
char=mat('NO_room_chair_charcoal_grey_UNVERIFIED',(0.075,0.075,0.08,1),0.7)
seats=[o for o in bpy.data.objects if o.name.startswith(('NK N classroom chair','NK S office chair')) and o.name.endswith('seat')]
for k,s in enumerate(sorted(seats,key=lambda o:o.name)):
    back=bpy.data.objects.get(s.name[:-4]+'back')
    lo=[s.matrix_world@mathutils.Vector(c) for c in s.bound_box]; p=sum(lo,mathutils.Vector())/8.0
    ang=math.radians(rng.uniform(-14,14)); d=mathutils.Vector((rng.uniform(-0.06,0.06),rng.uniform(-0.05,0.05),0))
    T=mathutils.Matrix.Translation(p+d)@mathutils.Matrix.Rotation(ang,4,'Z')@mathutils.Matrix.Translation(-p)
    lx0,ly0=min(c.x for c in lo),min(c.y for c in lo); lx1,ly1=max(c.x for c in lo),max(c.y for c in lo); zb=min(c.z for c in lo)
    lbm=bmesh.new()
    for qx in (lx0+0.03,lx1-0.03):
        for qy in (ly0+0.03,ly1-0.03): boxbm(lbm,qx-0.011,qx+0.011,qy-0.011,qy+0.011,137.706,zb)
    lg=addmesh('NO chair legs (%s)'%s.name[3:],lbm,bpy.data.materials.get('NK_room_chair_black_UNVERIFIED') or char,'furniture'); lg.matrix_world=T@lg.matrix_world
    for o in (s,back):
        if not o: continue
        state['mats'][o.name]=[x for row in o.matrix_world for x in row]
        o.matrix_world=T@o.matrix_world
        if k%3==1:
            sl=o.material_slots[0]; state['slots'][o.name]=(sl.link,sl.material.name if (sl.link=='OBJECT' and sl.material) else None)
            sl.link='OBJECT'; sl.material=char
# ---------- (c) PIR sensors + EXIT sign
wht=mat('NO_sensor_white_plastic_UNVERIFIED',(0.82,0.82,0.80,1),0.4)
dome=mat('NO_sensor_lens_milky_UNVERIFIED',(0.9,0.9,0.88,1),0.25)
DOORS={'N':[(0.02,1.98),(4.02,5.98)],'S':[(0.52,2.48),(5.02,6.98)]}
for side,pairs in DOORS.items():
    for i,(x0,x1) in enumerate(pairs):
        xm=(x0+x1)/2
        y0,y1=(13.75,13.795) if side=='N' else (7.205,7.25)
        box('NO PIR sensor %s%d body'%(side,i),xm-0.09,xm+0.09,y0,y1,140.30,140.35,wht,'hardware')
        yl=(y0-0.012,y0) if side=='N' else (y1,y1+0.012)
        box('NO PIR sensor %s%d lens'%(side,i),xm-0.03,xm+0.03,yl[0],yl[1],140.31,140.34,dome,'hardware')
A,B=-22.930214,0.238365
def L(y,off=0.0): return A+B*y+off
red=mat('NO_exit_sign_red_LED_UNVERIFIED',(1.0,0.06,0.04,1),0.4,emit=6.0)
hous=mat('NO_exit_sign_housing_white_UNVERIFIED',(0.85,0.85,0.83,1),0.35)
yc=11.80; zc=140.62; th=-math.atan(B)
hb=bmesh.new(); boxbm(hb,-0.03,0.03,-0.165,0.165,-0.10,0.10); H=addmesh('NO EXIT sign housing over front doors (inside, UNVERIFIED)',hb,hous,'sign')
H.location=(L(yc,0.077),yc,zc); H.rotation_euler=(0,0,th)
for nm,xs in (('E',0.034),('W',-0.034)):
    cu=bpy.data.curves.new('NO_exit_txt_'+nm,'FONT'); cu.body='EXIT'; cu.size=0.115; cu.align_x='CENTER'; cu.align_y='CENTER'; cu.extrude=0.002
    t=bpy.data.objects.new('NO_exit_txt_tmp_'+nm,cu); col.objects.link(t)
    # text lies in local XY; stand it up facing +x (into atrium) or -x
    t.rotation_euler=(math.pi/2,0,math.pi/2 if nm=='E' else -math.pi/2)
    t.location=(xs,0,0); t.parent=H
    bpy.context.view_layer.update()
    dg=bpy.context.evaluated_depsgraph_get(); me=bpy.data.meshes.new_from_object(t.evaluated_get(dg))
    mw=t.matrix_world.copy(); bpy.data.objects.remove(t); bpy.data.curves.remove(cu)
    me.transform(mw); me.materials.clear(); me.materials.append(red)
    o=bpy.data.objects.new('NO EXIT sign letters %s face'%nm,me); col.objects.link(o); tag(o,'sign'); o.visible_shadow=False
# ---------- cameras
def cam(n,loc,tgt,lens_):
    c=bpy.data.cameras.new(n); c.lens=lens_; c.clip_start=0.05; o=bpy.data.objects.new(n,c); o.location=loc
    o.rotation_euler=(mathutils.Vector(tgt)-mathutils.Vector(loc)).to_track_quat('-Z','Y').to_euler(); col.objects.link(o); tag(o,'camera')
cam('NO_CAM_aerial_cutaway_atrium_oblique',(-3.0,-12.0,176.0),(-8.5,10.5,138.0),30)
cam('NO_CAM_eye_atrium_looking_W_doors_exit_red_wall',(-6.0,11.2,139.3),(-19.5,10.4,139.9),20)
cam('NO_CAM_eye_1F_open_floor_east_looking_west',(10.8,10.2,139.2),(-12,10.6,139.4),20)
cam('NO_CAM_closeup_N_classroom_grid_chairs',(5.0,13.95,139.45),(2.2,17.4,139.15),14)
sc['no_state']=json.dumps(state)
sc['no_note']='no: red-wall washers + stair accents, room ceiling grids + chair variety, PIR sensors, EXIT sign over the front doors; ALL UNVERIFIED'
print('NO objects',len(col.objects),'total',len(bpy.data.objects))
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
