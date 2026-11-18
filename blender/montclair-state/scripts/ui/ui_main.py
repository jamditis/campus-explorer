"""Session ui (Nov 5 2026 ~6:23–~7:12 PM ET, MAIN, day-9 leftovers): Joe lawn strip E of Partridge.
Joe (Nov 5 ~5:43 PM): strip between south walk and plaza east of Partridge = lawn/grass (not paving).
Ortho/NAIP: west/near-building strip often grass; mid/east mixed; default to Joe + SC-quad-like lawn.
A) Sink QXP/QY paving that covers the strip under UG lawn (keep plaza north of strip).
B) Modest extra cx_grass on the newly exposed strip (UNVERIFIED density ~4/m²).
C) Further soften faint UG↔SA crease.
D) Soften residual QXP/QY S-edge jaggedness over the strip.
E) Soften W apron / 404 sawtooth / apron boxiness (gentle).
REVERT=1 restores UI_bak_* meshes and deletes ui_obj objects.
"""
import bpy, bmesh, os, json, math, random
from mathutils import Vector
REV = os.environ.get('REVERT') == '1'; SAVE = os.environ.get('SAVE') == '1'
D = '/workspace/nj-scenes/montclair-state/'
COLN = 'UI_Partridge_lawn_strip_UNVERIFIED'
# strip between south walk (~y 247) and plaza proper — cut paving south of Y_PLAZA
XA, XB = -67.5, -35.5
Y_WALK, Y_PLAZA = 247.0, 251.2

def revert():
    for me in [m for m in bpy.data.meshes if m.get('ui_bak_of')]:
        on = me['ui_bak_of']; o = bpy.data.objects.get(on)
        if o:
            mod = o.data; o.data = me
            if mod.users == 0: bpy.data.meshes.remove(mod)
        nm = me['ui_orig_name']; del me['ui_bak_of']; del me['ui_orig_name']
        me.use_fake_user = False; me.name = nm
    for o in [o for o in list(bpy.data.objects) if o.get('ui_obj')]:
        me = o.data; t = o.type
        bpy.data.objects.remove(o, do_unlink=True)
        if me is not None and me.users == 0:
            (bpy.data.meshes if t == 'MESH' else bpy.data.cameras).remove(me)
    c = bpy.data.collections.get(COLN)
    if c: bpy.data.collections.remove(c)
    print('UI REVERTED')

revert()
if REV:
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit

def backup(o):
    if any(m.get('ui_bak_of') == o.name for m in bpy.data.meshes):
        return o.data
    orig = o.data; nm = orig.name
    cp = orig.copy(); o.data = cp
    orig.name = 'UI_bak_' + nm[:50]; orig.use_fake_user = True
    orig['ui_bak_of'] = o.name; orig['ui_orig_name'] = nm
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
def gnd(x, y):
    for c in (UG, SA, DT):
        z, _ = c(x, y)
        if z is not None: return z
    return None

log = {'joe_direction': 'Partridge E strip south-walk↔plaza = lawn (Nov 5 ~5:43 PM)'}

# ---------- A) sink QXP / QY paving under lawn on the strip ----------
def sink_paving(name, under=0.10):
    o = bpy.data.objects.get(name)
    if not o: return 0
    me = backup(o); mw = o.matrix_world; imw = mw.inverted()
    # column tops in strip
    idxs = []
    for v in me.vertices:
        p = mw @ v.co
        if XA - 0.3 < p.x < XB + 0.3 and Y_WALK - 0.2 < p.y < Y_PLAZA + 0.15:
            idxs.append(v.index)
    if not idxs: return 0
    cols = {}
    for vi in idxs:
        p = mw @ me.vertices[vi].co
        k = (round(p.x / 0.04), round(p.y / 0.04))
        cols[k] = max(cols.get(k, -1e9), p.z)
    n = 0
    # feather: full sink south of Y_PLAZA-0.4; blend over 0.8 m into plaza
    for vi in idxs:
        v = me.vertices[vi]; p = mw @ v.co
        gz = gnd(p.x, p.y)
        if gz is None:
            # sample nearby into UG
            for dy in (-0.3, 0.3, -0.6, 0.6):
                gz = gnd(p.x, p.y + dy)
                if gz is not None: break
        if gz is None: continue
        # blend weight: 1 = fully under lawn, 0 = leave plaza
        if p.y >= Y_PLAZA:
            t = 0.0
        elif p.y <= Y_PLAZA - 0.8:
            t = 1.0
        else:
            t = (Y_PLAZA - p.y) / 0.8
        if t < 0.05: continue
        k = (round(p.x / 0.04), round(p.y / 0.04))
        top = cols[k]; is_top = abs(p.z - top) < 1e-4
        target_top = gz - under
        if is_top:
            newz = p.z * (1 - t) + target_top * t
            if abs(newz - p.z) > 0.002:
                p.z = newz; v.co = imw @ p; n += 1
        else:
            # keep ~0.28 thickness under the (possibly moved) top — apply after
            pass
    # second pass bottoms
    cols2 = {}
    for vi in idxs:
        p = mw @ me.vertices[vi].co
        k = (round(p.x / 0.04), round(p.y / 0.04))
        cols2[k] = max(cols2.get(k, -1e9), p.z)
    for vi in idxs:
        v = me.vertices[vi]; p = mw @ v.co
        k = (round(p.x / 0.04), round(p.y / 0.04))
        top = cols2[k]
        if abs(p.z - top) < 1e-4: continue
        if p.y >= Y_PLAZA: continue
        t = 1.0 if p.y <= Y_PLAZA - 0.8 else max(0.0, (Y_PLAZA - p.y) / 0.8)
        if t < 0.05: continue
        want = top - 0.28
        if abs(p.z - want) > 0.04 and p.z < top - 0.05:
            p.z = want; v.co = imw @ p; n += 1
    me.update()
    o['ui_touched'] = 1
    o['UNVERIFIED_ui'] = 'QXP/QY strip south of plaza sunk under UG lawn per Joe lawn call (ui)'
    print('UI A sink', name, n)
    return n

