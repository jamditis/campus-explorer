# nr (Oct 30 2026 ~5:35 PM ET, MAIN): CCOM interior furniture pass per nq 'Next' — ALL UNVERIFIED (no photo of CCOM furniture):
# (a) 1F open-floor cafe tables -> pedestal tables (bevelled top, dark edge band, column, cross foot, glides); cafe chairs -> shell chairs (rounded seat/back, splayed tube legs, glides);
# (b) S office chairs -> task chairs (cushion, reclined back, gas lift, 5-star base with casters, T-arms); NO leg sets for those chairs hidden;
# (c) NR_bevel modifiers on the remaining blocky furniture (classroom tables/chairs, S office table, atrium ottomans, chevron bench);
# (d) faint tree-line silhouette on the nq east view gradient (noise-modulated band height);
# (e) blocked-out floor fill for the green terrain slivers at the cutaway margins (0.5 m cells, enclosure test), UNVERIFIED.
import bpy, bmesh, os, json, mathutils, math, sys
sys.path.insert(0,os.path.abspath('scripts/nr')); import importlib, nr_furn_lib as FL; importlib.reload(FL)
SAVE=os.environ.get('SAVE')=='1'; REVERT=os.environ.get('REVERT')=='1'
CN='NR_CCOM_furniture_casters_bevels_20261030nr'
sc=bpy.context.scene
def revert():
    st=json.loads(sc.get('nr_state','{}'))
    for n,(hr,hv) in st.get('hidden',{}).items():
        o=bpy.data.objects.get(n)
        if o: o.hide_render=hr; o.hide_viewport=hv
    for n in st.get('bevel',[]):
        o=bpy.data.objects.get(n)
        if o and 'NR_bevel' in o.modifiers: o.modifiers.remove(o.modifiers['NR_bevel'])
    if 'nodes' in st:
        m=bpy.data.materials.get(st['nodes'])
        if m:
            nt=m.node_tree
            for nd in list(nt.nodes):
                if nd.name.startswith('NR_'): nt.nodes.remove(nd)
            sp=nt.nodes['Separate XYZ']; cr=nt.nodes['Color Ramp']; nt.links.new(sp.outputs['Z'],cr.inputs[0])
    c=bpy.data.collections.get(CN)
    if c:
        for o in list(c.objects):
            d=o.data; bpy.data.objects.remove(o)
            if d and d.users==0:
                for coll in (bpy.data.meshes,bpy.data.cameras,bpy.data.lights):
                    if d.name in coll and coll[d.name]==d: coll.remove(d); break
        bpy.data.collections.remove(c)
    for me in list(bpy.data.meshes):
        if me.name.startswith('NR_') and me.users==0: bpy.data.meshes.remove(me)
    for m in list(bpy.data.materials):
        if m.name.startswith('NR_') and m.users==0: bpy.data.materials.remove(m)
    for k in ('nr_state','nr_note'):
        if k in sc: del sc[k]
    bpy.context.view_layer.update()
if REVERT:
    revert(); bpy.ops.wm.save_mainfile(); raise SystemExit
revert()
state={'hidden':{},'bevel':[]}
col=bpy.data.collections.new(CN); sc.collection.children.link(col)
def tag(o,layer):
    o['msu_building']='School of Communication and Media'; o['msu_area']='ccom'; o['msu_layer']=layer
    o['msu_merge_role']='live'; o['msu_target_collection']='MSU_CCOM'; o['msu_tag_session']='nr'
def mat(name,c,rough=0.6,metal=0.0):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes=True; p=m.node_tree.nodes['Principled BSDF']
    p.inputs['Base Color'].default_value=c; p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal
    return m
def hide(o):
    if o.name not in state['hidden']: state['hidden'][o.name]=(o.hide_render,o.hide_viewport)
    o.hide_render=True; o.hide_viewport=True
def bb(o):
    cs=[o.matrix_world@mathutils.Vector(c) for c in o.bound_box]
    return mathutils.Vector([min(c[i] for c in cs) for i in range(3)]),mathutils.Vector([max(c[i] for c in cs) for i in range(3)])
def ctr(o):
    lo,hi=bb(o); return (lo+hi)/2
def mkmesh(name,fn,mats):
    bm=bmesh.new(); fn(bm); FL._smooth(bm)
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for m in mats: me.materials.append(m)
    # auto-smooth-ish: flat on big planar faces is fine at this scale; keep smooth shading + weighted normals via modifier
    return me
def place(name,me,loc,yaw,layer):
    o=bpy.data.objects.new(name,me); o.location=loc; o.rotation_euler=(0,0,yaw); col.objects.link(o); tag(o,layer)
    m=o.modifiers.new('NR_wn','WEIGHTED_NORMAL'); m.keep_sharp=True
    return o
