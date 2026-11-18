"""vh polish2: stash+punch VB cream brick (used on lips/belts); keep lettering. SAVE=1."""
import bpy, os, json
SAVE = os.environ.get('SAVE') == '1'
DATA = '/workspace/nj-scenes/montclair-state/data/vh'
STASH = DATA + '/vh_vb_cream_stash.json'
log = {'session': 'vh_polish2', 'fixes': []}

def stash_principled(path, mat_name, keys=('Base Color','Roughness','Alpha','Coat Weight','Coat Roughness','Specular IOR Level','Transmission Weight','Metallic','Emission Color','Emission Strength')):
    m = bpy.data.materials.get(mat_name)
    if not m or not m.use_nodes or os.path.exists(path): return
    b = m.node_tree.nodes.get('Principled BSDF')
    if not b: return
    d = {}
    for k in keys:
        if k in b.inputs:
            v = b.inputs[k].default_value
            try: d[k] = list(v)
            except TypeError: d[k] = float(v)
    json.dump(d, open(path, 'w'), indent=2)

stash_principled(STASH, 'VB_Freeman_cream_brick_strong_UNVERIFIED')
m = bpy.data.materials.get('VB_Freeman_cream_brick_strong_UNVERIFIED')
if m and m.use_nodes:
    b = m.node_tree.nodes.get('Principled BSDF')
    if b:
        # slightly warmer/brighter for punch at entrance eye (not milky)
        cur = list(b.inputs['Base Color'].default_value)
        b.inputs['Base Color'].default_value = (
            min(0.92, cur[0] * 1.08 + 0.04),
            min(0.85, cur[1] * 1.06 + 0.03),
            min(0.70, cur[2] * 1.04 + 0.02),
            1.0,
        )
        b.inputs['Roughness'].default_value = max(0.55, min(0.85, float(b.inputs['Roughness'].default_value) * 0.95))
        log['fixes'].append('VB_cream_brick_punch')
        log['VB_cream'] = [round(x, 3) for x in b.inputs['Base Color'].default_value]

# also ensure VH cream mat exists and is punched (for any lips using it)
cm = bpy.data.materials.get('VH_Freeman_N_cream_punch_UNVERIFIED')
if cm and cm.use_nodes:
    b = cm.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Base Color'].default_value = (0.84, 0.74, 0.56, 1.0)
        b.inputs['Roughness'].default_value = 0.76
        log['fixes'].append('VH_cream_punch_mat')

let = bpy.data.objects.get('UV_Freeman_N_lettering_GRACE_H_FREEMAN_HALL_UNVERIFIED')
if let:
    mw = let.matrix_world
    log['letter'] = {'body': let.data.body, 'size': round(let.data.size, 6),
                     'loc': [round(mw[0][3], 4), round(mw[1][3], 4), round(mw[2][3], 4)]}

json.dump(log, open(DATA + '/vh_polish2.json', 'w'), indent=2)
print('VH POLISH2', json.dumps(log, indent=2))
print('OBJECTS', len(bpy.data.objects))
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED')
