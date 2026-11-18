# vv (Nov 7 2026 ~8:30 AM ET, MAIN, day 11 east dorms). ALL UNVERIFIED, reversible (REVERT=1).
# Connect Blanton TU door landings to OSM-sourced TJ walks so landings no longer dead-end on lawn.
# tu shifted doors into clear pier bays and added short landings from old OSM end → new door; the
# landing strip still leaves a gap in front of the *new* door to the OSM walk (walk stays at the
# old footway end). Build short draped concrete path links from each landing's door-front outer
# edge to the nearest preferred TJ walk. Width ~1.8 m, ground +6 cm, soft end ~8 mm above walk
# (SELF_REVIEW 4a). No invented OSM ways; no furniture; no cladding/mat nudging.
import bpy, bmesh, os, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree

REV = os.environ.get('REVERT') == '1'
SAVE = os.environ.get('SAVE') == '1'
DRY = os.environ.get('DRY') == '1'
OUT = 'data/vv/apply.json'

def revert():
    for o in [o for o in bpy.data.objects if 'vv_obj' in o]:
        me = o.data
        bpy.data.objects.remove(o)
        if me and me.users == 0:
            if hasattr(me, 'vertices'):
                bpy.data.meshes.remove(me)
            elif hasattr(me, 'lens'):
                bpy.data.cameras.remove(me)
    for m in [m for m in bpy.data.materials if 'vv_mat' in m]:
        if m.users == 0:
            bpy.data.materials.remove(m)
    c = bpy.data.collections.get('VV_Blanton_landing_path_join_UNVERIFIED')
    if c:
        bpy.data.collections.remove(c)
    print('VV reverted')

revert()
if REV:
    if SAVE:
        bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit

sc = bpy.context.scene
dg = bpy.context.evaluated_depsgraph_get()

GN = ['Terrain_LiDAR_DTM_1m', 'Context_skirt_3DEP_ortho_4km', 'RZ2_SC_LiDAR_ground_patch',
      'QW_DTM_north_edge_ramp_UNVERIFIED', 'SA_ground_lower_patch_UNVERIFIED']
gnd = [(bpy.data.objects[n].evaluated_get(dg), bpy.data.objects[n].matrix_world)
       for n in GN if n in bpy.data.objects]

def hit(x, y):
    best = None
    for e, mw in gnd:
        iw = mw.inverted()
        r = e.ray_cast(iw @ Vector((x, y, 400)), (iw.to_3x3() @ Vector((0, 0, -1))).normalized())
        if r[0]:
            z = (mw @ r[1]).z
            if best is None or z > best:
                best = z
    return best

# Preferred OSM-sourced walks per door (TJ ribbons from east_osm footways ending on Blanton)
WALK_FOR = {
    0: 'TJ_walk_313029110_UNVERIFIED',
    1: 'TJ_walk_313029908_UNVERIFIED',
    2: 'TJ_walk_313029910_UNVERIFIED',  # 313029910 continues NW; 909 is short tunnel
}
# door 2 also touches 909 — use 910 as the continuous outward path; also try 909 if closer
WALK_ALT = {
    2: ['TJ_walk_313029909_UNVERIFIED', 'TJ_walk_313029910_UNVERIFIED'],
    1: ['TJ_walk_313029908_UNVERIFIED'],
    0: ['TJ_walk_313029110_UNVERIFIED'],
}

def door_basis(k):
    G = bpy.data.objects['TJ_Blanton_entrance_%d_glass_UNVERIFIED' % k]
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
    return gc, u, n

def walk_verts(nm):
    o = bpy.data.objects.get(nm)
    if not o or o.type != 'MESH' or not o.data.vertices:
        return None, None, None
    bm = bmesh.new(); bm.from_object(o, dg); bm.transform(o.matrix_world)
    verts = [v.co.copy() for v in bm.verts]
    faces_ok = bool(bm.faces)
    bvh = BVHTree.FromBMesh(bm) if faces_ok else None
    bm.free()
    return o, verts, bvh

# walk material (copy assignment, do not invent bright white)
wm = None
for nm in ('TJ_walk_313029110_UNVERIFIED', 'QW_footway_546643369_ext_UNVERIFIED',
           'TJ_walk_313029908_UNVERIFIED'):
    o = bpy.data.objects.get(nm)
    if o and o.data.materials:
        wm = o.data.materials[0]
        break
