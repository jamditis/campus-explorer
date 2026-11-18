"""ve polish after WIP self-review. SAVE=1 saves. REVERT no-op (ve_main handles)."""
import bpy, os, json
from mathutils import Vector
REV = os.environ.get('REVERT') == '1'
SAVE = os.environ.get('SAVE') == '1'
DATA='/workspace/nj-scenes/montclair-state/data/ve'
OSM=json.load(open('/workspace/nj-scenes/montclair-state/data/uv/freeman_osm_probe.json'))
GR=float(json.load(open('/workspace/nj-scenes/montclair-state/data/uv/uv_main.json')).get('GR',129.053))
OUT=0.08
log={'session':'ve_polish','fixes':[]}
if REV:
    print('VE POLISH REVERT: no-op')
    raise SystemExit

# Nudge W close-up if present; mild glass alpha bump if still too dark
g=bpy.data.materials.get('VD_Freeman_W_glass_pane_UNVERIFIED')
if g and g.use_nodes:
    b=g.node_tree.nodes.get('Principled BSDF')
    if b:
        # slight further sky bias if review still dark
        a=b.inputs['Alpha'].default_value
        if a < 0.52:
            b.inputs['Alpha'].default_value=0.52
            log['fixes'].append('W_glass_alpha_0.52')
        if 'Coat Weight' in b.inputs and b.inputs['Coat Weight'].default_value < 0.6:
            b.inputs['Coat Weight'].default_value=0.60
            log['fixes'].append('W_glass_coat_0.60')

# Re-aim W close-up onto bay + interbay
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
    cam.location=(c.x+N1.x*6.5 - U1.x*0.55, c.y+N1.y*6.5 - U1.y*0.55, GR+5.7)
    target=(c.x+N1.x*(OUT+0.22), c.y+N1.y*(OUT+0.22), GR+7.5)
    cam.rotation_euler=(Vector(target)-Vector(cam.location)).to_track_quat('-Z','Y').to_euler()
    cam.data.lens=46
    log['fixes'].append(f'reaim_W_closeup_t{t:.2f}')

json.dump(log, open(DATA+'/ve_polish.json','w'), indent=2)
print('VE POLISH', json.dumps(log))
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED')
