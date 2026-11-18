"""vz: soften Blanton cream-infill faint vertical striping (material only).
Target: TR_Blanton_infill_cream_UNVERIFIED (objs TI_Blanton_Hall_*).
Broaden anisotropic Mapping Z + lower noise contrast / Mix.008 multiply.
Do NOT invent a new colour. Do NOT stack overlays. ALL UNVERIFIED.
"""
import bpy, json, os

STASH = '/workspace/nj-scenes/montclair-state/data/vz/vz_infill_stash.json'
MAT = 'TR_Blanton_infill_cream_UNVERIFIED'

m = bpy.data.materials.get(MAT)
if not m or not m.use_nodes:
    raise SystemExit(f'missing mat {MAT}')
nt = m.node_tree

mp = nt.nodes.get('Mapping')
mp1 = nt.nodes.get('Mapping.001')
nz1 = nt.nodes.get('Noise Texture.001')
nz3 = nt.nodes.get('Noise Texture.003')
cr2 = nt.nodes.get('Color Ramp.002')
mx8 = nt.nodes.get('Mix.008')
m38 = nt.nodes.get('Math.038')
if not all([mp, mp1, nz1, nz3, cr2, mx8, m38]):
    raise SystemExit('missing striping nodes')

def col4(e):
    return [float(x) for x in e.color]

stash = {
    'mat': MAT,
    'Mapping_scale': [float(x) for x in mp.inputs['Scale'].default_value],
    'Mapping001_scale': [float(x) for x in mp1.inputs['Scale'].default_value],
    'Noise001_Scale': float(nz1.inputs['Scale'].default_value),
    'Noise001_Detail': float(nz1.inputs['Detail'].default_value),
    'Noise003_Scale': float(nz3.inputs['Scale'].default_value),
    'Noise003_Detail': float(nz3.inputs['Detail'].default_value),
    'ColorRamp002': [
        {'pos': float(e.position), 'color': col4(e)} for e in cr2.color_ramp.elements
    ],
    'Mix008_fac': float(mx8.inputs[0].default_value),
    'Math038_Value': float(m38.inputs[1].default_value),  # second operand (amplitude)
    'Math038_op': m38.operation,
}
os.makedirs(os.path.dirname(STASH), exist_ok=True)
json.dump(stash, open(STASH, 'w'), indent=1)
print('STASHED', STASH)
print('PRIOR Mapping', stash['Mapping_scale'], 'Mapping.001', stash['Mapping001_scale'])
print('PRIOR Mix008_fac', stash['Mix008_fac'], 'Math038', stash['Math038_Value'])

# --- apply soften (no colour invent) ---
# Broaden Z so noise is less woodgrain-vertical; slightly lower XY frequency.
mp.inputs['Scale'].default_value = (1.15, 1.15, 0.36)
mp1.inputs['Scale'].default_value = (0.70, 0.70, 0.24)
# Lower detail / contrast of the streak noises
nz1.inputs['Detail'].default_value = 2.0
nz3.inputs['Detail'].default_value = 2.0
nz3.inputs['Scale'].default_value = 2.2
# Soften Color Ramp.002 multiply streak contrast (keep near-white; no hue change)
# prior: pos0.42 color~(0.88,0.865,0.84) → pos0.62 white
els = cr2.color_ramp.elements
els[0].position = 0.28
els[0].color = (0.94, 0.93, 0.91, 1.0)  # closer to white → less dark streaking
els[1].position = 0.72
els[1].color = (1.0, 1.0, 1.0, 1.0)
# Reduce Mix.008 multiply strength
mx8.inputs[0].default_value = 0.45
# Lower Math.038 stripe amplitude (was 0.5)
m38.inputs[1].default_value = 0.28

m['vz_mat'] = 1
m['vz_note'] = 'Blanton cream infill striping softened UNVERIFIED'

# no twin found in probe; skip

bpy.ops.wm.save_mainfile()
print('VZ saved', len(bpy.data.objects))
print('NEW Mapping', list(mp.inputs['Scale'].default_value))
print('NEW Mapping.001', list(mp1.inputs['Scale'].default_value))
print('NEW Mix008_fac', mx8.inputs[0].default_value, 'Math038', m38.inputs[1].default_value)
print('NEW CR002', [(e.position, list(e.color)) for e in els])
