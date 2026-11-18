# vv rebuild: path links must leave the landing and meet the OSM walk further from the wall.
# Prior links nested inside the landing bbox (lateral only). Now: start at door-front landing
# outer edge; end at a walk point ~4–8 m along the OSM centreline from the wall end.
import bpy, bmesh, os, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree

SAVE = os.environ.get('SAVE') == '1'
sc = bpy.context.scene
dg = bpy.context.evaluated_depsgraph_get()

# remove prior path_link only
for o in [o for o in bpy.data.objects if 'vv_obj' in o and 'path_link' in o.name]:
    me = o.data; bpy.data.objects.remove(o)
    if me and me.users == 0 and hasattr(me, 'vertices'): bpy.data.meshes.remove(me)
# remove prior grass-hide marker objs if any
for o in [o for o in bpy.data.objects if 'vv_obj' in o and 'grass_keepout' in o.name]:
    me = o.data; bpy.data.objects.remove(o)
    if me and me.users == 0 and hasattr(me, 'vertices'): bpy.data.meshes.remove(me)

GN = ['Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km','RZ2_SC_LiDAR_ground_patch',
      'QW_DTM_north_edge_ramp_UNVERIFIED','SA_ground_lower_patch_UNVERIFIED']
gnd = [(bpy.data.objects[n].evaluated_get(dg), bpy.data.objects[n].matrix_world)
       for n in GN if n in bpy.data.objects]

def hit(x, y):
    best = None
    for e, mw in gnd:
        iw = mw.inverted()
        r = e.ray_cast(iw @ Vector((x, y, 400)), (iw.to_3x3() @ Vector((0, 0, -1))).normalized())
        if r[0]:
            z = (mw @ r[1]).z
            if best is None or z > best: best = z
    return best

def door_basis(k):
    G = bpy.data.objects['TJ_Blanton_entrance_%d_glass_UNVERIFIED' % k]
    gv = [G.matrix_world @ v.co for v in G.data.vertices]
    gc = sum(gv, Vector()) / len(gv)
    best = None
    for i in range(len(gv)):
        for j in range(i + 1, len(gv)):
            d = gv[j] - gv[i]; d.z = 0
            if best is None or d.length > best.length: best = d
    u = best.normalized(); n = Vector((-u.y, u.x, 0))
    BC = Vector((141.6, 450.4, 0))
    if (gc - BC).to_2d().dot(n.to_2d()) < 0: n = -n
    return gc, u, n

# OSM centres from east_osm (scene xy already)
import json as _j
_W = _j.load(open('data/td/east_osm.json'))['ways']
# door → (walk_obj, osm_way_id, prefer_outward)
SPEC = {
    0: dict(walk='TJ_walk_313029110_UNVERIFIED', osm='313029110', outward=True),
    1: dict(walk='TJ_walk_313029908_UNVERIFIED', osm='313029908', outward=False),  # tunnel; no lawn path
    2: dict(walk='TJ_walk_313029910_UNVERIFIED', osm='313029910', outward=True),
}

wm = None
for nm in ('TJ_walk_313029110_UNVERIFIED','TJ_walk_313029908_UNVERIFIED'):
    o = bpy.data.objects.get(nm)
    if o and o.data.materials: wm = o.data.materials[0]; break

col = bpy.data.collections.get('VV_Blanton_landing_path_join_UNVERIFIED')
if col is None:
    col = bpy.data.collections.new('VV_Blanton_landing_path_join_UNVERIFIED')
    sc.collection.children.link(col)

def walk_bvh(nm):
    o = bpy.data.objects[nm]
    bm = bmesh.new(); bm.from_object(o, dg); bm.transform(o.matrix_world)
    verts = [v.co.copy() for v in bm.verts]
    bvh = BVHTree.FromBMesh(bm)
    bm.free()
    return o, verts, bvh

def densify_osm(pts, step=0.5):
    P = [Vector((p[0], p[1], 0)) for p in pts]
    S = []
    for i in range(len(P) - 1):
        a, b = P[i], P[i + 1]; L = (b - a).length
        n = max(1, int(L / step))
        for j in range(n):
            S.append(a + (b - a) * (j / n))
    S.append(P[-1])
    return S

log = []
keepout_polys = []  # xy polygons for grass hide

