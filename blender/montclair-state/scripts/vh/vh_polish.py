"""vh polish after WIP review: clearer W glass + stronger N cream mats; reaim N cam. SAVE=1."""
import bpy, os, json
from mathutils import Vector
SAVE = os.environ.get('SAVE') == '1'
D = '/workspace/nj-scenes/montclair-state/'
DATA = D + 'data/vh'
OSM = json.load(open(D + 'data/uv/freeman_osm_probe.json'))
GR = float(json.load(open(D + 'data/uv/uv_main.json')).get('GR', 129.053))
OUT = 0.08
log = {'session': 'vh_polish', 'fixes': []}

# A) W glass still dark at grazing — push clearer (avoid milky)
wg = bpy.data.materials.get('VD_Freeman_W_glass_pane_UNVERIFIED')
if wg and wg.use_nodes:
    b = wg.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Alpha'].default_value = 0.40
        if 'Coat Weight' in b.inputs:
            b.inputs['Coat Weight'].default_value = 0.95
            b.inputs['Coat Roughness'].default_value = 0.012
        b.inputs['Base Color'].default_value = (0.78, 0.90, 0.99, 1.0)
        b.inputs['Roughness'].default_value = 0.006
        log['fixes'].append('W_glass_Alpha0.40_Coat0.95')
        log['W_glassA'] = 0.40

sky = bpy.data.materials.get('VF_Freeman_W_sky_tint_UNVERIFIED')
if sky and sky.use_nodes:
    b = sky.node_tree.nodes.get('Principled BSDF')
    if b:
        if 'Emission Strength' in b.inputs:
            b.inputs['Emission Strength'].default_value = 1.65
        b.inputs['Base Color'].default_value = (0.76, 0.87, 0.98, 1.0)
        if 'Emission Color' in b.inputs:
            b.inputs['Emission Color'].default_value = (0.78, 0.88, 0.99, 1.0)
        b.inputs['Alpha'].default_value = 0.50
        log['fixes'].append('sky_emiss1.65')

# SE glass match toward W
sg = bpy.data.materials.get('VG_Freeman_SE_glass_pane_UNVERIFIED')
if sg and sg.use_nodes:
    b = sg.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Alpha'].default_value = 0.44
        if 'Coat Weight' in b.inputs:
            b.inputs['Coat Weight'].default_value = 0.90
        b.inputs['Base Color'].default_value = (0.74, 0.88, 0.98, 1.0)
        log['fixes'].append('SE_glass_Alpha0.44_Coat0.90')

# B) Stronger cream / darker shadows for punch read
cm = bpy.data.materials.get('VH_Freeman_N_cream_punch_UNVERIFIED')
if cm and cm.use_nodes:
    b = cm.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Base Color'].default_value = (0.82, 0.72, 0.55, 1.0)
        b.inputs['Roughness'].default_value = 0.78
        log['fixes'].append('VH_cream_warmer_brighter')

sh = bpy.data.materials.get('VH_Freeman_N_shadow_deep_UNVERIFIED')
if sh and sh.use_nodes:
    b = sh.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Base Color'].default_value = (0.010, 0.008, 0.006, 1.0)
        log['fixes'].append('VH_shadow_deeper')

mo = bpy.data.materials.get('VH_Freeman_N_mortar_line_UNVERIFIED')
if mo and mo.use_nodes:
    b = mo.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Base Color'].default_value = (0.42, 0.36, 0.28, 1.0)
        log['fixes'].append('VH_mortar_darker')

# Reaim N cream closeup slightly higher / clearer of tree
e6 = [e for e in OSM['edges'] if e['i'] == 6][0]
U6 = Vector((e6['u'][0], e6['u'][1], 0)).normalized()
N6 = Vector((e6['n'][0], e6['n'][1], 0)).normalized()
A6 = Vector((e6['a'][0], e6['a'][1], 0))
scr = A6 + U6 * 6.82
cam = bpy.data.objects.get('VH_CAM_closeup_Freeman_N_cream_punch')
if cam:
    cam.location = (scr.x + N6.x * 8.5 - U6.x * 0.8, scr.y + N6.y * 8.5 - U6.y * 0.8, GR + 5.0)
    target = (scr.x + N6.x * (OUT + 0.12), scr.y + N6.y * (OUT + 0.12), GR + 7.5)
    cam.rotation_euler = (Vector(target) - Vector(cam.location)).to_track_quat('-Z', 'Y').to_euler()
    if cam.data: cam.data.lens = 42
    log['fixes'].append('reaim_N_cream_closeup')

# W closeup — slight slide to clearer bay
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
camw = bpy.data.objects.get('VH_CAM_closeup_Freeman_W_glass_grazing')
if camw:
    camw.location = (c_w.x + N1.x * 8.0 - U1.x * 0.5, c_w.y + N1.y * 8.0 - U1.y * 0.5, GR + 6.0)
    target = (c_w.x + N1.x * (OUT + 0.14), c_w.y + N1.y * (OUT + 0.14), GR + 8.0)
    camw.rotation_euler = (Vector(target) - Vector(camw.location)).to_track_quat('-Z', 'Y').to_euler()
    if camw.data: camw.data.lens = 45
    log['fixes'].append(f'reaim_W_glass_closeup_t{t_w:.2f}')

let = bpy.data.objects.get('UV_Freeman_N_lettering_GRACE_H_FREEMAN_HALL_UNVERIFIED')
if let:
    mw = let.matrix_world
    log['letter'] = {
        'body': let.data.body, 'size': round(let.data.size, 6),
        'loc': [round(mw[0][3], 4), round(mw[1][3], 4), round(mw[2][3], 4)],
    }

json.dump(log, open(DATA + '/vh_polish.json', 'w'), indent=2)
print('VH POLISH', json.dumps(log, indent=2))
print('OBJECTS', len(bpy.data.objects))
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED')
