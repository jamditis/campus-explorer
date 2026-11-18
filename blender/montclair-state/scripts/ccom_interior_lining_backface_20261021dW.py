"""2026-10-21 session dW (~11:37 AM ET). Corridor walls between the south/west windows showed the CCOM building shell's rough
exterior precast stucco from INSIDE (dV flag; Joe's photos 04/05 show smooth white painted walls). The shell's outward normals mean
the interior sees its BACK faces, so the shell material 'Wall_SCM_precast*' and the loading-dock window patches 'CCOM_equip_wall_match*' (backs seen from SOUTH0, probe data/dW/probe4_dW.py) get a backface-only smooth white paint
(Mix Shader by Geometry.Backfacing; front faces unchanged). Nodes are named dW_*; idempotent; REVERT=1 removes. SAVE=1 saves.
Reports the backfacing test at 6 interior wall hits first (must be all backfaces, else nothing is changed)."""
import bpy, os
from mathutils import Vector
dg = bpy.context.evaluated_depsgraph_get(); scn = bpy.context.scene
def clean(m):
    nt = m.node_tree; out = nt.nodes.get('dW_orig_out_link')
    for n in [n for n in nt.nodes if n.name.startswith('dW_')]:
        if n.name == 'dW_mix':
            src = n.inputs[1].links[0].from_socket if n.inputs[1].links else None
            outn = [l.to_socket for l in n.outputs[0].links]
            for s in outn:
                if src: nt.links.new(src, s)
        nt.nodes.remove(n)
# backface test: rays from inside the raised corridors toward the exterior wall
tests = [((0, -20.5, 138.4), (0.24, -0.97, 0)), ((5, -21.7, 138.0), (0.24, -0.97, 0)), ((-16, -12.5, 138.2), (0.24, -0.97, 0)),
         ((-20.0, -6, 138.3), (-0.97, -0.24, 0)), ((-20.5, -1, 138.0), (-0.97, -0.24, 0)), ((10, -19.5, 138.2), (0.24, -0.97, 0))]
mats = set(); bf = []
for o, d in tests:
    org = Vector(o); dv = Vector(d).normalized()
    for _ in range(8):
        hit, loc, no, idx, ob, mt = scn.ray_cast(dg, org, dv, distance=10)
        if not hit: break
        if ob.name.startswith('School of Communication'):
            e = ob.evaluated_get(dg); m = e.material_slots[e.data.polygons[idx].material_index].material
            mats.add(m.name); bf.append(no.dot(dv) > 0); break
        org = loc + dv * 1e-3
print('DW3 hits', len(bf), 'backfacing', bf, 'mats', mats, flush=True)
targets = [m for m in bpy.data.materials if m.name.startswith(('Wall_SCM_precast', 'CCOM_equip_wall_match')) and m.use_nodes and m.library is None]
for m in targets: clean(m)
if os.environ.get('REVERT') != '1':
    assert bf and all(bf), 'interior hits are not all backfaces; abort'
    for m in targets:
        nt = m.node_tree
        out = next(n for n in nt.nodes if n.type == 'OUTPUT_MATERIAL' and n.is_active_output)
        src = out.inputs['Surface'].links[0].from_socket
        geo = nt.nodes.new('ShaderNodeNewGeometry'); geo.name = 'dW_geo'
        p = nt.nodes.new('ShaderNodeBsdfPrincipled'); p.name = 'dW_paint'
        p.inputs['Base Color'].default_value = (0.80, 0.79, 0.76, 1); p.inputs['Roughness'].default_value = 0.55
        mix = nt.nodes.new('ShaderNodeMixShader'); mix.name = 'dW_mix'
        nt.links.new(geo.outputs['Backfacing'], mix.inputs[0]); nt.links.new(src, mix.inputs[1]); nt.links.new(p.outputs[0], mix.inputs[2])
        nt.links.new(mix.outputs[0], out.inputs['Surface'])
        # displacement stays (shell is mostly flat); bump only from texture
        print('DW3 lined', m.name, 'users', m.users, flush=True)
if os.environ.get('SAVE') == '1': bpy.ops.wm.save_mainfile(); print('DW3_SAVED', flush=True)
