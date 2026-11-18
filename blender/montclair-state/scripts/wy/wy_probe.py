"""wy: read-only probe of the WF Reid-footprint hole (x~69-109, y320-334)
and the WU/WT north fade into that hole. No save."""
import bpy, json, os, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from collections import deque

R = '/workspace/nj-scenes/montclair-state'
os.chdir(R)
O = bpy.data.objects
PN = 'WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED'
X0, Y0 = 50.0, 320.0
rep = {}

M = np.load('data/wf/patch_mask.npz')
inside = M['inside_b'].astype(bool)
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
comps.sort(key=lambda c: -c['n'])
rep['inside_components'] = [dict(n=c['n'], xmin=c['xmin'], xmax=c['xmax'],
                                 ymin=c['ymin'], ymax=c['ymax']) for c in comps]
reid = None
for c in comps:
    if c['ymin'] <= 322 and c['xmax'] < 120 and c['n'] < 800:
        reid = c; break
if reid is None:
    raise SystemExit('Reid component not found')
rep['reid'] = dict(n=reid['n'], xmin=reid['xmin'], xmax=reid['xmax'],
                   ymin=reid['ymin'], ymax=reid['ymax'])
print('REID', rep['reid'], flush=True)

def hcell(i, j, grid=filled, x0=X0, y0=Y0):
    zs = []
    ny, nx = grid.shape
    for jj in (j - 1, j):
        for ii in (i - 1, i):
            if 0 <= ii < nx and 0 <= jj < ny and np.isfinite(grid[jj, ii]):
                zs.append(grid[jj, ii])
    return float(np.mean(zs)) if zs else None

G = np.load('data/wo/chm_grid_sw_1m.npz')
kd = [f for f in G.files if f.endswith('dtm')][0]
L = G[kd].copy()
GX0, GY0 = 40, 140
for _ in range(40):
    n = np.isnan(L)
    if not n.any():
        break
    P = np.pad(L, 1, constant_values=np.nan)
    nb = np.stack([P[0:-2, 1:-1], P[2:, 1:-1], P[1:-1, 0:-2], P[1:-1, 2:],
                   P[0:-2, 0:-2], P[2:, 2:], P[0:-2, 2:], P[2:, 0:-2]])
    with np.errstate(all='ignore'):
        m = np.nanmean(nb, axis=0)
    L[n] = m[n]

def dtm(x, y):
    if y >= 320:
        return hcell(int(round(x - X0)), int(round(y - Y0)))
    i = int(round(x)) - GX0; j = int(round(y)) - GY0
    zs = [L[jj, ii] for jj in (j - 1, j) for ii in (i - 1, i)
          if 0 <= jj < L.shape[0] and 0 <= ii < L.shape[1] and np.isfinite(L[jj, ii])]
    return float(np.mean(zs)) if zs else None

names = {
    'WF': PN,
    'WU': 'WU_richardson_reid_LiDAR_patch_UNVERIFIED',
    'WT': 'WT_richardson_west_LiDAR_patch_UNVERIFIED',
    'SK': 'Context_skirt_3DEP_ortho_4km',
    'QW': 'QW_DTM_north_edge_ramp_UNVERIFIED',
}
dg = bpy.context.evaluated_depsgraph_get()

def bvh(o):
    e = o.evaluated_get(dg)
    m = e.to_mesh()
    b = BVHTree.FromPolygons([o.matrix_world @ v.co for v in m.vertices],
                             [tuple(p.vertices) for p in m.polygons])
    e.to_mesh_clear()
    return b

print('building BVHs...', flush=True)
BV = {k: bvh(O[n]) for k, n in names.items() if O.get(n)}
print('BVHs ready', list(BV), flush=True)

def hz(key, x, y):
    b = BV.get(key)
    if b is None:
        return None
    h = b.ray_cast(Vector((x, y, 500)), Vector((0, 0, -1)))
    return None if h[0] is None else h[0].z

def top(x, y):
    best = None; who = None
    for k in BV:
        z = hz(k, x, y)
        if z is not None and (best is None or z > best):
            best = z; who = k
    return who, best

# sample hole cells (every other cell)
hole_hits = {'none_wf': 0, 'has_wf': 0}
who_counts = {}
dz_dtm = []
samples = []
for j, i in reid['cells'][::2]:
    x, y = X0 + i + 0.5, Y0 + j + 0.5
    zf = hz('WF', x, y)
    who, zt = top(x, y)
    zdt = dtm(x, y)
    who_counts[who] = who_counts.get(who, 0) + 1
    if zf is None:
        hole_hits['none_wf'] += 1
    else:
        hole_hits['has_wf'] += 1
    rec = dict(xy=[round(x, 1), round(y, 1)], who=who,
               z=None if zt is None else round(zt, 3),
               dtm=None if zdt is None else round(zdt, 3),
               dz=None if (zt is None or zdt is None) else round(zt - zdt, 3))
    if rec['dz'] is not None:
        dz_dtm.append(rec['dz'])
    samples.append(rec)
rep['hole_hits'] = hole_hits
rep['hole_who'] = who_counts
if dz_dtm:
    a = np.array(dz_dtm)
    rep['hole_top_minus_dtm'] = dict(n=len(a), med=round(float(np.median(a)), 3),
                                     p5=round(float(np.percentile(a, 5)), 3),
                                     p95=round(float(np.percentile(a, 95)), 3),
                                     mn=round(float(a.min()), 3), mx=round(float(a.max()), 3))
