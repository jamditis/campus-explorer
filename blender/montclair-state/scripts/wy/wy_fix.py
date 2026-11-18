"""wy: fill the Reid Hall OSM-mask hole in WF_east_dorm_LiDAR_terrain_patch.

Session wf masked Irvin D. Reid Hall's footprint out of the east-dorm 1 m DTM
patch, leaving a 329-cell sliver at x69-109, y320-334 where the coarse 3DEP
skirt shows through. There is no Reid mesh in the scene (wu did not invent a
hole in Tile B). The 2017 DTM inside the sliver matches the surrounding lawn
(median delta about -1 cm), so fill it the same way wl filled the Webster
lawn hole. Also un-fade the WU north edge (wu_fix3) and any WT north-edge
dip that was blended toward this hole, reseat grass, and tuck the new ground
under overlapping walk slabs. Bohn, Blanton and the already-filled Webster
hole are left masked. No Reid building is added. No walls are moved.
"""
import bpy, bmesh, json, os, math
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from collections import deque

ROOT = '/workspace/nj-scenes/montclair-state'
os.chdir(ROOT)
SAVE = os.environ.get('SAVE') == '1'
PN = 'WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED'
WUN = 'WU_richardson_reid_LiDAR_patch_UNVERIFIED'
WTN = 'WT_richardson_west_LiDAR_patch_UNVERIFIED'
SKN = 'Context_skirt_3DEP_ortho_4km'
X0, Y0 = 50.0, 320.0
GX0, GY0 = 40, 140
rep = {}

O = bpy.data.objects
P = O[PN]
me = P.data
rep['start_verts'] = len(me.vertices)
rep['start_faces'] = len(me.polygons)
print('START WF', rep['start_verts'], 'faces', rep['start_faces'], flush=True)

M = np.load('data/wf/patch_mask.npz')
inside = M['inside_b']
D = np.load('data/wf/east_dorm_dtm_1m.npz')
filled = D['dtm_filled']
H, W = inside.shape

vis = np.zeros_like(inside, dtype=bool)
comps = []
for j in range(H):
    for i in range(W):
        if not inside[j, i] or vis[j, i]:
            continue
        q = deque([(j, i)]); vis[j, i] = True; cells = []
        while q:
            y, x = q.popleft(); cells.append((y, x))
            for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                yy, xx = y + dy, x + dx
                if 0 <= yy < H and 0 <= xx < W and inside[yy, xx] and not vis[yy, xx]:
                    vis[yy, xx] = True; q.append((yy, xx))
        ys = [c[0] for c in cells]; xs = [c[1] for c in cells]
        comps.append(dict(n=len(cells),
                          xmin=X0 + min(xs), xmax=X0 + max(xs),
                          ymin=Y0 + min(ys), ymax=Y0 + max(ys),
                          cells=cells))
reid = None
for c in comps:
    if c['ymin'] <= 322 and c['xmax'] < 120 and c['n'] < 800:
        reid = c; break
if reid is None:
    raise SystemExit('Reid component not found')
rep['reid'] = dict(n=reid['n'], xmin=reid['xmin'], xmax=reid['xmax'],
                   ymin=reid['ymin'], ymax=reid['ymax'])
print('REID', rep['reid'], flush=True)

def hcell(i, j):
    zs = []
    for jj in (j - 1, j):
        for ii in (i - 1, i):
            if 0 <= ii < W and 0 <= jj < H and np.isfinite(filled[jj, ii]):
                zs.append(filled[jj, ii])
    return float(np.mean(zs)) if zs else None

G = np.load('data/wo/chm_grid_sw_1m.npz')
kd = [f for f in G.files if f.endswith('dtm')][0]
L = G[kd].copy()
for _ in range(40):
    n = np.isnan(L)
    if not n.any():
        break
    Pgrid = np.pad(L, 1, constant_values=np.nan)
    nb = np.stack([Pgrid[0:-2, 1:-1], Pgrid[2:, 1:-1], Pgrid[1:-1, 0:-2], Pgrid[1:-1, 2:],
                   Pgrid[0:-2, 0:-2], Pgrid[2:, 2:], Pgrid[0:-2, 2:], Pgrid[2:, 0:-2]])
    with np.errstate(all='ignore'):
        m = np.nanmean(nb, axis=0)
    L[n] = m[n]

