"""uh pass4: xy-smooth QXP/QY south boundary over UG strip (sawtooth into lawn) + densify seam grass."""
import bpy, bmesh, os, random, json
from mathutils import Vector, Matrix
SAVE = os.environ.get('SAVE') == '1'
D = '/workspace/nj-scenes/montclair-state/'

def xy_smooth_south(name, y_lo=247.5, y_hi=251.5, x0=-68.0, x1=-36.0, rounds=6, lerp=0.55):
    o = bpy.data.objects[name]; me = o.data; mw = o.matrix_world; imw = mw.inverted()
    eu = {}
    for p in me.polygons:
        for ek in p.edge_keys:
            eu[ek] = eu.get(ek, 0) + 1
    bvi = set()
    for ek, c in eu.items():
        if c == 1: bvi.update(ek)
    # south boundary verts in box
    idxs = []
    for vi in bvi:
        p = mw @ me.vertices[vi].co
        if x0 < p.x < x1 and y_lo < p.y < y_hi:
            idxs.append(vi)
    # also include near-boundary tops (within 0.4 m of a boundary vert) for smoother lip
    near = set(idxs)
    for v in me.vertices:
        p = mw @ v.co
        if not (x0 < p.x < x1 and y_lo < p.y < y_hi): continue
        for vi in idxs:
            q = mw @ me.vertices[vi].co
            if (p.x - q.x) ** 2 + (p.y - q.y) ** 2 < 0.45 ** 2:
                near.add(v.index); break
    # adjacency
    adj = {}
    for e in me.edges:
        a, b = e.vertices
        adj.setdefault(a, []).append(b)
        adj.setdefault(b, []).append(a)
    n = 0
    for _ in range(rounds):
        newxy = {}
        for vi in near:
            nbrs = [j for j in adj.get(vi, []) if j in near]
            if len(nbrs) < 2: continue
            ax = sum((mw @ me.vertices[j].co).x for j in nbrs) / len(nbrs)
            ay = sum((mw @ me.vertices[j].co).y for j in nbrs) / len(nbrs)
            p = mw @ me.vertices[vi].co
            # stronger on exact boundary
            w = lerp if vi in idxs else lerp * 0.6
            newxy[vi] = (p.x * (1 - w) + ax * w, p.y * (1 - w) + ay * w, p.z)
        for vi, (x, y, z) in newxy.items():
            me.vertices[vi].co = imw @ Vector((x, y, z)); n += 1
    me.update(); print('UH_EDGE4', name, 'boundary', len(idxs), 'near', len(near), 'ops', n)
    return n

n1 = xy_smooth_south('QXP_pedestrian_area_313024781_paving_UNVERIFIED')
n2 = xy_smooth_south('QY_plaza_rim_band_313024781_UNVERIFIED')

# densify grass: add more points on UG strip if current < 900
go = bpy.data.objects.get('UH_Partridge_E_seam_grass_points_UNVERIFIED')
if go and len(go.data.vertices) < 900:
    rnd = random.Random(20261105 + 7)
    ugo = bpy.data.objects['UG_Partridge_E_seam_fill_lawn_UNVERIFIED']
    umw = ugo.matrix_world
    dg = bpy.context.evaluated_depsgraph_get()
    uge = ugo.evaluated_get(dg)
    FP = [tuple(p) for p in json.load(open(D + 'data/tx/nursing_geom.json'))['footprint']]
    def inside(x, y):
        c = False; n = len(FP)
        for i in range(n):
            x1, y1 = FP[i]; x2, y2 = FP[(i + 1) % n]
            if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-12) + x1: c = not c
        return c
    existing = [(umw @ v.co) for v in go.data.vertices]  # actually grass is identity
    existing = [tuple(v.co) for v in go.data.vertices]
    XA, XB = -67.2, -36.0
    pts = list(existing)
    blk_names = ['QXP_pedestrian_area_313024781_paving_UNVERIFIED','QY_plaza_rim_band_313024781_UNVERIFIED',
                 'Footpaths_OSM','TY_footway_313026406_to_Partridge_UNVERIFIED',
                 'TY_footway_313026407_to_Partridge_UNVERIFIED','TY_footway_313026405_to_Partridge_UNVERIFIED',
                 'TY Partridge entrance steps+landings (UNVERIFIED)']
    blk = [(bpy.data.objects[n].evaluated_get(dg), bpy.data.objects[n].matrix_world)
           for n in blk_names if n in bpy.data.objects]
    def hit_blk(x, y, z):
        for e, mw in blk:
            iw = mw.inverted()
            o0 = iw @ Vector((x, y, z + 40)); o1 = iw @ Vector((x, y, z - 0.05)); d = o1 - o0
            if d.length < 1e-6: continue
            if e.ray_cast(o0, d.normalized(), distance=d.length)[0]: return True
        return False
    added = 0
    for _ in range(2500):
        x = XA + rnd.random() * (XB - XA)
        y = 247.0 + rnd.random() * 4.2
        if inside(x, y): continue
        # avoid stacking on existing
        if any((x - p[0]) ** 2 + (y - p[1]) ** 2 < 0.35 ** 2 for p in pts[-200:] + pts[::max(1,len(pts)//50)]):
            continue
        r = uge.ray_cast(ugo.matrix_world.inverted() @ Vector((x, y, 400)),
                         (ugo.matrix_world.inverted().to_3x3() @ Vector((0, 0, -1))).normalized())
        if not r[0]: continue
        z = (umw @ r[1]).z
        if hit_blk(x, y, z): continue
        pts.append((x, y, z - 0.005)); added += 1
        if len(pts) >= 850: break
    me = bpy.data.meshes.new('UH_Partridge_E_seam_grass_points_UNVERIFIED')
    me.from_pydata(pts, [], [])
    old = go.data; go.data = me
    if old.users == 0: bpy.data.meshes.remove(old)
    print('UH_EDGE4 grass', len(existing), '->', len(pts), 'added', added)
else:
    print('UH_EDGE4 grass skip', go, len(go.data.vertices) if go else None)

if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
