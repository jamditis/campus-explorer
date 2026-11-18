"""Session ty (Nov 5 2026 ~9:25 AM ET, MAIN, day 9): Partridge Hall approaches.
(1) Real steps + landings from grade up to door sill (GR=140.06) at the 6 OSM-junction entrances.
(2) Drape OSM footways 313026403/404 (and 399/405/406/407 stubs) as concrete walks ~2.2 m onto LiDAR/DTM; snap to landings.
(3) Soften W lawn bank burying GF glass with a reversible concrete areaway apron + hide overlapping SB grass points.
(4) Subtle spandrel weathering streak decals under E/W precast frame (UNVERIFIED).
ALL UNVERIFIED where noted. REVERT=1 removes everything tagged ty_obj (+ restores SB grass hide flags).
"""
import bpy, bmesh, os, json, math
from mathutils import Vector
from mathutils.kdtree import KDTree

REV = os.environ.get('REVERT') == '1'
SAVE = os.environ.get('SAVE') == '1'
D = '/workspace/nj-scenes/montclair-state/'
COLN = 'TY_Nursing_Partridge_approaches_UNVERIFIED'
GR = 140.06          # door sill / ring DTM median (MEASURED, tx)
W_WIDTH = 2.2        # walk width UNVERIFIED (ortho not re-measured; 2.0-2.4 band)
RISER = 0.152        # ~6 in riser UNVERIFIED
TREAD = 0.30         # tread depth UNVERIFIED

def revert():
    # restore SB grass points hidden by ty
    for o in bpy.data.objects:
        if o.get('ty_hid_grass'):
            o.hide_set(False); o.hide_render = False
            del o['ty_hid_grass']
        # restore per-vert hide on SB grass if we stored mask — we use a separate hidden-dupe approach instead
    # restore SB grass points: object TY stores culled indices on custom prop of SB object
    sb = bpy.data.objects.get('SB_AnnexWest_lawn_grass_points_UNVERIFIED')
    if sb and 'ty_grass_z_backup' in sb:
        # restore z of culled points (we set them to -999)
        bak = json.loads(sb['ty_grass_z_backup'])
        me = sb.data
        for i, z in bak:
            if i < len(me.vertices):
                me.vertices[i].co.z = z
        del sb['ty_grass_z_backup']
        me.update()
        print('TY restored SB grass z', len(bak))
    for o in [o for o in list(bpy.data.objects) if o.get('ty_obj')]:
        me = o.data; t = o.type
        bpy.data.objects.remove(o, do_unlink=True)
        if me is not None and me.users == 0:
            if t == 'MESH': bpy.data.meshes.remove(me)
            elif t == 'CAMERA': bpy.data.cameras.remove(me)
    c = bpy.data.collections.get(COLN)
    if c: bpy.data.collections.remove(c)
    for m in [m for m in bpy.data.materials if m.name.startswith('TY_') and m.users == 0]:
        bpy.data.materials.remove(m)
    print('TY REVERTED')

revert()
if REV:
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit

FP = [tuple(p) for p in json.load(open(D + 'data/tx/nursing_geom.json'))['footprint']]
ENT = json.load(open(D + 'data/tx/nursing_entr_nodes.json'))
SD = json.load(open(D + 'data/scene_data.json'))
F = {str(f['id']): f for f in SD['features']}
nFP = len(FP)
A = sum(FP[i][0] * FP[(i + 1) % nFP][1] - FP[(i + 1) % nFP][0] * FP[i][1] for i in range(nFP)) / 2
ccw = A > 0

col = bpy.data.collections.new(COLN)
bpy.context.scene.collection.children.link(col)

