"""Build mesh data (terrain, buildings, paths, trees) in local meters from LiDAR + OSM. Output: data/geom.npz + data/geom_meta.json"""
import json, numpy as np, warnings
from scipy import ndimage
from scipy.spatial import Delaunay
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import unary_union
from shapely import contains_xy
warnings.filterwarnings('ignore')
d = json.load(open('data/scene_data.json')); H = d['half_m']
P = np.load('data/pts_crop.npz'); X, Y, Z, C = P['x'], P['y'], P['z'], P['c']
dtm = np.load('data/dtm_1m.npy').astype(np.float64)
def fill(g, it=400):
    g = g.copy()
    for _ in range(it):
        n = np.isnan(g)
        if not n.any(): break
        p = np.pad(g, 1, constant_values=np.nan)
        nb = np.stack([p[:-2,1:-1], p[2:,1:-1], p[1:-1,:-2], p[1:-1,2:]])
        g[n] = np.nanmean(nb, axis=0)[n]
    return g
def mkgrid(sel, res):
    n = int(2*H/res); g = np.full((n, n), np.nan)
    ix = np.clip(((X[sel]+H)/res).astype(int), 0, n-1); iy = np.clip(((Y[sel]+H)/res).astype(int), 0, n-1)
    np.fmax.at(g, (iy, ix), Z[sel].astype(np.float64)); return g
RES = 0.5
dsm = fill(mkgrid(~np.isin(C, [7, 18]), RES))
g6 = mkgrid(C == 6, RES); g1 = mkgrid(C == 1, RES); gg = mkgrid(C == 2, RES)
g6l = ndimage.maximum_filter(np.nan_to_num(g6, nan=-1e9), 9)  # local building max (4.5 m window)
g1ok = np.where(np.isnan(g6) & (g1 <= g6l + 0.8) & (g6l > -1e8), g1, np.nan)  # unclassified points not above nearby roof
roofg = np.where(~np.isnan(g6), g6, g1ok)
roofg = np.where(np.isnan(roofg), gg, roofg)
roofg = fill(roofg)
dsm_m = ndimage.median_filter(roofg, 3)
dsm_s = ndimage.gaussian_filter(ndimage.median_filter(roofg, 5), 1.4)
zm = lambda x, y: samp(dsm_m, RES, x, y)
from PIL import Image
ORT = np.asarray(Image.open('data/ortho2020.png').convert('RGB')).astype(np.float32)/255
ORTb = ndimage.uniform_filter(ORT, size=(7, 7, 1))
def ortho(x, y, blur=True):
    o = ORTb if blur else ORT; n = o.shape[0]
    px = np.clip(((np.asarray(x)+H)/(2*H)*n).astype(int), 0, n-1); py = np.clip(((H-np.asarray(y))/(2*H)*n).astype(int), 0, n-1)
    return o[py, px]
def samp(g, res, x, y):
    n = g.shape[0]; fx = np.clip((np.asarray(x)+H)/res-0.5, 0, n-1.001); fy = np.clip((np.asarray(y)+H)/res-0.5, 0, n-1.001)
    i, j = fy.astype(int), fx.astype(int); a, b = fy-i, fx-j
    return g[i,j]*(1-a)*(1-b)+g[i,j+1]*(1-a)*b+g[i+1,j]*a*(1-b)+g[i+1,j+1]*a*b
zg = lambda x, y: samp(dtm, 1.0, x, y)
zs = lambda x, y: samp(dsm_s, RES, x, y)
out = {}; meta = {'buildings': [], 'paths': [], 'E0_ftUS': d['E0_ftUS'], 'N0_ftUS': d['N0_ftUS'], 'half_m': H}
# terrain 1 m grid (vertex at cell centres)
n = dtm.shape[0]; xs = -H + 0.5 + np.arange(n)
out['terrain_z'] = dtm.astype(np.float32)
TARGET = {'1188721159': 'School of Communication and Media', '312933183': 'Morehead Hall', '313021866': 'Life Hall'}
def densify(coords, step):
    pts = []
    for a, b in zip(coords[:-1], coords[1:]):
        L = np.hypot(b[0]-a[0], b[1]-a[1]); k = max(1, int(np.ceil(L/step)))
        for t in range(k): pts.append((a[0]+(b[0]-a[0])*t/k, a[1]+(b[1]-a[1])*t/k))
    return np.array(pts)
