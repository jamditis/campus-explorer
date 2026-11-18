# vv_probe: measure Blanton landing outer edges vs nearby walk meshes / Footpaths_OSM
import bpy, json, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
import bmesh

OUT = 'data/vv/probe.json'
sc = bpy.context.scene
dg = bpy.context.evaluated_depsgraph_get()

landings = [o for o in bpy.data.objects if o.name.startswith('TU_Blanton_entrance_') and 'landing' in o.name]

# Prefer OSM-sourced walks that serve Blanton doors
PRIORITY = [
    'TJ_walk_313029110_UNVERIFIED',
    'TJ_walk_313029908_UNVERIFIED',
    'TJ_walk_313029909_UNVERIFIED',
    'TJ_walk_313029910_UNVERIFIED',
    'QW_footway_546643369_ext_UNVERIFIED',
    'QW_footway_313027428_ext_UNVERIFIED',
    'QS_footway_313027428_UNVERIFIED',
    'QS_footway_546643369_UNVERIFIED',
    'TR_footway_546643369_S_gap_UNVERIFIED',
    'Footpaths_OSM',
]

walks = []
seen = set()
for nm in PRIORITY:
    o = bpy.data.objects.get(nm)
    if o and o.type == 'MESH' and o.name not in seen:
        walks.append(o); seen.add(o.name)

# also any TJ_walk / QW near Blanton bbox
for o in bpy.data.objects:
    if o.type != 'MESH' or o.name in seen:
        continue
    n = o.name
    if not (n.startswith('TJ_walk_') or n.startswith('QW_footway_') or n.startswith('QS_footway_') or n.startswith('TR_footway_') or n == 'Footpaths_OSM'):
        continue
    if 'bak_' in n or n.startswith('UD_bak'):
        continue
    bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
    cx = sum(v.x for v in bb) / 8; cy = sum(v.y for v in bb) / 8
    if 60 < cx < 200 and 380 < cy < 480:
        walks.append(o); seen.add(o.name)

print('VV landings', [(o.name, len(o.data.vertices)) for o in landings])
print('VV walks', [o.name for o in walks])

def bvh_of(o):
    if not o.data or not getattr(o.data, 'vertices', None) or len(o.data.vertices) == 0:
        return None, None
    try:
        bm = bmesh.new()
        bm.from_object(o, dg)
        bm.transform(o.matrix_world)
        bm.faces.ensure_lookup_table()
        if not bm.faces:
            bm.free(); return None, None
        bvh = BVHTree.FromBMesh(bm)
        verts = [v.co.copy() for v in bm.verts]
        bm.free()
        return bvh, verts
    except Exception as e:
        print('BVH skip', o.name, e)
        return None, None

walk_bvhs = []
for o in walks:
    bvh, verts = bvh_of(o)
    if bvh:
        walk_bvhs.append((o.name, bvh, verts))
        xs = [v.x for v in verts]; ys = [v.y for v in verts]
        print('  walk', o.name, 'verts', len(verts), 'xy', round(min(xs),1), round(max(xs),1), round(min(ys),1), round(max(ys),1))

doors = {}
for k in range(3):
    G = bpy.data.objects.get('TJ_Blanton_entrance_%d_glass_UNVERIFIED' % k)
    F = bpy.data.objects.get('TJ_Blanton_entrance_%d_frame_UNVERIFIED' % k)
    if not G:
        continue
    gv = [G.matrix_world @ v.co for v in G.data.vertices]
    gc = sum(gv, Vector()) / len(gv)
    best = None
    for i in range(len(gv)):
        for j in range(i + 1, len(gv)):
            d = gv[j] - gv[i]; d.z = 0
            if best is None or d.length > best.length:
                best = d
    u = best.normalized(); n = Vector((-u.y, u.x, 0))
    BC = Vector((141.6, 450.4, 0))
    if (gc - BC).to_2d().dot(n.to_2d()) < 0:
        n = -n
    doors[k] = dict(gc=gc, u=u, n=n, G=G.name, F=F.name if F else None)
    print('DOOR', k, 'gc', [round(x,2) for x in gc], 'n', [round(x,3) for x in n])

log = {'doors': {}, 'landings': [], 'walks': [o.name for o in walks]}

# Expected OSM way per door from TJ notes / osm proximity
OSM_FOR_DOOR = {
    0: ['313029110', 'TJ_walk_313029110_UNVERIFIED'],
    1: ['313029908', '313027428', 'TJ_walk_313029908_UNVERIFIED', 'QW_footway_313027428_ext_UNVERIFIED', 'QS_footway_313027428_UNVERIFIED'],
    2: ['313029909', '313029910', 'TJ_walk_313029909_UNVERIFIED', 'TJ_walk_313029910_UNVERIFIED'],
}