charcoal=mat('NR_powder_coat_charcoal_UNVERIFIED',(0.035,0.035,0.038,1),0.45,0.6)
glide=mat('NR_black_nylon_UNVERIFIED',(0.015,0.015,0.016,1),0.55)
chrome=mat('NR_chrome_UNVERIFIED',(0.8,0.8,0.82,1),0.12,1.0)
wheel=mat('NR_caster_wheel_UNVERIFIED',(0.02,0.02,0.022,1),0.35)
edge=mat('NR_table_edge_band_UNVERIFIED',(0.20,0.20,0.21,1),0.4)
# (a) cafe furniture
seatm=bpy.data.objects['NG cafe chair 0_0 seat'].active_material
topm=bpy.data.objects['NG cafe table 0 top'].active_material
meC=mkmesh('NR_cafe_shell_chair_UNVERIFIED',FL.cafe_chair,[seatm,charcoal,glide])
meT=mkmesh('NR_cafe_pedestal_table_UNVERIFIED',FL.pedestal_table,[topm,charcoal,glide,edge])
FLOOR=137.70
for t in range(4):
    top=bpy.data.objects['NG cafe table %d top'%t]; post=bpy.data.objects['NG cafe table %d post'%t]
    c=ctr(top); place('NR cafe pedestal table %d (UNVERIFIED)'%t,meT,(c.x,c.y,FLOOR),0,'furniture'); hide(top); hide(post)
    for k in range(2):
        s=bpy.data.objects['NG cafe chair %d_%d seat'%(t,k)]; b=bpy.data.objects['NG cafe chair %d_%d back'%(t,k)]; st_=bpy.data.objects['NG cafe chair %d_%d stem'%(t,k)]
        cs=ctr(s); cb=ctr(b); yaw=math.atan2(cb.y-cs.y,cb.x-cs.x)
        oc=place('NR cafe shell chair %d_%d (UNVERIFIED)'%(t,k),meC,(cs.x,cs.y,FLOOR),yaw,'furniture')
        sl=oc.material_slots[0]; sl.link='OBJECT'; sl.material=s.active_material   # keep ng's alternating orange/white shells
        for o in (s,b,st_): hide(o)
# (b) S office task chairs
offm=bpy.data.objects['NK S office chair 00 seat'].active_material
meK=mkmesh('NR_task_chair_casters_UNVERIFIED',FL.task_chair,[offm,glide,chrome,wheel])
for i in (0,1,2,3):
    for j in (0,1):
        s=bpy.data.objects.get('NK S office chair %d%d seat'%(i,j)); b=bpy.data.objects.get('NK S office chair %d%d back'%(i,j))
        if not s: continue
        cs=ctr(s); cb=ctr(b); yaw=math.atan2(cb.y-cs.y,cb.x-cs.x)
        lo,_=bb(s); place('NR S office task chair %d%d (UNVERIFIED)'%(i,j),meK,(cs.x,cs.y,137.71),yaw,'furniture')
        hide(s); hide(b); l=bpy.data.objects.get('NO chair legs (S office chair %d%d seat)'%(i,j))
        if l: hide(l)
# (c) bevels on remaining blocky furniture
def bev(o,w,seg=2):
    if o.type!='MESH' or 'NR_bevel' in o.modifiers: return
    b=o.modifiers.new('NR_bevel','BEVEL'); b.width=w; b.segments=seg; b.limit_method='NONE'; b.harden_normals=False
    state['bevel'].append(o.name)
for o in bpy.data.objects:
    n=o.name
    if n.startswith('NK N classroom table') and not n.endswith('legs'): bev(o,0.006)
    elif n.startswith('NK N classroom chair') and (n.endswith('seat') or n.endswith('back')): bev(o,0.008)
    elif n.startswith('NK S office meeting table'): bev(o,0.006)
    elif n.startswith('NG atrium ottoman'): bev(o,0.035,4)
    elif n.startswith('NG chevron bench'): bev(o,0.012,3)
for o in bpy.data.objects:
    if o.name.startswith('NK S office meeting table') and o.type=='MESH' and o.name not in state['bevel']: bev(o,0.006)