def dtm_xy(x, y):
    if y >= 320.0:
        return hcell(int(round(x - X0)), int(round(y - Y0)))
    i = int(round(x)) - GX0; j = int(round(y)) - GY0
    zs = [L[jj, ii] for jj in (j - 1, j) for ii in (i - 1, i)
          if 0 <= jj < L.shape[0] and 0 <= ii < L.shape[1] and np.isfinite(L[jj, ii])]
    return float(np.mean(zs)) if zs else None

# UV fit near the hole
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

# snapshot point attrs
old_attr = {}
anames = []
for a in me.attributes:
    if a.name.startswith('.') or a.name == 'position':
        continue
    if a.domain == 'POINT' and a.data_type in ('FLOAT', 'FLOAT_VECTOR'):
        anames.append((a.name, a.data_type))
for vi, v in enumerate(me.vertices):
    i = int(round(v.co.x - X0)); j = int(round(v.co.y - Y0))
    rec = {}
    for name, dt in anames:
        a = me.attributes[name]
        rec[name] = list(a.data[vi].vector) if dt == 'FLOAT_VECTOR' else float(a.data[vi].value)
    old_attr[(i, j)] = rec

# old BVHs for grass deltas
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
    h = b.ray_cast(Vector((x, y, 500)), Vector((0, 0, -1)))
    return None if h[0] is None else h[0].z

print('old BVHs...', flush=True)
BOLD = {n: make_bvh(O[n]) for n in (PN, WUN, WTN, SKN) if O.get(n)}
print('old BVHs ready', flush=True)

# --- edit WF ---
np.save('data/wy/WF_verts_pre_wy.npy', np.array([v.co[:] for v in me.vertices]))
bm = bmesh.new()
bm.from_mesh(me)
bm.verts.ensure_lookup_table()
keymap = {}
for v in bm.verts:
    i = int(round(v.co.x - X0)); j = int(round(v.co.y - Y0))
    keymap[(i, j)] = v

near_set = set()
for j, i in reid['cells']:
    for dj in range(-4, 5):
        for di in range(-4, 5):
            near_set.add((i + di, j + dj))

unfeathered = 0
unfeather_dz = []
for (i, j), v in keymap.items():
    if (i, j) not in near_set:
        continue
    z = hcell(i, j)
    if z is None:
        continue
    dz = z - v.co.z
    if abs(dz) > 0.002:
        v.co.z = z
        unfeathered += 1
        unfeather_dz.append(dz)
rep['wf_unfeathered'] = unfeathered
rep['wf_unfeather_dz'] = ([round(float(min(unfeather_dz)), 4),
                           round(float(np.median(unfeather_dz)), 4),
                           round(float(max(unfeather_dz)), 4)] if unfeather_dz else None)
print('WF UNFEATHER', unfeathered, 'dz', rep['wf_unfeather_dz'], flush=True)

new_vert_keys = []

def get_or_make(i, j):
    if (i, j) in keymap:
        return keymap[(i, j)]
    z = hcell(i, j)
    if z is None:
        z = 137.60
    v = bm.verts.new((X0 + i, Y0 + j, z))
    keymap[(i, j)] = v
    new_vert_keys.append((i, j))
    return v

new_faces = []
skipped = 0
for j, i in reid['cells']:
    try:
        f = bm.faces.new([get_or_make(i, j), get_or_make(i + 1, j),
                          get_or_make(i + 1, j + 1), get_or_make(i, j + 1)])
        f.smooth = True
        new_faces.append(f)
    except ValueError:
        skipped += 1
