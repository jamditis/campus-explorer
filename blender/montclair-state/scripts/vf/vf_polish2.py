"""vf polish2: brighter sky-tint cards; glass alpha/coat bump; lighten VC BP slightly;
stronger N cream punch mats; re-aim W closeup more frontal. SAVE=1.
"""
import bpy, os, json, bmesh
from mathutils import Vector
SAVE = os.environ.get('SAVE') == '1'
D='/workspace/nj-scenes/montclair-state/'
DATA=D+'data/vf'
OSM=json.load(open(D+'data/uv/freeman_osm_probe.json'))
GR=float(json.load(open(D+'data/uv/uv_main.json')).get('GR',129.053))
OUT=0.08
TOPZ=147.05
log={'session':'vf_polish2','fixes':[]}

# A) sky tint punch
sky=bpy.data.materials.get('VF_Freeman_W_sky_tint_UNVERIFIED')
if sky and sky.use_nodes:
    b=sky.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Base Color'].default_value=(0.72,0.84,0.98,1.0)
        if 'Emission Color' in b.inputs:
            b.inputs['Emission Color'].default_value=(0.78,0.88,1.0,1.0)
        if 'Emission Strength' in b.inputs:
            b.inputs['Emission Strength'].default_value=2.2
        b.inputs['Roughness'].default_value=0.95
        log['fixes'].append('sky_tint_emiss_2.2')

# Widen existing sky cards slightly by scaling along U in object space — rebuild thinner/wider
# Simpler: leave geo; boost glass instead.

g=bpy.data.materials.get('VD_Freeman_W_glass_pane_UNVERIFIED')
if g and g.use_nodes:
    b=g.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Base Color'].default_value=(0.55,0.74,0.95,1.0)
        b.inputs['Alpha'].default_value=0.65
        b.inputs['Roughness'].default_value=0.01
        if 'Coat Weight' in b.inputs:
            b.inputs['Coat Weight'].default_value=0.85
            b.inputs['Coat Roughness'].default_value=0.012
        if 'Specular IOR Level' in b.inputs:
            b.inputs['Specular IOR Level'].default_value=1.0
        log['fixes'].append('W_glass_alpha0.65_coat0.85')

# Lighten VC backplanes a touch so see-through isn't pure black (stash once)
BP_STASH=DATA+'/vf_vc_bp_stash.json'
def stash_principled(path, mat_name):
    m=bpy.data.materials.get(mat_name)
    if not m or not m.use_nodes or os.path.exists(path): return
    b=m.node_tree.nodes.get('Principled BSDF')
    if not b: return
    d={}
    for k in ('Base Color','Roughness','Alpha','Emission Color','Emission Strength','Specular IOR Level'):
        if k in b.inputs:
            v=b.inputs[k].default_value
            try: d[k]=list(v)
            except TypeError: d[k]=float(v)
    json.dump(d, open(path,'w'), indent=2)

stash_principled(BP_STASH, 'VC_Freeman_glass_backplane_dark_UNVERIFIED')
bp=bpy.data.materials.get('VC_Freeman_glass_backplane_dark_UNVERIFIED')
if bp and bp.use_nodes:
    b=bp.node_tree.nodes.get('Principled BSDF')
    if b:
        # lift from near-black toward deep cool interior so glass isn't void
        b.inputs['Base Color'].default_value=(0.12,0.14,0.18,1.0)
        if 'Emission Color' in b.inputs:
            b.inputs['Emission Color'].default_value=(0.08,0.10,0.14,1.0)
        if 'Emission Strength' in b.inputs:
            b.inputs['Emission Strength'].default_value=0.08
        log['fixes'].append('VC_BP_lift_cool_interior')

# Also bump VB cool glass used on S/E/entrance
vg=bpy.data.materials.get('VB_Freeman_glass_cool_clear_UNVERIFIED')
if vg and vg.use_nodes:
    b=vg.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Alpha'].default_value=0.58
        if 'Coat Weight' in b.inputs:
            b.inputs['Coat Weight'].default_value=0.70
        b.inputs['Base Color'].default_value=(0.58,0.76,0.94,1.0)
        log['fixes'].append('VB_glass_alpha0.58_coat0.70')

# B) N cream punch mats darker/warmer
cm=bpy.data.materials.get('VF_Freeman_N_cream_punch_UNVERIFIED')
if cm and cm.use_nodes:
    nt=cm.node_tree
    for n in nt.nodes:
        if n.type=='VALTORGB':
            n.color_ramp.elements[0].color=(0.42,0.36,0.26,1)
            n.color_ramp.elements[1].color=(0.64,0.58,0.44,1)
        if n.type=='BUMP':
            n.inputs['Strength'].default_value=0.32
    log['fixes'].append('N_cream_punch_darker_bump')

sh=bpy.data.materials.get('VF_Freeman_shadow_punch_UNVERIFIED')
if sh and sh.use_nodes:
    b=sh.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Base Color'].default_value=(0.08,0.06,0.05,1.0)
        log['fixes'].append('shadow_punch_darker')

# Add a few extra proud horizontal belt lips on pier faces only (cheap punch)
COL='VF_Freeman_polish_UNVERIFIED'
col=bpy.data.collections.get(COL)
e6=[e for e in OSM['edges'] if e['i']==6][0]
U=Vector((e6['u'][0],e6['u'][1],0)).normalized()
N=Vector((e6['n'][0],e6['n'][1],0)).normalized()
A=Vector((e6['a'][0],e6['a'][1],0))

