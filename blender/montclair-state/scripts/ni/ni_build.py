# ni (Oct 30 2026): CCOM front entrance doors rebuilt per Joe 10:49 AM + usgbc_03/epic_01 photos:
# single clear glass pane per leaf (no crossbars), window mullions stopped above a solid maroon transom (photo), inside push bar + outside pull per leaf.
import bpy, bmesh, os, json, mathutils
SAVE=os.environ.get('SAVE')=='1'; REVERT=os.environ.get('REVERT')=='1'
CN='NI_CCOM_front_doors_single_pane_20261030ni'
sc=bpy.context.scene
A,B=-22.930214,0.238365
def L(y,off=0.0): return A+B*y+off
VM=['CCOM atrium mullion v%d'%i for i in range(6)]
HIDE=['CCOM atrium mullion h6','CCOM atrium mullion h7']+['CCOM push bar %s'%s for s in ('+1-0.47','+10.47','-1-0.47','-10.47')]
def revert():
    st=json.loads(sc.get('ni_state','{}'))
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
    for n,e in st.get('light_energy',{}).items():
        o=bpy.data.objects.get(n)
        if o: o.data.energy=e
    for n,v in st.get('mat_emit',{}).items():
        m=bpy.data.materials.get(n)
        if m: m.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value=v
    for n,v in st.get('vis_glossy',{}).items():
        o=bpy.data.objects.get(n)
        if o: o.visible_glossy=v
    c=bpy.data.collections.get(CN)
    if c:
        for o in list(c.objects):
            d=o.data; bpy.data.objects.remove(o)
            if d and d.users==0:
                (bpy.data.meshes if isinstance(d,bpy.types.Mesh) else bpy.data.cameras).remove(d)
        bpy.data.collections.remove(c)
    for m in list(bpy.data.materials):
        if m.name.startswith('NI_') and m.users==0: bpy.data.materials.remove(m)
    for k in ('ni_state','ni_note'):
        if k in sc: del sc[k]
    bpy.context.view_layer.update()
if REVERT:
    revert(); bpy.ops.wm.save_mainfile(); raise SystemExit
revert()
state={'hidden':{},'verts':{},'slots':{},'light_energy':{},'mat_emit':{},'vis_glossy':{}}
col=bpy.data.collections.new(CN); sc.collection.children.link(col)
def tag(o,layer):
    o['msu_building']='School of Communication and Media'; o['msu_area']='ccom'; o['msu_layer']=layer
    o['msu_merge_role']='live'; o['msu_target_collection']='MSU_CCOM'; o['msu_tag_session']='ni'
mar=bpy.data.materials['Mullion_mahogany']; steel=bpy.data.materials.get('Push_bar_steel')
DOOR_HEAD=140.29; TR_TOP=141.06   # door head frame top (existing 'CCOM door frame +-1') ; top of window mullion h9
# 1) window vertical mullions v0..v5 no longer run down through the door leaves: bottom verts lifted to the top of h9 (transom top)
for n in VM:
    o=bpy.data.objects[n]; keep=[]; Mw=o.matrix_world; Mi=Mw.inverted()
    zs=sorted(set(round((Mw@v.co).z,4) for v in o.data.vertices)); zmin=zs[0]
    for v in o.data.vertices:
        w=Mw@v.co
        if abs(w.z-zmin)<1e-3:
            keep.append((v.index,tuple(v.co))); w.z=TR_TOP; v.co=Mi@w
    o.data.update(); state['verts'][n]=keep
# 2) hide the window's horizontal bars h6/h7 (they crossed every door leaf) + the old outside-mounted push bars
for n in HIDE:
    o=bpy.data.objects.get(n)
    if o: state['hidden'][n]=(o.hide_render,o.hide_viewport); o.hide_render=True; o.hide_viewport=True
def prism(name,poly,z0,z1,m,layer):
    me=bpy.data.meshes.new(name); bm=bmesh.new()
    lo=[bm.verts.new((x,y,z0)) for x,y in poly]; hi=[bm.verts.new((x,y,z1)) for x,y in poly]
    bm.faces.new(lo[::-1]); bm.faces.new(hi); k=len(poly)
    for i in range(k): bm.faces.new([lo[i],lo[(i+1)%k],hi[(i+1)%k],hi[i]])
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(me); bm.free(); me.materials.append(m)
    ob=bpy.data.objects.new(name,me); col.objects.link(ob); tag(ob,layer); return ob
def strip(name,y0,y1,o0,o1,z0,z1,m,layer):
    return prism(name,[(L(y0,o0),y0),(L(y1,o0),y1),(L(y1,o1),y1),(L(y0,o1),y0)],z0,z1,m,layer)
# 3) short h6/h7 stubs only in the fixed glass outside the door assembly (arch edge -> outer door stile), so the window rows still read there
for zc,nm in ((138.47,'h6'),(139.32,'h7')):
    strip('NI window bar %s stub S (outside doors)'%nm,9.31,9.60,-0.06,0.06,zc-0.03,zc+0.03,mar,'mullion')
    strip('NI window bar %s stub N (outside doors)'%nm,14.01,14.29,-0.06,0.06,zc-0.03,zc+0.03,mar,'mullion')
