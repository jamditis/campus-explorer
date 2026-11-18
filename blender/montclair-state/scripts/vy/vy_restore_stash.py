"""Restore TR_Stone_brick_detail from data/vy/vy_brick_stash.json (soft; prefer vy_revert_all.sh)."""
import bpy, json
STASH='/workspace/nj-scenes/montclair-state/data/vy/vy_brick_stash.json'
s=json.load(open(STASH))
m=bpy.data.materials[s['mat']]; nt=m.node_tree
bt=nt.nodes['Brick Texture']; cr=nt.nodes['Color Ramp']; cr1=nt.nodes['Color Ramp.001']
mix=nt.nodes['Mix']; mix001=nt.nodes['Mix.001']; mix009=nt.nodes['Mix.009']
bt.inputs['Color1'].default_value=s['brick_color1']
bt.inputs['Color2'].default_value=s['brick_color2']
bt.inputs['Mortar'].default_value=s['mortar']
bt.inputs['Mortar Size'].default_value=s['mortar_size']
cr.color_ramp.elements[0].color=s['ramp0']; cr.color_ramp.elements[1].color=s['ramp1']
cr1.color_ramp.elements[0].color=s['ramp001_0']; cr1.color_ramp.elements[1].color=s['ramp001_1']
mix.inputs[7].default_value=s['mix_b']; mix001.inputs[7].default_value=s['mix001_b']
mix009.inputs[0].default_value=s['overlay_fac']
if 'vy_mat' in m: del m['vy_mat']
bpy.ops.wm.save_mainfile(); print('stash restored')
