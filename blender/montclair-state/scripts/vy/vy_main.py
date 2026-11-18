"""vy: Stone Hall buff/cream face-brick tone from 1966 slide 285 (material only).
ALL UNVERIFIED. Edits TR_Stone_brick_detail_UNVERIFIED in place; stashes prior values.
Does NOT copy Freeman mats. Target pale buff ~sRGB #cfc8b8 (not white, not grey).
"""
import bpy, json, os

STASH = '/workspace/nj-scenes/montclair-state/data/vy/vy_brick_stash.json'
MAT_NAME = 'TR_Stone_brick_detail_UNVERIFIED'

# Target linear-ish pale buff (AgX-friendly; slightly warm cream, not white)
# Slide 285 shaded sRGB ~#cfc8b8 → ~linear (0.62, 0.57, 0.48); brick variation around that.
NEW = {
    'brick_color1': (0.70, 0.65, 0.54, 1.0),   # sunlit pale buff
    'brick_color2': (0.60, 0.55, 0.45, 1.0),   # shaded brick variation
    'mortar':       (0.78, 0.75, 0.68, 1.0),   # fine light mortar (subtle)
    'mortar_size':  0.010,                     # slightly finer/lighter read vs heavy grid
    'ramp0':        (0.58, 0.54, 0.46, 1.0),   # Color Ramp (was ~0.27 dark brown)
    'ramp1':        (0.70, 0.66, 0.56, 1.0),
    'ramp001_0':    (0.62, 0.57, 0.47, 1.0),   # Color Ramp.001 (was orange-brown 0.46/0.54)
    'ramp001_1':    (0.72, 0.67, 0.55, 1.0),
    'mix_b':        (0.92, 0.90, 0.84, 1.0),   # Mix multiply B was (0.72,0.70,0.66) — lifts overall
    'mix001_b':     (0.96, 0.94, 0.90, 1.0),   # Mix.001 multiply B was (0.88,0.87,0.85)
    'overlay_fac':  0.28,                      # Mix.009 was 0.35 — keep brick readable, less muddy
}

m = bpy.data.materials.get(MAT_NAME)
if not m or not m.use_nodes:
    raise SystemExit(f'missing mat {MAT_NAME}')
nt = m.node_tree
bt = nt.nodes.get('Brick Texture')
cr = nt.nodes.get('Color Ramp')
cr1 = nt.nodes.get('Color Ramp.001')
mix = nt.nodes.get('Mix')
mix001 = nt.nodes.get('Mix.001')
mix009 = nt.nodes.get('Mix.009')
if not all([bt, cr, cr1, mix, mix001, mix009]):
    raise SystemExit(f'missing nodes bt={bt} cr={cr} cr1={cr1} mix={mix} mix001={mix001} mix009={mix009}')

stash = {
    'mat': MAT_NAME,
    'brick_color1': list(bt.inputs['Color1'].default_value),
    'brick_color2': list(bt.inputs['Color2'].default_value),
    'mortar': list(bt.inputs['Mortar'].default_value),
    'mortar_size': float(bt.inputs['Mortar Size'].default_value),
    'ramp0': list(cr.color_ramp.elements[0].color),
    'ramp1': list(cr.color_ramp.elements[1].color),
    'ramp001_0': list(cr1.color_ramp.elements[0].color),
    'ramp001_1': list(cr1.color_ramp.elements[1].color),
    'mix_b': list(mix.inputs[7].default_value),
    'mix001_b': list(mix001.inputs[7].default_value),
    'overlay_fac': float(mix009.inputs[0].default_value),
}
os.makedirs(os.path.dirname(STASH), exist_ok=True)
json.dump(stash, open(STASH, 'w'), indent=1)
print('STASHED', STASH)

# Apply
bt.inputs['Color1'].default_value = NEW['brick_color1']
bt.inputs['Color2'].default_value = NEW['brick_color2']
bt.inputs['Mortar'].default_value = NEW['mortar']
bt.inputs['Mortar Size'].default_value = NEW['mortar_size']
cr.color_ramp.elements[0].color = NEW['ramp0']
cr.color_ramp.elements[1].color = NEW['ramp1']
cr1.color_ramp.elements[0].color = NEW['ramp001_0']
cr1.color_ramp.elements[1].color = NEW['ramp001_1']
mix.inputs[7].default_value = NEW['mix_b']
mix001.inputs[7].default_value = NEW['mix001_b']
mix009.inputs[0].default_value = NEW['overlay_fac']

m['vy_mat'] = 1
m['vy_note'] = 'Stone buff brick tone slide285 UNVERIFIED'

# Also lightly sync orphan TQ_Stone_buff_brick (fake-user twin) so future swaps stay coherent
m2 = bpy.data.materials.get('TQ_Stone_buff_brick_UNVERIFIED')
if m2 and m2.use_nodes:
    nt2 = m2.node_tree
    bt2 = nt2.nodes.get('Brick Texture')
    cr2 = nt2.nodes.get('Color Ramp')
    cr12 = nt2.nodes.get('Color Ramp.001')
    mix2 = nt2.nodes.get('Mix')
    mix001_2 = nt2.nodes.get('Mix.001')
    mix009_2 = nt2.nodes.get('Mix.009')
    if bt2:
        bt2.inputs['Color1'].default_value = NEW['brick_color1']
        bt2.inputs['Color2'].default_value = NEW['brick_color2']
        bt2.inputs['Mortar'].default_value = NEW['mortar']
        bt2.inputs['Mortar Size'].default_value = NEW['mortar_size']
    if cr2 and len(cr2.color_ramp.elements) >= 2:
        cr2.color_ramp.elements[0].color = NEW['ramp0']
        cr2.color_ramp.elements[1].color = NEW['ramp1']
    if cr12 and len(cr12.color_ramp.elements) >= 2:
        cr12.color_ramp.elements[0].color = NEW['ramp001_0']
        cr12.color_ramp.elements[1].color = NEW['ramp001_1']
    if mix2:
        mix2.inputs[7].default_value = NEW['mix_b']
    if mix001_2:
        mix001_2.inputs[7].default_value = NEW['mix001_b']
    if mix009_2:
        mix009_2.inputs[0].default_value = NEW['overlay_fac']
    m2['vy_mat'] = 1
    print('also synced TQ_Stone_buff_brick_UNVERIFIED (fake-user twin)')

bpy.ops.wm.save_mainfile()
print('VY saved', len(bpy.data.objects))
print('NEW brick1', tuple(round(x,3) for x in bt.inputs['Color1'].default_value))
print('NEW brick2', tuple(round(x,3) for x in bt.inputs['Color2'].default_value))
print('NEW mortar', tuple(round(x,3) for x in bt.inputs['Mortar'].default_value))
