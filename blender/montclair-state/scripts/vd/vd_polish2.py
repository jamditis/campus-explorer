"""vd polish2 after WIP review: W close-up was on cream stripe / copper glass;
pull cam back onto bay center; clear glass; deepen frame vs cream.
SAVE=1 saves.
"""
import bpy, os, json
from mathutils import Vector
SAVE = os.environ.get('SAVE') == '1'
DATA='/workspace/nj-scenes/montclair-state/data/vd'
OSM=json.load(open('/workspace/nj-scenes/montclair-state/data/uv/freeman_osm_probe.json'))
GR=float(json.load(open('/workspace/nj-scenes/montclair-state/data/uv/uv_main.json')).get('GR',129.053))
OUT=0.08
log={'session':'vd_polish2','fixes':[]}

# Clearer cooler glass (less copper read)
g=bpy.data.materials.get('VD_Freeman_W_glass_pane_UNVERIFIED')
if g and g.use_nodes:
    b=g.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Base Color'].default_value=(0.78, 0.88, 0.96, 1.0)
        b.inputs['Alpha'].default_value=0.26
        b.inputs['Roughness'].default_value=0.01
        if 'Transmission Weight' in b.inputs:
            b.inputs['Transmission Weight'].default_value=1.0
        if 'Coat Weight' in b.inputs:
            b.inputs['Coat Weight'].default_value=0.45
            b.inputs['Coat Roughness'].default_value=0.02
        if 'Specular IOR Level' in b.inputs:
            b.inputs['Specular IOR Level'].default_value=0.85
        log['fixes'].append('W_glass_clearer_cooler_alpha0.26')

# Frame darker so pane grid punches against cream
f=bpy.data.materials.get('VD_Freeman_W_frame_dark_UNVERIFIED')
if f and f.use_nodes:
    b=f.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Base Color'].default_value=(0.03, 0.025, 0.022, 1.0)
        log['fixes'].append('frame_darker')
# also punch UV darkred frame used on mesh
f2=bpy.data.materials.get('UV_Freeman_window_frame_darkred_UNVERIFIED')
if f2 and f2.use_nodes:
    # stash once
    stash=DATA+'/vd_uy_frame_stash.json'
    b=f2.node_tree.nodes.get('Principled BSDF')
    if b:
        if not os.path.exists(stash):
            json.dump({'Base Color':list(b.inputs['Base Color'].default_value),
                       'Roughness':b.inputs['Roughness'].default_value}, open(stash,'w'))
        b.inputs['Base Color'].default_value=(0.08, 0.04, 0.035, 1.0)
        b.inputs['Roughness'].default_value=0.55
        log['fixes'].append('UV_frame_darker_for_W_grid')

# Spandrel keep deep but not copper-glowing
s=bpy.data.materials.get('VD_Freeman_W_spandrel_deep_UNVERIFIED')
if s and s.use_nodes:
    b=s.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Base Color'].default_value=(0.32, 0.12, 0.08, 1.0)
        b.inputs['Roughness'].default_value=0.85
        if 'Specular IOR Level' in b.inputs:
            b.inputs['Specular IOR Level'].default_value=0.08
        log['fixes'].append('spandrel_matte_deep')

# Soften W cream interbay skin so it doesn't stripe harder than panes
# (material is VB cream shared — don't flatten N). Instead slightly push hide? 
# Better: leave cream; camera + glass fix is enough.
# Optional: scale Mapping on a COPY — skip to avoid N regression.

# Re-aim W close-up: farther, centered on bay glass mid-height
e1=[e for e in OSM['edges'] if e['i']==1][0]
U1=Vector((e1['u'][0],e1['u'][1],0)).normalized()
N1=Vector((e1['n'][0],e1['n'][1],0)).normalized()
A1=Vector((e1['a'][0],e1['a'][1],0))
L1=e1['len']
pitch=3.6
centers=[]
for i in range(max(1,int((L1-4.0)/pitch))):
    t=2.0+pitch*(i+0.5)
    if t>L1-2.0: break
    centers.append(t)
# pick bay near 1/3 — confirm it's a window center
t=centers[max(0, len(centers)//3)]
c=A1+U1*t
cam=bpy.data.objects.get('VD_CAM_closeup_Freeman_W_pane_grid')
if cam:
    # stand farther so full bay width + neighbors cream context
    cam.location=(c.x+N1.x*7.5, c.y+N1.y*7.5, GR+6.2)
    target=(c.x+N1.x*(OUT+0.22), c.y+N1.y*(OUT+0.22), GR+8.0)
    cam.rotation_euler=(Vector(target)-Vector(cam.location)).to_track_quat('-Z','Y').to_euler()
    cam.data.lens=50
    log['fixes'].append(f'reaim_W_closeup_far_t{t:.2f}_lens50')

# Also nudge W eye slightly higher to catch mid glass bands
eye=bpy.data.objects.get('UY_CAM_eye_Freeman_W_side')
if eye and centers:
    t2=centers[len(centers)//2]
    c2=A1+U1*t2
    eye.location=(c2.x+N1.x*26, c2.y+N1.y*26, GR+4.2)
    tgt=(c2.x, c2.y, GR+9.5)
    eye.rotation_euler=(Vector(tgt)-Vector(eye.location)).to_track_quat('-Z','Y').to_euler()
    log['fixes'].append('nudge_W_eye_cam')

json.dump(log, open(DATA+'/vd_polish2.json','w'), indent=2)
print('VD POLISH2', json.dumps(log))
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED')
