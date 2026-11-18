"""Session tz (Nov 5 2026 ~10:21 AM ET, MAIN, day 9): College Hall E/N + 2020 north addition polish.

1) Cream Mission stucco on historic EAST + NORTH wall faces (reuse TW_Cole_stucco_cream_UNVERIFIED;
   S/W already creamed by tw — do not undo).
2) Punched windows on E + exposed N edges using bm rhythm x0.70 (same family as tw S/W). Skip
   north edges behind the 2020 addition footprint. ALL UNVERIFIED (no clear current E photo).
3) Hide bq north addition; rebuild polished modern massing (LiDAR footprint/eave/ridge MEASURED;
   glass/metal contemporary language distinct from 1908 Mission; clean junction, no 4a coplanar
   shared wall with historic mass). Openings UNVERIFIED.
4) Optional subtle sill drips on new E windows.

ALL new geometry/materials UNVERIFIED; tag tz_obj=1; collection TZ_Cole_Hall_EN_UNVERIFIED.
REVERT=1 removes tz objects and restores wall material slots + unhides bq addition.
"""
import bpy, bmesh, os, math, json
from mathutils import Vector, Matrix

REV = os.environ.get('REVERT') == '1'
SAVE = os.environ.get('SAVE') == '1'
DRY = os.environ.get('DRY') == '1'
D = '/workspace/nj-scenes/montclair-state/'
CN = 'TZ_Cole_Hall_EN_UNVERIFIED'
WALLS = 'Susan A. Cole Hall walls'
TW_STUCCO = 'TW_Cole_stucco_cream_UNVERIFIED'
ADD_BQ = 'Cole Hall 2020 north addition (LiDAR footprint/eave/ridge MEASURED; openings UNVERIFIED) bq'
# Blender truncates object names to 63 chars
ADD_BQ_SHORT = None  # resolved at runtime
TAG = 'tz_obj'
TW_TAG_SLOT = 'tz_wall_slots'  # backup of material indices before tz cream

