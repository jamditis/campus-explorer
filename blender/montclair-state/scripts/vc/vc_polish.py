"""vc polish after WIP self-review: nudge backplane inset / cream if needed.
SAVE=1 saves. REVERT is no-op (materials removed by vc_main REVERT).
"""
import bpy, os, json
REV = os.environ.get('REVERT') == '1'
SAVE = os.environ.get('SAVE') == '1'
DATA='/workspace/nj-scenes/montclair-state/data/vc'
os.makedirs(DATA, exist_ok=True)
log={'session':'vc_polish','fixes':[]}
if REV:
    print('VC POLISH REVERT: no-op')
    raise SystemExit

# Ensure dark backplane stays near-black (no accidental lift)
d=bpy.data.materials.get('VC_Freeman_glass_backplane_dark_UNVERIFIED')
if d and d.use_nodes:
    b=d.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Base Color'].default_value=(0.018, 0.018, 0.020, 1.0)
        b.inputs['Roughness'].default_value=0.95
        log['fixes'].append('backplane_darker')

# Keep VB glass transmission punch intact (do not overwrite vb glass)
g=bpy.data.materials.get('VB_Freeman_glass_cool_clear_UNVERIFIED')
if g and g.use_nodes:
    b=g.node_tree.nodes.get('Principled BSDF')
    if b:
        # slight further clarity so dark backplanes read through
        b.inputs['Alpha'].default_value=0.22
        if 'Transmission Weight' in b.inputs:
            b.inputs['Transmission Weight'].default_value=1.0
        log['fixes'].append('glass_alpha_for_backplane_read')

json.dump(log, open(DATA+'/vc_polish.json','w'), indent=2)
print('VC POLISH', json.dumps(log))
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED')
