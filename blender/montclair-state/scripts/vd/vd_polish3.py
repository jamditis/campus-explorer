"""vd polish3: spandrel was as dark as glass → grid died. Restore terracotta spandrel
contrast; glass more sky-reflective (vc-style alpha) so panes read vs cream.
SAVE=1.
"""
import bpy, os, json
from mathutils import Vector
SAVE = os.environ.get('SAVE') == '1'
DATA='/workspace/nj-scenes/montclair-state/data/vd'
OSM=json.load(open('/workspace/nj-scenes/montclair-state/data/uv/freeman_osm_probe.json'))
GR=float(json.load(open('/workspace/nj-scenes/montclair-state/data/uv/uv_main.json')).get('GR',129.053))
OUT=0.08
log={'session':'vd_polish3','fixes':[]}

# Terracotta/orange spandrel so glass bands alternate visibly (slide 1114 language)
s=bpy.data.materials.get('VD_Freeman_W_spandrel_deep_UNVERIFIED')
if s and s.use_nodes:
    b=s.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Base Color'].default_value=(0.62, 0.28, 0.14, 1.0)
        b.inputs['Roughness'].default_value=0.72
        if 'Specular IOR Level' in b.inputs:
            b.inputs['Specular IOR Level'].default_value=0.18
        log['fixes'].append('spandrel_terracotta_contrast')

# Glass: sky-read like vc (alpha ~0.36) + cool tint; keep transmission
g=bpy.data.materials.get('VD_Freeman_W_glass_pane_UNVERIFIED')
if g and g.use_nodes:
    b=g.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Base Color'].default_value=(0.70, 0.84, 0.95, 1.0)
        b.inputs['Alpha'].default_value=0.36
        b.inputs['Roughness'].default_value=0.018
        if 'Transmission Weight' in b.inputs:
            b.inputs['Transmission Weight'].default_value=1.0
        if 'Coat Weight' in b.inputs:
            b.inputs['Coat Weight'].default_value=0.30
            b.inputs['Coat Roughness'].default_value=0.03
        if 'Specular IOR Level' in b.inputs:
            b.inputs['Specular IOR Level'].default_value=0.7
        log['fixes'].append('W_glass_sky_alpha0.36')

# Reveal stay near-black for lip contrast
r=bpy.data.materials.get('VD_Freeman_W_reveal_dark_UNVERIFIED')
if r and r.use_nodes:
    b=r.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Base Color'].default_value=(0.015, 0.012, 0.010, 1.0)
        log['fixes'].append('reveal_near_black')

# Close-up: slightly off-center to catch pane+spandrel+mullion together, not dead-on dark
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
cam=bpy.data.objects.get('VD_CAM_closeup_Freeman_W_pane_grid')
if cam:
    # offset along U a bit so left cream + bay both read; aim mid glass band
    cam.location=(c.x+N1.x*6.8 - U1.x*0.35, c.y+N1.y*6.8 - U1.y*0.35, GR+5.8)
    target=(c.x+N1.x*(OUT+0.22), c.y+N1.y*(OUT+0.22), GR+7.8)
    cam.rotation_euler=(Vector(target)-Vector(cam.location)).to_track_quat('-Z','Y').to_euler()
    cam.data.lens=48
    log['fixes'].append(f'reaim_W_closeup_offset_t{t:.2f}')

json.dump(log, open(DATA+'/vd_polish3.json','w'), indent=2)
print('VD POLISH3', json.dumps(log))
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED')