# (d) tree-line silhouette on the east view gradient
m=bpy.data.materials.get('NQ_east_view_gradient_UNVERIFIED')
if m:
    nt=m.node_tree; sp=nt.nodes['Separate XYZ']; cr=nt.nodes['Color Ramp']; tc=nt.nodes['Texture Coordinate']
    nz=nt.nodes.new('ShaderNodeTexNoise'); nz.name='NR_treeline_noise'; nz.inputs['Scale'].default_value=9.0; nz.inputs['Detail'].default_value=6.0; nz.inputs['Roughness'].default_value=0.62
    mp=nt.nodes.new('ShaderNodeMapping'); mp.name='NR_treeline_map'; mp.inputs['Scale'].default_value=(0.0,1.0,0.0)   # horizontal-only noise (card spans Y)
    nt.links.new(tc.outputs['Generated'],mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'],nz.inputs['Vector'])
    mr=nt.nodes.new('ShaderNodeMapRange'); mr.name='NR_treeline_range'; mr.inputs['To Min'].default_value=-0.10; mr.inputs['To Max'].default_value=0.10
    nt.links.new(nz.outputs['Fac'],mr.inputs['Value'])
    sub=nt.nodes.new('ShaderNodeMath'); sub.name='NR_treeline_sub'; sub.operation='SUBTRACT'
    nt.links.new(sp.outputs['Z'],sub.inputs[0]); nt.links.new(mr.outputs['Result'],sub.inputs[1]); nt.links.new(sub.outputs[0],cr.inputs[0])
    state['nodes']=m.name
# (e) green sliver fill at the cutaway margins
dg=bpy.context.evaluated_depsgraph_get()
from mathutils.bvhtree import BVHTree
rb=[(o,BVHTree.FromObject(o,dg),o.matrix_world.inverted()) for o in bpy.data.objects if o.name.startswith('School of Communication and Media roof') and o.type=='MESH']
def roofz(x,y):
    for o,t,Mi in rb:
        org=Mi@mathutils.Vector((x,y,175.0)); d=(Mi.to_3x3()@mathutils.Vector((0,0,-1))).normalized(); hit=t.ray_cast(org,d)
        if hit[0] is not None: return (o.matrix_world@hit[0]).z
    return None
nqf=bpy.data.objects.get('NQ blocked-out interior floor under CCOM roof (UNVERIFIED)')
import time; t0=time.time()
# local BVH of everything visible in the CCOM box (faster than scene.ray_cast on the full 6.7k-object scene)
VS=[];PS=[];OWN=[]
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render or o.name.startswith('School of Communication and Media roof'): continue
    lo,hi=bb(o)
    if hi.x<-25 or lo.x>18 or hi.y<-18 or lo.y>30 or hi.z<130 or lo.z>150: continue
    oe=o.evaluated_get(dg); me_=oe.to_mesh(); M=o.matrix_world; base=len(VS)
    VS.extend(M@v.co for v in me_.vertices)
    for pg in me_.polygons: PS.append([base+i for i in pg.vertices]); OWN.append(o.name)
    oe.to_mesh_clear()
LB=BVHTree.FromPolygons(VS,PS)
print('NR local bvh',len(VS),len(PS),round(time.time()-t0,1),'s',flush=True)
cells=[]; S=0.5
for ix in range(-46,32):
    for iy in range(-32,56):
        x=ix*S+S/2; y=iy*S+S/2; rz=roofz(x,y)
        if rz is None or any(roofz(x+dx,y+dy) is None for dx,dy in ((-0.6,-0.6),(0.6,-0.6),(0.6,0.6),(-0.6,0.6))): continue
        l,n,fi,dd=LB.ray_cast(mathutils.Vector((x,y,rz-0.3)),mathutils.Vector((0,0,-1)))
        if l is None or not OWN[fi].startswith('Terrain_LiDAR') or l.z>=137.45: continue
        enc=0
        for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
            l2,_,f2,_=LB.ray_cast(mathutils.Vector((x,y,138.6)),mathutils.Vector((dx,dy,0)),30.0)
            if l2 is not None and not OWN[f2].startswith('Terrain'): enc+=1
        if enc==4: cells.append((x,y,l.z))
print('NR sliver cells',len(cells))
if cells and nqf:
    fl=nqf.active_material
    bm=bmesh.new(); ZT=137.39
    for x,y,z in cells:
        r=bmesh.ops.create_cube(bm,size=1.0)
        for v in r['verts']: v.co=mathutils.Vector((x+v.co.x*S*1.02,y+v.co.y*S*1.02,(ZT+z-0.05)/2+v.co.z*(ZT-z+0.05)))
    me2=bpy.data.meshes.new('NR_blocked_out_floor_margins'); bm.to_mesh(me2); bm.free(); me2.materials.append(fl)
    ob=bpy.data.objects.new('NR blocked-out floor margin fill under CCOM roof (UNVERIFIED)',me2); col.objects.link(ob); tag(ob,'floor')
    state['fill_cells']=len(cells)
# cameras
def cam(n,loc,tgt,lens_):
    c=bpy.data.cameras.new(n); c.lens=lens_; c.clip_start=0.05; o=bpy.data.objects.new(n,c); o.location=loc
    o.rotation_euler=(mathutils.Vector(tgt)-mathutils.Vector(loc)).to_track_quat('-Z','Y').to_euler(); col.objects.link(o); tag(o,'camera')
cam('NR_CAM_aerial_cutaway_open_floor_oblique',(-6.0,-20.0,176.0),(3.0,9.0,138.0),26)
cam('NR_CAM_eye_1F_open_floor_cafe_looking_east',(-0.6,8.4,139.25),(10.0,10.2,138.6),20)
cam('NR_CAM_eye_1F_open_floor_east_end_looking_west',(11.4,11.6,139.2),(-6.0,9.6,138.9),18)
cam('NR_CAM_closeup_cafe_table_chairs',(5.75,8.15,138.75),(4.5,10.5,138.15),28)
cam('NR_CAM_closeup_S_office_task_chairs',(1.2,6.6,139.3),(3.6,4.6,138.0),22)
sc['nr_state']=json.dumps(state)
sc['nr_note']='nr: cafe pedestal tables + shell chairs, office task chairs w/ casters, furniture bevels, east view tree-line, cutaway margin floor fill; ALL UNVERIFIED'
print('NR objects',len(col.objects),'hidden',len(state['hidden']),'bevel',len(state['bevel']),'total',len(bpy.data.objects))
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