print('VV walk mat', wm.name if wm else None)

col = bpy.data.collections.new('VV_Blanton_landing_path_join_UNVERIFIED')
sc.collection.children.link(col)

log = {'links': [], 'skipped': [], 'mat': wm.name if wm else None}
GAP_MIN = 0.35  # m; below this, already joined

for k in range(3):
    gc, u, n = door_basis(k)
    L = bpy.data.objects.get('TU_Blanton_entrance_%d_landing_UNVERIFIED' % k)
    if not L:
        log['skipped'].append(dict(k=k, reason='no landing')); print('VV skip', k, 'no landing'); continue

    # door-front outer sample on landing: verts with high n and near door along u
    lv = [L.matrix_world @ v.co for v in L.data.vertices]
    # top surface approx
    zhi = max(p.z for p in lv)
    top = [p for p in lv if p.z > zhi - 0.1]
    # door-front band: |u| small, high n
    door_front = [p for p in top if abs((p - gc).dot(u)) < 1.6]
    if not door_front:
        door_front = top
    # start = centroid of the outer-most third of door-front verts
    door_front.sort(key=lambda p: (p - gc).dot(n))
    outer_band = door_front[max(0, len(door_front)*2//3):]
    start = sum(outer_band, Vector()) / len(outer_band)

    # pick walk + nearest point
    cands = []
    for nm in WALK_ALT.get(k, [WALK_FOR[k]]):
        o, verts, bvh = walk_verts(nm)
        if not verts:
            continue
        # nearest vert to start
        nv = min(verts, key=lambda q: (q.x - start.x)**2 + (q.y - start.y)**2)
        xy = ((nv.x - start.x)**2 + (nv.y - start.y)**2) ** 0.5
        cands.append((xy, nm, o, verts, bvh, nv))
    if not cands:
        log['skipped'].append(dict(k=k, reason='no walk')); print('VV skip', k, 'no walk'); continue
    cands.sort(key=lambda t: t[0])
    gap, wnm, wo, wverts, wbvh, wpt = cands[0]

    # Also try: nearest walk point that is "outward" enough (for door 1 walk is on -n;
    # still join to nearest — that closes the apron to the OSM end)
    print('VV door', k, 'start', [round(x, 2) for x in start], 'gap', round(gap, 3), 'to', wnm,
          'wpt', [round(x, 2) for x in wpt])

    if gap < GAP_MIN:
        log['skipped'].append(dict(k=k, reason='already_joined', gap=round(gap, 3), walk=wnm))
        print('VV skip', k, 'already joined gap', round(gap, 3)); continue

    # Centreline from start → wpt; soft-end: stop 0.15 m short of walk centre so we butt onto the
    # walk surface rather than overlapping the whole ribbon. End sits 8 mm above walk z.
    direction = wpt - start; direction.z = 0
    length = direction.length
    if length < 1e-3:
        log['skipped'].append(dict(k=k, reason='zero_length')); continue
    dhat = direction.normalized()
    # perpendicular in xy for width (prefer wall-u if nearly parallel to dhat, else rotate dhat)
    side = Vector((-dhat.y, dhat.x, 0))
    # keep side roughly aligned with wall u for nicer butt on landing
    if side.dot(u) < 0:
        side = -side

    HALF_W = 0.90  # 1.8 m total — matches TJ 2.0 m walks closely, slightly under to soft-butt
    # sample along centreline; pull end 0.12 m short so we overlap walk edge softly
    end = start + dhat * max(0.2, length - 0.12)
    N = max(3, int(length / 0.45) + 1)
    rows = []
    bm = bmesh.new()
    g0 = hit(start.x, start.y) or start.z - 0.06
    for i in range(N + 1):
        t = i / N
        c = start.lerp(end, t)
        # width taper slightly at walk end (0.95) for soft visual butt
        hw = HALF_W * (1.0 - 0.08 * t)
        row_top = []
        for s in (-hw, hw):
            q = c + side * s
            z = hit(q.x, q.y) or g0
            # +6 cm like tu/tj; at the walk end (t→1) sit +8 mm above walk hit if available
            z_off = 0.06
            if t > 0.85 and wbvh:
                loc, normal, idx, dist = wbvh.find_nearest(Vector((q.x, q.y, z + 0.06)))
                if loc is not None and dist < 1.5:
                    z_off = max(0.06, (loc.z + 0.008) - z)
            row_top.append(bm.verts.new((q.x, q.y, z + z_off)))
        # skirt down 0.22 m
        row = ([bm.verts.new((row_top[0].co.x, row_top[0].co.y, row_top[0].co.z - 0.22))]
               + row_top
               + [bm.verts.new((row_top[1].co.x, row_top[1].co.y, row_top[1].co.z - 0.22))])
        rows.append(row)
    for a, b in zip(rows, rows[1:]):
        for j in range(len(a) - 1):
            try:
                bm.faces.new((a[j], a[j + 1], b[j + 1], b[j]))
            except ValueError:
                pass
    # close ends
    for row, rev in ((rows[0], False), (rows[-1], True)):
        try:
            bm.faces.new(list(reversed(row)) if rev else row)
        except ValueError:
            pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])

    me = bpy.data.meshes.new('VV_Blanton_entrance_%d_path_link_UNVERIFIED' % k)
    bm.to_mesh(me); bm.free()
    if wm:
        me.materials.append(wm)
    ob = bpy.data.objects.new(me.name, me)
    col.objects.link(ob)
    ob['vv_obj'] = 1
    ob['UNVERIFIED'] = (
        'short draped concrete link from TU Blanton door %d landing to OSM-sourced walk %s; '
        'width ~1.8 m typical; joins shifted door apron to footway that still ends at pre-shift OSM node'
        % (k, wnm.replace('_UNVERIFIED', '').replace('TJ_walk_', ''))
    )
    entry = dict(
        k=k, obj=ob.name, walk=wnm, gap=round(gap, 3), length=round(length, 3),
        start=[round(x, 2) for x in start], end=[round(x, 2) for x in end],
        wpt=[round(x, 2) for x in wpt],
        door_gc=[round(x, 2) for x in gc],
    )
    log['links'].append(entry)
    print('VV link', entry)

