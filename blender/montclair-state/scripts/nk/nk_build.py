# nk (Oct 30 2026, MAIN): CCOM interior per nj 'Next':
# (a) hallway maroon door pairs on the N/S 1F open-floor walls: real openings (Boolean) + satin glass + simple blocked-out rooms behind (N classroom, S office), UNVERIFIED;
# (b) warmer, more contrasty interior light: big NG area lights smaller/warmer/dimmer, warm spot downlights with ceiling cans, LED strips dimmer/warmer (UNVERIFIED);
# (c) door hardware: overhead closers + butt hinges on the hallway and red-wall door pairs (UNVERIFIED).
# Cutaway roof list for the aerial lives in nk_render.py (render-only, restored after each camera).
import bpy, bmesh, os, json, mathutils, math
SAVE=os.environ.get('SAVE')=='1'; REVERT=os.environ.get('REVERT')=='1'
CN='NK_CCOM_hallway_rooms_light_20261030nk'
sc=bpy.context.scene
def revert():
    st=json.loads(sc.get('nk_state','{}'))
    for mn,nn,inp,v in st.get('inputs',[]):
        m=bpy.data.materials.get(mn)
        if m: m.node_tree.nodes[nn].inputs[inp].default_value=v
    for n,(e,s,c) in st.get('lights',{}).items():
        o=bpy.data.objects.get(n)
        if o: o.data.energy=e; o.data.size=s; o.data.color=c
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
                if md.name.startswith('NK_'): o.modifiers.remove(md)
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
        if m.name.startswith('NK_') and m.users==0: bpy.data.materials.remove(m)
    for k in ('nk_state','nk_note'):
        if k in sc: del sc[k]
    bpy.context.view_layer.update()
if REVERT:
    revert(); bpy.ops.wm.save_mainfile(); raise SystemExit
revert()
state={'inputs':[],'lights':{},'slots':{},'mods':[]}
col=bpy.data.collections.new(CN); sc.collection.children.link(col)
def tag(o,layer):
    o['msu_building']='School of Communication and Media'; o['msu_area']='ccom'; o['msu_layer']=layer
    o['msu_merge_role']='live'; o['msu_target_collection']='MSU_CCOM'; o['msu_tag_session']='nk'
def setin(mn,inp,v,nn='Principled BSDF'):
    m=bpy.data.materials.get(mn)
    if not m: return
    i=m.node_tree.nodes[nn].inputs[inp]; old=i.default_value
    state['inputs'].append((mn,nn,inp,tuple(old) if hasattr(old,'__len__') else old)); i.default_value=v
def mat(name,col_,rough=0.6,emit=0.0,trans=0.0,metal=0.0):
    m=bpy.data.materials.new(name); m.use_nodes=True; p=m.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value=col_; p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal
    if emit: p.inputs['Emission Color'].default_value=col_; p.inputs['Emission Strength'].default_value=emit
    if trans: p.inputs['Transmission Weight'].default_value=trans
    return m
def box(name,x0,x1,y0,y1,z0,z1,m,layer,inward=False,shadow=True,open_y=None):
    me=bpy.data.meshes.new(name); bm=bmesh.new(); bmesh.ops.create_cube(bm,size=1.0)
    for v in bm.verts: v.co=mathutils.Vector(((x0+x1)/2+v.co.x*(x1-x0),(y0+y1)/2+v.co.y*(y1-y0),(z0+z1)/2+v.co.z*(z1-z0)))
    if open_y is not None:   # leave the door-side face out (the hallway wall closes it)
        bmesh.ops.delete(bm,geom=[f for f in bm.faces if abs(f.calc_center_median().y-open_y)<1e-4 and abs(f.normal.y)>0.9],context='FACES')
    if inward: bmesh.ops.reverse_faces(bm,faces=bm.faces)
    bm.to_mesh(me); bm.free(); me.materials.append(m); ob=bpy.data.objects.new(name[:63],me); col.objects.link(ob); tag(ob,layer)
    if not shadow: ob.visible_shadow=False
    return ob
def cyl(name,x,y,z0,z1,r,m,layer,seg=16):
    me=bpy.data.meshes.new(name); bm=bmesh.new()
    bmesh.ops.create_cone(bm,cap_ends=True,segments=seg,radius1=r,radius2=r,depth=z1-z0)
    bmesh.ops.translate(bm,verts=bm.verts,vec=(x,y,(z0+z1)/2)); bm.to_mesh(me); bm.free(); me.materials.append(m)
    ob=bpy.data.objects.new(name[:63],me); col.objects.link(ob); tag(ob,layer); return ob
