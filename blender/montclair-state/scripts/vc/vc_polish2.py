"""vc polish2 after WIP review: glass was reading as solid dark panels — restore sky reflection
while keeping dark backplanes; re-aim W close-up onto a glass bay center.
SAVE=1 saves.
"""
import bpy, os, json
from mathutils import Vector
SAVE = os.environ.get('SAVE') == '1'
DATA='/workspace/nj-scenes/montclair-state/data/vc'
OSM=json.load(open('/workspace/nj-scenes/montclair-state/data/uv/freeman_osm_probe.json'))
GR=float(json.load(open('/workspace/nj-scenes/montclair-state/data/uv/uv_main.json')).get('GR',129.053))
OUT=0.08
log={'session':'vc_polish2','fixes':[]}

# Glass: more reflective/see-through so sky+dark void both read (not solid charcoal slab)
g=bpy.data.materials.get('VB_Freeman_glass_cool_clear_UNVERIFIED')
if g and g.use_nodes:
    b=g.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Base Color'].default_value=(0.72, 0.84, 0.93, 1.0)
        b.inputs['Roughness'].default_value=0.02
        b.inputs['Alpha'].default_value=0.38  # was 0.22 — too solid with dark BP
        if 'Transmission Weight' in b.inputs:
            b.inputs['Transmission Weight'].default_value=1.0
        elif 'Transmission' in b.inputs:
            b.inputs['Transmission'].default_value=1.0
        if 'Coat Weight' in b.inputs:
            b.inputs['Coat Weight'].default_value=0.25
            b.inputs['Coat Roughness'].default_value=0.04
        try: b.inputs['Specular IOR Level'].default_value=0.7
        except Exception: pass
        log['fixes'].append('glass_alpha_0.38_coat_refl')

# Backplane: keep dark but tiny lift so not crushed black
d=bpy.data.materials.get('VC_Freeman_glass_backplane_dark_UNVERIFIED')
if d and d.use_nodes:
    b=d.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Base Color'].default_value=(0.035, 0.036, 0.040, 1.0)
        log['fixes'].append('backplane_soft_charcoal')

# Re-aim close-up onto mid W bay glass (centers_w[3] ~14.6)
e1=[e for e in OSM['edges'] if e['i']==1][0]
U1=Vector((e1['u'][0],e1['u'][1],0)).normalized()
N1=Vector((e1['n'][0],e1['n'][1],0)).normalized()
A1=Vector((e1['a'][0],e1['a'][1],0))
t=14.6  # bay center
c=A1+U1*t
# stand in front of glass plane (glass at OUT+0.18)
cam=bpy.data.objects.get('VC_CAM_closeup_Freeman_W_glass_backplane')
if cam:
    loc=c + N1*5.5 + Vector((0,0,GR+5.5-c.z if False else 0))
    # location: out from wall + eye height
    cam.location = (c.x + N1.x*5.2, c.y + N1.y*5.2, GR + 5.8)
    target = (c.x + N1.x*(OUT+0.18), c.y + N1.y*(OUT+0.18), GR + 7.5)
    direction = Vector(target) - Vector(cam.location)
    cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    cam.data.lens = 55
    log['fixes'].append('reaim_W_glass_closeup_t14.6')

# Also bump N midwall cream close-up unused in final four — leave

json.dump(log, open(DATA+'/vc_polish2.json','w'), indent=2)
print('VC POLISH2', json.dumps(log))
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED')