log['qxp_sink'] = sink_paving('QXP_pedestrian_area_313024781_paving_UNVERIFIED', under=0.12)
log['qy_sink'] = sink_paving('QY_plaza_rim_band_313024781_UNVERIFIED', under=0.11)

# Also delete (hide by removing) QXP/QY faces whose centers sit fully in the strip
# so no thin vertical curtain remains at the lawn surface. Keep north plaza intact.
def cut_strip_faces(name, y_cut=Y_PLAZA - 0.05):
    o = bpy.data.objects.get(name)
    if not o: return 0
    # already backed up
    bm = bmesh.new(); bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    mw = o.matrix_world
    doomed = []
    for f in bm.faces:
        c = mw @ f.calc_center_median()
        if XA - 0.5 < c.x < XB + 0.5 and Y_WALK - 0.5 < c.y < y_cut:
            doomed.append(f)
    n = len(doomed)
    if doomed:
        bmesh.ops.delete(bm, geom=doomed, context='FACES')
    # drop loose verts
    loose = [v for v in bm.verts if not v.link_faces]
    if loose:
        bmesh.ops.delete(bm, geom=loose, context='VERTS')
    bm.to_mesh(o.data); bm.free(); o.data.update()
    print('UI A cut faces', name, n)
    return n

log['qxp_cut'] = cut_strip_faces('QXP_pedestrian_area_313024781_paving_UNVERIFIED')
log['qy_cut'] = cut_strip_faces('QY_plaza_rim_band_313024781_UNVERIFIED')

# refresh casters after edits
dg = bpy.context.evaluated_depsgraph_get()
UG = caster('UG_Partridge_E_seam_fill_lawn_UNVERIFIED')
SA = caster('SA_ground_lower_patch_UNVERIFIED')
DT = caster('Terrain_LiDAR_DTM_1m')

# ---------- C) further soften UG↔SA crease ----------
ugo = bpy.data.objects['UG_Partridge_E_seam_fill_lawn_UNVERIFIED']
ume = backup(ugo); umw = ugo.matrix_world; uimw = umw.inverted()
n_ug = 0
for v in ume.vertices:
    p = umw @ v.co
    if not (XA - 0.8 < p.x < XB + 0.8): continue
    if p.y < 249.0: continue
    saz = None
    for dy in (0.0, 0.4, 0.8, 1.2, 1.8):
        saz, _ = SA(p.x, p.y + dy)
        if saz is not None: break
    if saz is None: continue
    # stronger feather than uh: y 249.2 → 251.5
    t = min(1.0, max(0.0, (p.y - 249.2) / 2.3))
    target = p.z * (1 - t) + (saz + 0.004) * t
    if abs(target - p.z) > 0.0015:
        p.z = target; v.co = uimw @ p; n_ug += 1
ume.update(); log['ug_crease'] = n_ug
print('UI C ug crease', n_ug)