def setslots(o,mats):
    state['slots'][o.name]=[(s.link,(s.material.name if (s.link=='OBJECT' and s.material) else None)) for s in o.material_slots]
    for s in o.material_slots:
        if s.link=='OBJECT' and s.material and not s.material.use_fake_user:
            s.material.use_fake_user=True; state.setdefault('fake_mats',[]).append(s.material.name)
    for s,m in zip(o.material_slots,mats): s.link='OBJECT'; s.material=m
def boolean(target,cutter,tagname):
    w=bpy.data.objects.get(target)
    if not w: print('NK missing',target); return
    md=w.modifiers.new(tagname,'BOOLEAN'); md.object=cutter; md.operation='DIFFERENCE'; md.solver='EXACT'
    if target not in state['mods']: state['mods'].append(target)
WHITE=bpy.data.materials['NG_wall_white']; TERR=bpy.data.materials['NG_terrazzo_1F_open_floor']
# ---------------- (a) hallway door openings + satin glass + rooms behind
DOORS={'N':[(0.02,1.98),(4.02,5.98)],'S':[(0.52,2.48),(5.02,6.98)]}
WALL={'N':'NG 1F hallway N wall','S':'NG 1F hallway S wall red'}
YC={'N':(13.80,14.20),'S':(6.80,7.20)}
satin=mat('NK_hallway_door_glass_satin_UNVERIFIED',(0.95,0.95,0.94,1),rough=0.11,trans=1.0)
for side,pairs in DOORS.items():
    for i,(x0,x1) in enumerate(pairs):
        c=box('NK %s door opening cutter %d (hidden)'%(side,i),x0+0.14,x1-0.14,YC[side][0],YC[side][1],137.80,140.04,WHITE,'cutter')
        c.hide_render=True; c.display_type='BOUNDS'
        boolean(WALL[side],c,'NK_door_opening_%s%d'%(side,i))
        boolean('NG hallway %s maroon doors %d frame'%(side,i),c,'NK_door_opening_%s%d'%(side,i))
        g=bpy.data.objects.get('NG hallway %s maroon doors %d frosted glass'%(side,i))
        if g: setslots(g,[satin])
        if side=='N':
            k=box('NK N skirting cutter %d (hidden)'%i,x0+0.14,x1-0.14,13.80,13.95,137.65,137.90,WHITE,'cutter'); k.hide_render=True; k.display_type='BOUNDS'
            boolean('NH hallway N wall skirting',k,'NK_skirting_gap_%d'%i)
roomw=mat('NK_room_wall_warm_white_UNVERIFIED',(0.66,0.64,0.60,1),0.8)
carpet=mat('NK_room_carpet_charcoal_blue_UNVERIFIED',(0.05,0.06,0.075,1),0.95)
tabl=mat('NK_room_table_top_light_oak_UNVERIFIED',(0.45,0.33,0.20,1),0.45)
chair=mat('NK_room_chair_black_UNVERIFIED',(0.02,0.02,0.022,1),0.6)
wb=mat('NK_room_whiteboard_UNVERIFIED',(0.85,0.86,0.86,1),0.12)
pan=mat('NK_room_led_panel_UNVERIFIED',(1.0,0.95,0.88,1),0.5,emit=3.0)
def lamp(name,loc,energy,size,color=(1,0.9,0.78)):
    ld=bpy.data.lights.new(name,'AREA'); ld.energy=energy; ld.size=size; ld.color=color
    lo=bpy.data.objects.new(name,ld); lo.location=loc; col.objects.link(lo); tag(lo,'light'); return lo
# N classroom: x -0.6..6.6, y 14.11..17.9 (nothing else there per ray probe), ceiling 140.90
box('NK N classroom room shell (inward, UNVERIFIED)',-0.6,6.6,14.08,17.9,137.69,140.90,roomw,'room',inward=True,open_y=14.08)
box('NK N classroom floor carpet (UNVERIFIED)',-0.58,6.58,14.09,17.88,137.68,137.705,carpet,'floor')
box('NK N classroom whiteboard (UNVERIFIED)',0.6,5.4,17.86,17.88,138.55,139.75,wb,'trim')
for r,yr in enumerate((15.3,16.6)):
    for k,xt in enumerate((0.6,3.0,5.4)):
        box('NK N classroom table r%d t%d'%(r,k),xt-0.9,xt+0.9,yr-0.30,yr+0.30,138.42,138.46,tabl,'furniture')
        for dx in (-0.45,0.45):
            box('NK N classroom chair r%d t%d %+.2f seat'%(r,k,dx),xt+dx-0.22,xt+dx+0.22,yr-0.78,yr-0.36,138.10,138.16,chair,'furniture')
            box('NK N classroom chair r%d t%d %+.2f back'%(r,k,dx),xt+dx-0.22,xt+dx+0.22,yr-0.82,yr-0.78,138.16,138.62,chair,'furniture')
        box('NK N classroom table r%d t%d legs'%(r,k),xt-0.85,xt+0.85,yr-0.02,yr+0.02,137.705,138.42,chair,'furniture')
