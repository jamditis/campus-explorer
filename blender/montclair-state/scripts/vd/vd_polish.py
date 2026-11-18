"""vd polish after WIP self-review. SAVE=1 saves. REVERT no-op (vd_main handles)."""
import bpy, os, json
from mathutils import Vector
REV = os.environ.get('REVERT') == '1'
SAVE = os.environ.get('SAVE') == '1'
DATA='/workspace/nj-scenes/montclair-state/data/vd'
OSM=json.load(open('/workspace/nj-scenes/montclair-state/data/uv/freeman_osm_probe.json'))
GR=float(json.load(open('/workspace/nj-scenes/montclair-state/data/uv/uv_main.json')).get('GR',129.053))
OUT=0.08
log={'session':'vd_polish','fixes':[]}
if REV:
    print('VD POLISH REVERT: no-op')
    raise SystemExit

# Ensure W glass reads clear against dark BP / deep spandrel
g=bpy.data.materials.get('VD_Freeman_W_glass_pane_UNVERIFIED')
if g and g.use_nodes:
    b=g.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Alpha'].default_value=0.30
        b.inputs['Roughness'].default_value=0.012
        if 'Coat Weight' in b.inputs:
            b.inputs['Coat Weight'].default_value=0.40
        log['fixes'].append('W_glass_alpha_0.30_coat')

# Spandrel deeper contrast
s=bpy.data.materials.get('VD_Freeman_W_spandrel_deep_UNVERIFIED')
if s and s.use_nodes:
    b=s.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Base Color'].default_value=(0.36, 0.13, 0.08, 1.0)
        b.inputs['Roughness'].default_value=0.82
        log['fixes'].append('spandrel_deeper')

# Re-aim W close-up onto a mid bay
e1=[e for e in OSM['edges'] if e['i']==1][0]
U1=Vector((e1['u'][0],e1['u'][1],0)).normalized()
N1=Vector((e1['n'][0],e1['n'][1],0)).normalized()
A1=Vector((e1['a'][0],e1['a'][1],0))
L1=e1['len']
pitch=3.6
centers=[]
n_bays=max(1,int((L1-4.0)/pitch))
for i in range(n_bays):
    t=2.0+pitch*(i+0.5)
    if t>L1-2.0: break
    centers.append(t)
t=centers[len(centers)//3] if centers else 14.6
c=A1+U1*t
cam=bpy.data.objects.get('VD_CAM_closeup_Freeman_W_pane_grid')
if cam:
    cam.location=(c.x+N1.x*4.8, c.y+N1.y*4.8, GR+5.5)
    target=(c.x+N1.x*(OUT+0.22), c.y+N1.y*(OUT+0.22), GR+7.0)
    cam.rotation_euler=(Vector(target)-Vector(cam.location)).to_track_quat('-Z','Y').to_euler()
    cam.data.lens=58
    log['fixes'].append(f'reaim_W_closeup_t{t:.1f}')

json.dump(log, open(DATA+'/vd_polish.json','w'), indent=2)
print('VD POLISH', json.dumps(log))
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED')
