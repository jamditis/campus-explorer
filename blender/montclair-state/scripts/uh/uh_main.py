"""Session uh (Nov 5 2026 ~5:24–6:12 PM ET, MAIN, day-9 leftovers): Partridge polish after ug.
A) Soften faint crease where UG_Partridge_E_seam_fill_lawn meets lifted SA_ground_lower_patch
   (feather UG N edge down to SA; lift SA S edge to meet; thin overlap strip).
B) Flatten curled QXP plaza paving / QY rim corner near y≈246 (top verts → ground+0.04).
C) Soften saw-tooth paving edge right of W stair + apron (xy-smooth + densify + light bevel).
D) Modest cx_grass points on the UG seam-fill strip (UNVERIFIED).
REVERT=1 restores UH_bak_* meshes and deletes uh_obj objects.
"""
import bpy, bmesh, os, json, math, random
from mathutils import Vector
REV = os.environ.get('REVERT') == '1'; SAVE = os.environ.get('SAVE') == '1'
D = '/workspace/nj-scenes/montclair-state/'
COLN = 'UH_Partridge_leftover_polish_UNVERIFIED'
XA, XB = -67.2, -36.0
Y_SEAM0, Y_SEAM1 = 246.5, 258.0

def revert():
    for me in [m for m in bpy.data.meshes if m.get('uh_bak_of')]:
        on = me['uh_bak_of']; o = bpy.data.objects.get(on)
        if o:
            mod = o.data; o.data = me
            if mod.users == 0: bpy.data.meshes.remove(mod)
        nm = me['uh_orig_name']; del me['uh_bak_of']; del me['uh_orig_name']
        me.use_fake_user = False; me.name = nm
    for o in [o for o in list(bpy.data.objects) if o.get('uh_obj')]:
        me = o.data; t = o.type
        bpy.data.objects.remove(o, do_unlink=True)
        if me is not None and me.users == 0:
            (bpy.data.meshes if t == 'MESH' else bpy.data.cameras).remove(me)
    c = bpy.data.collections.get(COLN)
    if c: bpy.data.collections.remove(c)
    print('UH REVERTED')

revert()
if REV:
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit

def backup(o):
    orig = o.data; nm = orig.name
    cp = orig.copy(); o.data = cp
    orig.name = 'UH_bak_' + nm[:50]; orig.use_fake_user = True
    orig['uh_bak_of'] = o.name; orig['uh_orig_name'] = nm
    cp.name = nm
    return cp

dg = bpy.context.evaluated_depsgraph_get()
def caster(n):
    o = bpy.data.objects.get(n)
    if not o: return lambda x, y: (None, None)
    e = o.evaluated_get(dg); mw = o.matrix_world; iw = mw.inverted()
    d = (iw.to_3x3() @ Vector((0, 0, -1))).normalized()
    def f(x, y):
        r = e.ray_cast(iw @ Vector((x, y, 400)), d)
        return ((mw @ r[1]).z, r[3]) if r[0] else (None, None)
    return f
UG = caster('UG_Partridge_E_seam_fill_lawn_UNVERIFIED')
SA = caster('SA_ground_lower_patch_UNVERIFIED')
DT = caster('Terrain_LiDAR_DTM_1m')
def trusted(x, y):
    z = DT(x, y)[0]
    return z if z is not None else SA(x, y)[0]

log = {}

# ---------- A) crease: feather UG N edge + lift SA S edge ----------
ugo = bpy.data.objects['UG_Partridge_E_seam_fill_lawn_UNVERIFIED']
ume = backup(ugo); umw = ugo.matrix_world; uimw = umw.inverted()
n_ug = 0
for v in ume.vertices:
    p = umw @ v.co
    if not (XA - 0.6 < p.x < XB + 0.6): continue
    if p.y < 249.5: continue
    saz, _ = SA(p.x, p.y)
    if saz is None:
        # sample a bit north into SA
        for dy in (0.3, 0.6, 1.0, 1.5):
            saz, _ = SA(p.x, p.y + dy)
            if saz is not None: break
    if saz is None: continue
    # blend: at y=249.5 keep UG; at y>=251 fully match SA+0.005
    t = min(1.0, max(0.0, (p.y - 249.5) / 1.5))
    target = p.z * (1 - t) + (saz + 0.005) * t
    if abs(target - p.z) > 0.002:
        p.z = target; v.co = uimw @ p; n_ug += 1
