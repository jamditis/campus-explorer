"""ve polish3: flatten W/S cream (brick→soft stucco) so interbay stops fluting;
glass more sky-reflective; keep N depth overlays. SAVE=1.
"""
import bpy, os, json
from mathutils import Vector
SAVE = os.environ.get('SAVE') == '1'
DATA='/workspace/nj-scenes/montclair-state/data/ve'
OSM=json.load(open('/workspace/nj-scenes/montclair-state/data/uv/freeman_osm_probe.json'))
GR=float(json.load(open('/workspace/nj-scenes/montclair-state/data/uv/uv_main.json')).get('GR',129.053))
OUT=0.08
log={'session':'ve_polish3','fixes':[]}

def rebuild_stucco(mat_name, color1=(0.78,0.72,0.58,1), color2=(0.72,0.66,0.54,1), rough=0.90):
    m=bpy.data.materials.get(mat_name)
    if not m: return False
    m.use_nodes=True
    nt=m.node_tree
    # wipe nodes except keep material
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out=nt.nodes.new('ShaderNodeOutputMaterial'); out.location=(400,200)
    b=nt.nodes.new('ShaderNodeBsdfPrincipled'); b.location=(100,200); b.name='Principled BSDF'
    # subtle noise variation instead of brick fluting
    noise=nt.nodes.new('ShaderNodeTexNoise'); noise.location=(-500,200)
    noise.inputs['Scale'].default_value=12.0
    noise.inputs['Detail'].default_value=6.0
    noise.inputs['Roughness'].default_value=0.55
    ramp=nt.nodes.new('ShaderNodeValToRGB'); ramp.location=(-250,200)
    ramp.color_ramp.elements[0].position=0.35
    ramp.color_ramp.elements[0].color=color2
    ramp.color_ramp.elements[1].position=0.75
    ramp.color_ramp.elements[1].color=color1
    bump=nt.nodes.new('ShaderNodeBump'); bump.location=(-50,50)
    bump.inputs['Strength'].default_value=0.08
    bump.inputs['Distance'].default_value=0.002
    texcoord=nt.nodes.new('ShaderNodeTexCoord'); texcoord.location=(-700,200)
    mapping=nt.nodes.new('ShaderNodeMapping'); mapping.location=(-600,200)
    mapping.inputs['Scale'].default_value=(1.0,1.0,1.0)
    nt.links.new(texcoord.outputs['Generated'], mapping.inputs['Vector'])
    nt.links.new(mapping.outputs['Vector'], noise.inputs['Vector'])
    nt.links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], b.inputs['Base Color'])
    nt.links.new(noise.outputs['Fac'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], b.inputs['Normal'])
    nt.links.new(b.outputs['BSDF'], out.inputs['Surface'])
    b.inputs['Roughness'].default_value=rough
    if 'Specular IOR Level' in b.inputs:
        b.inputs['Specular IOR Level'].default_value=0.18
    return True

if rebuild_stucco('VE_Freeman_W_cream_soft_UNVERIFIED'):
    log['fixes'].append('W_cream_soft_to_stucco_noise')
if rebuild_stucco('VE_Freeman_N_cream_depth_UNVERIFIED',
                  color1=(0.70,0.64,0.50,1), color2=(0.58,0.52,0.40,1), rough=0.88):
    log['fixes'].append('N_cream_depth_to_stucco_noise')

# Glass: more reflective sky read at grazing
g=bpy.data.materials.get('VD_Freeman_W_glass_pane_UNVERIFIED')
if g and g.use_nodes:
    b=g.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Base Color'].default_value=(0.55,0.72,0.90,1.0)
        b.inputs['Alpha'].default_value=0.55
        b.inputs['Roughness'].default_value=0.015
        if 'Coat Weight' in b.inputs:
            b.inputs['Coat Weight'].default_value=0.70
            b.inputs['Coat Roughness'].default_value=0.02
        if 'Specular IOR Level' in b.inputs:
            b.inputs['Specular IOR Level'].default_value=1.0
        log['fixes'].append('W_glass_alpha0.55_coat0.70')

# Spandrel slightly brighter terracotta for contrast vs softer cream
s=bpy.data.materials.get('VD_Freeman_W_spandrel_deep_UNVERIFIED')
if s and s.use_nodes:
    b=s.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Base Color'].default_value=(0.72,0.34,0.16,1.0)
        log['fixes'].append('spandrel_brighter_terracotta')

# Hide the tall interbay cream COVER boxes (they read as fluted columns); keep shadow edge objs only
# Interbay objs named VE_Freeman_W_interbay_soft_XX — each has cream cover + shadow edges in ONE mesh.
# Better: reduce cream cover depth visually by swapping whole interbay to mostly flat + thinner.
# Simplest: set interbay object materials to soft stucco already rebuilt; also scale down visual
# by replacing with thinner soft covers via material only — already stucco now.
# Additionally hide every other interbay if still heavy? Keep all — stucco should fix fluting.

# Re-aim W closeup slightly lower / more frontal
e1=[e for e in OSM['edges'] if e['i']==1][0]
U1=Vector((e1['u'][0],e1['u'][1],0)).normalized()
N1=Vector((e1['n'][0],e1['n'][1],0)).normalized()
A1=Vector((e1['a'][0],e1['a'][1],0))
centers=[]
for i in range(max(1,int((e1['len']-4.0)/3.6))):
    t=2.0+3.6*(i+0.5)
    if t>e1['len']-2.0: break
    centers.append(t)
t=centers[max(0,len(centers)//3)]
c=A1+U1*t
cam=bpy.data.objects.get('VE_CAM_closeup_Freeman_W_cream_glass')
if cam:
    cam.location=(c.x+N1.x*9.5 - U1.x*1.1, c.y+N1.y*9.5 - U1.y*1.1, GR+5.2)
    target=(c.x+N1.x*(OUT+0.12), c.y+N1.y*(OUT+0.12), GR+7.2)
    cam.rotation_euler=(Vector(target)-Vector(cam.location)).to_track_quat('-Z','Y').to_euler()
    cam.data.lens=40
    log['fixes'].append(f'reaim_W_closeup_frontal_t{t:.2f}')

json.dump(log, open(DATA+'/ve_polish3.json','w'), indent=2)
print('VE POLISH3', json.dumps(log))
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED')
