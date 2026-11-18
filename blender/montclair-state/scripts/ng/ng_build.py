import mathutils
# ng (Oct 30 2026): CCOM 1F open floor + atrium stair/bridge + 2F east balcony + back hallway. ALL UNVERIFIED blockout.
import bpy, bmesh, os, math, mathutils, json
SAVE=os.environ.get('SAVE')=='1'; REVERT=os.environ.get('REVERT')=='1'
CN='NG_CCOM_1F_open_floor_20261030ng'
HIDE=['CCOM_int_lounge_accent_red_20261014v','CCOM_int_office_L1_20261014v','CCOM_int_office_ceil_20261014v',
 'CCOM_int_partition_glass_20261014v']+['CCOM_int_partition_m%s%d_20261014v'%(a,i) for a in 'hv' for i in range(5)]+\
 ['CCOM_lounge_east_wallW_20261014jf','CCOM_lounge_east_wallN_20261014jf','dc_base_N','dc_base_W']
sc=bpy.context.scene
def revert():
    st=json.loads(sc.get('ng_hidden','{}'))
    for n,(hr,hv) in st.items():
        o=bpy.data.objects.get(n)
        if o: o.hide_render=hr; o.hide_viewport=hv
    c=bpy.data.collections.get(CN)
    if c:
        for o in list(c.objects):
            d=o.data; bpy.data.objects.remove(o)
            if d and d.users==0:
                (bpy.data.meshes if isinstance(d,bpy.types.Mesh) else bpy.data.lights if isinstance(d,bpy.types.Light) else bpy.data.cameras).remove(d)
        bpy.data.collections.remove(c)
    for m in list(bpy.data.materials):
        if m.name.startswith('NG_') and m.users==0: bpy.data.materials.remove(m)
    for k in ('ng_hidden','ng_note'):
        if k in sc: del sc[k]
if REVERT:
    revert(); bpy.ops.wm.save_mainfile(); raise SystemExit
revert()
col=bpy.data.collections.new(CN); sc.collection.children.link(col)
def mat(n,c,rough=0.5,emit=0,trans=0,alpha=1,wave=None,noise=None):
    m=bpy.data.materials.new('NG_'+n); m.use_nodes=True; p=m.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value=(*c,1); p.inputs['Roughness'].default_value=rough
    if emit: p.inputs['Emission Color'].default_value=(*c,1); p.inputs['Emission Strength'].default_value=emit
    if trans: p.inputs['Transmission Weight'].default_value=trans
    if alpha<1: p.inputs['Alpha'].default_value=alpha; m.blend_method='BLEND' if hasattr(m,'blend_method') else None
    nt=m.node_tree
    if noise:
        tc=nt.nodes.new('ShaderNodeTexCoord'); nz=nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=noise
        ramp=nt.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].color=(c[0]*0.82,c[1]*0.82,c[2]*0.82,1); ramp.color_ramp.elements[1].color=(min(1,c[0]*1.08),min(1,c[1]*1.08),min(1,c[2]*1.08),1)
        nt.links.new(tc.outputs['Object'],nz.inputs['Vector']); nt.links.new(nz.outputs['Fac'],ramp.inputs['Fac']); nt.links.new(ramp.outputs['Color'],p.inputs['Base Color'])
    if wave:
        tc=nt.nodes.new('ShaderNodeTexCoord'); wv=nt.nodes.new('ShaderNodeTexWave'); wv.inputs['Scale'].default_value=wave[0]; wv.inputs['Distortion'].default_value=wave[1]
        ramp=nt.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].color=(*wave[2],1); ramp.color_ramp.elements[1].color=(*c,1)
        nt.links.new(tc.outputs['Object'],wv.inputs['Vector']); nt.links.new(wv.outputs['Fac'],ramp.inputs['Fac']); nt.links.new(ramp.outputs['Color'],p.inputs['Base Color'])
    return m