def mat(name, col, rough=0.6, metal=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes.get('Principled BSDF')
    b.inputs['Base Color'].default_value = (*col, 1)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    return m

def find_bq_addition():
    o = bpy.data.objects.get(ADD_BQ)
    if o:
        return o
    for cand in bpy.data.objects:
        if 'north addition' in cand.name.lower() and 'cole' in cand.name.lower():
            return cand
    return None

def revert():
    for o in [o for o in list(bpy.data.objects) if o.get(TAG)]:
        me = o.data
        bpy.data.objects.remove(o, do_unlink=True)
        if me and me.users == 0:
            if hasattr(me, 'vertices'):
                bpy.data.meshes.remove(me)
            elif hasattr(me, 'lens'):
                bpy.data.cameras.remove(me)
    c = bpy.data.collections.get(CN)
    if c:
        bpy.data.collections.remove(c)
    # unhide bq addition
    bq = find_bq_addition()
    if bq and bq.get('tz_hidden'):
        bq.hide_set(False)
        bq.hide_render = False
        del bq['tz_hidden']
    # restore wall material slots
    w = bpy.data.objects.get(WALLS)
    if w and TW_TAG_SLOT in w:
        slots = list(w[TW_TAG_SLOT])
        for i, poly in enumerate(w.data.polygons):
            if i < len(slots):
                poly.material_index = int(slots[i])
        del w[TW_TAG_SLOT]
    # drop orphan TZ materials
    for m in list(bpy.data.materials):
        if m.name.startswith('TZ_Cole_'):
            for ob in bpy.data.objects:
                if ob.type != 'MESH':
                    continue
                for i, s in enumerate(ob.material_slots):
                    if s.material == m:
                        ob.material_slots[i].material = None
            for me in bpy.data.meshes:
                for i, mm in enumerate(list(me.materials)):
                    if mm == m:
                        me.materials[i] = None
            if m.users == 0:
                bpy.data.materials.remove(m)
    print('TZ REVERTED')

revert()
if REV:
    if SAVE:
        bpy.ops.wm.save_mainfile()
        print('SAVED')
    raise SystemExit

# ---- materials ----
# reuse tw cream if present
M_st = bpy.data.materials.get(TW_STUCCO) or mat(TW_STUCCO, (0.86, 0.835, 0.78), 0.88)
M_fr = bpy.data.materials.get('TW_Cole_win_frame_UNVERIFIED') or mat('TW_Cole_win_frame_UNVERIFIED', (0.92, 0.90, 0.86), 0.55)
M_gl = bpy.data.materials.get('TW_Cole_win_glass_UNVERIFIED') or mat('TW_Cole_win_glass_UNVERIFIED', (0.04, 0.05, 0.055), 0.25)
# modern addition: light grey metal panel + dark mullion + clear-ish glass + membrane roof
M_panel = mat('TZ_Cole_add_panel_UNVERIFIED', (0.38, 0.41, 0.45), 0.40, 0.28)
M_mull = mat('TZ_Cole_add_mullion_UNVERIFIED', (0.08, 0.085, 0.09), 0.35, 0.70)
M_agl = mat('TZ_Cole_add_glass_UNVERIFIED', (0.18, 0.22, 0.26), 0.12, 0.0)
# make glass a bit transmissive via Specular/Alpha if available
try:
    nt = M_agl.node_tree.nodes.get('Principled BSDF')
    if 'Transmission Weight' in nt.inputs:
        nt.inputs['Transmission Weight'].default_value = 0.85
    elif 'Transmission' in nt.inputs:
        nt.inputs['Transmission'].default_value = 0.85
    nt.inputs['Alpha'].default_value = 0.35
    M_agl.blend_method = 'HASHED'
except Exception:
    pass
M_roof = mat('TZ_Cole_add_roof_UNVERIFIED', (0.28, 0.30, 0.32), 0.70)
M_drip = mat('TZ_Cole_sill_drip_UNVERIFIED', (0.18, 0.16, 0.14), 0.85)

sc = bpy.context.scene
col = bpy.data.collections.get(CN) or bpy.data.collections.new(CN)
if CN not in [c.name for c in sc.collection.children]:
    sc.collection.children.link(col)

def new_obj(name, mats):
    me = bpy.data.meshes.new(name)
    o = bpy.data.objects.new(name, me)
    col.objects.link(o)
    for m in mats:
        me.materials.append(m)
    o[TAG] = 1
    o['tz_source'] = '20261105tz'
    return o

def add_box(bm, cx, cy, z0, z1, hx, hy, rot, mi):
    R = Matrix.Rotation(rot, 4, 'Z')
    vs = []
    for z in (z0, z1):
        for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            vs.append(bm.verts.new(Vector((cx, cy, 0)) + (R @ Vector((sx * hx, sy * hy, 0))).to_3d() + Vector((0, 0, z))))
    for f in ((0, 1, 2, 3), (7, 6, 5, 4), (0, 4, 5, 1), (1, 5, 6, 2), (2, 6, 7, 3), (3, 7, 4, 0)):
        bm.faces.new([vs[i] for i in f]).material_index = mi

# ---- 1) cream E + N historic faces (tw flip convention) ----
w = bpy.data.objects.get(WALLS)
ncream = 0
if w and not DRY:
    me = w.data
    # only backup if not already backed up this session (idempotent after revert)
    if TW_TAG_SLOT not in w:
        w[TW_TAG_SLOT] = [p.material_index for p in me.polygons]
    if TW_STUCCO not in [m.name if m else '' for m in me.materials]:
        me.materials.append(M_st)
    names = [m.name if m else '' for m in me.materials]
    si = names.index(TW_STUCCO)
    for poly in me.polygons:
        nw = -(w.matrix_world.to_3x3() @ poly.normal).normalized()  # tw flip
        if abs(nw.z) > 0.5:
            continue
        # E or N after flip (tw: S is nw.y<-0.55, W is nw.x<-0.55)
        if nw.y > 0.55 or nw.x > 0.55:
            # skip faces already cream (S/W from tw) — harmless to re-set
            poly.material_index = si
            ncream += 1
    print('TZ wall cream E+N faces', ncream, 'si', si)

# ---- 2) punched windows E + exposed N ----
GRADE = 131.61
SCALE = 0.70
pitch = 2.11 * SCALE
ww = 1.39 * SCALE
wh_r1 = 2.72 * SCALE
wh_r2 = 3.27 * SCALE
wh_r3 = 3.05 * SCALE
sill = [1.58 * SCALE, 6.29 * SCALE, 11.64 * SCALE]

ring = json.load(open(D + 'north/data/day_heroes/day9_cole_hall_levels_prep_20261016be.json'))['footprint']['ring_scene_xy_m']
P = [Vector((x, y)) for x, y in ring]
if P[0] == P[-1]:
    P = P[:-1]
area = sum(P[i].x * P[(i + 1) % len(P)].y - P[(i + 1) % len(P)].x * P[i].y for i in range(len(P))) / 2

# addition footprint (identity rect) — skip N windows whose mid falls inside expanded rect
ident = json.load(open(D + 'north/data/day_heroes/day9_cole_hall_identity_20261016bq.json'))
ARECT = [Vector(p) for p in ident['lidar_MEASURED']['north_addition_rect']]
# axis-aligned pad around addition for window skip (historic wall behind addition)
ax = [p.x for p in ARECT]; ay = [p.y for p in ARECT]
ADD_PAD = (min(ax) - 1.0, max(ax) + 1.0, min(ay) - 3.5, max(ay) + 1.0)  # pad south into junction

def in_add_zone(x, y):
    return ADD_PAD[0] <= x <= ADD_PAD[1] and ADD_PAD[2] <= y <= ADD_PAD[3]

nwin = 0
ndrip = 0
if not DRY:
    win = new_obj('TZ_Cole_windows_EN_UNVERIFIED', [M_fr, M_gl, M_st])
    drip = new_obj('TZ_Cole_sill_drips_EN_UNVERIFIED', [M_drip])
    bm = bmesh.new()
    bm_d = bmesh.new()
    for i in range(len(P)):
        a, b = P[i], P[(i + 1) % len(P)]
        d = b - a
        L = d.length
        if L < 5.0:
            continue
        t = d / L
        n = Vector((t.y, -t.x)) if area > 0 else Vector((-t.y, t.x))
        is_east = n.x > 0.55
        is_north = n.y > 0.55
        if not (is_east or is_north):
            continue
        mid = (a + b) / 2
        # north edges mostly behind addition: skip whole edge if mid in pad
        if is_north and in_add_zone(mid.x, mid.y):
            continue
        edge_rot = math.atan2(t.y, t.x)
        margin = 1.2
        usable = L - 2 * margin
        if usable < pitch:
            continue
        nb = max(1, int(round(usable / pitch)))
        for row, (sz, wh) in enumerate(zip(sill, (wh_r1, wh_r2, wh_r3))):
            z0 = GRADE + sz
            z1 = z0 + wh
            if z1 > 142.6:
                z1 = 142.55
            for k in range(nb):
                # east: denser all rows; alternate ground like west for long east runs only
                if row == 0 and is_east and L > 20 and (k % 2) == 1:
                    continue
                u = margin + (k + 0.5) * (usable / nb)
                cx = a.x + t.x * u
                cy = a.y + t.y * u
                if is_north and in_add_zone(cx, cy):
                    continue
                add_box(bm, cx + n.x * 0.10, cy + n.y * 0.10, z0, z1, ww / 2, 0.07, edge_rot, 0)
                add_box(bm, cx + n.x * 0.16, cy + n.y * 0.16, z0 + 0.05, z1 - 0.05, ww / 2 * 0.78, 0.04, edge_rot, 1)
                nwin += 1
                # subtle sill drip (3 mm proud under sill)
                if row in (0, 1):
                    add_box(bm_d, cx + n.x * 0.12, cy + n.y * 0.12, z0 - 0.04, z0 + 0.01, ww / 2 * 0.95, 0.03, edge_rot, 0)
                    ndrip += 1
    bm.to_mesh(win.data)
    bm.free()
    bm_d.to_mesh(drip.data)
    bm_d.free()
    print('TZ windows EN', nwin, 'drips', ndrip)

# ---- 3) polish 2020 north addition ----
A = Vector((-120.51, -77.88))
B = Vector((-98.02, -83.07))
Dd = Vector((-116.57, -60.79))
uu = (B - A); Lu = uu.length; uu /= Lu
vv = (Dd - A); Lv = vv.length; vv /= Lv
EAVE, RIDGE = 143.2, 149.3

def Q(u, v, z):
    p = A + uu * u + vv * v
    return Vector((p.x, p.y, z))

def ground(x, y):
    dg = bpy.context.evaluated_depsgraph_get()
    best = None
    for nm in ('Terrain_LiDAR_DTM_1m', 'Context_skirt_3DEP_ortho_4km'):
        o = bpy.data.objects.get(nm)
        if not o:
            continue
        e = o.evaluated_get(dg)
        iw = o.matrix_world.inverted()
        r = e.ray_cast(iw @ Vector((x, y, 400)), (iw.to_3x3() @ Vector((0, 0, -1))).normalized())
        if r[0]:
            z = (o.matrix_world @ r[1]).z
            if best is None or z > best:
                best = z
    return best if best is not None else 132.0

if not DRY:
    bq = find_bq_addition()
    if bq:
        bq.hide_set(True)
        bq.hide_render = True
        bq['tz_hidden'] = 1
        print('TZ hid bq addition', bq.name)

    gzN = min(
        ground(*(A + uu * (Lu / 2) + vv * (Lv + 2.0))),
        ground(*(A + vv * (Lv + 2.0))),
        ground(*(B + vv * (Lv + 2.0))),
    )
    # footprint: slight inset from historic south (v0 = +0.15 into addition, NOT into historic wall plane)
    # bq used v0=-2.5 (2.5 m into old building). Keep a small tuck for junction but avoid coplanar 4a.
    u0, u1 = -0.3, Lu + 0.3
    v0, v1 = 0.15, Lv + 0.4  # start just north of historic face; overhang roof southward separately
    um = (u0 + u1) / 2
    Z0 = gzN - 0.8

    nad = new_obj('TZ_Cole_north_addition_UNVERIFIED', [M_panel, M_roof, M_mull, M_agl])
    bm = bmesh.new()

    def face(pts, mi):
        vs = [bm.verts.new(p) for p in pts]
        f = bm.faces.new(vs)
        f.material_index = mi

    # walls: W / E long sides + N gable end + S junction end (panel, not shared with historic)
    face([Q(u0, v0, Z0), Q(u0, v1, Z0), Q(u0, v1, EAVE), Q(u0, v0, EAVE)][::-1], 0)
    face([Q(u1, v0, Z0), Q(u1, v0, EAVE), Q(u1, v1, EAVE), Q(u1, v1, Z0)][::-1], 0)
    face([Q(u0, v1, Z0), Q(u1, v1, Z0), Q(u1, v1, EAVE), Q(um, v1, RIDGE), Q(u0, v1, EAVE)], 0)
    face([Q(u0, v0, Z0), Q(u0, v0, EAVE), Q(um, v0, RIDGE), Q(u1, v0, EAVE), Q(u1, v0, Z0)], 0)

    # roof slabs, 0.55 m overhang, 0.22 thick; south overhang covers junction gap without shared plane
    ov = 0.55
    sl = (RIDGE - EAVE) / max(um - u0, 0.1)
    for side in (-1, 1):
        ue = (u0 - ov) if side < 0 else (u1 + ov)
        ze = EAVE - ov * sl
        top = [Q(ue, v0 - 0.4, ze), Q(ue, v1 + ov, ze), Q(um, v1 + ov, RIDGE + 0.04), Q(um, v0 - 0.4, RIDGE + 0.04)]
        if side > 0:
            top = top[::-1]
        addv = [bm.verts.new(p) for p in top]
        bm.faces.new(addv).material_index = 1
        bot = [bm.verts.new(p - Vector((0, 0, 0.22))) for p in top]
        bm.faces.new(bot[::-1]).material_index = 1
        for k in range(4):
            bm.faces.new([addv[k], bot[k], bot[(k + 1) % 4], addv[(k + 1) % 4]]).material_index = 1

    # modern curtain language on N end: tall glass wall + dark mullions (UNVERIFIED)
    nrm = vv
    rr = math.atan2(uu.y, uu.x)
    cN = A + uu * um + vv * (v1 + 0.05)
    # full-height curtain panel field
    zb = gzN + 0.3
    zt = EAVE - 0.15
    Wcurtain = min(Lu * 0.72, 14.0)
    # outer frame
    add_box(bm, cN.x, cN.y, zb, zt, Wcurtain / 2 + 0.15, 0.06, rr, 2)
    # glass field
    p = cN + nrm * 0.04
    add_box(bm, p.x, p.y, zb + 0.08, zt - 0.08, Wcurtain / 2, 0.05, rr, 3)
    # vertical mullions
    nmull = 7
    for i in range(nmull):
        xm = -Wcurtain / 2 + (i + 0.5) * (Wcurtain / nmull)
        pp = cN + uu * xm + nrm * 0.07
        add_box(bm, pp.x, pp.y, zb + 0.08, zt - 0.08, 0.06, 0.04, rr, 2)
    # horizontal transoms
    for frac in (0.33, 0.66):
        zz = zb + (zt - zb) * frac
        pp = cN + nrm * 0.07
        add_box(bm, pp.x, pp.y, zz - 0.05, zz + 0.05, Wcurtain / 2 - 0.05, 0.04, rr, 2)
    # glazed entrance band at grade
    add_box(bm, cN.x, cN.y, gzN - 0.15, gzN + 3.0, 3.4, 0.07, rr, 2)
    p = cN + nrm * 0.04
    add_box(bm, p.x, p.y, gzN - 0.05, gzN + 2.9, 3.2, 0.05, rr, 3)

    # E/W side punched ribbon windows (modern, distinct from Mission) — 2 rows
    for side_u, sign in ((u0, -1), (u1, +1)):
        # outward normal along +/- uu
        sn = uu * sign
        side_rot = math.atan2(vv.y, vv.x)
        for vi, zz0, zz1 in ((0.18, gzN + 1.0, gzN + 3.2), (0.18, gzN + 5.0, gzN + 7.4)):
            # skip near south junction and north end
            nslots = 5
            for k in range(nslots):
                vvpos = v0 + 1.5 + (k + 0.5) * ((v1 - v0 - 3.0) / nslots)
                if vvpos >= v1 - 1.2:
                    continue
                c = A + uu * side_u + vv * vvpos + sn * 0.08
                add_box(bm, c.x, c.y, zz0, zz1, 0.06, 0.85, side_rot, 2)
                c2 = c + sn * 0.04
                add_box(bm, c2.x, c2.y, zz0 + 0.06, zz1 - 0.06, 0.04, 0.72, side_rot, 3)

    # thin metal coping / eave trim band
    for u_edge in (u0, u1):
        # skip — roof overhang already reads
        pass
    # fascia strip under eave on long sides
    for side_u, sign in ((u0, -1), (u1, +1)):
        sn = uu * sign
        for vvpos in (v0, v1):
            pass
    # simple continuous fascia along E/W eaves
    for side_u, sign in ((u0 - 0.02, -1), (u1 + 0.02, +1)):
        c0 = Q(side_u, v0, EAVE)
        c1 = Q(side_u, v1, EAVE)
        mid = (c0 + c1) / 2
        side_rot = math.atan2(vv.y, vv.x)
        add_box(bm, mid.x, mid.y, EAVE - 0.18, EAVE + 0.05, 0.08, (v1 - v0) / 2 + 0.1, side_rot, 2)

    bm.to_mesh(nad.data)
    bm.free()
    zs = [(nad.matrix_world @ v.co).z for v in nad.data.vertices]
    print('TZ addition verts', len(nad.data.vertices), 'z', min(zs), max(zs), 'target eave/ridge', EAVE, RIDGE, 'gzN', gzN)

if SAVE and not DRY:
    bpy.ops.wm.save_mainfile()
    print('SAVED')
print('TZ DONE ncream', ncream, 'nwin', nwin)