ume.update(); log['ug_feather'] = n_ug
print('UH A ug feather', n_ug)

sao = bpy.data.objects['SA_ground_lower_patch_UNVERIFIED']
sme = backup(sao); smw = sao.matrix_world; simw = smw.inverted()
n_sa = 0
# rebuild UG caster after edit
dg = bpy.context.evaluated_depsgraph_get()
UG2 = caster('UG_Partridge_E_seam_fill_lawn_UNVERIFIED')
for v in sme.vertices:
    p = smw @ v.co
    if not (XA - 0.5 < p.x < XB + 0.5): continue
    if not (250.5 < p.y < 253.5): continue
    ugz, _ = UG2(p.x, min(p.y, 251.0))
    if ugz is None:
        ugz, _ = UG2(p.x, 250.5)
    if ugz is None: continue
    # if SA is below UG by more than 1 cm, lift toward UG (keep SA slightly under for no z-fight)
    if p.z < ugz - 0.01:
        # feather: stronger at south edge
        t = min(1.0, max(0.0, (253.5 - p.y) / 3.0))
        target = p.z * (1 - t) + (ugz - 0.008) * t
        if target > p.z + 0.002:
            p.z = target; v.co = simw @ p; n_sa += 1
sme.update(); log['sa_lift'] = n_sa
print('UH A sa lift', n_sa)

# thin overlap blend strip: extend UG N edge verts that sit short of SA by nudging y slightly + z
# (mesh topology kept; just z match already done)