M=dict(terr=mat('terrazzo_1F_open_floor',(0.80,0.79,0.76),0.25,noise=60),
 wall=mat('wall_white',(0.86,0.86,0.84),0.7), red=mat('red_wall',(0.55,0.06,0.07),0.6),
 maroon=mat('maroon_frame',(0.28,0.04,0.05),0.35), frost=mat('frosted_glass',(0.85,0.85,0.86),0.35,trans=0.0),
 glass=mat('rail_glass',(0.9,0.95,0.95),0.02,trans=1.0), dark=mat('room_glass_dark',(0.05,0.06,0.07),0.05),
 wood=mat('wood_cladding',(0.45,0.25,0.11),0.45,wave=(3.0,4.0,(0.32,0.17,0.07))), tread=mat('stair_tread',(0.72,0.71,0.68),0.4),
 ceil=mat('ceiling_white',(0.9,0.9,0.9),0.8), led=mat('led_strip',(1,0.97,0.92),0.5,emit=6), steel=mat('steel',(0.6,0.6,0.62),0.3),
 sign_bg=mat('sign_panel_dark',(0.04,0.03,0.05),0.3), sign_led=mat('sign_led_white',(1,1,1),0.3,emit=8),
 day=mat('daylight_behind_east_glass_UNVERIFIED',(0.85,0.92,1.0),0.5,emit=3.5),
 org=mat('ottoman_orange',(0.85,0.32,0.06),0.8), yel=mat('ottoman_yellow',(0.9,0.68,0.05),0.8), redo=mat('ottoman_red',(0.6,0.08,0.08),0.8),
 chev=mat('chevron_bench_blue',(0.12,0.25,0.55),0.8,wave=(6.0,0.0,(0.75,0.78,0.85))), white=mat('table_white',(0.93,0.93,0.92),0.3))
objs=[]
def tag(o,layer):
    o['msu_building']='School of Communication and Media'; o['msu_area']='ccom'; o['msu_layer']=layer
    o['msu_merge_role']='live'; o['msu_target_collection']='MSU_CCOM'; o['msu_tag_session']='ng'
def box(name,x0,x1,y0,y1,z0,z1,m,layer='interior'):
    me=bpy.data.meshes.new(name); bm=bmesh.new()
    r=bmesh.ops.create_cube(bm,size=1.0); bmesh.ops.scale(bm,vec=(x1-x0,y1-y0,z1-z0),verts=bm.verts)
    bmesh.ops.translate(bm,vec=((x0+x1)/2,(y0+y1)/2,(z0+z1)/2),verts=bm.verts); bm.to_mesh(me); bm.free()
    me.materials.append(m); o=bpy.data.objects.new(name,me); col.objects.link(o); tag(o,layer); objs.append(o); return o
# floor level: terrain pokes through at ~137.48-137.64 inside -> F = max terrain under atrium+hallway + 4 cm
_dg=bpy.context.evaluated_depsgraph_get(); _T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; _mx=137.41
for _x in [i*0.5 for i in range(-39,31)]:
    for _y in [j*0.5 for j in range(12,34)]:
        if _x>-2.2 and not (7.0<=_y<=14.0): continue
        _h=sc.ray_cast(_dg,mathutils.Vector((_x,_y,139.5)),mathutils.Vector((0,0,-1)))
        if _h[0] and _h[4]==_T: _mx=max(_mx,_h[1].z)
F=round(_mx+0.04,3); print('TERRAIN_MAX',_mx,'F',F)
F2B=141.45; F2=141.85; C2=144.9; CA=146.0; C1=141.50; FL=137.415
# floors
box('NG 1F open floor atrium terrazzo',-19.55,-2.2,6.2,16.6,F-0.2,F,M['terr'],'floor')
box('NG 1F open floor hallway terrazzo',-2.2,8.5,7.0,14.0,F-0.2,F,M['terr'],'floor'); box('NG 1F open floor east double-height terrazzo',8.5,12.2,7.0,13.3,F-0.2,F,M['terr'],'floor')
_c=box('NG 1F open floor connector terrazzo (gentle 1.5% slope down to the east-window seating)',9.5,14.6,-13.6,7.0,FL-0.2,FL,M['terr'],'floor')
for v in _c.data.vertices:
    if v.co.y>0: v.co.z+= (F-FL)