for L in landings:
    parts = L.name.split('_')
    k = int(parts[3])
    lv = [L.matrix_world @ v.co for v in L.data.vertices]
    lc = sum(lv, Vector()) / len(lv)
    dinfo = doors[k]
    n = dinfo['n']; u = dinfo['u']; gc = dinfo['gc']
    # outer verts: top surface (high z among high-n)
    # classify verts by n projection
    proj_n = [(p, (p - gc).dot(n)) for p in lv]
    max_n = max(t[1] for t in proj_n)
    outer_pts = [p for p, pn in proj_n if pn > max_n - 0.15]
    # keep top of slab (high z)
    zmax = max(p.z for p in outer_pts)
    outer_pts = [p for p in outer_pts if p.z > zmax - 0.08]
    if not outer_pts:
        outer_pts = [max(lv, key=lambda p: (p - gc).dot(n))]

    # prefer walks matching OSM_FOR_DOOR
    prefer = set(OSM_FOR_DOOR.get(k, []))
    nearest = []
    for p in outer_pts:
        best = None
        for nm, bvh, verts in walk_bvhs:
            loc, normal, idx, dist = bvh.find_nearest(p)
            if loc is None:
                continue
            xy_best = min(verts, key=lambda q: (q.x - p.x)**2 + (q.y - p.y)**2)
            xy_d = ((xy_best.x - p.x)**2 + (xy_best.y - p.y)**2) ** 0.5
            dz = p.z - xy_best.z
            # boost preferred walks (treat as smaller for ranking if close)
            rank = xy_d
            if any(tok in nm for tok in prefer):
                rank = xy_d - 0.5  # slight preference
            cand = dict(walk=nm, dist3=round(dist, 3), xy=round(xy_d, 3), dz=round(dz, 3),
                        hit=[round(x, 3) for x in loc],
                        walk_pt=[round(xy_best.x, 2), round(xy_best.y, 2), round(xy_best.z, 2)],
                        sample=[round(p.x, 2), round(p.y, 2), round(p.z, 2)],
                        preferred=any(tok in nm for tok in prefer),
                        rank=rank)
            if best is None or cand['rank'] < best['rank']:
                best = cand
        if best:
            nearest.append(best)

    nearest.sort(key=lambda c: c['xy'])
    # also: gap from landing outer centroid to preferred walk end
    oc = sum(outer_pts, Vector()) / len(outer_pts)
    pref_gap = None
    for nm, bvh, verts in walk_bvhs:
        if not any(tok in nm for tok in prefer):
            continue
        xy_best = min(verts, key=lambda q: (q.x - oc.x)**2 + (q.y - oc.y)**2)
        xy_d = ((xy_best.x - oc.x)**2 + (xy_best.y - oc.y)**2) ** 0.5
        # walk verts farthest along -n from door (the "end" near wall) vs outer
        # better: find walk verts with high n near door, and verts with low n (far)
        cand = dict(walk=nm, xy=round(xy_d, 3), dz=round(oc.z - xy_best.z, 3),
                    walk_pt=[round(xy_best.x, 2), round(xy_best.y, 2), round(xy_best.z, 2)])
        if pref_gap is None or cand['xy'] < pref_gap['xy']:
            pref_gap = cand

    # How far does preferred walk extend along n from door?
    walk_extent = []
    for nm, bvh, verts in walk_bvhs:
        if not any(tok in nm for tok in prefer):
            continue
        near_door = [v for v in verts if ((v.x - gc.x)**2 + (v.y - gc.y)**2) < 25**2]
        if not near_door:
            continue
        nprojs = [(v - gc).dot(n) for v in near_door]
        walk_extent.append(dict(walk=nm, n_min=round(min(nprojs), 2), n_max=round(max(nprojs), 2),
                                n_landing_outer=round((oc - gc).dot(n), 2)))

    entry = dict(
        name=L.name, k=k,
        centre=[round(x, 2) for x in lc],
        outer_c=[round(x, 2) for x in oc],
        door_gc=[round(x, 2) for x in gc],
        n=[round(x, 3) for x in n],
        u=[round(x, 3) for x in u],
        nearest_min=nearest[0] if nearest else None,
        nearest_med=nearest[len(nearest)//2] if nearest else None,
        pref_gap=pref_gap,
        walk_extent=walk_extent,
        osm_prefer=OSM_FOR_DOOR.get(k),
        n_outer_samples=len(outer_pts),
    )
    log['landings'].append(entry)
    print('LANDING', k, 'outer_c', entry['outer_c'],
          'gap_any', nearest[0]['xy'] if nearest else None, 'to', nearest[0]['walk'] if nearest else None,
          'pref_gap', pref_gap, 'extent', walk_extent)

for k, dinfo in doors.items():
    gc = dinfo['gc']; n = dinfo['n']
    prefer = set(OSM_FOR_DOOR.get(k, []))
    hits = []
    for dist in [i * 0.25 for i in range(0, 60)]:
        p = gc + n * dist
        for nm, bvh, verts in walk_bvhs:
            if not any(tok in nm for tok in prefer) and prefer:
                continue
            loc, normal, idx, d3 = bvh.find_nearest(Vector((p.x, p.y, gc.z)))
            if loc is None:
                continue
            xy = ((loc.x - p.x)**2 + (loc.y - p.y)**2) ** 0.5
            if xy < 1.1:
                hits.append(dict(along=round(dist, 2), walk=nm, xy=round(xy, 3), z=round(loc.z, 3)))
                break
    log['doors'][str(k)] = dict(
        gc=[round(x, 2) for x in gc],
        n=[round(x, 3) for x in n],
        first_pref_walk=hits[0] if hits else None,
        last_pref_walk=hits[-1] if hits else None,
        n_hits=len(hits),
        osm=OSM_FOR_DOOR.get(k),
    )
    print('DOORRAY', k, 'first', hits[0] if hits else None, 'last', hits[-1] if hits else None, 'n', len(hits))

# material name on TJ walk
wm = None
for nm in ('TJ_walk_313029110_UNVERIFIED', 'QW_footway_546643369_ext_UNVERIFIED'):
    o = bpy.data.objects.get(nm)
    if o and o.data.materials:
        wm = o.data.materials[0].name
        break
log['walk_mat'] = wm
print('WALK MAT', wm)

json.dump(log, open(OUT, 'w'), indent=1)
print('WROTE', OUT)
