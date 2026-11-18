"""uy polish after self-review of 1033 WIPs.
Fixes:
  1) N terracotta bay: panels/glass must sit proud of surround (surround was solid occluder)
  2) W cream skin: was continuous slab burying recessed windows → strip panels BETWEEN bays
  3) Push W windows slightly proud of skin plane
  4) Reframe W eye + lettering/terracotta closeup cams
REVERT=1 removes uy_polish extras tagged uy_polish; prefer full uy_revert_all.
SAVE=1 saves.
"""
import bpy, bmesh, os, json
from mathutils import Vector

REV = os.environ.get('REVERT') == '1'
SAVE = os.environ.get('SAVE') == '1'
D = '/workspace/nj-scenes/montclair-state/'
DATA = D + 'data/uy'
OSM = json.load(open(D + 'data/uv/freeman_osm_probe.json'))
GR = float(json.load(open(D + 'data/uv/uv_main.json')).get('GR', 129.053))
TOPZ = 147.05
OUT = 0.08
COL_ENT = 'UV_Freeman_entrance_1096_UNVERIFIED'
COL_SHELL = 'UY_Freeman_cream_shell_UNVERIFIED'
COL_SIDE = 'UY_Freeman_W_S_windows_1114_UNVERIFIED'
COL_CAM = 'UY_Freeman_cams'

def remove_obj(o):
    if not o: return
    me=o.data; t=o.type
    bpy.data.objects.remove(o, do_unlink=True)
    if me is not None and me.users==0:
        if t=='MESH': bpy.data.meshes.remove(me)
        elif t=='CAMERA': bpy.data.cameras.remove(me)

def revert_polish():
    for o in [o for o in list(bpy.data.objects) if o.get('uy_polish')]:
        remove_obj(o)
    print('UY POLISH REVERTED')

if REV:
    revert_polish()
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit

log = {'session': 'uy_polish', 'fixes': []}

def mat_by(substr, fallback):
    for m in bpy.data.materials:
        if substr in m.name and (m.get('uy_mat') or m.get('uv_mat')):
            return m
    m=bpy.data.materials.new('UY_pol_'+substr); m.use_nodes=True; m['uy_mat']=1
    m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*fallback,1)
    return m

M = dict(
    brick=mat_by('cream_brick_shell', (0.72,0.66,0.54)),
    terracotta=mat_by('terracotta_panel', (0.70,0.30,0.12)),
    glass=mat_by('curtain_glass', (0.55,0.62,0.68)),
    white=mat_by('white_frame', (0.92,0.92,0.90)),
    dark=mat_by('window_frame_darkred', (0.28,0.10,0.07)),
    spandrel=mat_by('spandrel_reddish', (0.55,0.22,0.14)),
)

class MB:
    def __init__(s, name, mats, coll):
        s.bm=bmesh.new(); s.name=name; s.mats=mats; s.coll=coll
    def box(s, c, u, n, w, dep, z0, z1, mi=0):
        u=Vector((u[0],u[1],0)).normalized(); n=Vector((n[0],n[1],0)).normalized(); c=Vector((c[0],c[1],0))
        vs=[]
        for z in (z0,z1):
            for a,b_ in ((-1,-1),(1,-1),(1,1),(-1,1)):
                p=c+u*(a*w/2)+n*(b_*dep/2)
                vs.append(s.bm.verts.new((p.x,p.y,z)))
        for f in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)):
            try: s.bm.faces.new([vs[i] for i in f]).material_index=mi
            except ValueError: pass
    def done(s):
        bmesh.ops.recalc_face_normals(s.bm, faces=s.bm.faces)
        me=bpy.data.meshes.new(s.name); s.bm.to_mesh(me); s.bm.free()
        for m in s.mats: me.materials.append(m)
        o=bpy.data.objects.new(s.name, me); s.coll.objects.link(o)
        o['uy_obj']=1; o['uy_polish']=1
        o['UNVERIFIED']='uy polish Freeman; sizes UNVERIFIED'
        for p in me.polygons: p.use_smooth=False
        return o

col_ent = bpy.data.collections.get(COL_ENT)
col_shell = bpy.data.collections.get(COL_SHELL)
col_side = bpy.data.collections.get(COL_SIDE)

e6=[e for e in OSM['edges'] if e['i']==6][0]
U=Vector((e6['u'][0],e6['u'][1],0)).normalized()
N=Vector((e6['n'][0],e6['n'][1],0)).normalized()
A=Vector((e6['a'][0],e6['a'][1],0))
T_WIN0,T_WIN1=3.35,6.55
ob_bay=bpy.data.objects.get('UY_Freeman_N_terracotta_3panel_window_bay_UNVERIFIED')
if ob_bay and ob_bay.type=='MESH' and ob_bay.data.vertices:
    ts=sorted((ob_bay.matrix_world@Vector(v.co)-A).dot(U) for v in ob_bay.data.vertices)
    T_WIN0,T_WIN1=ts[0],ts[-1]