for k,xc in enumerate((1.0,4.2)):
    box('NK N classroom LED panel %d'%k,xc-0.6,xc+0.6,15.4,16.6,140.88,140.895,pan,'light',shadow=False)
    lamp('NK N classroom light %d'%k,(xc,16.0,140.85),200,1.0)
# S office/meeting room: x -0.2..7.6, y 3.4..6.89, ceiling 140.90
box('NK S office room shell (inward, UNVERIFIED)',-0.2,7.6,3.40,6.92,137.69,140.90,roomw,'room',inward=True,open_y=6.92)
box('NK S office floor carpet (UNVERIFIED)',-0.18,7.58,3.42,6.90,137.68,137.705,carpet,'floor')
box('NK S office meeting table',1.6,5.8,4.55,5.55,138.42,138.46,tabl,'furniture')
box('NK S office meeting table base',3.4,4.0,4.95,5.15,137.705,138.42,chair,'furniture')
for j,xc in enumerate((2.1,3.2,4.3,5.4)):
    for side,(ys,yb) in enumerate(((4.12,3.95),(5.98,6.15))):
        box('NK S office chair %d%d seat'%(j,side),xc-0.24,xc+0.24,min(ys,ys+(0.42 if side==0 else -0.42)),max(ys,ys+(0.42 if side==0 else -0.42)),138.10,138.16,chair,'furniture')
        box('NK S office chair %d%d back'%(j,side),xc-0.24,xc+0.24,min(yb,yb+0.05),max(yb,yb+0.05),138.16,138.70,chair,'furniture')
box('NK S office wall screen (UNVERIFIED)',3.0,4.8,3.42,3.45,138.6,139.6,chair,'trim')
for k,xc in enumerate((2.2,5.4)):
    box('NK S office LED panel %d'%k,xc-0.6,xc+0.6,4.55,5.75,140.88,140.895,pan,'light',shadow=False)
    lamp('NK S office light %d'%k,(xc,5.15,140.85),200,1.0)
vo=next((o for o in bpy.data.objects if o.name.startswith('NJ vestibule behind red-wall doors (room shell')),None)
if vo:
    om=vo.data; cp=om.copy(); cp.name=om.name+'_nk'; bm=bmesh.new(); bm.from_mesh(cp); M=vo.matrix_world
    kill=[f for f in bm.faces if abs((M@f.calc_center_median()).y-6.08)<1e-3]
    bmesh.ops.delete(bm,geom=kill,context='FACES'); bm.to_mesh(cp); bm.free()
    state['mesh_swap']={vo.name:(om.name,om.use_fake_user)}; om.use_fake_user=True; vo.data=cp; print('NK vestibule N face removed',len(kill))
# ---------------- (b) warmer, more contrasty light (UNVERIFIED)
WARM=(1.0,0.86,0.70)
def relight(n,f_e,size,color=WARM):
    o=bpy.data.objects.get(n)
    if not o: print('NK missing light',n); return
    state['lights'][n]=(o.data.energy,o.data.size,tuple(o.data.color)); o.data.energy=round(o.data.energy*f_e,2); o.data.size=size; o.data.color=color
relight('NG atrium area light A',0.22,1.6); relight('NG atrium area light B',0.22,1.6)
relight('NG 1F hallway light 0',0.25,1.0); relight('NG 1F hallway light 1',0.25,1.0)
relight('NG double-height light',0.6,2.0); relight('NG connector light 0',0.6,1.2); relight('NG connector light 1',0.6,1.2)
setin('NG_led_strip','Emission Strength',1.7)
can=mat('NK_downlight_can_trim_UNVERIFIED',(0.8,0.8,0.8,1),0.35,metal=0.6)
lens=mat('NK_downlight_lens_warm_UNVERIFIED',(1.0,0.85,0.66,1),0.4,emit=12.0)
def spot(name,x,y,zc,energy,ang=62):
    ld=bpy.data.lights.new(name,'SPOT'); ld.energy=energy; ld.spot_size=math.radians(ang); ld.spot_blend=0.55; ld.color=(1.0,0.84,0.66); ld.shadow_soft_size=0.06
    lo=bpy.data.objects.new(name,ld); lo.location=(x,y,zc-0.04); col.objects.link(lo); tag(lo,'light')
    t=cyl(name+' can trim',x,y,zc-0.012,zc,0.10,can,'light'); t.visible_shadow=False
    l=cyl(name+' can lens',x,y,zc-0.016,zc-0.012,0.075,lens,'light'); l.visible_shadow=False