sao = bpy.data.objects['SA_ground_lower_patch_UNVERIFIED']
sme = backup(sao); smw = sao.matrix_world; simw = smw.inverted()
dg = bpy.context.evaluated_depsgraph_get(); UG2 = caster('UG_Partridge_E_seam_fill_lawn_UNVERIFIED')
n_sa = 0
for v in sme.vertices:
    p = smw @ v.co
    if not (XA - 0.6 < p.x < XB + 0.6): continue
    if not (250.2 < p.y < 254.0): continue
    ugz, _ = UG2(p.x, min(p.y, 250.8))
    if ugz is None:
        ugz, _ = UG2(p.x, 250.3)
    if ugz is None: continue
    if p.z < ugz - 0.008:
        t = min(1.0, max(0.0, (254.0 - p.y) / 3.5))
        target = p.z * (1 - t) + (ugz - 0.006) * t
        if target > p.z + 0.0015:
            p.z = target; v.co = simw @ p; n_sa += 1
sme.update(); log['sa_crease'] = n_sa
print('UI C sa crease', n_sa)

# ---------- D) soften residual QXP/QY S-edge jaggedness ----------
def soften_s_edge(name, rounds=4, lerp=0.45):
    o = bpy.data.objects.get(name)
    if not o: return 0
    me = o.data  # already backed up
    mw = o.matrix_world; imw = mw.inverted()
    # boundary-ish top verts near new south edge
    idxs = []
    for v in me.vertices:
        p = mw @ v.co
        if XA - 1.0 < p.x < XB + 2.0 and (Y_PLAZA - 1.2) < p.y < (Y_PLAZA + 1.5):
            idxs.append(v.index)
    if not idxs: return 0
    # find local zmax for top band
    zs = [(mw @ me.vertices[i].co).z for i in idxs]
    zmax = max(zs)
    top = [i for i in idxs if (mw @ me.vertices[i].co).z > zmax - 0.12]
    n = 0
    for _ in range(rounds):
        adj = {}
        for e in me.edges:
            a, b = e.vertices
            if a in top or b in top:
                adj.setdefault(a, []).append(b)
                adj.setdefault(b, []).append(a)
        newxy = {}
        for vi in top:
            nbr = [j for j in adj.get(vi, []) if j in top]
            if len(nbr) < 2: continue
            ax = sum((mw @ me.vertices[j].co).x for j in nbr) / len(nbr)
            ay = sum((mw @ me.vertices[j].co).y for j in nbr) / len(nbr)
            p = mw @ me.vertices[vi].co
            newxy[vi] = (p.x * (1 - lerp) + ax * lerp, p.y * (1 - lerp) + ay * lerp, p.z)
        for vi, (x, y, z) in newxy.items():
            me.vertices[vi].co = imw @ Vector((x, y, z)); n += 1
    me.update()
    print('UI D soften', name, n)
    return n

log['qxp_soften'] = soften_s_edge('QXP_pedestrian_area_313024781_paving_UNVERIFIED')
log['qy_soften'] = soften_s_edge('QY_plaza_rim_band_313024781_UNVERIFIED', rounds=3, lerp=0.4)

# ---------- E) W apron / 404 sawtooth soften (gentle extra pass) ----------
def soften_outline(o, tag, rounds=3, lerp=0.35, focus_box=(-110, -96, 240, 270)):
    if o is None: return 0
    backup(o)
    bm = bmesh.new(); bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table(); bm.verts.ensure_lookup_table()
    mw = o.matrix_world
    wz = [(v, (mw @ v.co).z) for v in bm.verts]
    zmax = max(z for _, z in wz)
    top_set = {v for v, z in wz if z > zmax - 0.10}
    x0, x1, y0, y1 = focus_box
    focus = {v for v in top_set if x0 < (mw @ v.co).x < x1 and y0 < (mw @ v.co).y < y1} or top_set
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
    bm.to_mesh(o.data); bm.free(); o.data.update()
    o['ui_touched'] = 1
    o['UNVERIFIED_ui_w'] = f'{tag} extra xy-smooth UNVERIFIED (ui)'
    print('UI E', tag, 'verts', len(o.data.vertices))
    return len(o.data.vertices)

apron = bpy.data.objects.get('TY Partridge W areaway apron cutting lawn bank (UNVERIFIED)')
walk404 = bpy.data.objects.get('TY_footway_313026404_to_Partridge_UNVERIFIED')
walk399 = bpy.data.objects.get('TY_footway_313026399_to_Partridge_UNVERIFIED')
log['apron_v'] = soften_outline(apron, 'apron')
log['w404_v'] = soften_outline(walk404, 'walk404', rounds=3, lerp=0.3)
if walk399:
    log['w399_v'] = soften_outline(walk399, 'walk399', rounds=2, lerp=0.3)

