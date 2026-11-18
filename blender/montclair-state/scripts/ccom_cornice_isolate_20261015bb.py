"""2026-10-15 bb: isolate remaining hot CCOM lab facade mats (main only).

UNVERIFIED artistic. Materials only — no geometry, soft-light recipe untouched.
Does NOT further darken ba ×0.58 eave/parapet mats.

Session ba darkened 5 eave/parapet mats; eye/oblique still read hot. Inspect
found different high-albedo sun-facing mats near lab east glazing:
  - CCOM_east_sill_stucco_20261014v  (0.88 cream sill bands, 11 users)
  - CCOM_east_pier_20261014jf        (0.78 cream piers/walls, 16 users)
  - CCOM_shade_gray_20261014jf       (0.78 roller shades reading near-white)

Idempotent via material['bb_cornice_tone']=MUL.
Args after --: [--save] [--mul_sill=0.58] [--mul_pier=0.62] [--mul_shade=0.68]
"""
import bpy, sys
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
SAVE = '--save' in argv

def argf(key, default):
    for a in argv:
        if a.startswith(key + '='):
            return float(a.split('=', 1)[1])
    return default

MUL_SILL = argf('--mul_sill', 0.58)
MUL_PIER = argf('--mul_pier', 0.62)
MUL_SHADE = argf('--mul_shade', 0.68)

# name -> mul; skip anything already ba_cornice_tone (eave set)
TARGETS = {
    'CCOM_east_sill_stucco_20261014v': MUL_SILL,
    'CCOM_east_pier_20261014jf': MUL_PIER,
    'CCOM_shade_gray_20261014jf': MUL_SHADE,
}

changed = 0
for name, MUL in TARGETS.items():
    m = bpy.data.materials.get(name)
    if not m:
        print('MISSING', name)
        continue
    if m.get('ba_cornice_tone'):
        print('SKIP_BA', name, 'already ba', m.get('ba_cornice_tone'))
        continue
    if m.get('bb_cornice_tone') == MUL:
        print('SKIP', name, 'already bb', MUL)
        continue
    if not m.use_nodes:
        print('NO_NODES', name)
        continue
    prin = next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if not prin:
        print('NO_PRIN', name)
        continue
    t = m.node_tree
    mul_node = t.nodes.get('BB_cornice_mul')
    if mul_node is None:
        mul_node = t.nodes.new('ShaderNodeMix')
        mul_node.name = 'BB_cornice_mul'
        mul_node.label = 'BB_cornice_mul'
        mul_node.data_type = 'RGBA'
        mul_node.blend_type = 'MULTIPLY'
        mul_node.inputs['Factor'].default_value = 1.0
        mul_node.location = (-200, 200)
    mul_node.inputs[7].default_value = (MUL, MUL, MUL, 1.0)
    base_in = prin.inputs['Base Color']
    existing = list(base_in.links)
    if existing:
        src = existing[0].from_socket
        if src.node == mul_node:
            pass
        else:
            for l in existing:
                t.links.remove(l)
            t.links.new(src, mul_node.inputs[6])
            t.links.new(mul_node.outputs[2], base_in)
    else:
        orig = tuple(base_in.default_value)
        mul_node.inputs[6].default_value = orig
        t.links.new(mul_node.outputs[2], base_in)
        if not prin.inputs['Roughness'].links:
            r = prin.inputs['Roughness'].default_value
            prin.inputs['Roughness'].default_value = max(r, 0.62)
        if 'Specular IOR Level' in prin.inputs and not prin.inputs['Specular IOR Level'].links:
            prin.inputs['Specular IOR Level'].default_value = min(
                prin.inputs['Specular IOR Level'].default_value, 0.28)
    m['bb_cornice_tone'] = MUL
    m['bb_cornice_tone_note'] = (
        'UNVERIFIED artistic; local sill/pier/shade albedo ×%.2f; soft-light untouched; ba eave mats left alone' % MUL
    )
    eff = tuple(round(mul_node.inputs[6].default_value[i] * MUL, 3) for i in range(3))
    print('TONED', name, 'mul', MUL, 'eff~', eff, 'users', m.users)
    changed += 1
print('CHANGED', changed)
# Confirm ba mats untouched
for n in ('CCOM_east_parapet_z_20261014z', 'CCOM_east_par_z2_20261014z',
          'CCOM_east_wall_cap_20261014z', 'CCOM_east_soffit_z_20261014z'):
    m = bpy.data.materials.get(n)
    print('BA_CHECK', n, m.get('ba_cornice_tone') if m else None, 'bb', m.get('bb_cornice_tone') if m else None)
if SAVE:
    bpy.ops.wm.save_mainfile()
    print('SAVED', bpy.data.filepath)
