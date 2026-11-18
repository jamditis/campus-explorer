"""vm polish after WIP review: clearer W glass + stronger N cream mats; assign cream to lips; reaim cams. SAVE=1."""
import bpy, os, json
from mathutils import Vector
SAVE = os.environ.get('SAVE') == '1'
D = '/workspace/nj-scenes/montclair-state/'
DATA = D + 'data/vm'
OSM = json.load(open(D + 'data/uv/freeman_osm_probe.json'))
GR = float(json.load(open(D + 'data/uv/uv_main.json')).get('GR', 129.053))
OUT = 0.08
log = {'session': 'vm_polish', 'fixes': []}

wg = bpy.data.materials.get('VD_Freeman_W_glass_pane_UNVERIFIED')
if wg and wg.use_nodes:
    b = wg.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Alpha'].default_value = 0.160
        if 'Coat Weight' in b.inputs:
            b.inputs['Coat Weight'].default_value = 1.0
            b.inputs['Coat Roughness'].default_value = 0.002
        b.inputs['Base Color'].default_value = (0.88, 0.96, 1.0, 1.0)
        b.inputs['Roughness'].default_value = 0.001
        if 'Specular IOR Level' in b.inputs:
            b.inputs['Specular IOR Level'].default_value = 1.36
        log['fixes'].append('W_glass_Alpha0.160_Coat1.0_Spec1.36')
        log['W_glassA'] = 0.160

sky = bpy.data.materials.get('VF_Freeman_W_sky_tint_UNVERIFIED')
if sky and sky.use_nodes:
    b = sky.node_tree.nodes.get('Principled BSDF')
    if b:
        if 'Emission Strength' in b.inputs:
            b.inputs['Emission Strength'].default_value = 3.10
        b.inputs['Base Color'].default_value = (0.82, 0.91, 1.0, 1.0)
        if 'Emission Color' in b.inputs:
            b.inputs['Emission Color'].default_value = (0.84, 0.93, 1.0, 1.0)
        b.inputs['Alpha'].default_value = 0.25
        log['fixes'].append('sky_emiss3.10_Alpha0.25')

sg = bpy.data.materials.get('VG_Freeman_SE_glass_pane_UNVERIFIED')
if sg and sg.use_nodes:
    b = sg.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Alpha'].default_value = 0.185
        if 'Coat Weight' in b.inputs:
            b.inputs['Coat Weight'].default_value = 1.0
        if 'Specular IOR Level' in b.inputs:
            b.inputs['Specular IOR Level'].default_value = 1.28
        b.inputs['Base Color'].default_value = (0.83, 0.93, 1.0, 1.0)
        log['fixes'].append('SE_glass_Alpha0.185_Coat1.0_Spec1.28')

# Ensure VL cream punch mat exists and is used on pier lips
cm = bpy.data.materials.get('VM_Freeman_N_cream_punch_UNVERIFIED')
if cm is None:
    cm = bpy.data.materials.new('VM_Freeman_N_cream_punch_UNVERIFIED')
    cm.use_nodes = True
    cm['vm_mat'] = 1
    log['fixes'].append('recreate_VM_cream_mat')
if cm and cm.use_nodes:
    b = cm.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Base Color'].default_value = (0.99, 0.87, 0.65, 1.0)
        b.inputs['Roughness'].default_value = 0.58
        if 'Specular IOR Level' in b.inputs:
            b.inputs['Specular IOR Level'].default_value = 0.22
        log['fixes'].append('VM_cream_warmer_brighter')

assigned = 0
for o in bpy.data.objects:
    if not o.get('vm_obj'): continue
    if 'N_cream_lip_' not in o.name and 'N_belt_punch_' not in o.name and 'N_quoin_punch_' not in o.name and 'N_return_belt_' not in o.name:
        continue
    if len(o.material_slots) == 0:
        o.data.materials.append(cm)
    else:
        o.material_slots[0].material = cm
    assigned += 1
log['fixes'].append(f'assigned_VM_cream_to_{assigned}_overlays')

sh = bpy.data.materials.get('VM_Freeman_N_shadow_deep_UNVERIFIED')
if sh and sh.use_nodes:
    b = sh.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Base Color'].default_value = (0.0007, 0.0005, 0.0004, 1.0)
        log['fixes'].append('VM_shadow_deeper')

ib = bpy.data.materials.get('VM_Freeman_W_interbay_dark_UNVERIFIED')
if ib and ib.use_nodes:
    b = ib.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Base Color'].default_value = (0.0012, 0.0010, 0.0008, 1.0)
        log['fixes'].append('VM_interbay_darker')

mo = bpy.data.materials.get('VM_Freeman_N_mortar_line_UNVERIFIED')
if mo and mo.use_nodes:
    b = mo.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Base Color'].default_value = (0.13, 0.09, 0.06, 1.0)
        log['fixes'].append('VM_mortar_darker')

e6 = [e for e in OSM['edges'] if e['i'] == 6][0]
U6 = Vector((e6['u'][0], e6['u'][1], 0)).normalized()
N6 = Vector((e6['n'][0], e6['n'][1], 0)).normalized()
A6 = Vector((e6['a'][0], e6['a'][1], 0))
scr = A6 + U6 * 6.82
cam = bpy.data.objects.get('VM_CAM_closeup_Freeman_N_cream_punch')
if cam:
    cam.location = (scr.x + N6.x * 6.75 - U6.x * 0.26, scr.y + N6.y * 6.75 - U6.y * 0.26, GR + 5.6)
    target = (scr.x + N6.x * (OUT + 0.22), scr.y + N6.y * (OUT + 0.22), GR + 8.2)
    cam.rotation_euler = (Vector(target) - Vector(cam.location)).to_track_quat('-Z', 'Y').to_euler()
    if cam.data: cam.data.lens = 42
    log['fixes'].append('reaim_N_cream_closeup')

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
camw = bpy.data.objects.get('VM_CAM_closeup_Freeman_W_glass_grazing')
if camw:
    camw.location = (c_w.x + N1.x * 8.3 - U1.x * 1.25, c_w.y + N1.y * 8.3 - U1.y * 1.25, GR + 6.2)
    target = (c_w.x + N1.x * (OUT + 0.14), c_w.y + N1.y * (OUT + 0.14), GR + 8.5)
    camw.rotation_euler = (Vector(target) - Vector(camw.location)).to_track_quat('-Z', 'Y').to_euler()
    if camw.data: camw.data.lens = 42
    log['fixes'].append(f'reaim_W_glass_grazing_t{t_w:.2f}')

let = bpy.data.objects.get('UV_Freeman_N_lettering_GRACE_H_FREEMAN_HALL_UNVERIFIED')
if let:
    mw = let.matrix_world
    log['letter'] = {
        'body': let.data.body, 'size': round(let.data.size, 6),
        'loc': [round(mw[0][3], 4), round(mw[1][3], 4), round(mw[2][3], 4)],
    }

json.dump(log, open(DATA + '/vm_polish.json', 'w'), indent=2)
print('VM POLISH', json.dumps(log, indent=2))
print('OBJECTS', len(bpy.data.objects))
print('VMMAT', sum(1 for m in bpy.data.materials if m.get('vm_mat')))
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED')