def tri_poly(poly, step, grid_step):
    """Delaunay over densified boundary + interior grid; keep triangles inside polygon."""
    bnd = densify(list(poly.exterior.coords), step)
    holes = [densify(list(h.coords), step) for h in poly.interiors]
    minx, miny, maxx, maxy = poly.bounds
    gx, gy = np.meshgrid(np.arange(minx, maxx, grid_step), np.arange(miny, maxy, grid_step))
    gx, gy = gx.ravel(), gy.ravel()
    inner = poly.buffer(-grid_step*0.4)
    keep = contains_xy(inner, gx, gy) if not inner.is_empty else np.zeros(len(gx), bool)
    pts = np.vstack([bnd] + holes + [np.c_[gx[keep], gy[keep]]])
    t = Delaunay(pts).simplices
    cen = pts[t].mean(axis=1)
    t = t[contains_xy(poly.buffer(0.01), cen[:,0], cen[:,1])]
    return pts, t, len(bnd)
bverts, btris, bmat, wverts, wuv, wbid = [], [], [], [], [], []
bid = 0; footprints = []; bcols = []; hip_info = {}; bflags = []
for f in d['features']:
    t = f['tags']
    if 'building' not in t or not f['closed'] or len(f['pts']) < 4: continue
    poly = Polygon(f['pts']).buffer(0)
    if poly.geom_type != 'Polygon' or poly.area < 15: continue
    c = poly.centroid
    if abs(c.x) > H-15 or abs(c.y) > H-15: continue
    footprints.append(poly)
    tgt = f['id'] in TARGET
    poly = poly.simplify(0.15)
    pts, tri, nb = tri_poly(poly, 0.7 if tgt else 1.5, 0.5 if tgt else 1.0)
    # roof heights: interior from smoothed DSM; boundary sampled ~0.7 m inside
    z = zs(pts[:,0], pts[:,1])
    inner = poly.buffer(-0.7)
    if not inner.is_empty:
        ib = inner.exterior if inner.geom_type == 'Polygon' else max(inner.geoms, key=lambda g: g.area).exterior
        for k in range(nb):
            q = ib.interpolate(ib.project(Point(pts[k]))); z[k] = zs(q.x, q.y)
    gmin = float(np.min(zg(pts[:nb,0], pts[:nb,1])))
    # boundary: running median along the ring (~10 m) to remove LiDAR edge waviness
    zb = z[:nb].copy(); w_ = 7
    ext = np.r_[zb[-w_:], zb, zb[:w_]]
    z[:nb] = np.array([np.median(ext[k:k+2*w_+1]) for k in range(nb)])
    # snap near-flat roof levels to histogram peaks (crisp flat roofs / parapets)
    zr_ = zm(pts[nb:,0], pts[nb:,1]) if len(pts) > nb else np.array([])
    allz = np.r_[z[:nb], zr_]
    hist, edges = np.histogram(allz, bins=np.arange(allz.min()-0.5, allz.max()+0.75, 0.25))
    pk = [0.5*(edges[i]+edges[i+1]) for i in range(1, len(hist)-1) if hist[i] >= max(hist[i-1], hist[i+1]) and hist[i] > 0.04*len(allz)]
    if pk:
        pk = np.array(pk)
        for arr_idx, arr in ((slice(None, nb), z[:nb]), (slice(nb, None), zr_)):
            if len(arr) == 0: continue
            dd = np.abs(arr[:, None] - pk[None, :]); j = dd.argmin(1); near = dd[np.arange(len(arr)), j] < (0.6 if arr_idx.stop == nb else 0.35)
            arr = np.where(near, pk[j], z[arr_idx]); z[arr_idx] = arr
    z = np.maximum(z, gmin + 2.8)
    st = d['bstats'].get(f['id'], {})
    oc = ortho(pts[:,0], pts[:,1])
    red = np.clip(((oc[:,0] - oc[:,2]) - 0.10) / 0.08, 0, 1) * (oc[:,0] > oc[:,1])
    tile_b = float(red[:nb].mean())
    # hip-roof regularization: pitched tile areas follow z = eave + slope * distance-to-edge (clean hips/ridges),
    # capped by the LiDAR surface so flat centres stay flat
    import shapely
    dist = shapely.distance(poly.exterior, shapely.points(pts[:,0], pts[:,1]))
    redb = red[:nb] > 0.5
    if redb.sum() > 8:
        eave = float(np.median(z[:nb][redb]))
        selp = (red > 0.5) & (dist > 0.8) & (dist < 6) & (z > eave + 0.2)
        slope = float(np.clip(np.median((z[selp] - eave) / dist[selp]), 0.3, 0.75)) if selp.sum() > 20 else 0.45
        zhip = eave + slope * dist
        from scipy.spatial import cKDTree
        kd = cKDTree(pts); nbrs = kd.query_ball_point(pts, 2.5)
        reds = np.array([red[n_].mean() for n_ in nbrs])
        tilev = (reds > 0.2) | (tile_b > 0.3)
        tilev = ndimage.binary_closing(tilev) if False else tilev
        z = np.where(tilev, np.minimum(zhip, z + 0.25), z)
        z[:nb] = np.where(redb, eave, z[:nb])
        hip_info[f['id']] = (eave - gmin, slope)
    # eaves: for tile roofs push a skirt 0.55 m out and 0.35 m down from boundary ring
    eave = []
    rr = np.convolve(np.r_[red[:nb][-3:], red[:nb], red[:nb][:3]], np.ones(7)/7, 'valid')
    rr = np.clip((rr - 0.15)/0.3, 0, 1)
    if True:
        ringp = pts[:nb]; sgn = 1 if Polygon(ringp).exterior.is_ccw else -1
        for k in range(nb):
            a, b_, c_ = ringp[k-1], ringp[k], ringp[(k+1) % nb]
            e1 = (b_-a)/max(np.linalg.norm(b_-a), 1e-6); e2 = (c_-b_)/max(np.linalg.norm(c_-b_), 1e-6)
            n1 = np.array([e1[1], -e1[0]])*sgn; n2 = np.array([e2[1], -e2[0]])*sgn
            nv = n1+n2; nv = nv/max(np.linalg.norm(nv), 1e-6)
            eave.append([*(b_ + nv*(0.05 + 0.85*rr[k])), z[k]-0.05-0.32*rr[k]])
    base = sum(len(v) for v in bverts)
    allv = np.c_[pts, z]; cols = np.c_[oc, red]
    if eave:
        ev = np.array(eave); ne = len(ev); i0 = len(allv)
        q = [[k, (k+1) % nb, i0+(k+1) % nb, i0+k] for k in range(nb)]
        qt = np.array([[a, b_, c_] for a, b_, c_, d_ in q] + [[a, c_, d_] for a, b_, c_, d_ in q])
        ev2 = ev.copy(); ev2[:, 2] -= 0.32 * rr[:nb]; i1 = i0 + ne
        q2 = [[i0+k, i0+(k+1) % nb, i1+(k+1) % nb, i1+k] for k in range(nb)]
        qt2 = np.array([[a, b_, c_] for a, b_, c_, d_ in q2] + [[a, c_, d_] for a, b_, c_, d_ in q2])
        tflag = np.r_[np.zeros(len(tri), np.int8), np.ones(len(qt), np.int8), np.full(len(qt2), 2, np.int8)]
        allv = np.vstack([allv, ev, ev2]); cols = np.vstack([cols, cols[:nb], cols[:nb]]); tri = np.vstack([tri, qt, qt2])
    if not eave: tflag = np.zeros(len(tri), np.int8)
    bflags.append(tflag)
    bverts.append(allv); btris.append(tri + base); bcols.append(cols)
    # walls along boundary ring (first nb pts are exterior ring in order)
    ring = pts[:nb]; zr = z[:nb]; gb = zg(ring[:,0], ring[:,1]) - 0.6
    wg = 8; gext = np.r_[gb[-wg:], gb, gb[:wg]]; gref = np.array([np.median(gext[k:k+2*wg+1]) for k in range(nb)]) + 0.6
    u = 0.0
    for k in range(nb):
        k2 = (k+1) % nb; L = float(np.hypot(*(ring[k2]-ring[k])))
        wverts.append([[*ring[k], gb[k]], [*ring[k2], gb[k2]], [*ring[k2], zr[k2]], [*ring[k], zr[k]]])
        wuv.append([[u, gb[k]-gref[k]], [u+L, gb[k2]-gref[k2]], [u+L, zr[k2]-gref[k2]], [u, zr[k]-gref[k]]])
        wbid.append(bid); u += L
    lv = t.get('building:levels')
    meta['buildings'].append({'bid': bid, 'osm_id': f['id'], 'name': t.get('name') or TARGET.get(f['id']), 'target': tgt, 'ground_min': gmin,
        'roof_p50': st.get('roof_p50'), 'roof_max': st.get('roof_max'), 'height_p50_m': (st.get('roof_p50', gmin) - st.get('ground_p10', gmin)) if st else None,
        'osm_levels': lv, 'tile_frac': tile_b, 'nverts': int(len(pts)), 'area_m2': float(poly.area)})
    bid += 1
