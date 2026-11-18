"""wz fix: close the y=320 south-seam crack with a cover flap + short curtain.

Probe (data/wz/probe.json) found the crack is not an empty hole. South-eye and
close-up crack pixels hit at y≈320.05–320.32:
  - WU's top in the 35 cm overlap (tucked 2–10 cm under WF; max gap 10.4 cm
    at x≈85–86) — that surface sits in WF's shadow, so it renders black;
  - WF's underside (backface, ndot +0.04..+0.09) — unlit, also black;
  - Context_skirt through the same slot (also under the sheets / unlit).
North-eye rays hit WF's lit top further north (y≈322–327) and stay clean.
Sliding WU under WF (wy fix4) cannot fix a south grazing view; the 3 cm tuck
is the slot the south camera looks into. Do not tuck further.

Fix: extend a cover flap 1.5 m SOUTH from WF's open y=320 lip over WU/WT,
4–8 mm (6 mm) above the south sheet, and hang an 8 cm curtain from the new
south edge so under-flap rays hit geometry instead of the slot. End caps on
the west and east sides. Same material / UV fit as neighbouring WF faces.
WU/WT verts are not moved (keeps the 11 mm height match and avoids a
coplanar z-fight in the overlap). Grass in the flap band is reseated onto
the new top. New verts get edge-darkening attrs zeroed.
"""
import bpy, bmesh, json, os
import numpy as np
from collections import defaultdict
from mathutils import Vector
from mathutils.bvhtree import BVHTree

R = '/workspace/nj-scenes/montclair-state'
os.chdir(R)
SAVE = os.environ.get('SAVE') == '1'
WFN = 'WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED'
WUN = 'WU_richardson_reid_LiDAR_patch_UNVERIFIED'
WTN = 'WT_richardson_west_LiDAR_patch_UNVERIFIED'
O = bpy.data.objects
P = O[WFN]
me = P.data
mw = P.matrix_world
mi = mw.inverted()

FLAP = 1.50          # metres south of the WF lip
LIFT = 0.006         # 6 mm above WU/WT
CURTAIN = 0.08       # 8 cm down from the flap south edge (closes the 6 mm slot)
X1, X2 = 66.0, 112.0
Y_LIP = 320.0
YTOL = 0.12

rep = dict(flap_m=FLAP, lift_m=LIFT, curtain_m=CURTAIN,
           start_verts=len(me.vertices), start_faces=len(me.polygons))
print('START WF', rep['start_verts'], 'faces', rep['start_faces'], flush=True)
np.save('data/wz/WF_verts_pre_wz.npy', np.array([v.co[:] for v in me.vertices]))

dg = bpy.context.evaluated_depsgraph_get()

def make_bvh(o):
    e = o.evaluated_get(dg)
    m = e.to_mesh()
    b = BVHTree.FromPolygons([o.matrix_world @ v.co for v in m.vertices],
                             [tuple(p.vertices) for p in m.polygons])
    e.to_mesh_clear()
    return b

def hz(b, x, y):
    if b is None:
        return None
    h = b.ray_cast(Vector((x, y, 500.0)), Vector((0.0, 0.0, -1.0)))
    return None if h[0] is None else float(h[0].z)

print('BVH WU/WT (pre)...', flush=True)
BU = make_bvh(O[WUN]) if O.get(WUN) else None
BT = make_bvh(O[WTN]) if O.get(WTN) else None
BOLD_TOP = {}
for n in (WFN, WUN, WTN):
    if O.get(n):
        BOLD_TOP[n] = make_bvh(O[n])

def south_z(x, y):
    zs = []
    for b in (BU, BT):
        z = hz(b, x, y)
        if z is not None:
            zs.append(z)
    return max(zs) if zs else None

def top_old(x, y):
    best = None
    for b in BOLD_TOP.values():
        z = hz(b, x, y)
        if z is not None and (best is None or z > best):
            best = z
    return best

