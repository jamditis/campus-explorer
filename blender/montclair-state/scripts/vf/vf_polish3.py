"""vf polish3: replace per-bay sky cards with one continuous sheet (kill sawtooth);
re-aim W closeup like successful VE framing; keep glass/N punch. SAVE=1.
"""
import bpy, os, json, bmesh
from mathutils import Vector
SAVE = os.environ.get('SAVE') == '1'
D='/workspace/nj-scenes/montclair-state/'
DATA=D+'data/vf'
OSM=json.load(open(D+'data/uv/freeman_osm_probe.json'))
GR=float(json.load(open(D+'data/uv/uv_main.json')).get('GR',129.053))
OUT=0.08; TOPZ=147.05
log={'session':'vf_polish3','fixes':[]}

COL='VF_Freeman_polish_UNVERIFIED'
col=bpy.data.collections.get(COL)
sky=bpy.data.materials.get('VF_Freeman_W_sky_tint_UNVERIFIED')

# remove all per-bay sky tint cards
for o in list(bpy.data.objects):
    if o.get('vf_obj') and 'VF_Freeman_W_sky_tint_' in o.name:
        me=o.data; bpy.data.objects.remove(o, do_unlink=True)
        if me and me.users==0: bpy.data.meshes.remove(me)
log['fixes'].append('removed_per_bay_sky_cards')

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
        o['vf_obj']=1; o['UNVERIFIED']='vf polish3 continuous sky; UNVERIFIED'
        for p in me.polygons: p.use_smooth=False
        return o

e1=[e for e in OSM['edges'] if e['i']==1][0]
U1=Vector((e1['u'][0],e1['u'][1],0)).normalized()
N1=Vector((e1['n'][0],e1['n'][1],0)).normalized()
A1=Vector((e1['a'][0],e1['a'][1],0))
L1=e1['len']
# continuous sheet spanning bay centers region (inset from corners)
t0,t1=2.5, L1-2.5
mid=A1+U1*((t0+t1)/2)
w=t1-t0
if col and sky:
    # tonedown emission a bit so continuous sheet isn't a glowing slab
    b=sky.node_tree.nodes.get('Principled BSDF')
    if b:
        if 'Emission Strength' in b.inputs:
            b.inputs['Emission Strength'].default_value=1.1
        b.inputs['Base Color'].default_value=(0.68,0.80,0.95,1.0)
        if 'Emission Color' in b.inputs:
            b.inputs['Emission Color'].default_value=(0.70,0.82,0.96,1.0)
        log['fixes'].append('sky_tint_emiss_1.1_continuous')
    mb=MB('VF_Freeman_W_sky_tint_continuous_UNVERIFIED',[sky],col)
    mb.box(mid+N1*0.14, U1, N1, w, 0.02, GR+0.90, TOPZ-0.40, 0)
    mb.done()
    log['fixes'].append(f'continuous_sky_sheet_w{w:.1f}')

# Soften glass slightly if continuous sheet glows — keep alpha 0.62 (between 0.55 and 0.65)
g=bpy.data.materials.get('VD_Freeman_W_glass_pane_UNVERIFIED')
if g and g.use_nodes:
    b=g.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Alpha'].default_value=0.60
        b.inputs['Base Color'].default_value=(0.58,0.76,0.94,1.0)
        if 'Coat Weight' in b.inputs:
            b.inputs['Coat Weight'].default_value=0.80
        log['fixes'].append('W_glass_alpha0.60_coat0.80_balance')

# Re-aim W closeup like VE polish3 (worked for framing)
centers=[]
for i in range(max(1,int((L1-4.0)/3.6))):
    t=2.0+3.6*(i+0.5)
    if t>L1-2.0: break
    centers.append(t)
t=centers[max(0,len(centers)//3)]
c=A1+U1*t
cam=bpy.data.objects.get('VF_CAM_closeup_Freeman_W_glass_sky')
if cam:
    cam.location=(c.x+N1.x*9.5 - U1.x*1.1, c.y+N1.y*9.5 - U1.y*1.1, GR+5.2)
    target=(c.x+N1.x*(OUT+0.12), c.y+N1.y*(OUT+0.12), GR+7.2)
    cam.rotation_euler=(Vector(target)-Vector(cam.location)).to_track_quat('-Z','Y').to_euler()
    cam.data.lens=40
    log['fixes'].append(f'reaim_W_closeup_VE_style_t{t:.2f}')

log['n_objects']=len(bpy.data.objects)
log['n_vf_obj']=sum(1 for o in bpy.data.objects if o.get('vf_obj'))
# lettering guard
let=bpy.data.objects.get('UV_Freeman_N_lettering_GRACE_H_FREEMAN_HALL_UNVERIFIED')
if let:
    mw=let.matrix_world
    log['letter']={'body':let.data.body,'size':round(let.data.size,6),'loc':[round(mw[i][3],4) for i in range(3)]}
json.dump(log, open(DATA+'/vf_polish3.json','w'), indent=2)
print('VF POLISH3', json.dumps(log))
print('OBJECTS', len(bpy.data.objects))
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED')