# ---- day 2: CCOM tall section as a crisp prism (LiDAR cells > 18 m above low grade inside the CCOM footprint)
from shapely.geometry import box as _box
tall_parts = []
for f in d['features']:
    if f['id'] != '1188721159': continue
    poly = Polygon(f['pts']).buffer(0)
    gmin_c = float(np.min(zg(*np.array(poly.exterior.coords).T)))
    n_ = dsm_m.shape[0]; xs5 = -H + RES*(np.arange(n_) + 0.5)
    minx, miny, maxx, maxy = poly.bounds
    ix0, ix1 = int((minx+H)/RES), int((maxx+H)/RES)+1; iy0, iy1 = int((miny+H)/RES), int((maxy+H)/RES)+1
    sub = dsm_m[iy0:iy1, ix0:ix1]
    m_ = sub > gmin_c + 18.0
    m_ = ndimage.binary_opening(m_, iterations=2)
    lab, nl = ndimage.label(m_)
    for li in range(1, nl+1):
        cells = np.argwhere(lab == li)
        if len(cells) < 40: continue
        geoms = [_box(xs5[ix0+j]-RES/2, xs5[iy0+i]-RES/2, xs5[ix0+j]+RES/2, xs5[iy0+i]+RES/2) for i, j in cells]
        g = unary_union(geoms).intersection(poly)
        rect = g.minimum_rotated_rectangle
        if rect.area > 1.6 * g.area: rect = g.simplify(0.8)
        top = float(np.percentile(sub[lab == li], 75))
        tall_parts.append({'coords': list(rect.exterior.coords)[:-1], 'top': top, 'area': float(g.area), 'gmin': gmin_c})
        print('CCOM tall part', round(g.area, 1), 'm2 top', round(top - gmin_c, 1), 'm above low grade')
