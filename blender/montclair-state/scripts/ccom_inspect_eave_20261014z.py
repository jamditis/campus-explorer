"""Inspect SE eave / wall after 20261014y vert collapse; atrium glass; lounge shell."""
import bpy, bmesh
from mathutils import Vector
from collections import defaultdict

wo = bpy.data.objects['School of Communication and Media walls']
mw = wo.matrix_world
me = wo.data
EAVE = 143.017

# SE-east verts near eave
near = []
for v in me.vertices:
    p = mw @ v.co
    if p.x > 18 and p.y < 12 and abs(p.z - EAVE) < 1.5:
        near.append((p.x, p.y, p.z))
print(f'SE-east verts within 1.5 of eave: {len(near)}')
if near:
    zs = [t[2] for t in near]
    print(f'  z min/max {min(zs):.3f}..{max(zs):.3f}')
    # check for non-manifold / holes via bmesh
bm = bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table(); bm.faces.ensure_lookup_table()
# world-space SE faces with z near eave
bad_edges = 0
boundary = 0
for e in bm.edges:
    if not e.is_manifold:
        # check if in SE region
        pts = [mw @ v.co for v in e.verts]
        if all(p.x > 16 and p.y < 14 for p in pts) and any(p.z > EAVE - 2 for p in pts):
            bad_edges += 1
    if e.is_boundary:
        pts = [mw @ v.co for v in e.verts]
        if all(p.x > 16 and p.y < 14 for p in pts) and any(abs(p.z - EAVE) < 2 for p in pts):
            boundary += 1
print(f'SE non-manifold edges near eave: {bad_edges}; boundary edges near eave: {boundary}')
# duplicate verts at same XY different Z collapsed?
xy_z = defaultdict(list)
for v in me.vertices:
    p = mw @ v.co
    if p.x > 18 and p.y < 12 and p.z > EAVE - 3:
        key = (round(p.x, 2), round(p.y, 2))
        xy_z[key].append(round(p.z, 3))
multi = {k: v for k, v in xy_z.items() if len(set(v)) > 1}
print(f'SE XY with multiple Z above eave-3: {len(multi)} (sample {list(multi.items())[:5]})')
bm.free()

# Roof objects SE
for rnm in ['School of Communication and Media roof (LiDAR)',
            'School of Communication and Media eave soffit + fascia + rafter',
            'School of Communication and Media barrel tile eave course',
            'School of Communication and Media hip + ridge cap tiles']:
    ro = bpy.data.objects.get(rnm)
    if not ro: print(f'MISSING {rnm}'); continue
    zs = []
    for v in ro.data.vertices:
        p = ro.matrix_world @ v.co
        if p.x > 18 and p.y < 12:
            zs.append(p.z)
    if zs:
        print(f'{rnm}: SE n={len(zs)} z={min(zs):.3f}..{max(zs):.3f}')

# Massing plugs
for o in bpy.data.objects:
    if 'CCOM_east' in o.name and ('parapet' in o.name or 'flat_roof' in o.name or 'massing' in o.name):
        bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
        print(f'  {o.name}: z={min(p.z for p in bb):.2f}..{max(p.z for p in bb):.2f} hide={o.hide_render}')

# Atrium glass
ag = bpy.data.objects.get('CCOM atrium glass (arched, 7x10 grid)')
if ag:
    bb = [ag.matrix_world @ Vector(c) for c in ag.bound_box]
    xs=[p.x for p in bb]; ys=[p.y for p in bb]; zs=[p.z for p in bb]
    print(f'atrium glass: x={min(xs):.2f}..{max(xs):.2f} y={min(ys):.2f}..{max(ys):.2f} z={min(zs):.2f}..{max(zs):.2f}')
    print(f'  loc={tuple(round(x,3) for x in ag.location)} rot={tuple(round(x,3) for x in ag.rotation_euler)}')
else:
    print('NO atrium glass object')
    for o in bpy.data.objects:
        if 'atrium' in o.name.lower() or 'Atrium' in o.name:
            print('  cand', o.name)

# Lounge shell objects
col = bpy.data.collections.get('CCOM_interior_20261014v')
if col:
    for o in col.objects:
        if 'lounge' in o.name.lower():
            bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
            print(f'lounge {o.name}: x={min(p.x for p in bb):.1f}..{max(p.x for p in bb):.1f} '
                  f'y={min(p.y for p in bb):.1f}..{max(p.y for p in bb):.1f} '
                  f'z={min(p.z for p in bb):.1f}..{max(p.z for p in bb):.1f}')

# Lettering
for nm in ('CCOM tower 4a lettering COLLEGE OF', 'CCOM tower 4a lettering COMMUNICATION AND MEDIA'):
    print('lettering', 'OK' if bpy.data.objects.get(nm) else 'MISSING', nm)

print('DONE inspect')
