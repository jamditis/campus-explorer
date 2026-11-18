"""Follow-up for 20261014ab: assign real CCOM wall plaster (Wall_SCM_precast) to equip wall patches.
Renders showed procedural noise still reading as bright plates vs textured facade.
RERUNNABLE. --save to write."""
import bpy, sys
SAVE = '--save' in sys.argv
TAG = '20261014ab'
src = bpy.data.materials.get('Wall_SCM_precast')
if not src:
    raise SystemExit('MISSING Wall_SCM_precast')
# Duplicate so we can nudge albedo slightly darker without changing whole building
name = 'CCOM_equip_wall_match_' + TAG
m = bpy.data.materials.get(name)
if m is None:
    m = src.copy(); m.name = name
# If principled base is linked to texture, add a Mix/Multiply darken after color
nt = m.node_tree
bsdf = next(n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED')
# find existing color link into Base Color
links = list(bsdf.inputs['Base Color'].links)
# insert HueSat or Mix to darken ~8%
hs = nt.nodes.get('AB_Darken') or nt.nodes.new('ShaderNodeHueSaturation')
hs.name = 'AB_Darken'; hs.label = 'AB_Darken'; hs.location = (-150, 200)
hs.inputs['Value'].default_value = 0.90  # darken
hs.inputs['Saturation'].default_value = 1.05
# reconnect: tex -> hs -> bsdf
if links:
    from_sock = links[0].from_socket
    nt.links.remove(links[0])
    nt.links.new(from_sock, hs.inputs['Color'])
else:
    hs.inputs['Color'].default_value = bsdf.inputs['Base Color'].default_value
nt.links.new(hs.outputs['Color'], bsdf.inputs['Base Color'])
print('mat ready', m.name, 'from', src.name)

dcol = bpy.data.collections.get('CCOM_loading_dock_20261014jf3')
n = 0
for o in (dcol.objects if dcol else []):
    if any(k in o.name for k in ('wallpatch', 'wallhead', 'wallback')):
        if o.data and o.material_slots:
            o.material_slots[0].material = m
        elif o.data:
            o.data.materials.clear(); o.data.materials.append(m)
        n += 1
print('reassigned', n)
# keep pier mat alone (shared elsewhere)
print('TAG', TAG, 'patchfix done')
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED')
else:
    print('dry-run')