rep['faces_added'] = len(new_faces)
rep['faces_skipped'] = skipped
rep['verts_added'] = len(new_vert_keys)
print('ADDED faces', len(new_faces), 'verts', len(new_vert_keys), 'skipped', skipped, flush=True)

bm.faces.ensure_lookup_table()
flipped = 0
for f in new_faces:
    f.normal_update()
    if f.normal.z < 0:
        f.normal_flip(); flipped += 1
rep['faces_flipped'] = flipped

uv_layer = bm.loops.layers.uv.get('ortho')
if uv_layer is None:
    uv_layer = bm.loops.layers.uv.new('ortho')
for f in new_faces:
    for l in f.loops:
        l[uv_layer].uv = uv_at(l.vert.co.x, l.vert.co.y)

bm.to_mesh(me)
bm.free()
me.update()
print('MESH now', len(me.vertices), 'verts', len(me.polygons), 'faces', flush=True)
rep['end_verts'] = len(me.vertices)
rep['end_faces'] = len(me.polygons)

def nearest_old(i, j):
    for rad in range(0, 8):
        for dj in range(-rad, rad + 1):
            for di in range(-rad, rad + 1):
                rec = old_attr.get((i + di, j + dj))
                if rec:
                    return rec
    return None

filled_n = 0
for vi, v in enumerate(me.vertices):
    i = int(round(v.co.x - X0)); j = int(round(v.co.y - Y0))
    if (i, j) not in new_vert_keys:
        continue
    src = nearest_old(i, j) or {}
    for name, dt in anames:
        a = me.attributes.get(name)
        if a is None:
            continue
        if name == 'wh_edge':
            a.data[vi].value = 0.0
        elif name == 'wk_litter':
            a.data[vi].value = 0.0
        elif dt == 'FLOAT_VECTOR':
            a.data[vi].vector = src.get(name) or [0.0, 0.0, 1.0]
        else:
            a.data[vi].value = float(src.get(name, 0.0))
    filled_n += 1
rep['new_vert_attrs_filled'] = filled_n
print('ATTR fill', filled_n, 'anames', [n for n, _ in anames], flush=True)

prev_u = P.get('UNVERIFIED', '')
P['wy_obj'] = 1
P['UNVERIFIED'] = (
    'east-dorm 1m LiDAR DTM patch from 2017 B17 J5D6 class 2; feathered 4m into skirt; '
    'buildings masked except Webster Hall footprint (wl: filled — lawn per Joe) '
    'and Reid Hall south sliver (wy: filled — no Reid mesh in scene)'
)
rep['unverified_prev'] = prev_u

# --- unfade WU north edge (restore pre-wu_fix3 z in the hole x-range) ---
WU = O.get(WUN)
pre_path = 'data/wu/wu_patch_pre_fix3.npy'
rep['wu_unfade'] = None
if WU is not None and os.path.exists(pre_path):
    pre = np.load(pre_path)
    wme = WU.data
    if pre.shape[0] != len(wme.vertices):
        rep['wu_unfade'] = dict(error='vert count mismatch', npy=int(pre.shape[0]), live=len(wme.vertices))
        print('WU pre_fix3 mismatch', rep['wu_unfade'], flush=True)
    else:
        np.save('data/wy/WU_verts_pre_wy.npy', np.array([v.co[:] for v in wme.vertices]))
        xmin, xmax = reid['xmin'] - 2.0, reid['xmax'] + 2.0
        n = 0; dzs = []
        mw = WU.matrix_world
        for i, v in enumerate(wme.vertices):
            c = mw @ v.co
            if c.y < 311.5:
                continue
            if not (xmin <= c.x <= xmax):
                continue
            old = pre[i]
            if abs(old[0] - v.co.x) > 0.02 or abs(old[1] - v.co.y) > 0.02:
                continue
            dz = float(old[2] - v.co.z)
            if abs(dz) > 0.002:
                v.co.z = float(old[2])
                n += 1; dzs.append(dz)
        wme.update()
        rep['wu_unfade'] = dict(moved=n,
                                dz=[round(float(min(dzs)), 4), round(float(np.median(dzs)), 4),
                                    round(float(max(dzs)), 4)] if dzs else None)
        print('WU UNFADE', rep['wu_unfade'], flush=True)