# atrium ceiling ~146.0 (LED strips at 145.97); hallway ceiling 141.45; double-height 145
for i,(x,y) in enumerate([(-17.0,9.8),(-13.0,9.8),(-9.0,9.8),(-17.0,12.9),(-12.0,12.0),(-8.0,12.0)]):
    spot('NK atrium downlight %d'%i,x,y,145.96,1100,38)
for i,x in enumerate((-1.2,1.0,3.0,5.2,7.4)):
    spot('NK hallway downlight %d'%i,x,10.5 if i%2==0 else 10.1,141.44,380,44)
# ---------------- (c) door hardware: overhead closers + hinges on hallway + red-wall pairs (UNVERIFIED)
alu=mat('NK_door_closer_satin_aluminium_UNVERIFIED',(0.55,0.55,0.56,1),0.35,metal=0.9)
hin=mat('NK_door_hinge_satin_stainless_UNVERIFIED',(0.62,0.62,0.63,1),0.3,metal=1.0)
pairs=[('N',x0,x1,13.85,-1) for (x0,x1) in DOORS['N']]+[('S',x0,x1,7.15,1) for (x0,x1) in DOORS['S']]+[('R',x0,x1,6.32,1) for (x0,x1) in [(-13.48,-11.52),(-8.98,-7.02)]]
for k,(side,x0,x1,yf,dirn) in enumerate(pairs):
    xm=(x0+x1)/2
    for leaf,(xa,xb) in enumerate(((x0+0.12,xm-0.03),(xm+0.03,x1-0.12))):
        # closer body on the corridor face of the top rail, arm along the head
        hingeside= xa if leaf==0 else xb
        cx= xa+0.12 if leaf==0 else xb-0.40
        y0,y1=(yf+dirn*0.004,yf+dirn*0.062) if dirn>0 else (yf-0.062,yf-0.004)
        box('NK door closer %s%d L%d body'%(side,k,leaf),cx,cx+0.28,min(y0,y1),max(y0,y1),139.86,139.93,alu,'hardware')
        ya,yb=(yf+dirn*0.02,yf+dirn*0.04) if dirn>0 else (yf-0.04,yf-0.02)
        ax0= cx+0.05 if leaf==0 else cx-0.22; 
        box('NK door closer %s%d L%d arm'%(side,k,leaf),ax0,ax0+0.45,min(ya,yb),max(ya,yb),139.95,139.97,alu,'hardware')
        for z in (137.98,138.95,139.85):
            hx=hingeside-0.012 if leaf==0 else hingeside+0.012
            y0h,y1h=(yf+dirn*0.002,yf+dirn*0.016) if dirn>0 else (yf-0.016,yf-0.002)
            box('NK door hinge %s%d L%d z%.2f'%(side,k,leaf,z),hx-0.012,hx+0.012,min(y0h,y1h),max(y0h,y1h),z,z+0.11,hin,'hardware')
# ---------------- cameras
def cam(n,loc,tgt,lens_):
    c=bpy.data.cameras.new(n); c.lens=lens_; c.clip_start=0.05; o=bpy.data.objects.new(n,c); o.location=loc
    o.rotation_euler=(mathutils.Vector(tgt)-mathutils.Vector(loc)).to_track_quat('-Z','Y').to_euler(); col.objects.link(o); tag(o,'camera')
cam('NK_CAM_aerial_cutaway_atrium_oblique',(-3.0,-12.0,176.0),(-8.5,10.5,138.0),30)
cam('NK_CAM_eye_atrium_entry_looking_east',(-18.6,9.4,139.25),(4,11.2,139.0),20)
cam('NK_CAM_eye_hallway_looking_east_doors',(-3.6,8.0,139.2),(9,12.8,138.9),20)
cam('NK_CAM_closeup_hallway_N_doors_room_behind',(1.4,10.4,139.0),(1.4,16.5,138.8),24)
sc['nk_state']=json.dumps(state)
sc['nk_note']='nk: hallway door openings + satin glass + blocked-out N classroom / S office behind, warmer contrasty light (smaller/dimmer area lights, warm spot downlights), door closers + hinges; ALL UNVERIFIED'
print('NK objects',len(col.objects),'total',len(bpy.data.objects))
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