box('NG 1F south rooms floor blockout UNVERIFIED',-2.18,9.48,-13.58,6.98,F-0.25,F-0.03,M['wall'],'floor')
box('NG 1F open floor link to east windows terrazzo',14.6,21.0,-16.9,-13.6,FL-0.2,FL,M['terr'],'floor')
# 2F slabs
box('NG 2F hallway slab',-2.2,8.5,7.0,14.0,F2B,F2,M['terr'],'floor')
box('NG 2F hallway slab soffit',-2.2,8.5,7.0,14.0,F2B-0.01,F2B,M['ceil'],'ceiling')
box('NG atrium bridge slab',-5.2,-2.2,6.2,16.6,F2B,F2,M['terr'],'floor')
box('NG stair top landing',-7.5,-5.2,13.5,16.6,F2B,F2,M['terr'],'floor')
box('NG 2F back hallway (dips left to CCM old offices) slab',5.5,8.5,14.0,22.0,F2B,F2,M['terr'],'floor')
box('NG bridge fascia wood',-5.24,-5.2,6.2,16.6,F2B-0.5,F2+0.02,M['wood'])
# walls
t=0.15
def wy(n,y,x0,x1,z0,z1,m): return box(n,x0,x1,y-t/2,y+t/2,z0,z1,m,'wall')
def wx(n,x,y0,y1,z0,z1,m): return box(n,x-t/2,x+t/2,y0,y1,z0,z1,m,'wall')
wy('NG 1F hallway S wall red',7.0,-2.2,8.5,F,F2B,M['red'])
wy('NG 1F hallway S wall red W pier',7.0,8.5,9.5,F,C2,M['red']); wy('NG connector N end wall (behind east facade)',7.0,12.2,14.6,FL,C1,M['wall'])
wy('NG double-height S wall over connector',7.0,9.5,12.2,C1,C2,M['wall'])
wy('NG 1F hallway N wall',14.0,-2.2,8.5,F,F2B,M['wall']); wy('NG double-height N wall',13.3,8.5,12.2,F,C2,M['wall']); wx('NG double-height NW jog wall',8.5,13.3,14.0,F,C2,M['wall'])
wx('NG atrium E wall S pier',-2.2,6.2,7.0,F,CA,M['red']); wx('NG atrium E wall N pier',-2.2,14.0,16.6,F,CA,M['wall'])
wx('NG atrium E wall over 2F opening',-2.2,7.0,14.0,C2,CA,M['wall'])
wy('NG atrium N wall (tower face)',16.6,-19.55,-2.2,F,CA,M['wall']); wy('NG atrium S wall filler',6.2,-19.55,-16.75,F,CA,M['wall'])
box('NG atrium S wall red panel',-16.0,-2.3,6.22,6.25,F,F2B-0.05,M['red'],'wall')
wy('NG 2F hallway S wall',7.0,-2.2,8.5,F2,C2,M['wall']); wy('NG 2F hallway N wall W',14.0,-2.2,5.5,F2,C2,M['wall'])
wx('NG 2F back hallway W wall',5.5,14.0,22.0,F2,C2,M['wall']); wx('NG 2F back hallway E wall',8.5,14.0,22.0,F2,C2,M['wall'])
wy('NG 2F back hallway end wall (CCM old offices)',22.0,5.5,8.5,F2,C2,M['wall'])
box('NG 2F hallway ceiling',-2.2,8.5,7.0,14.0,C2,C2+0.1,M['ceil'],'ceiling'); box('NG double-height ceiling',8.5,12.2,7.0,13.3,C2,C2+0.1,M['ceil'],'ceiling'); box('NG 2F back hallway ceiling',5.5,8.5,14.0,22.0,C2,C2+0.1,M['ceil'],'ceiling')
wx('NG connector W wall',9.5,-13.6,7.0,FL,C1,M['wall']); wx('NG connector E wall',14.6,-13.6,7.0,FL,C1,M['wall'])
wy('NG link N wall',-13.6,14.6,21.0,FL,C1,M['wall']); wx('NG link E wall',21.0,-16.9,-13.6,FL,C1,M['wall'])
box('NG connector ceiling',9.5,14.6,-13.6,7.0,C1,C1+0.08,M['ceil'],'ceiling'); box('NG link ceiling',14.6,21.0,-16.9,-13.6,C1,C1+0.08,M['ceil'],'ceiling')
# east glazing (double-height end, city-facing) - frame + glass + daylight card behind (UNVERIFIED)
box('NG east end window glass',12.18,12.2,7.1,13.2,F+0.45,C2-0.3,M['glass'],'window')
for i,y in enumerate([7.05,8.6,10.15,11.7,13.25]): box('NG east end mullion %d'%i,12.1,12.2,y-0.05,y+0.05,F,C2,M['maroon'],'window')
for i,z in enumerate([F+0.4,140.6,143.2,C2-0.3]): box('NG east end transom %d'%i,12.1,12.2,7.0,13.3,z-0.05,z+0.05,M['maroon'],'window')
box('NG east daylight card behind glass UNVERIFIED',12.32,12.34,7.0,13.3,F,C2,M['day'],'window')
# balcony (2F east edge, x=9.0) glass rail + handrail
box('NG east balcony glass rail',8.47,8.5,7.08,13.28,F2,F2+1.05,M['glass'],'rail'); box('NG east balcony handrail',8.44,8.54,7.08,13.28,F2+1.05,F2+1.1,M['steel'],'rail')
box('NG east balcony slab edge',8.48,8.5,7.0,14.0,F2B-0.02,F2+0.01,M['wall'])
# maroon-framed 2F window on the double-height N wall (Joe 03)
box('NG double-height maroon window frame',9.0,11.8,13.2,13.22,142.35,144.65,M['maroon'],'window')
box('NG double-height maroon window glass',9.1,11.7,13.18,13.2,142.45,144.55,M['dark'],'window')
for i,xx in enumerate([9.97,10.83]): box('NG maroon window mullion %d'%i,xx-0.04,xx+0.04,13.16,13.18,142.45,144.55,M['maroon'],'window')
box('NG maroon window transom',9.1,11.7,13.16,13.18,143.6,143.68,M['maroon'],'window')
# bridge/landing glass rails
box('NG bridge W glass rail',-5.17,-5.14,6.25,13.5,F2,F2+1.05,M['glass'],'rail'); box('NG bridge W handrail',-5.2,-5.1,6.25,13.5,F2+1.05,F2+1.1,M['steel'],'rail')
box('NG landing S glass rail',-7.5,-5.2,13.53,13.56,F2,F2+1.05,M['glass'],'rail')
# stair: 25 treads, 26 risers 0.1708, along LEFT (north) side
R=(F2-F)/26; me=bpy.data.meshes.new('NG atrium wide stair wood clad'); bm=bmesh.new()
X0=-15.0
for i in range(25):
    x0=X0+0.3*i; x1=x0+0.3; zt=F+(i+1)*R
    vs=[bm.verts.new(v) for v in [(x0,13.5,F),(x1,13.5,F),(x1,16.5,F),(x0,16.5,F),(x0,13.5,zt),(x1,13.5,zt),(x1,16.5,zt),(x0,16.5,zt)]]
    for f in [(0,1,2,3),(4,7,6,5),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]:
        fa=bm.faces.new([vs[k] for k in f]); fa.material_index=1 if f==(4,7,6,5) else 0