# UV fit from nearby WF loops (same method as wy)
uvL = me.uv_layers.get('ortho') or (me.uv_layers[0] if me.uv_layers else None)
cu = np.array([0.0, 0.0, 0.0]); cv = np.array([0.0, 0.0, 0.0])
if uvL:
    A = []; U = []; V = []; ntake = 0
    for p in me.polygons:
        c = p.center
        if not (60 <= c.x <= 125 and 318 <= c.y <= 360):
            continue
        for li in p.loop_indices:
            v = me.vertices[me.loops[li].vertex_index].co
            uv = uvL.data[li].uv
            A.append([v.x, v.y, 1.0]); U.append(uv[0]); V.append(uv[1])
        ntake += 1
        if ntake >= 800:
            break
    if len(A) >= 10:
        A = np.array(A)
        cu = np.linalg.lstsq(A, np.array(U), rcond=None)[0]
        cv = np.linalg.lstsq(A, np.array(V), rcond=None)[0]
        print('UV fit from', len(A), 'loops', flush=True)
rep['uv_fit'] = [list(map(float, cu)), list(map(float, cv))]

def uv_at(x, y):
    return (float(cu[0] * x + cu[1] * y + cu[2]),
            float(cv[0] * x + cv[1] * y + cv[2]))

# snapshot point attrs for copying onto new verts
anames = []
for a in me.attributes:
    if a.name.startswith('.') or a.name == 'position':
        continue
    if a.domain == 'POINT' and a.data_type in ('FLOAT', 'FLOAT_VECTOR'):
        anames.append((a.name, a.data_type))
# pick a nearby existing vert as the attr source
src_attr = None
for vi, v in enumerate(me.vertices):
    if abs(v.co.y - Y_LIP) < 1.0 and X1 <= v.co.x <= X2:
        rec = {}
        for name, dt in anames:
            a = me.attributes[name]
            rec[name] = (list(a.data[vi].vector) if dt == 'FLOAT_VECTOR'
                         else float(a.data[vi].value))
        src_attr = rec
        break
print('ATTR names', [n for n, _ in anames], 'src', src_attr is not None, flush=True)

# material index from a nearby face
mat_i = 0
for p in me.polygons:
    if abs(p.center.y - Y_LIP) < 2.0 and X1 <= p.center.x <= X2:
        mat_i = p.material_index
        break
rep['material_index'] = int(mat_i)

# --- edit ---
bm = bmesh.new()
bm.from_mesh(me)
bm.verts.ensure_lookup_table()
bm.edges.ensure_lookup_table()
bm.faces.ensure_lookup_table()

# boundary edges along the lip
edge_count = defaultdict(int)
for f in bm.faces:
    vs = list(f.verts)
    for a, b in zip(vs, vs[1:] + vs[:1]):
        e = (a.index, b.index) if a.index < b.index else (b.index, a.index)
        edge_count[e] += 1

lip_edges = []  # (v_west, v_east) in world-ish local (WF is axis-aligned)
for e in bm.edges:
    a, b = e.verts
    key = (a.index, b.index) if a.index < b.index else (b.index, a.index)
    if edge_count.get(key, 0) != 1:
        continue
    ca = mw @ a.co
    cb = mw @ b.co
    ym = 0.5 * (ca.y + cb.y)
    xm = 0.5 * (ca.x + cb.x)
    if abs(ym - Y_LIP) > YTOL or not (X1 <= xm <= X2):
        continue
    # require the edge to run mostly along +x (the tile south lip)
    if abs(cb.x - ca.x) < 0.2:
        continue
    if ca.x <= cb.x:
        lip_edges.append((a, b, ca, cb))
    else:
        lip_edges.append((b, a, cb, ca))
lip_edges.sort(key=lambda t: t[2].x)
rep['lip_edges'] = len(lip_edges)
print('LIP EDGES', len(lip_edges),
      'x', [round(lip_edges[0][2].x, 2), round(lip_edges[-1][3].x, 2)] if lip_edges else None,
      flush=True)

# new verts keyed by rounded lip-x (share between adjacent edges) and role
# roles: 'flap', 'cur'
new_map = {}  # (round(x,3), role) -> bmvert
new_verts = []

def get_new(wx, role, wy, wz):
    key = (round(wx, 3), role)
    if key in new_map:
        return new_map[key]
    loc = mi @ Vector((wx, wy, wz))
    v = bm.verts.new(loc)
    new_map[key] = v
    new_verts.append((v, role, wx, wy, wz))
    return v

new_faces = []
def add_face(vs, want_up=None, want_ny=None):
    try:
        f = bm.faces.new(vs)
    except ValueError:
        return None
    f.smooth = True
    f.normal_update()
    if want_up is True and f.normal.z < 0:
        f.normal_flip()
    if want_ny is not None and f.normal.y * want_ny < 0:
        f.normal_flip()
    new_faces.append(f)
    return f