# ---------- materials ----------
def mat(name, rgb, rough=0.85, metal=0.0, noise=0.0, alpha=1.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    try: b.inputs['Specular IOR Level'].default_value = 0.3
    except Exception: pass
    if alpha < 1.0:
        m.blend_method = 'HASHED'
        try: b.inputs['Alpha'].default_value = alpha
        except Exception: pass
    if noise:
        n = nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value = 2.2; n.inputs['Detail'].default_value = 6
        r = nt.nodes.new('ShaderNodeValToRGB')
        r.color_ramp.elements[0].color = (rgb[0] * (1 - noise), rgb[1] * (1 - noise), rgb[2] * (1 - noise), 1)
        r.color_ramp.elements[1].color = (*rgb, 1)
        nt.links.new(n.outputs['Fac'], r.inputs['Fac']); nt.links.new(r.outputs['Color'], b.inputs['Base Color'])
    else:
        b.inputs['Base Color'].default_value = (*rgb, 1)
    return m

# reuse SC walk material when present
matw = bpy.data.materials.get('SC_walk_concrete_joints_UNVERIFIED')
if matw is None:
    matw = mat('TY_walk_concrete_UNVERIFIED', (0.42, 0.40, 0.37), 0.88, noise=0.12)
M_land = mat('TY_landing_concrete_UNVERIFIED', (0.40, 0.38, 0.35), 0.86, noise=0.14)
M_step = mat('TY_step_concrete_UNVERIFIED', (0.38, 0.36, 0.33), 0.84, noise=0.10)
M_apron = mat('TY_W_areaway_apron_UNVERIFIED', (0.36, 0.34, 0.31), 0.9, noise=0.16)
M_streak = mat('TY_spandrel_weather_streak_UNVERIFIED', (0.12, 0.11, 0.09), 0.95, alpha=0.55)

# ---------- ground ----------
dg = bpy.context.evaluated_depsgraph_get()
GN = [n for n in (
    'Terrain_LiDAR_DTM_1m', 'SA_ground_lower_patch_UNVERIFIED', 'RZ2_SC_LiDAR_ground_patch_UNVERIFIED',
    'Context_skirt_3DEP_ortho_4km', 'Terrain'
) if n in bpy.data.objects]
# also include existing walks so new walks sit on them cleanly
for nm in list(bpy.data.objects.keys()):
    if nm.startswith('SB_footway_') or nm.startswith('SB_pedestrian_') or nm.startswith('SC_') and 'soil' not in nm:
        if bpy.data.objects[nm].type == 'MESH':
            GN.append(nm)
GN_TERRAIN = [n for n in (
    'Terrain_LiDAR_DTM_1m', 'SA_ground_lower_patch_UNVERIFIED', 'RZ2_SC_LiDAR_ground_patch_UNVERIFIED',
    'Context_skirt_3DEP_ortho_4km', 'Terrain'
) if n in bpy.data.objects]
gnd = [(bpy.data.objects[n].evaluated_get(dg), bpy.data.objects[n].matrix_world) for n in GN]
gnd_t = [(bpy.data.objects[n].evaluated_get(dg), bpy.data.objects[n].matrix_world) for n in GN_TERRAIN]

def _gz_on(x, y, layers):
    best = None
    for e, mw in layers:
        iw = mw.inverted()
        r = e.ray_cast(iw @ Vector((x, y, 400)), (iw.to_3x3() @ Vector((0, 0, -1))).normalized())
        if r[0]:
            z = (mw @ r[1]).z
            if best is None or z > best: best = z
    return best

def gz(x, y):
    return _gz_on(x, y, gnd)

def gz_terrain(x, y):
    return _gz_on(x, y, gnd_t)

def edge_info(i):
    p = Vector((*FP[i], 0)); q = Vector((*FP[(i + 1) % nFP], 0)); e = q - p
    u = e.normalized()
    nr = Vector((u.y, -u.x, 0)) if ccw else Vector((-u.y, u.x, 0))  # outward
    return p, q, u, nr

# map entrance index -> (centre, u along wall, outward normal)
OFF = {3: (3, 4, 1.6), 4: (3, 4, -1.6), 8: (8, 8, 0), 12: (12, 13, 1.6), 13: (13, 13, 0), 14: (13, 14, -1.6)}

def entr_frame(en):
    i = en['i']; a, b, off = OFF[i]
    if a == b:
        p1, q1, u1, n1 = edge_info(i)
        p0, q0, u0, n0 = edge_info((i - 1) % nFP)
        if (q1 - p1).length >= (q0 - p0).length:
            u, nr = u1, n1
        else:
            u, nr = u0, n0
        c = Vector((*FP[i], 0))
    else:
        p, q, u, nr = edge_info(a)
        c = Vector((*FP[i], 0)) + u * off
    return c, u, nr

# ---------- helpers ----------
def box_mesh(bm, c, u, n, w, dep0, dep1, z0, z1, mi=0):
    """box: centreline c, along u width w, depth from dep0 to dep1 along n (outward +), z0..z1"""
    u = Vector((u[0], u[1], 0)).normalized(); n = Vector((n[0], n[1], 0)).normalized()
    c = Vector((c[0], c[1], 0))
    vs = []
    for z in (z0, z1):
        for a, b in ((-1, dep0), (1, dep0), (1, dep1), (-1, dep1)):
            p = c + u * (a * w / 2) + n * b
            vs.append(bm.verts.new((p.x, p.y, z)))
    for f in ((0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)):
        try: bm.faces.new([vs[i] for i in f]).material_index = mi
        except ValueError: pass

def finish(bm, name, mats, smooth=False):
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for m in mats:
        if m: me.materials.append(m)
    for p in me.polygons: p.use_smooth = smooth
    if not me.uv_layers: me.uv_layers.new(name='UVMap')
    for f in me.polygons:
        for li in f.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            me.uv_layers.active.data[li].uv = (co.x / 2.0, co.y / 2.0 + co.z / 2.0)
    o = bpy.data.objects.new(name, me); col.objects.link(o); o['ty_obj'] = 1
    return o

# ---------- 1) stepped landings at each entrance ----------
bmL = bmesh.new()
landing_meta = []
for en in ENT:
    c, u, nr = entr_frame(en)
    # terrain grade at OSM node + outward; E face uses max (skirt holes invented a 1.55 m stairwell in pass 1)
    nx, ny = en['xy']
    z_node = gz_terrain(nx, ny)
    z_door = gz_terrain(*(c + nr * 0.4).to_2d())
    z_out = gz_terrain(*(c + nr * 1.5).to_2d())
    cands = [z for z in (z_node, z_door, z_out) if z is not None]
    if not cands:
        z_grade = GR - 0.2
    elif nr.x > 0.5:  # east face
        z_grade = max(cands)
    else:
        z_grade = sorted(cands)[len(cands) // 2]
    sill = GR
    rise = max(0.0, sill - z_grade)
    if rise > 1.55:
        z_grade = sill - 1.55; rise = 1.55
    n_risers = max(1, int(round(rise / RISER))) if rise > 0.08 else 0
    # actual riser height
    rh = (rise / n_risers) if n_risers else 0.0
    Wdoor = 2.8  # landing width along wall
    # top landing pad at sill, from 0.05 out to 1.1 out
    box_mesh(bmL, c, u, nr, Wdoor + 0.4, 0.05, 1.15, sill - 0.12, sill + 0.02, 0)
    # steps descending outward
    for k in range(n_risers):
        z1 = sill - k * rh
        z0 = z1 - rh
        # tread k: deeper outward
        d0 = 1.15 + k * TREAD
        d1 = d0 + TREAD
        box_mesh(bmL, c, u, nr, Wdoor + 0.2 + 0.05 * k, d0, d1, z0 - 0.02, z1, 1)
    # bottom apron draped-ish flat at grade, further out to meet walk
    d_end = 1.15 + n_risers * TREAD
    box_mesh(bmL, c, u, nr, Wdoor + 0.5, d_end, d_end + 1.4, z_grade - 0.05, z_grade + 0.06, 0)
    landing_meta.append(dict(
        way=en['way'], xy=[round(c.x, 2), round(c.y, 2)],
        z_grade=round(z_grade, 3), rise=round(rise, 3), n_risers=n_risers,
        outward=[round(nr.x, 3), round(nr.y, 3)],
        bottom_xy=[round((c + nr * (d_end + 0.7)).x, 2), round((c + nr * (d_end + 0.7)).y, 2)],
        sill_xy=[round((c + nr * 0.6).x, 2), round((c + nr * 0.6).y, 2)],
    ))
oL = finish(bmL, 'TY Partridge entrance steps+landings (UNVERIFIED)', [M_land, M_step])
oL['UNVERIFIED'] = 'riser/tread sizes guessed; positions at OSM door nodes; grade from LiDAR/DTM'
print('TY landings', landing_meta)

# hide the old TX solid landing blocks visually? We can't easily split the TX mesh.
# Instead leave TX landing under/inside — our new steps sit on top / further out. OK.

# ---------- 2) draped footways ----------
# Prefer connecting OSM way end (outer) to landing bottom.
WANT = ['313026403', '313026404', '313026399', '313026405', '313026406', '313026407']
# existing SB walk for 403 — we extend from its east end to the landing rather than rebuild whole
exist_verts = []
for o in bpy.data.objects:
    if o.type != 'MESH': continue
    nm = o.name
    if not (nm.startswith('SB_footway_') or nm.startswith('SB_pedestrian_') or nm.startswith('QXP_') or nm.startswith('TR_footway_')):
        continue
    mw = o.matrix_world
    for v in o.data.vertices:
        p = mw @ v.co
        if -180 < p.x < -40 and 200 < p.y < 320:
            exist_verts.append(p)
kd_exist = KDTree(max(1, len(exist_verts)))
for i, p in enumerate(exist_verts):
    kd_exist.insert((p.x, p.y, 0), i)
kd_exist.balance()

# landing snap targets
snap = []
for m in landing_meta:
    snap.append(Vector((m['bottom_xy'][0], m['bottom_xy'][1], m['z_grade'] + 0.06)))
kd_snap = KDTree(len(snap))
for i, p in enumerate(snap):
    kd_snap.insert((p.x, p.y, 0), i)
kd_snap.balance()

def resample(pts, step=0.6):
    S = []
    for (ax, ay), (bx, by) in zip(pts[:-1], pts[1:]):
        L = math.hypot(bx - ax, by - ay); n = max(1, int(L / step))
        for i in range(n):
            t = i / n; S.append((ax + (bx - ax) * t, ay + (by - ay) * t))
    S.append(tuple(pts[-1][:2])); return S

def drape_centreline(S, w, name, force_end=None):
    """Build draped concrete ribbon along S; optionally snap last point to force_end (Vector)."""
    if force_end is not None and S:
        S = list(S)
        S[-1] = (force_end.x, force_end.y)
        # also pull last 2-3 samples toward landing
        for k in range(1, min(4, len(S))):
            t = k / 4
            i = -1 - k
            S[i] = (S[i][0] * (1 - t) + force_end.x * t, S[i][1] * (1 - t) + force_end.y * t)
    bm = bmesh.new(); rows = []; nq = 0
    for i, (x, y) in enumerate(S):
        a = S[max(i - 1, 0)]; b = S[min(i + 1, len(S) - 1)]
        tx, ty = b[0] - a[0], b[1] - a[1]; L = math.hypot(tx, ty) or 1
        nx, ny = -ty / L, tx / L
        Lp = (x + nx * w / 2, y + ny * w / 2); Rp = (x - nx * w / 2, y - ny * w / 2)
        zs = [z for z in (gz(*Lp), gz(x, y), gz(*Rp)) if z is not None]
        if not zs:
            rows.append(None); continue
        z = max(zs) + 0.05
        # near landing: lift toward sill apron
        co, idx, dd = kd_snap.find((x, y, 0))
        if dd < 2.5:
            z = max(z, snap[idx].z - 0.02)
        vL = bm.verts.new((Lp[0], Lp[1], z))
        vR = bm.verts.new((Rp[0], Rp[1], z))
        vLb = bm.verts.new((Lp[0], Lp[1], z - 0.28))
        vRb = bm.verts.new((Rp[0], Rp[1], z - 0.28))
        rows.append([vL, vR, vLb, vRb])
    for p, q in zip(rows[:-1], rows[1:]):
        if p is None or q is None: continue
        for quad in ((p[0], q[0], q[1], p[1]), (p[2], q[2], q[0], p[0]), (p[1], q[1], q[3], p[3])):
            try: bm.faces.new(quad); nq += 1
            except ValueError: pass
    if rows and rows[0]:
        try: bm.faces.new((rows[0][0], rows[0][1], rows[0][3], rows[0][2])); nq += 1
        except ValueError: pass
    if rows and rows[-1]:
        try: bm.faces.new((rows[-1][0], rows[-1][2], rows[-1][3], rows[-1][1])); nq += 1
        except ValueError: pass
    if nq == 0:
        bm.free(); return None, 0
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)
    o = finish(bm, name, [matw])
    o['UNVERIFIED'] = 'OSM centreline draped on LiDAR/DTM; width %.1f m assumed' % w
    return o, nq

walk_info = []
for wid in WANT:
    feat = F.get(wid)
    if not feat: continue
    pts = [tuple(p[:2]) for p in feat['pts']]
    if len(pts) < 2: continue
    # which end is the building (closer to footprint centroid)?
    cx = sum(p[0] for p in FP) / len(FP); cy = sum(p[1] for p in FP) / len(FP)
    d0 = math.hypot(pts[0][0] - cx, pts[0][1] - cy)
    d1 = math.hypot(pts[-1][0] - cx, pts[-1][1] - cy)
    if d0 < d1:
        pts = list(reversed(pts))  # outer first, building last
    # find matching landing
    force = None
    for m in landing_meta:
        if m['way'] == wid:
            force = Vector((m['bottom_xy'][0], m['bottom_xy'][1], m['z_grade']))
            break
    S = resample(pts, 0.55)
    # For 403: SB already has most of the walk; only build the last ~4-6 m gap to landing
    if wid == '313026403':
        sb = bpy.data.objects.get('SB_footway_313026403_UNVERIFIED')
        if sb:
            mw = sb.matrix_world
            # keep only samples near the building end that are >1.0 m from existing SB verts
            keep = []
            for x, y in S:
                # near building half
                if x > -100.5:  # eastward toward door
                    dd = kd_exist.find((x, y, 0))[2]
                    if dd >= 0.9 or (force and math.hypot(x - force.x, y - force.y) < 4.0):
                        keep.append((x, y))
            if len(keep) >= 2:
                S = keep
            else:
                # fallback: short stub from SB east tip to landing
                tip = max((mw @ v.co for v in sb.data.vertices), key=lambda p: p.x)
                S = resample([(tip.x, tip.y), (force.x, force.y)], 0.4) if force else S
    # For short E stubs (405/406/407 ~3-4 m): always build full
    # Skip if almost entirely covered already (except forced landing connect)
    if wid not in ('313026403', '313026404') and force is None:
        covered = sum(1 for x, y in S if kd_exist.find((x, y, 0))[2] < 1.0)
        if covered > 0.7 * len(S):
            walk_info.append(dict(way=wid, skipped='already_covered')); continue
    name = 'TY_footway_%s_to_Partridge_UNVERIFIED' % wid
    o, nq = drape_centreline(S, W_WIDTH, name, force_end=force)
    walk_info.append(dict(way=wid, faces=nq, nS=len(S), ok=bool(o)))
    print('TY walk', wid, 'faces', nq, 'samples', len(S))

json.dump({'landings': landing_meta, 'walks': walk_info}, open(D + 'data/ty/approaches.json', 'w'), indent=2)

# ---------- 3) W areaway apron (soften bank burying GF glass) ----------
# Along west face edges (those with outward ≈ -X), where grade > GR - 0.35, place apron at GR-0.08
bmA = bmesh.new(); nap = 0
for i in range(nFP):
    p, q, u, nr = edge_info(i)
    if nr.x > -0.7:  # not west-facing
        continue
    L = (q - p).length
    if L < 2.0: continue
    steps = max(2, int(L / 1.0))
    for k in range(steps):
        t0 = k / steps; t1 = (k + 1) / steps
        c0 = p.lerp(q, (t0 + t1) / 2)
        # sample grade 0.8 m out
        zg = gz(*(c0 + nr * 0.9).to_2d())
        if zg is None: continue
        if zg < GR - 0.35:
            continue  # already low enough (south dip near 404) — steps handle that
        # apron top at min(GR-0.05, zg-0.15) so we cut into the bank visually
        z_top = min(GR - 0.05, zg - 0.12)
        z_bot = z_top - 0.35
        seg_w = (q - p).length / steps + 0.02
        box_mesh(bmA, c0, u, nr, seg_w, 0.02, 1.55, z_bot, z_top + 0.04, 0)
        nap += 1
if nap:
    oA = finish(bmA, 'TY Partridge W areaway apron cutting lawn bank (UNVERIFIED)', [M_apron])
    oA['UNVERIFIED'] = 'areaway depth/extent guessed to reveal GF glass; not photo-measured'
    print('TY apron segments', nap)
else:
    bmA.free(); print('TY apron none')

# cull SB grass points that sit on the new apron / west bank strip (reversible via z backup)
sb = bpy.data.objects.get('SB_AnnexWest_lawn_grass_points_UNVERIFIED')
nculled = 0
if sb:
    mw = sb.matrix_world; imw = mw.inverted()
    bak = []
    # west strip bbox
    for i, v in enumerate(sb.data.vertices):
        p = mw @ v.co
        if -102.0 < p.x < -96.5 and 236.5 < p.y < 279.0 and 137.5 < p.z < 141.5:
            bak.append([i, float(v.co.z)])
            # park below terrain
            v.co.z = -500.0
            nculled += 1
    if bak:
        sb['ty_grass_z_backup'] = json.dumps(bak)
        sb.data.update()
    print('TY culled SB grass pts', nculled)

# ---------- 4) spandrel weathering streaks (E/W long faces) ----------
bmS = bmesh.new(); ns = 0
# FL from tx: GR+0, +3.85, +7.70, +11.55 — spandrels sit near those floors
spandrel_z = [GR + 0.45, GR + 3.85, GR + 7.70, GR + 11.55]
for i in range(nFP):
    p, q, u, nr = edge_info(i)
    # long E/W faces run N-S → |u.y| > |u.x|
    if abs(u.y) < abs(u.x):
        continue
    L = (q - p).length
    if L < 4.0: continue
    # streak every ~2.2 m under each spandrel lip
    n_st = max(3, int(L / 2.2))
    for zi, z in enumerate(spandrel_z):
        for k in range(n_st):
            t = (k + 0.5) / n_st
            c = p.lerp(q, t)
            # vary length/opacity via size
            h = 0.55 + 0.35 * ((k * 17 + zi * 9) % 5) / 4.0
            w = 0.08 + 0.04 * ((k * 3 + zi) % 3)
            # thin decal proud of frame (~0.12 out from mid wall) — frame is ~0.10 proud
            box_mesh(bmS, c, u, nr, w, 0.08, 0.14, z - h, z - 0.02, 0)
            ns += 1
oS = finish(bmS, 'TY Partridge E/W spandrel weathering streaks (UNVERIFIED)', [M_streak])
oS['UNVERIFIED'] = 'weathering pattern typical but guessed; no photo of current stains'
# make streak material more translucent via alpha on Principled
try:
    b = M_streak.node_tree.nodes['Principled BSDF']
    b.inputs['Alpha'].default_value = 0.42
    M_streak.blend_method = 'HASHED'
except Exception:
    pass
print('TY streaks', ns)

# ---------- cameras ----------
def add_cam(name, loc, tgt, lens=32):
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.clip_start = 0.3; cd.clip_end = 6000
    o = bpy.data.objects.new(name, cd); col.objects.link(o); o['ty_obj'] = 1
    o.location = Vector(loc)
    o.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
    return o

def eye(x, y, h=1.7):
    z = gz(x, y) or 139.0
    return (x, y, z + h)

# 1 oblique Partridge + approaches (adapt TX)
add_cam('TY_CAM_oblique_Nursing_approaches_from_SW', (-145, 190, 195), (-84, 255, 146), 40)
# 2 eye-level different sides
add_cam('TY_CAM_eye_Nursing_W_walks', eye(-118, 248), (-97, 250, 142.5), 28)
add_cam('TY_CAM_eye_Nursing_E_walks', eye(-52, 255), (-70, 256, 142.5), 28)
# 3 close-up landing/steps (W 404 has biggest rise) or weathered spandrel
# find 404 meta
m404 = next((m for m in landing_meta if m['way'] == '313026404'), landing_meta[0])
add_cam('TY_CAM_closeup_Nursing_W_steps', eye(m404['bottom_xy'][0] - 3.5, m404['bottom_xy'][1] - 1.2, 1.55),
        (m404['sill_xy'][0], m404['sill_xy'][1], GR + 0.8), 30)

print('TY done; objects', len(bpy.data.objects))
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED')
