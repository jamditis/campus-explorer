"""Session uj (Nov 5 2026 ~7:19–~8:12 PM ET, MAIN, day-9 leftovers): Partridge polish after ui.
Joe lawn strip (ui) stays — do not reverse.
A) Soften remaining UG↔SA crease (gentle z + light xy feather).
B) Soften residual QXP / Footpaths_OSM / QY south-edge jaggedness (boundary xy-smooth; keep plaza N).
C) Soften W apron boxiness + 404 sawtooth (gentle outline/bevel — don't erase stair).
D) Optional modest grass densify on bald strip patches.
Cams: UJ_CAM_*.
REVERT=1 restores UJ_bak_* meshes and deletes uj_obj objects.
"""
import bpy, bmesh, os, json, math, random
from mathutils import Vector, Matrix
REV = os.environ.get('REVERT') == '1'; SAVE = os.environ.get('SAVE') == '1'
D = '/workspace/nj-scenes/montclair-state/'
COLN = 'UJ_Partridge_leftover_polish_UNVERIFIED'
XA, XB = -67.5, -35.5
Y_WALK, Y_PLAZA = 247.0, 251.2

def revert():
    for me in [m for m in bpy.data.meshes if m.get('uj_bak_of')]:
        on = me['uj_bak_of']; o = bpy.data.objects.get(on)
        if o:
            mod = o.data; o.data = me
            if mod.users == 0: bpy.data.meshes.remove(mod)
        nm = me['uj_orig_name']; del me['uj_bak_of']; del me['uj_orig_name']
        me.use_fake_user = False; me.name = nm
    for o in [o for o in list(bpy.data.objects) if o.get('uj_obj')]:
        me = o.data; t = o.type
        bpy.data.objects.remove(o, do_unlink=True)
        if me is not None and me.users == 0:
            (bpy.data.meshes if t == 'MESH' else bpy.data.cameras).remove(me)
    c = bpy.data.collections.get(COLN)
    if c: bpy.data.collections.remove(c)
    print('UJ REVERTED')

revert()
if REV:
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit

def backup(o):
    if any(m.get('uj_bak_of') == o.name for m in bpy.data.meshes):
        return o.data
    orig = o.data; nm = orig.name
    cp = orig.copy(); o.data = cp
    orig.name = 'UJ_bak_' + nm[:50]; orig.use_fake_user = True
    orig['uj_bak_of'] = o.name; orig['uj_orig_name'] = nm
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

log = {'session': 'uj', 'joe_lawn_strip': 'kept (do not reverse)'}

# ---------- A) crease: UG N feather + SA S lift + light xy ----------
ugo = bpy.data.objects['UG_Partridge_E_seam_fill_lawn_UNVERIFIED']
ume = backup(ugo); umw = ugo.matrix_world; uimw = umw.inverted()
n_ug = 0
for v in ume.vertices:
    p = umw @ v.co
    if not (XA - 1.0 < p.x < XB + 1.0): continue
    if p.y < 248.8: continue
    saz = None
    for dy in (0.0, 0.35, 0.7, 1.2, 1.8, 2.4):
        saz, _ = SA(p.x, p.y + dy)
        if saz is not None: break
    if saz is None: continue
    # wider softer feather than ui: y 248.8 → 251.8
    t = min(1.0, max(0.0, (p.y - 248.8) / 3.0))
    target = p.z * (1 - t) + (saz + 0.003) * t
    if abs(target - p.z) > 0.0012:
        p.z = target; v.co = uimw @ p; n_ug += 1
ume.update(); log['ug_crease'] = n_ug
print('UJ A ug crease', n_ug)

# light xy laplace on UG N band (z locked)
n_ug_xy = 0
idxs_ug = [v.index for v in ume.vertices
           if XA - 0.8 < (umw @ v.co).x < XB + 0.8 and 249.0 < (umw @ v.co).y < 251.6]
