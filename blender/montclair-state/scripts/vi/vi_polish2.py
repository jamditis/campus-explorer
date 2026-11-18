"""vi polish2: reframe W glass closeup to show more panes + mild sky/coat nudge. SAVE=1."""
import bpy, os, json
from mathutils import Vector
SAVE = os.environ.get('SAVE') == '1'
D = '/workspace/nj-scenes/montclair-state/'
DATA = D + 'data/vi'
OSM = json.load(open(D + 'data/uv/freeman_osm_probe.json'))
GR = float(json.load(open(D + 'data/uv/uv_main.json')).get('GR', 129.053))
OUT = 0.08
log = {'session': 'vi_polish2', 'fixes': []}

# Mild clearer glass — keep reflective Coat/Spec from polish
wg = bpy.data.materials.get('VD_Freeman_W_glass_pane_UNVERIFIED')
if wg and wg.use_nodes:
    b = wg.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Alpha'].default_value = 0.32
        if 'Coat Weight' in b.inputs:
            b.inputs['Coat Weight'].default_value = 1.0
            b.inputs['Coat Roughness'].default_value = 0.006
        if 'Specular IOR Level' in b.inputs:
            b.inputs['Specular IOR Level'].default_value = 1.20
        b.inputs['Base Color'].default_value = (0.86, 0.95, 1.0, 1.0)
        b.inputs['Roughness'].default_value = 0.002
        log['fixes'].append('W_glass_Alpha0.32_Coat1.0_Spec1.20')
        log['W_glassA'] = 0.32

sky = bpy.data.materials.get('VF_Freeman_W_sky_tint_UNVERIFIED')
if sky and sky.use_nodes:
    b = sky.node_tree.nodes.get('Principled BSDF')
    if b:
        if 'Emission Strength' in b.inputs:
            b.inputs['Emission Strength'].default_value = 2.05
        b.inputs['Alpha'].default_value = 0.38
        log['fixes'].append('sky_emiss2.05_Alpha0.38')

# Reframe W glass: less extreme grazing so panes fill frame; still show coat/sky
e1 = [e for e in OSM['edges'] if e['i'] == 1][0]
U1 = Vector((e1['u'][0], e1['u'][1], 0)).normalized()
N1 = Vector((e1['n'][0], e1['n'][1], 0)).normalized()
A1 = Vector((e1['a'][0], e1['a'][1], 0))
L1 = e1['len']
centers = []
for i in range(max(1, int((L1 - 4.0) / 3.6))):
    t = 2.0 + 3.6 * (i + 0.5)
    if t > L1 - 2.0: break
    centers.append(t)
t_w = centers[min(2, len(centers) - 1)] if centers else L1 * 0.45
c_w = A1 + U1 * t_w
camw = bpy.data.objects.get('VI_CAM_closeup_Freeman_W_glass_grazing')
if camw:
    # pull back + less lateral offset = more glass in frame while still grazing
    camw.location = (c_w.x + N1.x * 9.5 - U1.x * 1.6, c_w.y + N1.y * 9.5 - U1.y * 1.6, GR + 6.2)
    target = (c_w.x + N1.x * (OUT + 0.14), c_w.y + N1.y * (OUT + 0.14), GR + 8.5)
    camw.rotation_euler = (Vector(target) - Vector(camw.location)).to_track_quat('-Z', 'Y').to_euler()
    if camw.data: camw.data.lens = 42
    log['fixes'].append(f'reframe_W_glass_t{t_w:.2f}_lens42')

# N cream cam — center on pier lip / lettering-safe zone
e6 = [e for e in OSM['edges'] if e['i'] == 6][0]
U6 = Vector((e6['u'][0], e6['u'][1], 0)).normalized()
N6 = Vector((e6['n'][0], e6['n'][1], 0)).normalized()
A6 = Vector((e6['a'][0], e6['a'][1], 0))
scr = A6 + U6 * 6.82
cam = bpy.data.objects.get('VI_CAM_closeup_Freeman_N_cream_punch')
if cam:
    cam.location = (scr.x + N6.x * 7.5 - U6.x * 0.4, scr.y + N6.y * 7.5 - U6.y * 0.4, GR + 5.5)
    target = (scr.x + N6.x * (OUT + 0.16), scr.y + N6.y * (OUT + 0.16), GR + 8.0)
    cam.rotation_euler = (Vector(target) - Vector(cam.location)).to_track_quat('-Z', 'Y').to_euler()
    if cam.data: cam.data.lens = 40
    log['fixes'].append('reaim_N_cream_pier')

let = bpy.data.objects.get('UV_Freeman_N_lettering_GRACE_H_FREEMAN_HALL_UNVERIFIED')
if let:
    mw = let.matrix_world
    log['letter'] = {'body': let.data.body, 'size': round(let.data.size, 6),
                     'loc': [round(mw[0][3], 4), round(mw[1][3], 4), round(mw[2][3], 4)]}

json.dump(log, open(DATA + '/vi_polish2.json', 'w'), indent=2)
print('VI POLISH2', json.dumps(log, indent=2))
print('OBJECTS', len(bpy.data.objects))
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED')