class MB:
    def __init__(s, name, mats, coll):
        s.bm=bmesh.new(); s.name=name; s.mats=mats; s.coll=coll
    def box(s,c,u,n,w,dep,z0,z1,mi=0):
        u=Vector((u[0],u[1],0)).normalized(); n=Vector((n[0],n[1],0)).normalized(); c=Vector((c[0],c[1],0))
        vs=[]
        for z in (z0,z1):
            for a,b_ in ((-1,-1),(1,-1),(1,1),(-1,1)):
                p=c+u*(a*w/2)+n*(b_*dep/2); vs.append(s.bm.verts.new((p.x,p.y,z)))
        for f in ((0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)):
            try: s.bm.faces.new([vs[i] for i in f]).material_index=mi
            except ValueError: pass
    def done(s):
        bmesh.ops.recalc_face_normals(s.bm, faces=s.bm.faces)
        me=bpy.data.meshes.new(s.name); s.bm.to_mesh(me); s.bm.free()
        for m in s.mats: me.materials.append(m)
        o=bpy.data.objects.new(s.name, me); s.coll.objects.link(o)
        o['vf_obj']=1; o['UNVERIFIED']='vf polish2; UNVERIFIED'
        for p in me.polygons: p.use_smooth=False
        return o

# remove prior polish2 extras if re-run
for o in list(bpy.data.objects):
    if o.get('vf_obj') and 'VF_Freeman_N_extra_lip_' in o.name:
        me=o.data; bpy.data.objects.remove(o, do_unlink=True)
        if me and me.users==0: bpy.data.meshes.remove(me)

extra=0
if col and cm and sh:
    for t0,t1,tag in ((6.68,6.95,'pierW'),(11.70,11.95,'pierE')):
        w=t1-t0; mid=A+U*((t0+t1)/2)
        for zi,z in enumerate((GR+5.2, GR+8.6, GR+12.0)):
            name=f'VF_Freeman_N_extra_lip_{tag}_{zi}_UNVERIFIED'
            mb=MB(name,[cm,sh],col)
            mb.box(mid+N*(OUT+0.145), U, N, w-0.01, 0.05, z, z+0.12, 0)
            mb.box(mid+N*(OUT+0.15), U, N, w-0.02, 0.025, z-0.035, z, 1)
            mb.done(); extra+=1
    log['fixes'].append(f'N_extra_lips_{extra}')

# Widen sky tint cards: rebuild slightly wider (delete+recreate)
e1=[e for e in OSM['edges'] if e['i']==1][0]
U1=Vector((e1['u'][0],e1['u'][1],0)).normalized()
N1=Vector((e1['n'][0],e1['n'][1],0)).normalized()
A1=Vector((e1['a'][0],e1['a'][1],0))
L1=e1['len']
for o in list(bpy.data.objects):
    if o.get('vf_obj') and 'VF_Freeman_W_sky_tint_' in o.name:
        me=o.data; bpy.data.objects.remove(o, do_unlink=True)
        if me and me.users==0: bpy.data.meshes.remove(me)
centers=[]
for i in range(max(1,int((L1-4.0)/3.6))):
    t=2.0+3.6*(i+0.5)
    if t>L1-2.0: break
    centers.append(t)
nsky=0
if col and sky:
    for i,t in enumerate(centers):
        c=A1+U1*t
        mb=MB(f'VF_Freeman_W_sky_tint_{i:02d}_UNVERIFIED',[sky],col)
        mb.box(c+N1*0.14, U1, N1, 1.28, 0.022, GR+0.85, TOPZ-0.40, 0)
        mb.done(); nsky+=1
    log['fixes'].append(f'rebuild_sky_tint_wider_{nsky}')

# Re-aim W closeup more frontal / mid-bay
t=centers[max(0,len(centers)//3)]
c=A1+U1*t
cam=bpy.data.objects.get('VF_CAM_closeup_Freeman_W_glass_sky')
if cam:
    cam.location=(c.x+N1.x*8.0 - U1.x*0.3, c.y+N1.y*8.0 - U1.y*0.3, GR+6.8)
    target=(c.x+N1.x*(OUT+0.20), c.y+N1.y*(OUT+0.20), GR+8.5)
    cam.rotation_euler=(Vector(target)-Vector(cam.location)).to_track_quat('-Z','Y').to_euler()
    cam.data.lens=45
    log['fixes'].append(f'reaim_W_closeup_frontal_t{t:.2f}')

# N cream closeup nudge
scr=A+U*6.85
ncam=bpy.data.objects.get('VF_CAM_closeup_Freeman_N_cream_punch')
if ncam:
    ncam.location=(scr.x+N.x*9.5 - U.x*1.2, scr.y+N.y*9.5 - U.y*1.2, GR+5.0)
    tgt=(scr.x, scr.y, GR+8.0)
    ncam.rotation_euler=(Vector(tgt)-Vector(ncam.location)).to_track_quat('-Z','Y').to_euler()
    ncam.data.lens=40
    log['fixes'].append('reaim_N_cream_closeup')

log['n_objects']=len(bpy.data.objects)
log['n_vf_obj']=sum(1 for o in bpy.data.objects if o.get('vf_obj'))
json.dump(log, open(DATA+'/vf_polish2.json','w'), indent=2)
print('VF POLISH2', json.dumps(log))
print('OBJECTS', len(bpy.data.objects))
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED')