for _ in range(3):
    adj = {}
    for e in ume.edges:
        a, b = e.vertices
        if a in idxs_ug or b in idxs_ug:
            adj.setdefault(a, []).append(b); adj.setdefault(b, []).append(a)
    newxy = {}
    for vi in idxs_ug:
        nbr = [j for j in adj.get(vi, []) if j in idxs_ug]
        if len(nbr) < 2: continue
        ax = sum((umw @ ume.vertices[j].co).x for j in nbr) / len(nbr)
        ay = sum((umw @ ume.vertices[j].co).y for j in nbr) / len(nbr)
        p = umw @ ume.vertices[vi].co
        newxy[vi] = (0.72 * p.x + 0.28 * ax, 0.72 * p.y + 0.28 * ay, p.z)
    for vi, (x, y, z) in newxy.items():
        ume.vertices[vi].co = uimw @ Vector((x, y, z)); n_ug_xy += 1
ume.update(); log['ug_xy'] = n_ug_xy
print('UJ A ug xy', n_ug_xy)

sao = bpy.data.objects['SA_ground_lower_patch_UNVERIFIED']
sme = backup(sao); smw = sao.matrix_world; simw = smw.inverted()
dg = bpy.context.evaluated_depsgraph_get(); UG2 = caster('UG_Partridge_E_seam_fill_lawn_UNVERIFIED')
n_sa = 0
for v in sme.vertices:
    p = smw @ v.co
    if not (XA - 0.8 < p.x < XB + 0.8): continue
    if not (249.8 < p.y < 254.5): continue
    ugz, _ = UG2(p.x, min(p.y, 250.6))
    if ugz is None:
        ugz, _ = UG2(p.x, 250.2)
    if ugz is None: continue
    # lift SA that sits below UG near join; also gently lower SA that sits proud
    if p.z < ugz - 0.006:
        t = min(1.0, max(0.0, (254.5 - p.y) / 4.0))
        target = p.z * (1 - t) + (ugz - 0.004) * t
        if target > p.z + 0.0012:
            p.z = target; v.co = simw @ p; n_sa += 1
    elif p.z > ugz + 0.025 and p.y < 251.8:
        t = min(1.0, max(0.0, (251.8 - p.y) / 1.8))
        target = p.z * (1 - 0.45 * t) + (ugz + 0.008) * (0.45 * t)
        if abs(target - p.z) > 0.0015:
            p.z = target; v.co = simw @ p; n_sa += 1
sme.update(); log['sa_crease'] = n_sa
print('UJ A sa crease', n_sa)

# ---------- B) QXP / QY / Footpaths S-edge jaggedness ----------
def xy_smooth_boundary(name, y_lo, y_hi, x0, x1, rounds=7, lerp=0.55, near_r=0.55):
    o = bpy.data.objects.get(name)
    if not o: return 0
    me = backup(o); mw = o.matrix_world; imw = mw.inverted()
    eu = {}
    for p in me.polygons:
        for ek in p.edge_keys:
            eu[ek] = eu.get(ek, 0) + 1
    bvi = set()
    for ek, c in eu.items():
        if c == 1: bvi.update(ek)
    idxs = []
    for vi in bvi:
        p = mw @ me.vertices[vi].co
        if x0 < p.x < x1 and y_lo < p.y < y_hi:
            idxs.append(vi)
    near = set(idxs)
    for v in me.vertices:
        p = mw @ v.co
        if not (x0 < p.x < x1 and y_lo < p.y < y_hi): continue
        for vi in idxs:
            q = mw @ me.vertices[vi].co
            if (p.x - q.x) ** 2 + (p.y - q.y) ** 2 < near_r ** 2:
                near.add(v.index); break
    # prefer top band
    if near:
        zs = [(mw @ me.vertices[i].co).z for i in near]
        zmax = max(zs)
        near = {i for i in near if (mw @ me.vertices[i].co).z > zmax - 0.18}
    adj = {}
    for e in me.edges:
        a, b = e.vertices
        adj.setdefault(a, []).append(b); adj.setdefault(b, []).append(a)
    n = 0
    for _ in range(rounds):
        newxy = {}
        for vi in near:
            nbrs = [j for j in adj.get(vi, []) if j in near]
            if len(nbrs) < 2: continue
            ax = sum((mw @ me.vertices[j].co).x for j in nbrs) / len(nbrs)
            ay = sum((mw @ me.vertices[j].co).y for j in nbrs) / len(nbrs)
            p = mw @ me.vertices[vi].co
            w = lerp if vi in idxs else lerp * 0.55
            newxy[vi] = (p.x * (1 - w) + ax * w, p.y * (1 - w) + ay * w, p.z)
        for vi, (x, y, z) in newxy.items():
            me.vertices[vi].co = imw @ Vector((x, y, z)); n += 1
    me.update()
    o['uj_touched'] = 1
    o['UNVERIFIED_uj'] = f'{name} S-edge xy-smooth UNVERIFIED (uj); Joe lawn strip kept'
    print('UJ B', name, 'boundary', len(idxs), 'near', len(near), 'ops', n)
    return n