flap_zs = []
for vw, ve, cw, ce in lip_edges:
    yf = Y_LIP - FLAP
    zw = south_z(cw.x, yf)
    ze = south_z(ce.x, yf)
    if zw is None:
        zw = cw.z
    if ze is None:
        ze = ce.z
    zw = zw + LIFT
    ze = ze + LIFT
    flap_zs.extend([zw - (south_z(cw.x, yf) or (zw - LIFT)),
                    ze - (south_z(ce.x, yf) or (ze - LIFT))])
    fw = get_new(cw.x, 'flap', yf, zw)
    fe = get_new(ce.x, 'flap', yf, ze)
    cw_ = get_new(cw.x, 'cur', yf, zw - CURTAIN)
    ce_ = get_new(ce.x, 'cur', yf, ze - CURTAIN)
    # flap (CCW from above): SW, SE, NE, NW = fw, fe, ve, vw
    add_face([fw, fe, ve, vw], want_up=True)
    # curtain (want normal -y / south): fw, fe, ce_, cw_
    add_face([fw, fe, ce_, cw_], want_ny=-1.0)

# end caps (west of first edge, east of last edge)
if lip_edges:
    vw, ve, cw, ce = lip_edges[0]
    yf = Y_LIP - FLAP
    zw = (south_z(cw.x, yf) or cw.z) + LIFT
    fw = get_new(cw.x, 'flap', yf, zw)
    cuw = get_new(cw.x, 'cur', yf, zw - CURTAIN)
    # downward from the lip itself for a closed west cap
    lip_down = get_new(cw.x, 'lipcur', cw.y, cw.z - CURTAIN)
    # west cap, normal -x: looking from west, CCW = lip, flap, flap_cur, lip_cur
    add_face([vw, fw, cuw, lip_down], want_ny=None)
    # flip if normal.x > 0
    if new_faces[-1].normal.x > 0:
        new_faces[-1].normal_flip()

    vw, ve, cw, ce = lip_edges[-1]
    ze = (south_z(ce.x, yf) or ce.z) + LIFT
    fe = get_new(ce.x, 'flap', yf, ze)
    cue = get_new(ce.x, 'cur', yf, ze - CURTAIN)
    lip_down_e = get_new(ce.x, 'lipcur', ce.y, ce.z - CURTAIN)
    add_face([ve, fe, cue, lip_down_e], want_ny=None)
    if new_faces[-1].normal.x < 0:
        new_faces[-1].normal_flip()

# UVs
uv_layer = bm.loops.layers.uv.get('ortho')
if uv_layer is None:
    uv_layer = bm.loops.layers.uv.active or bm.loops.layers.uv.new('ortho')
for f in new_faces:
    for l in f.loops:
        wc = mw @ l.vert.co
        l[uv_layer].uv = uv_at(wc.x, wc.y)

rep['faces_added'] = len(new_faces)
rep['verts_added'] = len(new_verts)
rep['faces_flipped_after'] = 0
# recount flips already applied; just note normal signs
up = sum(1 for f in new_faces if f.normal.z > 0.5)
south = sum(1 for f in new_faces if f.normal.y < -0.5)
print('ADDED faces', len(new_faces), 'verts', len(new_verts),
      'up_normals', up, 'south_normals', south, flush=True)
rep['n_up'] = up
rep['n_south'] = south

bm.to_mesh(me)
bm.free()
me.update()

# material index on the newly appended faces (they are the last N)
for p in list(me.polygons)[-rep['faces_added']:]:
    p.material_index = mat_i

# attrs on new verts (they are the last verts_added)
ZERO_ATTRS = {'wh_edge', 'ou_edge', 'wk_litter', 'wj_in'}
filled = 0
n_old = rep['start_verts']
for vi in range(n_old, len(me.vertices)):
    for name, dt in anames:
        a = me.attributes.get(name)
        if a is None:
            continue
        if name in ZERO_ATTRS:
            if dt == 'FLOAT_VECTOR':
                a.data[vi].vector = (0.0, 0.0, 0.0)
            else:
                a.data[vi].value = 0.0
        elif src_attr and name in src_attr:
            if dt == 'FLOAT_VECTOR':
                a.data[vi].vector = src_attr[name]
            else:
                a.data[vi].value = float(src_attr[name])
    filled += 1
rep['new_vert_attrs_filled'] = filled
print('ATTR fill', filled, flush=True)

