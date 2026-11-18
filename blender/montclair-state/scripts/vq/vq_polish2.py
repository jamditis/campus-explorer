"""vq polish2: charcoal variation on VN interbay (not pure black) + mild BP hue; reaim W closeup. SAVE=1."""
import bpy, os, json
from mathutils import Vector
SAVE = os.environ.get('SAVE') == '1'
D = '/workspace/nj-scenes/montclair-state/'
DATA = D + 'data/vq'
OSM = json.load(open(D + 'data/uv/freeman_osm_probe.json'))
GR = float(json.load(open(D + 'data/uv/uv_main.json')).get('GR', 129.053))
OUT = 0.08
log = {'session': 'vq_polish2', 'fixes': []}

# Soften VN interbay from near-black → mild charcoal with slight cool/warm variation
ib = bpy.data.materials.get('VQ_Freeman_W_interbay_dark_UNVERIFIED')
if ib and ib.use_nodes:
    b = ib.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Base Color'].default_value = (0.012, 0.010, 0.013, 1.0)  # charcoal not pure black
        b.inputs['Roughness'].default_value = 0.88
        if 'Specular IOR Level' in b.inputs:
            b.inputs['Specular IOR Level'].default_value = 0.08
        log['fixes'].append('VQ_interbay_charcoal_0.012')

sh = bpy.data.materials.get('VQ_Freeman_N_shadow_deep_UNVERIFIED')
# also used as secondary on interbay edge boxes — keep slightly warmer charcoal
if sh and sh.use_nodes:
    b = sh.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Base Color'].default_value = (0.016, 0.013, 0.012, 1.0)
        log['fixes'].append('VQ_shadow_charcoal_warm')

# Per-object mild tint variation on VN interbay meshes for depth (slot override colors via emission-free base)
# Instead: nudge prior VM/VL/VK/VJ ibay mats toward charcoal variation ladder
for mname, rgb, note in (
    ('VP_Freeman_W_interbay_dark_UNVERIFIED', (0.008, 0.0065, 0.0075, 1.0), 'VP_ibay_charcoal'),
    ('VO_Freeman_W_interbay_dark_UNVERIFIED', (0.009, 0.0075, 0.0085, 1.0), 'VO_ibay_charcoal'),
    ('VN_Freeman_W_interbay_dark_UNVERIFIED', (0.010, 0.0085, 0.009, 1.0), 'VN_ibay_charcoal'),
    ('VM_Freeman_W_interbay_dark_UNVERIFIED', (0.011, 0.009, 0.010, 1.0), 'VM_ibay_charcoal'),
    ('VL_Freeman_W_interbay_dark_UNVERIFIED', (0.012, 0.010, 0.011, 1.0), 'VL_ibay_charcoal'),
    ('VK_Freeman_W_interbay_dark_UNVERIFIED', (0.014, 0.012, 0.011, 1.0), 'VK_ibay_charcoal'),
    ('VJ_Freeman_W_interbay_dark_UNVERIFIED', (0.017, 0.014, 0.012, 1.0), 'VJ_ibay_charcoal'),
):
    mm = bpy.data.materials.get(mname)
    if mm and mm.use_nodes:
        b = mm.node_tree.nodes.get('Principled BSDF')
        if b:
            b.inputs['Base Color'].default_value = rgb
            log['fixes'].append(note)

# Ensure BP charcoal still mild (re-assert after any stash confusion)
for mname, rgb, note in (
    ('VC_Freeman_glass_backplane_dark_UNVERIFIED', (0.014, 0.012, 0.016, 1.0), 'VC_W_BP_charcoal_lift'),
    ('VG_Freeman_SE_glass_backplane_UNVERIFIED', (0.012, 0.010, 0.014, 1.0), 'VG_SE_BP_charcoal_lift'),
):
    mm = bpy.data.materials.get(mname)
    if mm and mm.use_nodes:
        b = mm.node_tree.nodes.get('Principled BSDF')
        if b:
            b.inputs['Base Color'].default_value = rgb
            b.inputs['Roughness'].default_value = 0.90
            log['fixes'].append(note)

# Slightly cooler/brighter glass reflection for grazing sky catch (keep Alpha 0.100)
wg = bpy.data.materials.get('VD_Freeman_W_glass_pane_UNVERIFIED')
if wg and wg.use_nodes:
    b = wg.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Base Color'].default_value = (0.62, 0.84, 1.0, 1.0)
        if 'Coat Roughness' in b.inputs:
            b.inputs['Coat Roughness'].default_value = 0.001
        log['fixes'].append('W_glass_cooler_base_CoatRough0.001')

sky = bpy.data.materials.get('VF_Freeman_W_sky_tint_UNVERIFIED')
if sky and sky.use_nodes:
    b = sky.node_tree.nodes.get('Principled BSDF')
    if b:
        if 'Emission Strength' in b.inputs:
            b.inputs['Emission Strength'].default_value = 4.30
        b.inputs['Alpha'].default_value = 0.32  # more sky catch at grazing
        log['fixes'].append('sky_Alpha0.32_keep_emiss4.30')

# Reaim W closeup slightly higher + more oblique to catch sky reflection + charcoal depth
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
camw = bpy.data.objects.get('VQ_CAM_closeup_Freeman_W_glass_grazing')
if camw:
    # pull back a bit, higher, more side angle so charcoal/sky read
    camw.location = (c_w.x + N1.x * 9.2 - U1.x * 2.0, c_w.y + N1.y * 9.2 - U1.y * 2.0, GR + 7.0)
    target = (c_w.x + N1.x * (OUT + 0.12), c_w.y + N1.y * (OUT + 0.12), GR + 9.5)
    camw.rotation_euler = (Vector(target) - Vector(camw.location)).to_track_quat('-Z', 'Y').to_euler()
    if camw.data: camw.data.lens = 40
    log['fixes'].append(f'reaim_W_grazing_pullback_t{t_w:.2f}')

let = bpy.data.objects.get('UV_Freeman_N_lettering_GRACE_H_FREEMAN_HALL_UNVERIFIED')
if let:
    mw = let.matrix_world
    log['letter'] = {
        'body': let.data.body, 'size': round(let.data.size, 6),
        'loc': [round(mw[0][3], 4), round(mw[1][3], 4), round(mw[2][3], 4)],
    }

json.dump(log, open(DATA + '/vq_polish2.json', 'w'), indent=2)
print('VQ POLISH2', json.dumps(log, indent=2))
print('OBJECTS', len(bpy.data.objects))
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED')