# ---- 1) Rebuild bay: frame strips only + panels proud ----
if ob_bay:
    remove_obj(ob_bay)
ww=T_WIN1-T_WIN0
wc=A+U*((T_WIN0+T_WIN1)/2)
# mats 0 white 1 glass 2 terracotta 3 brick
mw=MB('UY_Freeman_N_terracotta_3panel_window_bay_UNVERIFIED',
      [M['white'],M['glass'],M['terracotta'],M['brick']], col_ent)
# side brick jambs (not full solid slab)
for t in (T_WIN0+0.06, T_WIN1-0.06):
    mw.box(A+U*t + N*(OUT+0.12), U, N, 0.14, 0.22, GR-0.05, TOPZ-0.15, 3)
# top/bottom brick bands
mw.box(wc+N*(OUT+0.12), U, N, ww, 0.22, TOPZ-0.45, TOPZ-0.15, 3)
mw.box(wc+N*(OUT+0.12), U, N, ww, 0.22, GR-0.05, GR+0.35, 3)

n_cols=3
pane_w=(ww-0.30)/n_cols
terr_z0,terr_z1=GR+0.45, GR+4.55
glass_mid=GR+4.70
glass_top=TOPZ-0.55
glass_split=(glass_mid+glass_top)/2
PROUD = OUT + 0.32  # clearly in front of any skin
for i in range(n_cols):
    pc=A+U*(T_WIN0+0.15+pane_w*(i+0.5))
    # terracotta panel (solid, proud)
    mw.box(pc+N*PROUD, U, N, pane_w-0.10, 0.10, terr_z0, terr_z1, 2)
    # 2 rows glass
    mw.box(pc+N*PROUD, U, N, pane_w-0.10, 0.08, glass_mid, glass_split-0.05, 1)
    mw.box(pc+N*PROUD, U, N, pane_w-0.10, 0.08, glass_split+0.05, glass_top, 1)
    if i<n_cols-1:
        mc=A+U*(T_WIN0+0.15+pane_w*(i+1))
        mw.box(mc+N*(PROUD+0.02), U, N, 0.07, 0.10, GR+0.40, TOPZ-0.50, 0)
# horizontal rails
mw.box(wc+N*(PROUD+0.03), U, N, ww-0.2, 0.06, terr_z1, glass_mid, 0)
mw.box(wc+N*(PROUD+0.03), U, N, ww-0.2, 0.06, glass_split-0.05, glass_split+0.05, 0)
mw.box(wc+N*(PROUD+0.03), U, N, ww-0.2, 0.06, GR+0.35, GR+0.48, 0)
mw.done()
log['fixes'].append('bay_proud_3terracotta_2x3glass')

# bump terracotta color warmer/more saturated so it reads vs cream
tm=M['terracotta']
if tm and tm.use_nodes:
    for n in tm.node_tree.nodes:
        if n.type=='BSDF_PRINCIPLED':
            n.inputs['Base Color'].default_value=(0.78,0.28,0.08,1)
        if n.type=='TEX_BRICK':
            n.inputs['Color1'].default_value=(0.78,0.28,0.08,1)
    # if noise ramp
    for n in tm.node_tree.nodes:
        if n.type=='VALTORGB':
            n.color_ramp.elements[1].color=(0.78,0.28,0.08,1)
            n.color_ramp.elements[0].color=(0.55,0.18,0.06,1)
log['fixes'].append('terracotta_color_punch')

# ---- 2) Rebuild W cream skin as inter-bay strips; rebuild W windows proud ----
skin_w=bpy.data.objects.get('UY_Freeman_W_cream_brick_skin_UNVERIFIED')
win_w=bpy.data.objects.get('UY_Freeman_W_recessed_vertical_windows_UNVERIFIED')
if skin_w: remove_obj(skin_w)
if win_w: remove_obj(win_w)

e1=[e for e in OSM['edges'] if e['i']==1][0]
U1=Vector((e1['u'][0],e1['u'][1],0)).normalized()
N1=Vector((e1['n'][0],e1['n'][1],0)).normalized()
A1=Vector((e1['a'][0],e1['a'][1],0))
L1=e1['len']
pitch=3.6
# bay centers
centers=[]
n_bays=max(1,int((L1-4.0)/pitch))
for i in range(n_bays):
    t=2.0+pitch*(i+0.5)
    if t>L1-2.0: break
    centers.append(t)