rep['hole_samples_every_other'] = samples[::8]
print('HOLE', hole_hits, who_counts, rep.get('hole_top_minus_dtm'), flush=True)

# WF lip just outside the hole
cellset = set(map(tuple, reid['cells']))
lip = []
seen = set()
for j, i in reid['cells']:
    for dj, di in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        ii, jj = i + di, j + dj
        if (jj, ii) in cellset or (ii, jj) in seen:
            continue
        if not (0 <= jj < H and 0 <= ii < W):
            continue
        seen.add((ii, jj))
        x, y = X0 + ii, Y0 + jj
        zf = hz('WF', x, y); zdt = dtm(x, y)
        if zf is not None and zdt is not None:
            lip.append(zf - zdt)
rep['wf_lip_minus_dtm'] = None
if lip:
    a = np.array(lip)
    rep['wf_lip_minus_dtm'] = dict(n=len(a), med=round(float(np.median(a)), 3),
                                   mn=round(float(a.min()), 3), mx=round(float(a.max()), 3))
print('WF LIP vs DTM', rep['wf_lip_minus_dtm'], flush=True)

# WU / WT fade bands
def band_stats(key, xs, ys):
    rows = []
    dzs = []
    for y in ys:
        for x in xs:
            z = hz(key, x, y); zdt = dtm(x, y); zs = hz('SK', x, y)
            rec = dict(x=x, y=y,
                       z=None if z is None else round(z, 3),
                       dtm=None if zdt is None else round(zdt, 3),
                       sk=None if zs is None else round(zs, 3))
            if z is not None and zdt is not None:
                rec['dz'] = round(z - zdt, 3); dzs.append(z - zdt)
            rows.append(rec)
    out = {'rows': rows}
    if dzs:
        a = np.array(dzs)
        out['vs_dtm'] = dict(n=len(a), med=round(float(np.median(a)), 3),
                             mn=round(float(a.min()), 3), mx=round(float(a.max()), 3))
    return out

rep['wu_band'] = band_stats('WU', list(range(80, 111, 2)), [312, 314, 316, 318, 320])
rep['wt_band'] = band_stats('WT', list(range(68, 81, 2)), [312, 314, 316, 318, 320])
print('WU vs DTM', rep['wu_band'].get('vs_dtm'), flush=True)
print('WT vs DTM', rep['wt_band'].get('vs_dtm'), flush=True)

# y=320 seam
seam = []
for x in range(68, 112, 2):
    seam.append(dict(x=x,
                     wf=None if hz('WF', x, 320.4) is None else round(hz('WF', x, 320.4), 3),
                     wu=None if hz('WU', x, 319.6) is None else round(hz('WU', x, 319.6), 3),
                     wt=None if hz('WT', x, 319.6) is None else round(hz('WT', x, 319.6), 3),
                     sk=None if hz('SK', x, 320.2) is None else round(hz('SK', x, 320.2), 3),
                     dtm=None if dtm(x, 320.0) is None else round(dtm(x, 320.0), 3)))
rep['seam_y320'] = seam
print('SEAM sample', seam[0], seam[len(seam)//2], seam[-1], flush=True)

# overlapping objects (bbox)
box = (reid['xmin'] - 2, reid['xmax'] + 2, reid['ymin'] - 10, reid['ymax'] + 2)
olap = []
for o in O:
    if o.type not in ('MESH', 'CURVE'):
        continue
    if o.hide_get() and o.hide_render:
        continue
    bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
    xs = [p.x for p in bb]; ys = [p.y for p in bb]
    if max(xs) < box[0] or min(xs) > box[1] or max(ys) < box[2] or min(ys) > box[3]:
        continue
    olap.append(dict(name=o.name, nverts=len(o.data.vertices) if o.type == 'MESH' else 0,
                     xmin=round(min(xs), 1), xmax=round(max(xs), 1),
                     ymin=round(min(ys), 1), ymax=round(max(ys), 1)))
olap.sort(key=lambda r: r['name'])
rep['overlap_box'] = olap
print('OVERLAP', len(olap), [r['name'] for r in olap if any(k in r['name'].lower() for k in
      ('walk', 'foot', 'grass', 'apron', 'reid', 'hall', 'road', 'service', 'soil', 'plinth'))], flush=True)

# WU pre_fix3 vert count
pre_path = 'data/wu/wu_patch_pre_fix3.npy'
wu = O.get(names['WU'])
if wu and os.path.exists(pre_path):
    pre = np.load(pre_path)
    rep['wu_pre_fix3'] = dict(npy=list(pre.shape), live=len(wu.data.vertices),
                              match=pre.shape[0] == len(wu.data.vertices))
    print('WU pre_fix3', rep['wu_pre_fix3'], flush=True)

# WF current size / attrs
P = O[PN]
rep['wf'] = dict(nverts=len(P.data.vertices), nfaces=len(P.data.polygons),
                 attrs=[(a.name, a.domain, a.data_type) for a in P.data.attributes],
                 unverified=P.get('UNVERIFIED'))
rep['nobj'] = len(O)
print('WF', rep['wf']['nverts'], 'faces', rep['wf']['nfaces'], 'nobj', rep['nobj'], flush=True)

json.dump(rep, open('data/wy/probe.json', 'w'), indent=1)
print('WROTE data/wy/probe.json', flush=True)
