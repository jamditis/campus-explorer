"""2026-10-15 ba: local albedo tone on CCOM lab eave/cornice/parapet mats (main only).

UNVERIFIED artistic. Does NOT change global soft-light recipe. Materials only
(no geometry → no alignment rerun). Idempotent via material['ba_cornice_tone']=1.

Targets the bright white cornice/eave slab over the east lab windows that still
reads as the hottest facade strip in the oblique after az roof tone.

Args after --: [--save] [--mul=0.74]
"""
import bpy, sys
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
SAVE = '--save' in argv
MUL = 0.74
for a in argv:
    if a.startswith('--mul='):
        MUL = float(a.split('=', 1)[1])

# Visible eave/cornice/parapet strip over lab (hidden y parapet skipped but safe)
TARGETS = (
    'CCOM_east_parapet_z_20261014z',   # eave band
    'CCOM_east_par_z2_20261014z',      # face plug at eave
    'CCOM_east_wall_cap_20261014z',    # eave returns
    'CCOM_east_parapet_20261014y',     # hidden y band (keep in sync)
    'CCOM_east_soffit_z_20261014z',    # underside if lit
)

changed = 0
for name in TARGETS:
    m = bpy.data.materials.get(name)
    if not m:
        print('MISSING', name)
        continue
    if m.get('ba_cornice_tone') == MUL:
        print('SKIP', name, 'already', MUL)
        continue
    if not m.use_nodes:
        print('NO_NODES', name)
        continue
    prin = next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if not prin:
        print('NO_PRIN', name)
        continue
    # If Base Color already linked, insert/update a Multiply node; else scale default
    t = m.node_tree
    mul_node = t.nodes.get('BA_cornice_mul')
    if mul_node is None:
        mul_node = t.nodes.new('ShaderNodeMix')
        mul_node.name = 'BA_cornice_mul'
        mul_node.label = 'BA_cornice_mul'
        mul_node.data_type = 'RGBA'
        mul_node.blend_type = 'MULTIPLY'
        mul_node.inputs['Factor'].default_value = 1.0
        mul_node.location = (-200, 200)
    # factor color = (MUL,MUL,MUL)
    mul_node.inputs[7].default_value = (MUL, MUL, MUL, 1.0)
    base_in = prin.inputs['Base Color']
    existing = list(base_in.links)
    if existing:
        src = existing[0].from_socket
        if src.node == mul_node:
            # already wired; just update mul
            pass
        else:
            for l in existing:
                t.links.remove(l)
            t.links.new(src, mul_node.inputs[6])
            t.links.new(mul_node.outputs[2], base_in)
    else:
        # store original default into input 6, then link
        orig = tuple(base_in.default_value)
        mul_node.inputs[6].default_value = orig
        t.links.new(mul_node.outputs[2], base_in)
        # also bump roughness slightly so it is less specular-hot
        if not prin.inputs['Roughness'].links:
            r = prin.inputs['Roughness'].default_value
            prin.inputs['Roughness'].default_value = max(r, 0.62)
        if 'Specular IOR Level' in prin.inputs and not prin.inputs['Specular IOR Level'].links:
            prin.inputs['Specular IOR Level'].default_value = min(
                prin.inputs['Specular IOR Level'].default_value, 0.28)
    m['ba_cornice_tone'] = MUL
    m['ba_cornice_tone_note'] = (
        'UNVERIFIED artistic; local cornice/eave albedo ×%.2f; soft-light recipe untouched' % MUL
    )
    print('TONED', name, 'mul', MUL, 'users', m.users)
    changed += 1
print('CHANGED', changed, 'MUL', MUL)
if SAVE:
    bpy.ops.wm.save_mainfile()
    print('SAVED', bpy.data.filepath)