bm.to_mesh(me); bm.free(); me.materials.append(M['wood']); me.materials.append(M['tread'])
st=bpy.data.objects.new(me.name,me); col.objects.link(st); tag(st,'stair'); objs.append(st)
# stair glass rail (sloped) + handrail
def slopepanel(name,y,thick,zoff,h,m):
    me=bpy.data.meshes.new(name); bm=bmesh.new()
    xa,xb=X0,X0+7.5; za,zb=F+R,F+25*R
    p=[(xa,y,za+zoff),(xb,y,zb+zoff),(xb,y,zb+zoff+h),(xa,y,za+zoff+h)]
    v=[bm.verts.new(q) for q in p]+[bm.verts.new((q[0],q[1]+thick,q[2])) for q in p]
    for f in [(0,1,2,3),(7,6,5,4),(0,4,5,1),(1,5,6,2),(2,6,7,3),(3,7,4,0)]: bm.faces.new([v[k] for k in f])
    bm.to_mesh(me); bm.free(); me.materials.append(m); o=bpy.data.objects.new(name,me); col.objects.link(o); tag(o,'rail'); objs.append(o)
slopepanel('NG stair S glass rail',13.52,0.02,0.05,0.95,M['glass']); slopepanel('NG stair S handrail',13.49,0.08,1.0,0.05,M['steel'])
slopepanel('NG stair N wall handrail',16.42,0.05,0.9,0.05,M['steel'])
# LED sign on bridge fascia
cu=bpy.data.curves.new('ng_sign','FONT'); cu.body='MONTCLAIR STATE UNIVERSITY'; cu.size=0.42; cu.align_x='CENTER'; cu.extrude=0.01
to=bpy.data.objects.new('ng_sign_tmp',cu); col.objects.link(to)
to.rotation_euler=(math.radians(90),0,math.radians(-90)); to.location=(-5.30,11.4,F2B-0.42)
bpy.context.view_layer.update(); dg=bpy.context.evaluated_depsgraph_get()
sm=bpy.data.meshes.new_from_object(to.evaluated_get(dg)); so=bpy.data.objects.new('NG bridge LED sign MONTCLAIR STATE UNIVERSITY',sm); so.matrix_world=to.matrix_world.copy()
col.objects.link(so); sm.materials.clear(); sm.materials.append(M['sign_led']); tag(so,'sign'); objs.append(so)
bpy.data.objects.remove(to); bpy.data.curves.remove(cu)
box('NG bridge LED sign panel',-5.30,-5.25,7.3,15.5,F2B-0.62,F2B-0.04,M['sign_bg'],'sign')
# maroon frosted doors (overlay panels, no openings; UNVERIFIED positions)
def door_y(n,xc,y,face,w=1.8,h=2.4):
    d=0.03*face
    box(n+' frame',xc-w/2-0.08,xc+w/2+0.08,min(y,y+d),max(y,y+d)+0.0,F,F+h+0.08,M['maroon'],'door')
    box(n+' frosted glass',xc-w/2+0.04,xc+w/2-0.04,min(y+d,y+2*d),max(y+d,y+2*d),F+0.08,F+h-0.04,M['frost'],'door')
    box(n+' centre stile',xc-0.03,xc+0.03,min(y+d,y+2.4*d),max(y+d,y+2.4*d),F+0.08,F+h,M['maroon'],'door')
