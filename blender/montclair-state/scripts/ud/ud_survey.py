"""Survey UA asphalt + TY walks for session ud polish."""
import bpy, json, os
OUT = '/workspace/nj-scenes/montclair-state/data/ud/survey.md'
lines = []
def p(s=''):
    lines.append(s); print(s)

# Collections of interest
for cn in ['UA_Normal_Ave_edge_UNVERIFIED', 'TY_Nursing_Partridge_approaches_UNVERIFIED']:
    c = bpy.data.collections.get(cn)
    p(f'## Collection {cn}')
    if not c:
        p('  MISSING'); continue
    for o in sorted(c.objects, key=lambda x: x.name):
        mats = [slot.material.name if slot.material else None for slot in o.material_slots]
        nverts = len(o.data.vertices) if o.type=='MESH' and o.data else 0
        nfaces = len(o.data.polygons) if o.type=='MESH' and o.data else 0
        bb = [round(v,2) for v in o.bound_box[0]] if o.type=='MESH' else None
        # world bbox rough
        if o.type=='MESH' and o.data and nverts:
            from mathutils import Vector
            ws = [o.matrix_world @ v.co for v in o.data.vertices]
            xs=[v.x for v in ws]; ys=[v.y for v in ws]; zs=[v.z for v in ws]
            bbox = (round(min(xs),1), round(max(xs),1), round(min(ys),1), round(max(ys),1), round(min(zs),2), round(max(zs),2))
        else:
            bbox = None
        p(f'  {o.name} type={o.type} verts={nverts} faces={nfaces} mats={mats} bbox_xy_z={bbox} tags={{ua:{o.get("ua_obj")},ty:{o.get("ty_obj")},ud:{o.get("ud_obj")}}}')

p('\n## Asphalt-related materials')
for m in sorted(bpy.data.materials, key=lambda x: x.name):
    if any(k in m.name.lower() for k in ['asphalt','asph','road','worn']):
        rgb = None
        rough = None
        if m.use_nodes and m.node_tree:
            b = m.node_tree.nodes.get('Principled BSDF')
            if b:
                rgb = tuple(round(c,4) for c in b.inputs['Base Color'].default_value[:3])
                rough = round(b.inputs['Roughness'].default_value, 3)
                # check noise/ramp
                noise = [n for n in m.node_tree.nodes if n.type=='TEX_NOISE']
                ramps = [n for n in m.node_tree.nodes if n.type=='VALTORGB']
                ramp_cols = []
                for r in ramps:
                    for e in r.color_ramp.elements:
                        ramp_cols.append(tuple(round(c,4) for c in e.color[:3]))
        users = m.users
        objs_using = [o.name for o in bpy.data.objects if any(s.material==m for s in o.material_slots)]
        p(f'  {m.name} users={users} rgb={rgb} rough={rough} ramp={ramp_cols if m.use_nodes else None} objs={objs_using[:12]}{"..." if len(objs_using)>12 else ""}')

p('\n## TY walk mesh edge stats (jaggedness proxy)')
import bmesh
from mathutils import Vector
for o in bpy.data.objects:
    if not (o.get('ty_obj') and o.type=='MESH' and ('footway' in o.name or 'apron' in o.name.lower() or 'walk' in o.name.lower())):
        continue
    bm = bmesh.new(); bm.from_mesh(o.data); bm.edges.ensure_lookup_table()
    # boundary edges
    bnds = [e for e in bm.edges if e.is_boundary]
    # turn angles along boundary loops
    # rough: count verts with sharp exterior angle
    sharp = 0
    lengths = []
    for e in bnds:
        lengths.append(e.calc_length())
    # face count / perimeter
    perim = sum(lengths) if lengths else 0
    p(f'  {o.name}: faces={len(bm.faces)} verts={len(bm.verts)} boundary_edges={len(bnds)} perim={perim:.1f}m mean_edge={ (sum(lengths)/len(lengths) if lengths else 0):.3f}m')
    bm.free()

p('\n## Existing cams UA_/TY_/UD_')
for o in sorted(bpy.data.objects, key=lambda x: x.name):
    if o.type=='CAMERA' and (o.name.startswith('UA_') or o.name.startswith('TY_') or o.name.startswith('UD_') or o.name.startswith('UC_') or o.name.startswith('UB_')):
        loc = o.location
        p(f'  {o.name} loc=({loc.x:.1f},{loc.y:.1f},{loc.z:.1f})')

open(OUT,'w').write('\n'.join(lines)+'\n')
print('WROTE', OUT)