# ---------- B) curl: QXP / QY top verts near y≈246 ----------
def flatten_paving(name, y0=243.5, y1=252.0, x0=XA - 3, x1=XB + 5, off=0.04):
    o = bpy.data.objects.get(name)
    if not o: return 0
    me = backup(o); mw = o.matrix_world; imw = mw.inverted()
    # column tops
    cols = {}
    cand = []
    for v in me.vertices:
        p = mw @ v.co
        if x0 < p.x < x1 and y0 < p.y < y1:
            cand.append(v.index)
            k = (round(p.x / 0.03), round(p.y / 0.03))
            cols[k] = max(cols.get(k, -1e9), p.z)
    n = 0
    dg_local = bpy.context.evaluated_depsgraph_get()
    def gnd(x, y):
        for c in (UG2, SA, DT):
            z, _ = c(x, y)
            if z is not None: return z
        return None
    for vi in cand:
        v = me.vertices[vi]; p = mw @ v.co
        k = (round(p.x / 0.03), round(p.y / 0.03))
        top = cols[k]; is_top = abs(p.z - top) < 1e-4
        gz = gnd(p.x, p.y)
        if gz is None: continue
        # neighbour median of tops
        neigh = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0: continue
                kk = (k[0] + dx, k[1] + dy)
                if kk in cols: neigh.append(cols[kk])
        med = sorted(neigh)[len(neigh) // 2] if neigh else top
        if is_top:
            target = gz + off
            # also pull down if above neighbour median by >3 cm (curl)
            if top > med + 0.03:
                target = min(target, med + 0.01)
            # if clearly above ground+8cm, flatten
            if p.z > gz + 0.08 or p.z > med + 0.03 or abs(p.z - (gz + off)) > 0.025:
                # for curl near y=246 especially
                if p.y < 248.5 or p.z > gz + 0.06 or p.z > med + 0.025:
                    newz = 0.55 * p.z + 0.45 * max(gz + off, med - 0.005) if p.y < 248.5 else (gz + off)
                    # prefer ground+off when over-high
                    if p.z > gz + 0.06:
                        newz = gz + off
                    dz = newz - p.z
                    if abs(dz) > 0.002:
                        p.z = newz; v.co = imw @ p; n += 1
        else:
            # bottom: keep thickness ~0.28 if top moved — handled via column after
            pass
    # second pass: enforce thickness after top moves
    cols2 = {}
    for vi in cand:
        p = mw @ me.vertices[vi].co
        k = (round(p.x / 0.03), round(p.y / 0.03))
        cols2[k] = max(cols2.get(k, -1e9), p.z)
    for vi in cand:
        v = me.vertices[vi]; p = mw @ v.co
        k = (round(p.x / 0.03), round(p.y / 0.03))
        top = cols2[k]
        if abs(p.z - top) < 1e-4: continue
        # bottom should be top - ~0.28 (QXP thickness)
        want = top - 0.28
        if abs(p.z - want) > 0.05 and p.z < top - 0.05:
            p.z = want; v.co = imw @ p; n += 1
    me.update()
    print('UH B', name, 'moved', n)
    return n

log['qxp'] = flatten_paving('QXP_pedestrian_area_313024781_paving_UNVERIFIED')
log['qy'] = flatten_paving('QY_plaza_rim_band_313024781_UNVERIFIED', off=0.035)

# Extra targeted curl: QXP verts near the visible corner (~x -62..-50, y 245..249) that show underside
o = bpy.data.objects['QXP_pedestrian_area_313024781_paving_UNVERIFIED']
me = o.data; mw = o.matrix_world; imw = mw.inverted()
# already backed up; further nudge high edge verts
n_curl = 0
cols = {}
for v in me.vertices:
    p = mw @ v.co
    if -65 < p.x < -48 and 244.5 < p.y < 249.5:
        k = (round(p.x / 0.03), round(p.y / 0.03))
        cols[k] = max(cols.get(k, -1e9), p.z)
for v in me.vertices:
    p = mw @ v.co
    if not (-65 < p.x < -48 and 244.5 < p.y < 249.5): continue
    k = (round(p.x / 0.03), round(p.y / 0.03))
    if abs(p.z - cols[k]) > 1e-4: continue
    gz = None
    for c in (UG2, SA, DT):
        gz, _ = c(p.x, p.y)
        if gz is not None: break
    if gz is None: continue
    if p.z > gz + 0.055:
        p.z = gz + 0.04; v.co = imw @ p; n_curl += 1
me.update(); log['qxp_curl_extra'] = n_curl
print('UH B curl extra', n_curl)

# ---------- C) sawtooth W stair / apron / 404 ----------
def soften_outline(o, tag, rounds=4, lerp=0.45, bevel_off=0.06, subdivide_len=0.55):
    """XY-smooth top verts + subdivide long top edges + light bevel (UD-style, stronger)."""
    if o is None: return 0
    # only backup once
    if not any(m.get('uh_bak_of') == o.name for m in bpy.data.meshes):
        backup(o)
    bm = bmesh.new(); bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table(); bm.verts.ensure_lookup_table()
    mw = o.matrix_world
    # work in local; for apron/walks local ≈ world-ish but use world z via mw
    # Identify top band by world z
    wz = [(v, (mw @ v.co).z) for v in bm.verts]
    zmax = max(z for _, z in wz)
    top_set = {v for v, z in wz if z > zmax - 0.10}
    # Focus near W door box for apron/walks that span long N-S
    focus = set()
    for v in top_set:
        p = mw @ v.co
        if -110 < p.x < -96 and 240 < p.y < 270:
            focus.add(v)
    if not focus:
        focus = top_set
    for _ in range(rounds):
        coords = {}
        for v in focus:
            nbrs = [e.other_vert(v) for e in v.link_edges if e.other_vert(v) in top_set]
            if len(nbrs) < 2: continue
            # average neighbour LOCAL xy; keep z
            avg = sum((n.co for n in nbrs), Vector()) / len(nbrs)
            nc = v.co.lerp(avg, lerp)
            coords[v] = Vector((nc.x, nc.y, v.co.z))
        for v, c in coords.items():
            v.co = c
    # subdivide long top edges in focus region
    top_edges = []
    for e in bm.edges:
        if e.verts[0] not in top_set or e.verts[1] not in top_set: continue
        mid = mw @ ((e.verts[0].co + e.verts[1].co) * 0.5)
        if -110 < mid.x < -96 and 240 < mid.y < 270:
            top_edges.append(e)
    long = [e for e in top_edges if e.calc_length() > subdivide_len]
    if long:
        bmesh.ops.subdivide_edges(bm, edges=long, cuts=1)
        bm.edges.ensure_lookup_table(); bm.verts.ensure_lookup_table()
    # light bevel
    top_edges = [e for e in bm.edges
                 if all((mw @ v.co).z > zmax - 0.10 for v in e.verts)]
    # restrict to focus
    top_edges = [e for e in top_edges
                 if -110 < (mw @ ((e.verts[0].co + e.verts[1].co) * 0.5)).x < -96]
    n_before = len(bm.verts)
    if top_edges and bevel_off > 0:
        try:
            bmesh.ops.bevel(bm, geom=top_edges[:], offset=bevel_off, segments=1,
                            affect='EDGES', profile=0.5)
        except Exception as e:
            print('UH bevel fail', tag, e)
    bm.to_mesh(o.data); bm.free(); o.data.update()
    o['uh_fix'] = 1
    o['UNVERIFIED_uh'] = f'{tag} xy-smooth+bevel UNVERIFIED; bak UH_bak_*'
    print('UH C', tag, 'verts', n_before, '->', len(o.data.vertices))
    return len(o.data.vertices)

apron = bpy.data.objects.get('TY Partridge W areaway apron cutting lawn bank (UNVERIFIED)')
walk404 = bpy.data.objects.get('TY_footway_313026404_to_Partridge_UNVERIFIED')
# also soften nearby TY walks that meet the W stair south/north
walk399 = bpy.data.objects.get('TY_footway_313026399_to_Partridge_UNVERIFIED')
log['apron_verts'] = soften_outline(apron, 'apron', rounds=5, lerp=0.5, bevel_off=0.07)
log['w404_verts'] = soften_outline(walk404, 'walk404', rounds=4, lerp=0.4, bevel_off=0.04, subdivide_len=0.45)
if walk399:
    log['w399_verts'] = soften_outline(walk399, 'walk399', rounds=3, lerp=0.4, bevel_off=0.04)

# Footpaths_OSM near W stair — smooth verts that make the sawtooth paving edge
fp = bpy.data.objects.get('Footpaths_OSM')
if fp:
    if not any(m.get('uh_bak_of') == fp.name for m in bpy.data.meshes):
        backup(fp)
    me = fp.data; mw = fp.matrix_world; imw = mw.inverted()
    # collect verts in the W sawtooth zone (right of stair = south/east of door ~ y 246-250, x -105..-97)
    idxs = [v.index for v in me.vertices if -106 < (mw @ v.co).x < -96.5 and 245.5 < (mw @ v.co).y < 251.5]
    # laplacian xy smooth a few rounds
    nfp = 0
    for _ in range(5):
        # build adjacency from edges
        adj = {}
        for e in me.edges:
            a, b = e.vertices
            if a in idxs or b in idxs:
                adj.setdefault(a, []).append(b)
                adj.setdefault(b, []).append(a)
        newxy = {}
        for vi in idxs:
            nbr = adj.get(vi, [])
            if len(nbr) < 2: continue
            ax = sum((mw @ me.vertices[j].co).x for j in nbr) / len(nbr)
            ay = sum((mw @ me.vertices[j].co).y for j in nbr) / len(nbr)
            p = mw @ me.vertices[vi].co
            newxy[vi] = (0.55 * p.x + 0.45 * ax, 0.55 * p.y + 0.45 * ay, p.z)
        for vi, (x, y, z) in newxy.items():
            me.vertices[vi].co = imw @ Vector((x, y, z)); nfp += 1
    me.update(); log['fp_smooth'] = nfp
    print('UH C Footpaths smooth ops', nfp)

# ---------- D) grass on UG seam-fill strip ----------
rnd = random.Random(20261105)
ugo = bpy.data.objects['UG_Partridge_E_seam_fill_lawn_UNVERIFIED']
# sample face centers + jitter on UG mesh
umw = ugo.matrix_world
pts = []
# blockers: paving / walks / building
blk_names = [
    'QXP_pedestrian_area_313024781_paving_UNVERIFIED',
    'QY_plaza_rim_band_313024781_UNVERIFIED',
    'Footpaths_OSM',
    'TY_footway_313026406_to_Partridge_UNVERIFIED',
    'TY_footway_313026407_to_Partridge_UNVERIFIED',
    'TY_footway_313026405_to_Partridge_UNVERIFIED',
    'TY Partridge entrance steps+landings (UNVERIFIED)',
]
# Partridge footprint
FP = [tuple(p) for p in json.load(open(D + 'data/tx/nursing_geom.json'))['footprint']]
def inside(x, y):
    c = False; n = len(FP)
    for i in range(n):
        x1, y1 = FP[i]; x2, y2 = FP[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-12) + x1: c = not c
    return c

dg = bpy.context.evaluated_depsgraph_get()
blk = []
for n in blk_names:
    o = bpy.data.objects.get(n)
    if not o: continue
    blk.append((o.evaluated_get(dg), o.matrix_world))

def hit_blk(x, y, z):
    for e, mw in blk:
        iw = mw.inverted()
        o0 = iw @ Vector((x, y, z + 40)); o1 = iw @ Vector((x, y, z - 0.05)); d = o1 - o0
        if d.length < 1e-6: continue
        if e.ray_cast(o0, d.normalized(), distance=d.length)[0]:
            return True
    return False

# modest density ~8 / m² on the strip (strip ~31 x 4.5 ≈ 140 m² → ~1100 pts); keep modest ~4/m²
DENS = 4.0
area_est = (XB - XA) * 4.5
n_try = int(DENS * area_est * 2.2)
uge = ugo.evaluated_get(dg)
for _ in range(n_try):
    x = XA + rnd.random() * (XB - XA)
    y = 247.0 + rnd.random() * 4.2  # cover the seam strip
    if inside(x, y): continue
    # edge fade
    edge = min(x - XA, XB - x, y - 247.0, 251.2 - y)
    if edge < 0: continue
    if edge < 0.6 and rnd.random() > edge / 0.6: continue
    r = uge.ray_cast(ugo.matrix_world.inverted() @ Vector((x, y, 400)),
                     (ugo.matrix_world.inverted().to_3x3() @ Vector((0, 0, -1))).normalized())
    if not r[0]: continue
    z = (umw @ r[1]).z
    if hit_blk(x, y, z): continue
    pts.append((x, y, z - 0.005))

src = bpy.data.objects.get('QV_Richardson_NW_lawn_grass_points_UNVERIFIED') or bpy.data.objects['cx_grass_points']
col = bpy.data.collections.new(COLN); bpy.context.scene.collection.children.link(col)
me_g = bpy.data.meshes.new('UH_Partridge_E_seam_grass_points_UNVERIFIED')
me_g.from_pydata(pts, [], [])
ob_g = src.copy(); ob_g.data = me_g
ob_g.name = 'UH_Partridge_E_seam_grass_points_UNVERIFIED'
ob_g.matrix_world = __import__('mathutils').Matrix.Identity(4)
for c in list(ob_g.users_collection): c.objects.unlink(ob_g)
col.objects.link(ob_g)
ob_g['uh_obj'] = 1
ob_g['UNVERIFIED'] = 'modest cx_grass on UG Partridge E seam-fill strip; density~4/m2 UNVERIFIED (uh)'
# ensure GN modifier
if 'cx_grass' not in ob_g.modifiers:
    m = ob_g.modifiers.new('cx_grass', 'NODES')
    m.node_group = bpy.data.objects['cx_grass_points'].modifiers['cx_grass'].node_group
else:
    ob_g.modifiers['cx_grass'].node_group = bpy.data.objects['cx_grass_points'].modifiers['cx_grass'].node_group
log['grass'] = len(pts)
print('UH D grass', len(pts))

# ---------- cams ----------
def cam(name, loc, tgt, lens):
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.clip_end = 6000
    o = bpy.data.objects.new(name, cd); col.objects.link(o); o['uh_obj'] = 1
    o.location = loc
    o.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()

cam('UH_CAM_oblique_Partridge_E_seam_from_SE', (-20, 195, 178), (-62, 252, 140), 35)
cam('UH_CAM_eye_Partridge_E_face_from_E', (-48, 252.5, 141.6), (-68, 253.5, 141.0), 28)
cam('UH_CAM_eye_Partridge_W_steps_from_W', (-116, 246.5, 141.0), (-99, 250.5, 139.6), 30)
cam('UH_CAM_closeup_Partridge_E_seam_crease', (-55, 245, 142.2), (-62, 250.5, 139.9), 32)

json.dump(log, open(D + 'data/uh/uh_main.json', 'w'), indent=1)
print('UH LOG', log)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