# 4) solid maroon transom panel over the doors (usgbc_03 / epic_01 photos show an opaque red panel band between door heads and the glazing), with a mid reveal and joints at the door stiles
strip('NI door transom panel (maroon, photo usgbc_03)',9.60,14.01,-0.045,0.045,DOOR_HEAD-0.005,TR_TOP-0.03,mar,'door')
dk=bpy.data.materials.new('NI_transom_reveal_dark'); dk.use_nodes=True; dk.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(0.06,0.02,0.02,1)
strip('NI transom mid reveal OUT',9.62,13.99,-0.052,-0.044,140.655,140.67,dk,'door'); strip('NI transom mid reveal IN',9.62,13.99,0.044,0.052,140.655,140.67,dk,'door')
for y in (10.59,11.515,12.095,13.025):
    strip('NI transom joint OUT y%.2f'%y,y-0.006,y+0.006,-0.052,-0.044,DOOR_HEAD,TR_TOP-0.035,dk,'door')
    strip('NI transom joint IN y%.2f'%y,y-0.006,y+0.006,0.044,0.052,DOOR_HEAD,TR_TOP-0.035,dk,'door')
strip('NI door head frame centre (fixed panel between pairs)',11.515,12.095,-0.07,0.07,140.16,140.29,mar,'door')
# 5) per leaf: ONE horizontal push bar on the INSIDE (Joe) + one vertical pull on the OUTSIDE at the meeting stile (photo usgbc_03 shows pulls)
legs=[(9.665,10.59,'L'),(10.59,11.515,'R'),(12.095,13.025,'L'),(13.025,13.945,'R')]
st=steel or mar
for i,(a,b,side) in enumerate(legs):
    y0,y1=a+0.10,b-0.10
    strip('NI door leaf %d push bar (inside)'%i,y0,y1,0.075,0.105,138.60,138.64,st,'door')
    for yb in (y0+0.03,y1-0.03):
        strip('NI door leaf %d push bar bracket y%.2f'%(i,yb),yb-0.02,yb+0.02,0.02,0.105,138.585,138.655,st,'door')
    yp=(b-0.12) if side=='L' else (a+0.12)
    strip('NI door leaf %d outside pull'%i,yp-0.012,yp+0.012,-0.115,-0.09,138.35,138.95,st,'door')
    for zp in (138.38,138.92):
        strip('NI door leaf %d pull standoff z%.2f'%(i,zp),yp-0.01,yp+0.01,-0.10,-0.02,zp-0.01,zp+0.01,st,'door')
# 7) mirrored "R ST" ghost text near the stair top = the LED sign reflected in the NG stair S glass rail (ni test: gone with the rails hidden, rail still reflects with the sign hidden).
#    The sign is made invisible to glossy rays only (direct view + its light on the bridge unchanged).
SIGN='NG bridge LED sign MONTCLAIR STATE UNIVERSITY'
so=bpy.data.objects.get(SIGN)
if so: state['vis_glossy'][SIGN]=so.visible_glossy; so.visible_glossy=False
# 8) interior light levels down so the materials read (NG area lights x0.55, LED strip emission 6 -> 3.5)
for o in bpy.data.objects:
    if o.type=='LIGHT' and o.name.startswith('NG '):
        state['light_energy'][o.name]=o.data.energy; o.data.energy=round(o.data.energy*0.55,2)
lm=bpy.data.materials.get('NG_led_strip')
if lm:
    P=lm.node_tree.nodes['Principled BSDF']; state['mat_emit']['NG_led_strip']=P.inputs['Emission Strength'].default_value; P.inputs['Emission Strength'].default_value=3.5
# 6) cameras
def cam(n,loc,tgt,lens):
    c=bpy.data.cameras.new(n); c.lens=lens; c.clip_start=0.05; ob=bpy.data.objects.new(n,c); ob.location=loc
    ob.rotation_euler=(mathutils.Vector(tgt)-mathutils.Vector(loc)).to_track_quat('-Z','Y').to_euler(); col.objects.link(ob); tag(ob,'camera')
mid=11.80
cam('NI_CAM_aerial_front_oblique',(-52,-8,162),(-15,11,141),30)
cam('NI_CAM_eye_outside_front_doors',(L(mid,-9.0),mid+2.1,139.3),(L(mid,0),mid,140.0),24)
cam('NI_CAM_closeup_front_doors_straight',(L(mid,-4.4),mid+1.05,138.95),(L(mid,0),mid,139.1),28)
cam('NI_CAM_eye_atrium_looking_west_to_doors',(-8.5,10.2,139.3),(-20.3,11.6,139.6),20)
sc['ni_state']=json.dumps(state)
sc['ni_note']='ni: CCOM front doors = single clear pane per leaf (window mullions stop above a maroon transom, h6/h7 hidden), inside push bar + outside pull per leaf; ALL sizes UNVERIFIED'
print('NI objects',len(col.objects),'total',len(bpy.data.objects))
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