log['qxp_s'] = xy_smooth_boundary(
    'QXP_pedestrian_area_313024781_paving_UNVERIFIED',
    y_lo=249.0, y_hi=253.2, x0=-69.0, x1=-30.0, rounds=8, lerp=0.58)
log['qy_s'] = xy_smooth_boundary(
    'QY_plaza_rim_band_313024781_UNVERIFIED',
    y_lo=249.0, y_hi=253.2, x0=-69.0, x1=-30.0, rounds=6, lerp=0.5)
log['fp_s'] = xy_smooth_boundary(
    'Footpaths_OSM',
    y_lo=245.5, y_hi=250.5, x0=-69.0, x1=-34.0, rounds=6, lerp=0.5, near_r=0.7)

# thin any residual QXP/QY south curtain over the lawn strip (tops stay)
def thin_curtain(name, y_lo=247.5, y_hi=250.6, x0=-68.0, x1=-36.0, keep=0.035):
    o = bpy.data.objects.get(name)
    if not o: return 0
    me = o.data  # already backed up
    mw = o.matrix_world; imw = mw.inverted()
    cols = {}; band = []
    for v in me.vertices:
        p = mw @ v.co
        if x0 < p.x < x1 and y_lo < p.y < y_hi:
            band.append(v.index)
            k = (round(p.x / 0.03), round(p.y / 0.03))
            cols[k] = max(cols.get(k, -1e9), p.z)
    n = 0
    for vi in band:
        v = me.vertices[vi]; p = mw @ v.co
        k = (round(p.x / 0.03), round(p.y / 0.03))
        top = cols[k]
        if abs(p.z - top) < 1e-4: continue
        # pull non-top verts up toward top-keep (thin vertical face)
        want = top - keep
        if p.z < want - 0.02:
            p.z = want; v.co = imw @ p; n += 1
        elif p.z < top - 0.08:
            # also pull mid curtain
            p.z = 0.55 * p.z + 0.45 * want; v.co = imw @ p; n += 1
    me.update(); print('UJ B thin', name, n); return n

log['qxp_thin'] = thin_curtain('QXP_pedestrian_area_313024781_paving_UNVERIFIED')
log['qy_thin'] = thin_curtain('QY_plaza_rim_band_313024781_UNVERIFIED')

# ---------- C) W apron / 404 boxiness ----------
def soften_outline(o, tag, rounds=4, lerp=0.38, bevel_off=0.045, subdivide_len=0.50,
                   focus_box=(-110, -96, 243, 258)):
    if o is None: return 0
    backup(o)
    bm = bmesh.new(); bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table(); bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table()
    mw = o.matrix_world
    wz = [(v, (mw @ v.co).z) for v in bm.verts]
    zmax = max(z for _, z in wz)
    top_set = {v for v, z in wz if z > zmax - 0.12}
    x0, x1, y0, y1 = focus_box
    focus = {v for v in top_set if x0 < (mw @ v.co).x < x1 and y0 < (mw @ v.co).y < y1} or top_set
    # subdivide long top edges in focus
    top_edges = [e for e in bm.edges if e.verts[0] in focus and e.verts[1] in focus]
    long = [e for e in top_edges if e.calc_length() > subdivide_len]
    if long:
        bmesh.ops.subdivide_edges(bm, edges=long, cuts=1)
        bm.faces.ensure_lookup_table(); bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table()
        wz = [(v, (mw @ v.co).z) for v in bm.verts]
        zmax = max(z for _, z in wz)
        top_set = {v for v, z in wz if z > zmax - 0.12}
        focus = {v for v in top_set if x0 < (mw @ v.co).x < x1 and y0 < (mw @ v.co).y < y1} or top_set
        top_edges = [e for e in bm.edges if e.verts[0] in focus and e.verts[1] in focus]
    for _ in range(rounds):
        coords = {}
        for v in focus:
            nbrs = [e.other_vert(v) for e in v.link_edges if e.other_vert(v) in top_set]
            if len(nbrs) < 2: continue
            avg = sum((n.co for n in nbrs), Vector()) / len(nbrs)
            nc = v.co.lerp(avg, lerp)
            coords[v] = Vector((nc.x, nc.y, v.co.z))
        for v, c in coords.items():
            v.co = c
    if top_edges and bevel_off > 0:
        try:
            bmesh.ops.bevel(bm, geom=top_edges[:], offset=bevel_off, segments=1,
                            affect='EDGES', profile=0.5)
        except Exception as e:
            print('UJ bevel fail', tag, e)
    bm.to_mesh(o.data); bm.free(); o.data.update()
    o['uj_touched'] = 1
    o['UNVERIFIED_uj_w'] = f'{tag} xy-smooth+bevel UNVERIFIED (uj); stair not erased'
    print('UJ C', tag, 'verts', len(o.data.vertices))
    return len(o.data.vertices)