# windows proud
msw=MB('UY_Freeman_W_recessed_vertical_windows_UNVERIFIED',
       [M['dark'],M['glass'],M['spandrel'],M['brick']], col_side)
for t in centers:
    c=A1+U1*t
    # frame proud of wall
    msw.box(c+N1*(OUT+0.10), U1, N1, 1.20, 0.28, GR+0.8, TOPZ-0.4, 0)
    bands=[
        (GR+1.0,GR+3.4,1),(GR+3.4,GR+3.85,2),
        (GR+3.85,GR+6.25,1),(GR+6.25,GR+6.7,2),
        (GR+6.7,GR+9.1,1),(GR+9.1,GR+9.55,2),
        (GR+9.55,GR+11.95,1),(GR+11.95,GR+12.4,2),
        (GR+12.4,TOPZ-0.55,1),
    ]
    for z0,z1,mi in bands:
        msw.box(c+N1*(OUT+0.18), U1, N1, 0.98, 0.08, z0, z1, mi)
msw.done()
log['fixes'].append(f'W_windows_proud_x{len(centers)}')

# cream strips between bays + ends
mb=MB('UY_Freeman_W_cream_brick_skin_UNVERIFIED',[M['brick']], col_shell)
# end caps
edges_t=[0.4]+centers+[L1-0.4]
for i in range(len(edges_t)-1):
    t0,t1=edges_t[i],edges_t[i+1]
    # if this segment is a window bay (~1.2 wide), skip center; else fill
    mid=(t0+t1)/2
    is_bay=any(abs(mid-c)<0.8 for c in centers)
    if is_bay:
        # two thin flanks only around bay — skip solid over bay
        continue
    w=t1-t0-0.15
    if w<0.8: continue
    c=A1+U1*((t0+t1)/2)
    mb.box(c+N1*(OUT+0.05), U1, N1, w, 0.07, GR-0.02, TOPZ-0.12, 0)
# also thin strips above/below would help but height-full between is enough
mb.done()
log['fixes'].append('W_cream_skin_interbay')

# ---- 3) Reframe cams ----
cc=bpy.data.collections.get(COL_CAM)
def set_cam(name, loc, target, lens=32):
    o=bpy.data.objects.get(name)
    if not o:
        cd=bpy.data.cameras.new(name); cd.lens=lens; cd.clip_end=5000
        o=bpy.data.objects.new(name, cd)
        if cc: cc.objects.link(o)
        o['uy_obj']=1; o['uy_polish']=1
    o.location=loc
    if o.type=='CAMERA':
        o.data.lens=lens
    direction=Vector(target)-Vector(loc)
    o.rotation_euler=direction.to_track_quat('-Z','Y').to_euler()
    return o

# W eye: farther out, mid-face, looking at mid bay
t_mid=centers[len(centers)//2] if centers else L1*0.45
c_mid=A1+U1*t_mid
set_cam('UY_CAM_eye_Freeman_W_side',
        (c_mid.x+N1.x*28, c_mid.y+N1.y*28, GR+3.5),
        (c_mid.x, c_mid.y, GR+9.0), 28)
# closeup: from north, frame lettering wing + terracotta bay together
let=None
for o in bpy.data.objects:
    if o.type=='FONT' and 'FREEMAN' in o.name.upper():
        let=o; break
bay_c=A+U*((T_WIN0+T_WIN1)/2)
let_c=Vector(let.matrix_world.translation) if let else (A+U*1.7+Vector((0,0,GR+8.9)))
# stand further back and higher to catch lettering + bay
aim=Vector(((let_c.x+bay_c.x)/2, (let_c.y+bay_c.y)/2, GR+7.0))
set_cam('UY_CAM_closeup_Freeman_N_lettering_terracotta',
        (aim.x+N.x*11 - U.x*0.5, aim.y+N.y*11 - U.y*0.5, GR+3.0),
        (aim.x, aim.y, GR+7.5), 35)
# N entrance eye slightly wider to include bay
ec=A+U*((6.55+12.05)/2)
set_cam('UV_CAM_eye_Freeman_N_entrance',
        (ec.x+N.x*16, ec.y+N.y*16, GR+1.8),
        (ec.x - U.x*1.5, ec.y - U.y*1.5, GR+3.5), 30)

log['n_objects']=len(bpy.data.objects)
json.dump(log, open(DATA+'/uy_polish.json','w'), indent=2)
print('UY POLISH', json.dumps(log, indent=2))
print('OBJECTS', len(bpy.data.objects))
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED')