# --- unfade WT north edge onto DTM where it dipped toward the hole ---
WT = O.get(WTN)
rep['wt_unfade'] = None
if WT is not None:
    wme = WT.data
    np.save('data/wy/WT_verts_pre_wy.npy', np.array([v.co[:] for v in wme.vertices]))
    xmin, xmax = reid['xmin'] - 2.0, min(reid['xmax'] + 2.0, 80.6)
    mw = WT.matrix_world; mi = mw.inverted()
    n = 0; dzs = []
    for v in wme.vertices:
        c = mw @ v.co
        if c.y < 311.5:
            continue
        if not (xmin <= c.x <= xmax):
            continue
        z = dtm_xy(c.x, c.y)
        if z is None:
            continue
        dz = z - c.z
        if abs(dz) > 0.002:
            c.z = z
            v.co = mi @ c
            n += 1; dzs.append(dz)
    wme.update()
    rep['wt_unfade'] = dict(moved=n,
                            dz=[round(float(min(dzs)), 4), round(float(np.median(dzs)), 4),
                                round(float(max(dzs)), 4)] if dzs else None)
    print('WT UNFADE', rep['wt_unfade'], flush=True)

# --- tuck new/raised ground under walk slabs (lower-only, cap 0.15 m) ---
SLABS = [n for n in (
    'QS_footway_313027435_UNVERIFIED', 'QT_soil_edge_313027435_UNVERIFIED',
    'QS_footway_313027436_UNVERIFIED', 'QT_soil_edge_313027436_UNVERIFIED',
    'QS_footway_313027437_UNVERIFIED', 'QT_soil_edge_313027437_UNVERIFIED',
    'QW_footway_313027436_ext_UNVERIFIED', 'QW_soil_edge_313027436_ext_UNVERIFIED',
) if O.get(n)]
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
SB = [make_bvh(O[n]) for n in SLABS]
print('SLABS', SLABS, flush=True)

def tuck(obj, tag):
    if obj is None or not SB:
        return dict(moved=0)
    wme = obj.data; mw = obj.matrix_world; mi = mw.inverted()
    xmin, xmax = reid['xmin'] - 3.0, reid['xmax'] + 3.0
    ymin, ymax = 310.0, reid['ymax'] + 2.0
    n = 0; mx = 0.0
    for v in wme.vertices:
        c = mw @ v.co
        if not (xmin <= c.x <= xmax and ymin <= c.y <= ymax):
            continue
        lo = None
        for dx, dy in ((0, 0), (0.5, 0), (-0.5, 0), (0, 0.5), (0, -0.5)):
            for b in SB:
                h = b.ray_cast(Vector((c.x + dx, c.y + dy, 500)), Vector((0, 0, -1)))[0]
                if h is not None and (lo is None or h.z < lo):
                    lo = h.z
        if lo is not None and c.z > lo - 0.03 and c.z - (lo - 0.03) <= 0.15:
            d = c.z - (lo - 0.03)
            c.z = lo - 0.03
            v.co = mi @ c
            n += 1; mx = max(mx, d)
    wme.update()
    rec = dict(moved=n, max=round(mx, 3))
    print('TUCK', tag, rec, flush=True)
    return rec

rep['tuck_wf'] = tuck(P, 'WF')
rep['tuck_wu'] = tuck(O.get(WUN), 'WU')
rep['tuck_wt'] = tuck(O.get(WTN), 'WT')

# --- grass reseat by old-top -> new-top delta ---
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
BNEW = {n: make_bvh(O[n]) for n in (PN, WUN, WTN, SKN) if O.get(n)}

def top_of(B, x, y, keys):
    best = None
    for k in keys:
        z = hz(B.get(k), x, y)
        if z is not None and (best is None or z > best):
            best = z
    return best