apron = bpy.data.objects.get('TY Partridge W areaway apron cutting lawn bank (UNVERIFIED)')
walk404 = bpy.data.objects.get('TY_footway_313026404_to_Partridge_UNVERIFIED')
walk399 = bpy.data.objects.get('TY_footway_313026399_to_Partridge_UNVERIFIED')
# DO NOT touch 'TY Partridge entrance steps+landings (UNVERIFIED)' — preserve stair
log['apron_v'] = soften_outline(apron, 'apron', rounds=4, lerp=0.40, bevel_off=0.05)
log['w404_v'] = soften_outline(walk404, 'walk404', rounds=4, lerp=0.35, bevel_off=0.035, subdivide_len=0.42)
if walk399:
    log['w399_v'] = soften_outline(walk399, 'walk399', rounds=3, lerp=0.32, bevel_off=0.03)

# Footpaths near W apron / stair foot
fp = bpy.data.objects.get('Footpaths_OSM')
if fp:
    # already may have uj bak from B; ensure
    me = backup(fp); mw = fp.matrix_world; imw = mw.inverted()
    idxs = [v.index for v in me.vertices
            if -108 < (mw @ v.co).x < -96.0 and 244.5 < (mw @ v.co).y < 252.5]
    nfp = 0
    for _ in range(4):
        adj = {}
        for e in me.edges:
            a, b = e.vertices
            if a in idxs or b in idxs:
                adj.setdefault(a, []).append(b); adj.setdefault(b, []).append(a)
        newxy = {}
        for vi in idxs:
            nbr = adj.get(vi, [])
            if len(nbr) < 2: continue
            ax = sum((mw @ me.vertices[j].co).x for j in nbr) / len(nbr)
            ay = sum((mw @ me.vertices[j].co).y for j in nbr) / len(nbr)
            p = mw @ me.vertices[vi].co
            newxy[vi] = (0.62 * p.x + 0.38 * ax, 0.62 * p.y + 0.38 * ay, p.z)
        for vi, (x, y, z) in newxy.items():
            me.vertices[vi].co = imw @ Vector((x, y, z)); nfp += 1
    me.update(); log['fp_w'] = nfp
    print('UJ C Footpaths W', nfp)

# ---------- D) optional grass densify on bald strip patches ----------
rnd = random.Random(20261105 + 19)
src = bpy.data.objects.get('UI_Partridge_E_strip_grass_points_UNVERIFIED') or \
      bpy.data.objects.get('UH_Partridge_E_seam_grass_points_UNVERIFIED')