for i,xc in enumerate([-12.5,-8.0]): door_y('NG atrium red wall maroon doors %d'%i,xc,6.25,1)
for i,xc in enumerate([1.5,6.0]): door_y('NG hallway S maroon doors %d'%i,xc,7.0+t/2,1)
for i,xc in enumerate([1.0,5.0]): door_y('NG hallway N maroon doors %d'%i,xc,14.0-t/2,-1)
door_y('NG 2F CCM old offices door',7.0,22.0-t/2,-1,1.0,2.2)
# fix 2F door z
for o in objs[-3:]:
    for v in o.data.vertices: v.co.z+=F2-F
# LED strips
for i,y in enumerate([8.5,10.5,12.5]): box('NG 1F hallway LED %d'%i,-2.0,8.8,y-0.04,y+0.04,F2B-0.03,F2B-0.01,M['led'],'light')
for i,y in enumerate([8.5,10.5,12.5]): box('NG 2F hallway LED %d'%i,-2.0,12.0,y-0.04,y+0.04,C2-0.03,C2-0.01,M['led'],'light')
for i,x in enumerate([10.8,13.3]): box('NG connector LED %d'%i,x-0.04,x+0.04,-13.4,6.8,C1-0.03,C1-0.01,M['led'],'light')
for i,y in enumerate([8.5,11.5,14.5]): box('NG atrium LED %d'%i,-18.5,-6.0,y-0.05,y+0.05,CA-0.03,CA-0.01,M['led'],'light')
# furniture
for i,(x,y,m) in enumerate([(-14,9.0,'yel'),(-12.4,10.4,'org'),(-10.6,8.6,'org'),(-9.0,10.0,'redo'),(-11.5,12.0,'org')]):
    box('NG atrium ottoman %d'%i,x-0.45,x+0.45,y-0.45,y+0.45,F,F+0.45,M[m],'furniture')
for i,(x,y) in enumerate([(1.5,10.5),(4.5,10.5),(7.2,9.2),(10.3,9.6),(11.2,-4.0),(12.8,-9.0)]):
    box('NG cafe table %d top'%i,x-0.4,x+0.4,y-0.4,y+0.4,F+0.72,F+0.75,M['white'],'furniture'); box('NG cafe table %d post'%i,x-0.04,x+0.04,y-0.04,y+0.04,F,F+0.72,M['steel'],'furniture')
    for j,(dx,dy) in enumerate([(0.75,0),(-0.75,0)]):
        box('NG cafe chair %d_%d seat'%(i,j),x+dx-0.27,x+dx+0.27,y+dy-0.27,y+dy+0.27,F+0.40,F+0.46,M['org' if (i+j)%2 else 'wall'],'furniture')
        box('NG cafe chair %d_%d back'%(i,j),x+dx*1.3-0.04,x+dx*1.3+0.04,y-0.27,y+0.27,F+0.46,F+0.9,M['org' if (i+j)%2 else 'wall'],'furniture')
        box('NG cafe chair %d_%d stem'%(i,j),x+dx-0.03,x+dx+0.03,y+dy-0.03,y+dy+0.03,F,F+0.40,M['steel'],'furniture')