meta['tall_parts'] = tall_parts
# ---- day 2: Morehead west entrance frame (midpoint of the longest west-facing wall edge)
for f in d['features']:
    if f['id'] != '312933183': continue
    poly = Polygon(f['pts']).buffer(0).simplify(0.3)
    cc = np.array(poly.exterior.coords); sgn = 1 if poly.exterior.is_ccw else -1
    best = None
    for a, b_ in zip(cc[:-1], cc[1:]):
        e = b_ - a; L = np.linalg.norm(e); t = e / L; nrm = np.array([t[1], -t[0]]) * sgn
        if nrm[0] < -0.7 and (best is None or L > best[0]): best = (L, (a + b_) / 2, t, nrm)
    L, mid, t, nrm = best
    eave_rel = hip_info.get('312933183', (9.7, 0.5))[0]
    gm = float(np.min(zg(*cc.T)))
    meta['morehead_entrance'] = {'center': mid.tolist(), 't': t.tolist(), 'n': nrm.tolist(), 'ground': float(zg(mid[0]+nrm[0]*2, mid[1]+nrm[1]*2)),
                                 'eave': gm + eave_rel, 'wall_len': float(L)}
    print('Morehead entrance', meta['morehead_entrance'])
roofv = np.vstack(bverts); rbid = np.concatenate([np.full(len(v), i) for i, v in enumerate(bverts)])
out.update(roof_tflag=np.concatenate(bflags), roof_col=np.vstack(bcols).astype(np.float32), roof_v=roofv.astype(np.float32), roof_t=np.vstack(btris).astype(np.int32), roof_bid=rbid.astype(np.int32),
           wall_v=np.array(wverts, np.float32), wall_uv=np.array(wuv, np.float32), wall_bid=np.array(wbid, np.int32))