fp = bpy.data.objects.get('Footpaths_OSM')
if fp:
    backup(fp)
    me = fp.data; mw = fp.matrix_world; imw = mw.inverted()
    idxs = [v.index for v in me.vertices
            if -106 < (mw @ v.co).x < -96.5 and 245.5 < (mw @ v.co).y < 251.5]
    nfp = 0
    for _ in range(3):
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
            newxy[vi] = (0.65 * p.x + 0.35 * ax, 0.65 * p.y + 0.35 * ay, p.z)
        for vi, (x, y, z) in newxy.items():
            me.vertices[vi].co = imw @ Vector((x, y, z)); nfp += 1
    me.update(); log['fp_smooth'] = nfp
    print('UI E Footpaths', nfp)

# ---------- B) grass on newly exposed strip (esp. where QXP was) ----------
rnd = random.Random(20261105 + 1)
FP = [tuple(p) for p in json.load(open(D + 'data/tx/nursing_geom.json'))['footprint']]
def inside(x, y):
    c = False; n = len(FP)
    for i in range(n):
        x1, y1 = FP[i]; x2, y2 = FP[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-12) + x1: c = not c
    return c

dg = bpy.context.evaluated_depsgraph_get()
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

ugo = bpy.data.objects['UG_Partridge_E_seam_fill_lawn_UNVERIFIED']
umw = ugo.matrix_world
uge = ugo.evaluated_get(dg)
pts = []
DENS = 4.5
area_est = (XB - XA) * (Y_PLAZA - Y_WALK)
n_try = int(DENS * area_est * 2.5)
for _ in range(n_try):
    x = XA + rnd.random() * (XB - XA)
    y = Y_WALK + 0.15 + rnd.random() * (Y_PLAZA - Y_WALK - 0.25)
    if inside(x, y): continue
    edge = min(x - XA, XB - x, y - Y_WALK, Y_PLAZA - y)
    if edge < 0: continue
    if edge < 0.5 and rnd.random() > edge / 0.5: continue
    r = uge.ray_cast(ugo.matrix_world.inverted() @ Vector((x, y, 400)),
                     (ugo.matrix_world.inverted().to_3x3() @ Vector((0, 0, -1))).normalized())
    if not r[0]: continue
    z = (umw @ r[1]).z
    if hit_blk(x, y, z): continue
    pts.append((x, y, z - 0.004))

src = bpy.data.objects.get('UH_Partridge_E_seam_grass_points_UNVERIFIED') or \
      bpy.data.objects.get('QV_Richardson_NW_lawn_grass_points_UNVERIFIED') or \
      bpy.data.objects['cx_grass_points']
col = bpy.data.collections.new(COLN); bpy.context.scene.collection.children.link(col)
me_g = bpy.data.meshes.new('UI_Partridge_E_strip_grass_points_UNVERIFIED')
me_g.from_pydata(pts, [], [])
ob_g = src.copy(); ob_g.data = me_g
ob_g.name = 'UI_Partridge_E_strip_grass_points_UNVERIFIED'
ob_g.matrix_world = __import__('mathutils').Matrix.Identity(4)
for c in list(ob_g.users_collection): c.objects.unlink(ob_g)
col.objects.link(ob_g)
ob_g['ui_obj'] = 1
ob_g['UNVERIFIED'] = 'cx_grass on Partridge E strip after Joe lawn call; density~4.5/m2 UNVERIFIED (ui)'
if 'cx_grass' not in ob_g.modifiers:
    m = ob_g.modifiers.new('cx_grass', 'NODES')
    m.node_group = bpy.data.objects['cx_grass_points'].modifiers['cx_grass'].node_group
else:
    ob_g.modifiers['cx_grass'].node_group = bpy.data.objects['cx_grass_points'].modifiers['cx_grass'].node_group
log['grass'] = len(pts)
print('UI B grass', len(pts))

# ---------- cams ----------
def cam(name, loc, tgt, lens):
    cd = bpy.data.cameras.new(name); cd.lens = lens; cd.clip_end = 6000
    o = bpy.data.objects.new(name, cd); col.objects.link(o); o['ui_obj'] = 1
    o.location = loc
    o.rotation_euler = (Vector(tgt) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()

cam('UI_CAM_oblique_Partridge_E_lawn_from_SE', (-18, 198, 176), (-55, 250, 140), 35)
cam('UI_CAM_eye_Partridge_E_face_from_E', (-46, 252.0, 141.5), (-68, 253.0, 141.0), 28)
cam('UI_CAM_eye_Partridge_W_steps_from_W', (-116, 246.5, 141.0), (-99, 250.5, 139.6), 30)
cam('UI_CAM_closeup_Partridge_E_lawn_strip', (-52, 244.5, 142.0), (-58, 249.5, 139.85), 32)

json.dump(log, open(D + 'data/ui/ui_main.json', 'w'), indent=1)
print('UI LOG', log)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
