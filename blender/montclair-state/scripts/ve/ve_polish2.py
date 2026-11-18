"""ve polish2: fix black cream mats (Material Output was unlinked) + re-aim W closeup.
SAVE=1 saves.
"""
import bpy, os, json
from mathutils import Vector
SAVE = os.environ.get('SAVE') == '1'
DATA='/workspace/nj-scenes/montclair-state/data/ve'
OSM=json.load(open('/workspace/nj-scenes/montclair-state/data/uv/freeman_osm_probe.json'))
GR=float(json.load(open('/workspace/nj-scenes/montclair-state/data/uv/uv_main.json')).get('GR',129.053))
OUT=0.08
log={'session':'ve_polish2','fixes':[]}

def fix_mat_output(mat_name):
    m=bpy.data.materials.get(mat_name)
    if not m or not m.use_nodes: return False
    nt=m.node_tree
    bsdf=None; out=None
    for n in nt.nodes:
        if n.type=='BSDF_PRINCIPLED': bsdf=n
        if n.type=='OUTPUT_MATERIAL': out=n
    if not bsdf: return False
    if not out:
        out=nt.nodes.new('ShaderNodeOutputMaterial')
        out.location=(300,200)
    # ensure BSDF -> Output
    linked=False
    for l in nt.links:
        if l.from_node==bsdf and l.to_node==out:
            linked=True; break
    if not linked:
        nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
        return True
    return False

for name in ('VE_Freeman_W_cream_soft_UNVERIFIED','VE_Freeman_N_cream_depth_UNVERIFIED','VE_Freeman_shadow_lip_UNVERIFIED'):
    if fix_mat_output(name):
        log['fixes'].append(f'fix_output_{name}')
    else:
        # still verify link exists
        m=bpy.data.materials.get(name)
        if m and m.use_nodes:
            nt=m.node_tree
            ok=any(l.to_node.type=='OUTPUT_MATERIAL' for l in nt.links)
            log['fixes'].append(f'output_ok_{name}' if ok else f'output_MISSING_{name}')

# Also ensure brick Color still feeds Base Color
for name in ('VE_Freeman_W_cream_soft_UNVERIFIED','VE_Freeman_N_cream_depth_UNVERIFIED'):
    m=bpy.data.materials.get(name)
    if not m or not m.use_nodes: continue
    nt=m.node_tree
    bsdf=nt.nodes.get('Principled BSDF')
    brick=None; bump=None; mapping=None; texcoord=None
    for n in nt.nodes:
        if n.type=='TEX_BRICK': brick=n
        if n.type=='BUMP': bump=n
        if n.type=='MAPPING': mapping=n
        if n.type=='TEX_COORD': texcoord=n
    if bsdf and brick:
        # relink if needed
        has_col=any(l.to_node==bsdf and l.to_socket.name=='Base Color' for l in nt.links)
        if not has_col:
            nt.links.new(brick.outputs['Color'], bsdf.inputs['Base Color'])
            log['fixes'].append(f'relink_base_{name}')
        if bump:
            has_n=any(l.to_node==bsdf and l.to_socket.name=='Normal' for l in nt.links)
            if not has_n:
                nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
                nt.links.new(brick.outputs['Color'], bump.inputs['Height'])
                log['fixes'].append(f'relink_bump_{name}')
        if mapping and texcoord and brick:
            has_v=any(l.to_node==brick and l.to_socket.name=='Vector' for l in nt.links)
            if not has_v:
                nt.links.new(texcoord.outputs['Object'], mapping.inputs['Vector'])
                nt.links.new(mapping.outputs['Vector'], brick.inputs['Vector'])
                log['fixes'].append(f'relink_vec_{name}')
    # Prefer Generated over Object for more stable brick scale on large skins
    if texcoord and mapping:
        # switch to Generated
        for l in list(nt.links):
            if l.to_node==mapping and l.to_socket.name=='Vector':
                nt.links.remove(l)
        nt.links.new(texcoord.outputs['Generated'], mapping.inputs['Vector'])
        mapping.inputs['Scale'].default_value=(4.5, 4.5, 4.5)
        log['fixes'].append(f'use_Generated_{name}')

# Soften shadow lip so it doesn't chalk-black against cream
sh=bpy.data.materials.get('VE_Freeman_shadow_lip_UNVERIFIED')
if sh and sh.use_nodes:
    b=sh.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Base Color'].default_value=(0.22, 0.18, 0.14, 1.0)
        log['fixes'].append('shadow_lip_warmer')

# Re-aim W close-up: stand farther, look at facade face (not up into bay cavity)
e1=[e for e in OSM['edges'] if e['i']==1][0]
U1=Vector((e1['u'][0],e1['u'][1],0)).normalized()
N1=Vector((e1['n'][0],e1['n'][1],0)).normalized()
A1=Vector((e1['a'][0],e1['a'][1],0))
L1=e1['len']
centers=[]
for i in range(max(1,int((L1-4.0)/3.6))):
    t=2.0+3.6*(i+0.5)
    if t>L1-2.0: break
    centers.append(t)
t=centers[max(0,len(centers)//3)]
c=A1+U1*t
cam=bpy.data.objects.get('VE_CAM_closeup_Freeman_W_cream_glass')
if cam:
    # eye-height-ish, farther, slight U offset to catch interbay cream + bay
    cam.location=(c.x+N1.x*8.5 - U1.x*0.9, c.y+N1.y*8.5 - U1.y*0.9, GR+6.5)
    target=(c.x+N1.x*(OUT+0.15), c.y+N1.y*(OUT+0.15), GR+8.0)
    cam.rotation_euler=(Vector(target)-Vector(cam.location)).to_track_quat('-Z','Y').to_euler()
    cam.data.lens=42
    log['fixes'].append(f'reaim_W_closeup_far_t{t:.2f}_lens42')

# Also nudge N cream closeup
e6=[e for e in OSM['edges'] if e['i']==6][0]
U=Vector((e6['u'][0],e6['u'][1],0)).normalized()
N=Vector((e6['n'][0],e6['n'][1],0)).normalized()
A=Vector((e6['a'][0],e6['a'][1],0))
scr=A+U*6.85
ncam=bpy.data.objects.get('VE_CAM_closeup_Freeman_N_cream_depth')
if ncam:
    ncam.location=(scr.x+N.x*10.5 - U.x*2.0, scr.y+N.y*10.5 - U.y*2.0, GR+4.5)
    tgt=(scr.x, scr.y, GR+7.5)
    ncam.rotation_euler=(Vector(tgt)-Vector(ncam.location)).to_track_quat('-Z','Y').to_euler()
    ncam.data.lens=38
    log['fixes'].append('reaim_N_cream_closeup')

json.dump(log, open(DATA+'/ve_polish2.json','w'), indent=2)
print('VE POLISH2', json.dumps(log))
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED')