# paths / roads as draped polygons
WID = {'footway': 3.0, 'path': 2.5, 'pedestrian': 6.0, 'service': 5.5, 'residential': 8.0, 'tertiary': 10.0, 'secondary': 11.0,
       'primary': 12.0, 'steps': 3.0, 'cycleway': 2.5, 'unclassified': 7.0, 'living_street': 6.0, 'track': 3.0}
groups = {'paving': [], 'asphalt': []}
for f in d['features']:
    t = f['tags']; hw = t.get('highway') or (t.get('area:highway') and 'area')
    if not hw: continue
    if f['closed'] and (t.get('area') == 'yes' or 'area:highway' in t):
        g = Polygon(f['pts']).buffer(0)
    elif hw in WID:
        w = WID[hw]
        if t.get('width'):
            try: w = float(t['width'].split()[0])
            except: pass
        g = LineString(f['pts']).buffer(w/2, cap_style='flat', join_style='round', quad_segs=3)
    else: continue
    asph = hw in ('service', 'residential', 'tertiary', 'secondary', 'primary', 'unclassified', 'living_street') or t.get('surface') == 'asphalt'
    groups['asphalt' if asph else 'paving'].append(g)
foot_u = unary_union(footprints).buffer(0.2)
clip = Polygon([(-H+1, -H+1), (H-1, -H+1), (H-1, H-1), (-H+1, H-1)])
for name, gs in groups.items():
    u_ = unary_union(gs).intersection(clip).difference(foot_u)
    geoms = [u_] if u_.geom_type == 'Polygon' else list(getattr(u_, 'geoms', []))
    V, T = [], []; off = 0
    for g in geoms:
        if g.geom_type != 'Polygon' or g.area < 1: continue
        pts, tri, _ = tri_poly(g, 1.5, 2.0)
        z = zg(pts[:,0], pts[:,1]) + (0.06 if name == 'paving' else 0.04)
        V.append(np.c_[pts, z]); T.append(tri+off); off += len(pts)
    out[f'{name}_v'] = np.vstack(V).astype(np.float32); out[f'{name}_t'] = np.vstack(T).astype(np.int32)
    print(name, len(out[f'{name}_v']), 'verts')
# trees from canopy height model
chm = ndimage.zoom(dsm, 0.5, order=1) if False else None
dsm1 = fill(mkgrid(np.isin(C, [1, 5, 4, 3]), 1.0))
chm = ndimage.gaussian_filter(dsm1 - dtm, 1.0)
gx, gy = np.meshgrid(xs, xs)
bmask = contains_xy(unary_union(footprints).buffer(2.0), gx.ravel(), gy.ravel()).reshape(gx.shape)
pm = contains_xy(unary_union(groups['asphalt']).buffer(0.5), gx.ravel(), gy.ravel()).reshape(gx.shape) if groups['asphalt'] else np.zeros_like(bmask)
mx = ndimage.maximum_filter(chm, 7)
tp = (chm == mx) & (chm > 4.5) & ~bmask & ~pm
ty, tx = np.nonzero(tp)
th = chm[ty, tx]
out['trees'] = np.c_[xs[tx], xs[ty], dtm[ty, tx], th].astype(np.float32)
print('trees', len(th))
np.savez_compressed('data/geom.npz', **out)
meta['hip_info'] = hip_info
json.dump(meta, open('data/geom_meta.json', 'w'), indent=1)
print('hip', {k: (round(a,1), round(b,2)) for k,(a,b) in hip_info.items()})
for b in meta['buildings']:
    if b['target']: print(b)
print('buildings', len(meta['buildings']), 'roof verts', len(roofv), 'walls', len(wverts))