GBOX = (reid['xmin'] - 4.0, reid['xmax'] + 4.0, 308.0, reid['ymax'] + 3.0)
grass_rep = {}
for name in ('QS_Richardson_lawn_grass_points_UNVERIFIED',
             'QV_Richardson_NW_lawn_grass_points_UNVERIFIED'):
    o = O.get(name)
    if not o:
        continue
    gme = o.data; mw = o.matrix_world; mi = mw.inverted()
    np.save(f'data/wy/{name[:24]}_pre_wy.npy', np.array([v.co[:] for v in gme.vertices]))
    k = 0; mx = 0.0
    for v in gme.vertices:
        c = mw @ v.co
        if not (GBOX[0] <= c.x <= GBOX[1] and GBOX[2] <= c.y <= GBOX[3]):
            continue
        a0 = top_of(BOLD, c.x, c.y, (PN, WUN, WTN, SKN))
        a1 = top_of(BNEW, c.x, c.y, (PN, WUN, WTN))
        if a1 is None:
            a1 = top_of(BNEW, c.x, c.y, (SKN,))
        if a0 is None or a1 is None:
            continue
        d = a1 - a0
        if abs(d) < 0.002:
            continue
        c.z += d
        v.co = mi @ c
        k += 1; mx = max(mx, abs(d))
    gme.update()
    grass_rep[name[:2]] = [k, round(mx, 3)]
    print('GRASS', name[:2], k, round(mx, 3), flush=True)
rep['grass'] = grass_rep

# --- verify ---
bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get()
BVF = make_bvh(P)
checks = []
xs = np.linspace(reid['xmin'] + 1, reid['xmax'] - 1, 6)
ys = np.linspace(reid['ymin'] + 1, reid['ymax'] - 1, 5)
for y in ys:
    for x in xs:
        z = hz(BVF, x, y)
        zdt = dtm_xy(x, y)
        rec = dict(xy=[round(float(x), 1), round(float(y), 1)],
                   wf=None if z is None else round(z, 3),
                   dtm=None if zdt is None else round(zdt, 3),
                   dz=None if (z is None or zdt is None) else round(z - zdt, 3))
        checks.append(rec)
rep['verify_hole'] = checks
rep['verify_all_wf'] = all(c['wf'] is not None for c in checks)
dzs = [c['dz'] for c in checks if c['dz'] is not None]
rep['verify_dz_vs_dtm'] = ([round(float(min(dzs)), 3), round(float(np.median(dzs)), 3),
                            round(float(max(dzs)), 3)] if dzs else None)
print('VERIFY hole all_wf', rep['verify_all_wf'], 'dz', rep['verify_dz_vs_dtm'],
      'miss', sum(1 for c in checks if c['wf'] is None), flush=True)

# seam at y=320
BWU = make_bvh(O[WUN]) if O.get(WUN) else None
BWT = make_bvh(O[WTN]) if O.get(WTN) else None
seam = []
for x in range(int(reid['xmin']), int(reid['xmax']) + 1, 2):
    seam.append(dict(x=x,
                     wf=None if hz(BVF, x, 320.3) is None else round(hz(BVF, x, 320.3), 3),
                     wu=None if hz(BWU, x, 319.7) is None else round(hz(BWU, x, 319.7), 3),
                     wt=None if hz(BWT, x, 319.7) is None else round(hz(BWT, x, 319.7), 3),
                     dtm=None if dtm_xy(x, 320.0) is None else round(dtm_xy(x, 320.0), 3)))
rep['verify_seam'] = seam
print('SEAM mid', seam[len(seam)//2] if seam else None, flush=True)

rep['nobj'] = len(O)
json.dump(rep, open('data/wy/fix_report.json', 'w'), indent=1)
print('REP faces+', rep['faces_added'], 'verts+', rep['verts_added'],
      'wf_unfeather', unfeathered, 'nobj', rep['nobj'], flush=True)

if SAVE:
    bpy.ops.wm.save_mainfile(compress=True)
    print('SAVED', flush=True)
else:
    print('NO SAVE', flush=True)