if DRY:
    json.dump(log, open(OUT, 'w'), indent=1)
    print('DRY — not saving cams/file')
    # still remove what we made? keep for inspect; user said DRY
    raise SystemExit

# --- cameras ---
# 1) closeup of a fixed landing→path join (prefer door 0 S, largest visual shift)
k_show = 0 if any(e['k'] == 0 for e in log['links']) else (log['links'][0]['k'] if log['links'] else 0)
gc, u, n = door_basis(k_show)
# stand back along n+u, eye height
loc = gc + n * 9.0 + u * (-3.5)
gz = hit(loc.x, loc.y) or 137.0
loc.z = gz + 1.65
tgt = gc + n * 1.2 + Vector((0, 0, 0.4))
cd = bpy.data.cameras.new('VV_CAM_closeup_Blanton_landing_path_join')
cd.lens = 32; cd.clip_end = 30000
co = bpy.data.objects.new(cd.name, cd); col.objects.link(co); co['vv_obj'] = 1
co.location = loc
co.rotation_euler = (tgt - loc).to_track_quat('-Z', 'Y').to_euler()
print('VV cam closeup', [round(x, 1) for x in loc], 'door', k_show)

# 2) eye of Blanton W entrances showing path continuity (doors 1+2)
gc2, u2, n2 = door_basis(2)
loc2 = gc2 + n2 * 16.0 + u2 * (-5.0)
# also pull a bit toward door 1 for both W doors
gc1, u1, n1 = door_basis(1)
mid = (gc1 + gc2) / 2
loc2 = mid + n2 * 14.0 + u2 * (-4.0) + n1 * 2.0
gz2 = hit(loc2.x, loc2.y) or 137.0
loc2.z = gz2 + 1.70
tgt2 = mid + Vector((0, 0, 1.8))
cd = bpy.data.cameras.new('VV_CAM_eye_Blanton_W_path_continuity')
cd.lens = 28; cd.clip_end = 30000
co = bpy.data.objects.new(cd.name, cd); col.objects.link(co); co['vv_obj'] = 1
co.location = loc2
co.rotation_euler = (tgt2 - loc2).to_track_quat('-Z', 'Y').to_euler()
print('VV cam eye', [round(x, 1) for x in loc2])

json.dump(log, open(OUT, 'w'), indent=1)
print('VV links', len(log['links']), 'skipped', log['skipped'])
print('OBJS', len(bpy.data.objects))
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED')