# clear leftover ou_edge on existing lip / overlap verts (both sides of the
# seam) — ou_edge is a leftover fade (~0.44–0.58) and is not the black, but
# parent asked to clear leftover edge-darkening on both sides if any remain.
cleared = {}
for n, obj, ylo, yhi in (
    (WFN, P, 317.5, 322.0),
    (WUN, O.get(WUN), 317.5, 321.0),
    (WTN, O.get(WTN), 317.5, 321.0),
):
    if obj is None:
        continue
    ome = obj.data
    omw = obj.matrix_world
    rec = {}
    for an in ('ou_edge', 'wh_edge'):
        a = ome.attributes.get(an)
        if a is None or a.domain != 'POINT' or a.data_type != 'FLOAT':
            continue
        k = 0
        before = []
        for vi, v in enumerate(ome.vertices):
            c = omw @ v.co
            if not (X1 - 1 <= c.x <= X2 + 1 and ylo <= c.y <= yhi):
                continue
            old = float(a.data[vi].value)
            if old > 1e-4:
                before.append(old)
                a.data[vi].value = 0.0
                k += 1
        rec[an] = dict(cleared=k,
                       prev=[round(min(before), 4), round(float(np.median(before)), 4),
                             round(max(before), 4)] if before else None)
    cleared[n.split('_')[0]] = rec
    print('CLEARED', n.split('_')[0], rec, flush=True)
rep['cleared_edge_attrs'] = cleared

P['wz_obj'] = 1
prev_u = P.get('UNVERIFIED', '')
note = ('wz: 1.5 m south cover flap + 8 cm curtain at the y=320 WU/WF join '
        '(south-grazing views were looking into the unlit overlap slot)')
P['UNVERIFIED'] = ((prev_u + ' ') if prev_u else '') + note

# reseat grass onto the new top in the flap band
print('grass BVH...', flush=True)
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
BNEW = make_bvh(P)
# include WU/WT still, in case a point is just outside the flap

def top_new(x, y):
    zs = []
    z = hz(BNEW, x, y)
    if z is not None:
        zs.append(z)
    for b in (BU, BT):
        z = hz(b, x, y)
        if z is not None:
            zs.append(z)
    return max(zs) if zs else None

grass = {}
for name in ('QS_Richardson_lawn_grass_points_UNVERIFIED',
             'QV_Richardson_NW_lawn_grass_points_UNVERIFIED'):
    o = O.get(name)
    if not o:
        continue
    gme = o.data
    gmw = o.matrix_world
    gmi = gmw.inverted()
    k = 0
    mx = 0.0
    for v in gme.vertices:
        c = gmw @ v.co
        if not (X1 - 2 <= c.x <= X2 + 2 and (Y_LIP - FLAP - 0.8) <= c.y <= (Y_LIP + 1.5)):
            continue
        a0 = top_old(c.x, c.y)
        a1 = top_new(c.x, c.y)
        if a0 is None or a1 is None:
            continue
        d = a1 - a0
        if abs(d) < 0.001:
            continue
        c.z += d
        v.co = gmi @ c
        k += 1
        mx = max(mx, abs(d))
    gme.update()
    grass[name[:2]] = [k, round(mx, 4)]
    print('GRASS', name[:2], k, 'max', round(mx, 4), flush=True)
rep['grass'] = grass

rep['end_verts'] = len(me.vertices)
rep['end_faces'] = len(me.polygons)
print('END WF', rep['end_verts'], 'faces', rep['end_faces'], flush=True)

# quick overlap-height check: flap should sit 4–8 mm above WU along y=318.5
chk = []
for x in np.linspace(68, 110, 22):
    zf = hz(BNEW, float(x), Y_LIP - FLAP + 0.01)
    zs = south_z(float(x), Y_LIP - FLAP + 0.01)
    if zf is not None and zs is not None:
        chk.append(round(zf - zs, 4))
rep['flap_above_south_mm'] = ([round(min(chk) * 1000, 1),
                               round(float(np.median(chk)) * 1000, 1),
                               round(max(chk) * 1000, 1)] if chk else None)
print('FLAP above south sheet mm', rep['flap_above_south_mm'], 'n', len(chk), flush=True)

json.dump(rep, open('data/wz/fix_report.json', 'w'), indent=1)
print('WROTE data/wz/fix_report.json', flush=True)
if SAVE:
    bpy.ops.wm.save_mainfile(compress=True)
    print('SAVED', flush=True)
else:
    print('NO SAVE', flush=True)