for o in objs:
    if o.name.startswith(('NG cafe table 4','NG cafe table 5','NG cafe chair 4','NG cafe chair 5')):
        yy=o.data.vertices[0].co.y; dz=(FL-F)+(F-FL)*(yy+13.6)/20.6
        for v in o.data.vertices: v.co.z+=dz
box('NG chevron bench seat',8.9,11.9,12.6,13.2,F+0.42,F+0.48,M['chev'],'furniture'); box('NG chevron bench back',8.9,11.9,13.15,13.25,F+0.48,F+0.95,M['chev'],'furniture')
box('NG chevron bench base',8.95,11.85,12.65,13.12,F,F+0.42,M['steel'],'furniture')
# lights
def area(n,x,y,z,size,pw):
    L=bpy.data.lights.new(n,'AREA'); L.size=size; L.energy=pw; L.color=(1,0.97,0.92); o=bpy.data.objects.new(n,L); o.location=(x,y,z); col.objects.link(o); tag(o,'light')
area('NG atrium area light A',-14,11.4,145.7,5,1800); area('NG atrium area light B',-7,11.4,145.7,5,1500)
for i,x in enumerate([0.5,5.0]): area('NG 1F hallway light %d'%i,x,10.5,F2B-0.08,3,450)
area('NG double-height light',10.4,10.2,C2-0.15,4,1400)
for i,x in enumerate([1.0,6.0]): area('NG 2F hallway light %d'%i,x,10.5,C2-0.1,2.5,350)
area('NG 2F back hallway light',7.0,18.5,C2-0.1,2,250)
for i,y in enumerate([2.0,-7.0]): area('NG connector light %d'%i,12.0,y,C1-0.08,3,450)
area('NG link light',17.8,-15.2,C1-0.08,2.5,350)
# hide superseded (store for REVERT)
st={}
HIDE+=[o.name for o in bpy.data.objects if o.name.startswith('CCOM_east_RTU_20261014w') and o.type=='MESH' and (o.matrix_world@mathutils.Vector(o.bound_box[0])).x<16.5 and (o.matrix_world@mathutils.Vector(o.bound_box[6])).z<146.5]
HIDE+=[o.name for o in bpy.data.objects if o.name.startswith(('dc_door0_','dc_door1_'))]
for n in HIDE:
    o=bpy.data.objects.get(n)
    if o: st[n]=(o.hide_render,o.hide_viewport); o.hide_render=True; o.hide_viewport=True
    else: print('MISSING',n)
sc['ng_hidden']=json.dumps(st)
sc['ng_note']='ng: CCOM 1F open floor (atrium->hallway->east double-height + connector/link to the SE east-window seating), stair+bridge+LED sign, 2F hallway + east balcony + back hallway dipping left; ALL UNVERIFIED blockout'
# cameras
def cam(n,loc,rot,lens=24):
    c=bpy.data.cameras.new(n); c.lens=lens; c.clip_start=0.05; o=bpy.data.objects.new(n,c); o.location=loc; o.rotation_euler=[math.radians(a) for a in rot]; col.objects.link(o); tag(o,'camera')
cam('NG_CAM_aerial_cutaway',(-8,-24,172),(0,0,0),22)
cam('NG_CAM_eye_entry_east',(-18.6,10.6,139.05),(90,0,-80),20)
cam('NG_CAM_eye_balcony_down',(7.9,7.5,143.55),(60,0,-58),18)
cam('NG_CAM_closeup_stair_sign',(-15.5,8.3,138.9),(84,0,-52),24)
exec(open(os.path.join(os.path.dirname(bpy.data.filepath),'scripts/ng/ng_cams.py')).read())
print('NG objects',len(col.objects),'total',len(bpy.data.objects))
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