for k, spec in SPEC.items():
    gc, u, n = door_basis(k)
    L = bpy.data.objects['TU_Blanton_entrance_%d_landing_UNVERIFIED' % k]
    lv = [L.matrix_world @ v.co for v in L.data.vertices]
    zhi = max(p.z for p in lv)
    top = [p for p in lv if p.z > zhi - 0.1]
    door_front = [p for p in top if abs((p - gc).dot(u)) < 1.5] or top
    door_front.sort(key=lambda p: (p - gc).dot(n))
    start = sum(door_front[max(0, len(door_front)*2//3):], Vector()) / max(1, len(door_front)//3)
    # nudge start slightly past landing outer along n so ribbon clearly leaves the pad
    start = start + n * 0.15

    o, wverts, wbvh = walk_bvh(spec['walk'])
    osm_pts = _W[spec['osm']]['pts']
    # wall end = osm node nearest building (min |n| from gc, or nearest to gc)
    dens = densify_osm(osm_pts, 0.4)
    # annotate each dens point with along-path distance from wall end
    wall_end = min(dens, key=lambda p: (p.x - gc.x)**2 + (p.y - gc.y)**2)
    # order dens from wall_end along the polyline
    # find index of wall_end approx
    wi = min(range(len(dens)), key=lambda i: (dens[i] - wall_end).length)
    # build distance along chain from wi toward both directions; pick the direction
    # that goes more +n (outward) if outward else either
    def chain_from(i, direction):
        out = []; dist = 0.0; prev = dens[i]
        out.append((0.0, dens[i]))
        idx = i
        while True:
            nxt = idx + direction
            if nxt < 0 or nxt >= len(dens): break
            d = (dens[nxt] - prev).length
            dist += d; out.append((dist, dens[nxt])); prev = dens[nxt]; idx = nxt
        return out

    c1 = chain_from(wi, 1); c2 = chain_from(wi, -1)
    def outward_score(chain):
        if len(chain) < 2: return -1e9
        # mean n of points 2–8 m along
        pts = [p for d, p in chain if 2.0 <= d <= 10.0]
        if not pts: pts = [p for d, p in chain if d > 1.0][:5]
        if not pts: return -1e9
        return sum((p - gc).dot(n) for p in pts) / len(pts)

    if spec['outward']:
        chain = c1 if outward_score(c1) >= outward_score(c2) else c2
        # target: ~5.5 m along chain from wall, else farthest available >= 3 m
        cand = [p for d, p in chain if 4.5 <= d <= 7.5]
        if not cand:
            cand = [p for d, p in chain if d >= 3.0]
        if not cand:
            cand = [p for d, p in chain if d >= 1.5]
        if not cand:
            cand = [chain[-1][1]]
        end_xy = cand[len(cand)//2]
    else:
        # door 1: join landing to walk end near wall (apron). Target = average of walk
        # verts nearest wall_end, slightly into the walk along -n (building/tunnel side)
        near = sorted(wverts, key=lambda q: (q.x - wall_end.x)**2 + (q.y - wall_end.y)**2)[:20]
        end_xy = sum((Vector((q.x, q.y, 0)) for q in near), Vector((0,0,0))) / len(near)
        # also pull start toward walk a bit
        start = start  # keep

    end = Vector((end_xy.x, end_xy.y, 0))
    # z from ground / walk
    ez = hit(end.x, end.y) or (gc.z - 1.2)
    # if over walk, prefer walk z+8mm
    loc, normal, idx, dist = wbvh.find_nearest(Vector((end.x, end.y, ez + 0.06)))
    if loc is not None and dist < 1.2:
        ez = loc.z
    end.z = ez

    direction = Vector((end.x - start.x, end.y - start.y, 0))
    length = direction.length
    if length < 0.4:
        print('VV skip short', k, length); continue
    dhat = direction.normalized()
    side = Vector((-dhat.y, dhat.x, 0))
    if abs(side.dot(u)) > abs(side.dot(Vector((-n.y, n.x, 0)))):
        # prefer side aligned with something stable
        pass
    HALF_W = 0.95
    N = max(5, int(length / 0.4) + 1)
    bm = bmesh.new(); rows = []; g0 = hit(start.x, start.y) or start.z - 0.06
    for i in range(N + 1):
        t = i / N
        c = start.lerp(end, t)
        hw = HALF_W * (1.0 - 0.04 * t)
        tops = []
        for s in (-hw, hw):
            q = Vector((c.x, c.y, 0)) + side * s
            z = hit(q.x, q.y) or g0
            z_final = z + 0.06
            loc, normal, idx, dist = wbvh.find_nearest(Vector((q.x, q.y, z + 0.06)))
            if loc is not None and dist < 1.3:
                z_final = max(z + 0.06, loc.z + 0.008)
            # near start, also sit at least landing top - 2mm if overlapping landing xy
            tops.append(bm.verts.new((q.x, q.y, z_final)))
        row = ([bm.verts.new((tops[0].co.x, tops[0].co.y, tops[0].co.z - 0.22))]
               + tops
               + [bm.verts.new((tops[1].co.x, tops[1].co.y, tops[1].co.z - 0.22))])
        rows.append(row)
    for a, b in zip(rows, rows[1:]):
        for j in range(len(a) - 1):
            try: bm.faces.new((a[j], a[j+1], b[j+1], b[j]))
            except ValueError: pass
    for row, rev in ((rows[0], False), (rows[-1], True)):
        try: bm.faces.new(list(reversed(row)) if rev else row)
        except ValueError: pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new('VV_Blanton_entrance_%d_path_link_UNVERIFIED' % k)
    bm.to_mesh(me); bm.free()
    if wm: me.materials.append(wm)
    ob = bpy.data.objects.new(me.name, me); col.objects.link(ob)
    ob['vv_obj'] = 1
    ob['UNVERIFIED'] = (
        'draped concrete link door %d landing → OSM walk %s (~%.1fm); width ~1.9 m; '
        'joins shifted door to footway centreline away from wall' % (k, spec['osm'], length)
    )
    vs = [ob.matrix_world @ v.co for v in me.vertices]
    entry = dict(
        k=k, walk=spec['walk'], osm=spec['osm'], outward=spec['outward'], length=round(length, 2),
        start=[round(x, 2) for x in start], end=[round(x, 2) for x in end],
        bbox=[round(min(v.x for v in vs),2), round(max(v.x for v in vs),2),
              round(min(v.y for v in vs),2), round(max(v.y for v in vs),2)],
        land_bbox=[round(min(p.x for p in lv),2), round(max(p.x for p in lv),2),
                   round(min(p.y for p in lv),2), round(max(p.y for p in lv),2)],
    )
    # how much of link bbox sticks outside landing bbox?
    lx0,lx1,ly0,ly1 = entry['land_bbox']
    outside = sum(1 for v in vs if not (lx0-0.05 <= v.x <= lx1+0.05 and ly0-0.05 <= v.y <= ly1+0.05))
    entry['verts_outside_landing'] = outside
    entry['frac_outside'] = round(outside / max(1, len(vs)), 2)
    log.append(entry)
    print('REBUILD', entry)
    keepout_polys.append(dict(k=k, x0=entry['bbox'][0]-0.3, x1=entry['bbox'][1]+0.3,
                              y0=entry['bbox'][2]-0.3, y1=entry['bbox'][3]+0.3))

# Hide grass points under new links + landings (reversible: store indices on object prop)
g = bpy.data.objects.get('TJ_Webster_lawn_grass_points_UNVERIFIED')
if g and keepout_polys:
    # also include TU landings
    for k in range(3):
        L = bpy.data.objects.get('TU_Blanton_entrance_%d_landing_UNVERIFIED' % k)
        if not L: continue
        lv = [L.matrix_world @ v.co for v in L.data.vertices]
        keepout_polys.append(dict(k='L%d'%k, x0=min(p.x for p in lv)-0.2, x1=max(p.x for p in lv)+0.2,
                                  y0=min(p.y for p in lv)-0.2, y1=max(p.y for p in lv)+0.2))
    # Build new mesh without points in keepout; stash original name for revert via backup
    # Safer: set point positions to z=-999 (hide below) and store vv_grass_hidden list
    # Actually modifying TJ grass is invasive; use a vertex group / hide by moving.
    # Prefer: store indices in a JSON and set those verts' z very low; on revert restore from backup blend.
    mw = g.matrix_world; imw = mw.inverted()
    hidden = []
    me = g.data
    for i, v in enumerate(me.vertices):
        p = mw @ v.co
        for poly in keepout_polys:
            if poly['x0'] <= p.x <= poly['x1'] and poly['y0'] <= p.y <= poly['y1']:
                # store original local z
                hidden.append((i, v.co.z))
                v.co.z = -500.0  # bury
                break
    me.update()
    g['vv_grass_hidden'] = 1
    json.dump([{'i': i, 'z': z} for i, z in hidden], open('data/vv/grass_hidden.json', 'w'))
    print('VV grass hidden', len(hidden))

# Aim closeup cam better: stand where link 0 is visible (south of door, looking back N)
gc0, u0, n0 = door_basis(0)
# place cam along the link midpoint, offset sideways
link0 = bpy.data.objects.get('VV_Blanton_entrance_0_path_link_UNVERIFIED')
if link0:
    vs = [link0.matrix_world @ v.co for v in link0.data.vertices]
    mid = sum(vs, Vector()) / len(vs)
    loc = mid + n0 * 4.0 + u0 * 3.5
    gz = hit(loc.x, loc.y) or 137
    loc.z = gz + 1.7
    tgt = mid + Vector((0, 0, 0.2))
    cam = bpy.data.objects.get('VV_CAM_closeup_Blanton_landing_path_join')
    if cam:
        cam.location = loc
        cam.rotation_euler = (tgt - loc).to_track_quat('-Z', 'Y').to_euler()
        print('VV cam reaimed', [round(x,1) for x in loc], '→', [round(x,1) for x in tgt])

json.dump(log, open('data/vv/rebuild.json', 'w'), indent=1)
print('OBJS', len(bpy.data.objects))
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED')
