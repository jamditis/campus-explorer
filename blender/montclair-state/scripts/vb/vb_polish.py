"""vb polish after WIP self-review: punch cooler glass + fix cream brick course orientation.
SAVE=1 saves. REVERT not separate — fold into vb_main revert (same vb_mat tags).
"""
import bpy, os, json
REV = os.environ.get('REVERT') == '1'
SAVE = os.environ.get('SAVE') == '1'
DATA='/workspace/nj-scenes/montclair-state/data/vb'
log={'session':'vb_polish','fixes':[]}
if REV:
    print('VB POLISH REVERT: no-op (materials removed by vb_main REVERT)')
    raise SystemExit

# ---- Glass punch ----
g=bpy.data.materials.get('VB_Freeman_glass_cool_clear_UNVERIFIED')
if g and g.use_nodes:
    b=g.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Base Color'].default_value=(0.70, 0.82, 0.92, 1.0)  # cooler
        b.inputs['Roughness'].default_value=0.02
        if 'Transmission Weight' in b.inputs:
            b.inputs['Transmission Weight'].default_value=1.0
        elif 'Transmission' in b.inputs:
            b.inputs['Transmission'].default_value=1.0
        b.inputs['Alpha'].default_value=0.28  # more see-through at eye
        if 'IOR' in b.inputs:
            b.inputs['IOR'].default_value=1.45
        try: b.inputs['Specular IOR Level'].default_value=0.65
        except Exception: pass
        # slight coat for reflection read
        if 'Coat Weight' in b.inputs:
            b.inputs['Coat Weight'].default_value=0.15
            b.inputs['Coat Roughness'].default_value=0.05
    g.blend_method='HASHED'
    log['fixes'].append('glass_transmission_punch')

# ---- Cream brick: Generated+Mapping so courses read horizontal, not vertical ribs ----
br=bpy.data.materials.get('VB_Freeman_cream_brick_strong_UNVERIFIED')
if br and br.use_nodes:
    nt=br.node_tree
    brick=None; bump=None; princ=None; tc=None
    for n in nt.nodes:
        if n.type=='TEX_BRICK': brick=n
        if n.type=='BUMP': bump=n
        if n.type=='BSDF_PRINCIPLED': princ=n
        if n.type=='TEX_COORD': tc=n
    if brick and princ:
        # clear old Object links; use Generated via Mapping
        for l in list(brick.inputs['Vector'].links):
            nt.links.remove(l)
        if not tc:
            tc=nt.nodes.new('ShaderNodeTexCoord')
        mapping=None
        for n in nt.nodes:
            if n.type=='MAPPING': mapping=n; break
        if not mapping:
            mapping=nt.nodes.new('ShaderNodeMapping')
        mapping.inputs['Scale'].default_value=(2.2, 2.2, 2.2)
        mapping.inputs['Rotation'].default_value=(0.0, 0.0, 0.0)
        nt.links.new(tc.outputs['Generated'], mapping.inputs['Vector'])
        nt.links.new(mapping.outputs['Vector'], brick.inputs['Vector'])
        brick.inputs['Color1'].default_value=(0.80, 0.74, 0.60, 1)
        brick.inputs['Color2'].default_value=(0.70, 0.64, 0.52, 1)
        brick.inputs['Mortar'].default_value=(0.32, 0.28, 0.22, 1)
        brick.inputs['Brick Width'].default_value=0.22
        brick.inputs['Row Height'].default_value=0.068
        brick.inputs['Mortar Size'].default_value=0.018
        brick.inputs['Scale'].default_value=4.0  # more courses visible at eye
        if bump:
            bump.inputs['Strength'].default_value=0.28
            bump.inputs['Distance'].default_value=0.005
        log['fixes'].append('cream_brick_generated_mapping_scale')

json.dump(log, open(DATA+'/vb_polish.json','w'), indent=2)
print('VB POLISH', json.dumps(log))
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED')