added = 0
if src:
    existing = [tuple(v.co) for v in src.data.vertices]
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
    blk_names = [
        'QXP_pedestrian_area_313024781_paving_UNVERIFIED',
        'QY_plaza_rim_band_313024781_UNVERIFIED',
        'Footpaths_OSM',
        'TY_footway_313026406_to_Partridge_UNVERIFIED',
        'TY_footway_313026407_to_Partridge_UNVERIFIED',
        'TY_footway_313026405_to_Partridge_UNVERIFIED',
        'TY Partridge entrance steps+landings (UNVERIFIED)',
    ]
    blk = []
    for n in blk_names:
        o = bpy.data.objects.get(n)
        if o: blk.append((o.evaluated_get(dg), o.matrix_world))
    def hit_blk(x, y, z):
        for e, mw in blk:
            iw = mw.inverted()
            o0 = iw @ Vector((x, y, z + 40)); o1 = iw @ Vector((x, y, z - 0.05)); d = o1 - o0
            if d.length < 1e-6: continue
            if e.ray_cast(o0, d.normalized(), distance=d.length)[0]:
                return True
        return False
    pts = list(existing)
    # bias toward mid-strip where WIPs showed bald/tan underlayer (x≈-58..-48, y≈248..250)
    for _ in range(1800):
        if rnd.random() < 0.55:
            x = -60.5 + rnd.random() * 14.0
            y = 247.4 + rnd.random() * 3.2
        else:
            x = XA + rnd.random() * (XB - XA)
            y = Y_WALK + 0.2 + rnd.random() * (Y_PLAZA - Y_WALK - 0.3)
        if inside(x, y): continue
        if any((x - p[0]) ** 2 + (y - p[1]) ** 2 < 0.28 ** 2 for p in pts[::max(1, len(pts)//80)] + pts[-120:]):
            continue
        r = uge.ray_cast(ugo.matrix_world.inverted() @ Vector((x, y, 400)),
                         (ugo.matrix_world.inverted().to_3x3() @ Vector((0, 0, -1))).normalized())
        if not r[0]: continue
        z = (umw @ r[1]).z
        if hit_blk(x, y, z): continue
        pts.append((x, y, z - 0.004)); added += 1
        if added >= 420: break
    if added:
        # new uj grass object (keep UI grass; additive densify)
        col = bpy.data.collections.get(COLN) or bpy.data.collections.new(COLN)
        if COLN not in [c.name for c in bpy.context.scene.collection.children]:
            bpy.context.scene.collection.children.link(col)
        me_g = bpy.data.meshes.new('UJ_Partridge_E_strip_grass_fill_UNVERIFIED')
        me_g.from_pydata(pts[len(existing):], [], [])
        ob_g = src.copy(); ob_g.data = me_g
        ob_g.name = 'UJ_Partridge_E_strip_grass_fill_UNVERIFIED'
        ob_g.matrix_world = Matrix.Identity(4)
        for c in list(ob_g.users_collection): c.objects.unlink(ob_g)
        col.objects.link(ob_g)
        ob_g['uj_obj'] = 1
        ob_g['UNVERIFIED'] = 'cx_grass fill on bald Partridge E strip patches; density UNVERIFIED (uj)'
        if 'cx_grass' not in ob_g.modifiers:
            m = ob_g.modifiers.new('cx_grass', 'NODES')
            m.node_group = bpy.data.objects['cx_grass_points'].modifiers['cx_grass'].node_group
        else:
            ob_g.modifiers['cx_grass'].node_group = bpy.data.objects['cx_grass_points'].modifiers['cx_grass'].node_group
log['grass_added'] = added
print('UJ D grass added', added)

# ---------- cams ----------
col = bpy.data.collections.get(COLN)
if col is None:
    col = bpy.data.collections.new(COLN)
    bpy.context.scene.collection.children.link(col)

def cam(name, loc, tgt, lens):
    if name in bpy.data.objects:
        o = bpy.data.objects[name]
        o.location = loc
        o.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
        o['uj_obj'] = 1
        return
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.clip_end = 6000
    o = bpy.data.objects.new(name, cd); col.objects.link(o); o['uj_obj'] = 1
    o.location = loc
    o.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()

# oblique SE lawn strip; eye E face; eye W steps; closeup of worst leftover (S plaza/lawn join crease)
cam('UJ_CAM_oblique_Partridge_E_lawn_from_SE', (-16, 196, 177), (-55, 250, 140), 35)
cam('UJ_CAM_eye_Partridge_E_face_from_E', (-45, 251.8, 141.6), (-68, 253.0, 141.0), 28)
cam('UJ_CAM_eye_Partridge_W_steps_from_W', (-117, 246.2, 141.1), (-99, 250.5, 139.6), 30)
cam('UJ_CAM_closeup_Partridge_E_plaza_lawn_join', (-50, 246.0, 141.6), (-56, 250.2, 139.9), 30)

json.dump(log, open(D + 'data/uj/uj_main.json', 'w'), indent=1)
print('UJ LOG', log)
print('UJ objects', len(bpy.data.objects))
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
