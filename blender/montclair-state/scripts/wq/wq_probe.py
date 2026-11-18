"""wq probe (numpy): Priority A east column vs Priority B south woodland.
No Blender — uses wo CHM/DTM grid, wo coverage, td east OSM.
"""
import json
import numpy as np
from collections import Counter

ROOT = '/workspace/nj-scenes/montclair-state'
g = np.load(f'{ROOT}/data/wo/chm_grid_sw_1m.npz')
DTM = g['USGS_LPC_NJ_NW_New_Jersey_6_County_Lidar_2017_B17_J5D6.laz__dtm']
DSM = g['USGS_LPC_NJ_NW_New_Jersey_6_County_Lidar_2017_B17_J5D6.laz__dsm']
CHM = np.where(np.isfinite(DTM) & np.isfinite(DSM), DSM - DTM, np.nan)
c = np.load(f'{ROOT}/data/wo/coverage.npz')
cov, skz, names = c['cov'], c['skz'], list(c['names'])
d = json.load(open(f'{ROOT}/data/td/east_osm.json'))
GX0, GX1, GY0, GY1, RES = g['extent']
ny, nx = DTM.shape
xs = GX0 + np.arange(nx) + 0.5
ys = GY0 + np.arange(ny) + 0.5
XX, YY = np.meshgrid(xs, ys)


def pip_mask(pts, xs, ys):
    poly = np.array(pts, dtype=float)
    if len(poly) > 1 and np.allclose(poly[0], poly[-1]):
        poly = poly[:-1]
    n = len(poly)
    ny, nx = len(ys), len(xs)
    px, py = poly[:, 0], poly[:, 1]
    xmin, xmax, ymin, ymax = px.min(), px.max(), py.min(), py.max()
    mask = np.zeros((ny, nx), dtype=bool)
    for j, y in enumerate(ys):
        if y < ymin or y > ymax:
            continue
        xints = []
        for i in range(n):
            x1, y1 = poly[i]
            x2, y2 = poly[(i + 1) % n]
            if (y1 > y) != (y2 > y):
                xints.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1 + 1e-30))
        xints.sort()
        row = xs
        inside = np.zeros(nx, dtype=bool)
        for a, b in zip(xints[0::2], xints[1::2]):
            inside |= (row >= a) & (row <= b)
        mask[j] = inside
    return mask


def line_dist(pts, xs, ys):
    poly = np.array(pts, dtype=float)
    XX, YY = np.meshgrid(xs, ys)
    mind = np.full(XX.shape, 1e9)
    for i in range(len(poly) - 1):
        ax, ay = poly[i]
        bx, by = poly[i + 1]
        dx, dy = bx - ax, by - ay
        den = dx * dx + dy * dy
        if den < 1e-12:
            dist = np.hypot(XX - ax, YY - ay)
        else:
            t = np.clip(((XX - ax) * dx + (YY - ay) * dy) / den, 0, 1)
            dist = np.hypot(XX - ax - t * dx, YY - ay - t * dy)
        mind = np.minimum(mind, dist)
    return mind


wood = pip_mask(d['ways']['315835594']['pts'], xs, ys)
bldg = np.zeros_like(wood)
for wid in ['232853538', '313027426', '313027434', '313028565', '313029100', '313029108']:
    bldg |= pip_mask(d['ways'][wid]['pts'], xs, ys)
road_d = np.full(wood.shape, 1e9)
walk_d = np.full(wood.shape, 1e9)
for wid, w in d['ways'].items():
    hw = w['tags'].get('highway')
    if hw in ('service', 'secondary', 'residential', 'tertiary', 'unclassified'):
        road_d = np.minimum(road_d, line_dist(w['pts'], xs, ys))
    elif hw in ('footway', 'path', 'steps', 'cycleway', 'pedestrian'):
        walk_d = np.minimum(walk_d, line_dist(w['pts'], xs, ys))
roads, walks = road_d < 3.0, walk_d < 1.5
svc = line_dist(d['ways']['843003380']['pts'], xs, ys)
vr = line_dist(d['ways']['312841179']['pts'], xs, ys)
fw = line_dist(d['ways']['1504781934']['pts'], xs, ys)

A = (XX >= 245) & (XX <= 260) & (YY >= 140) & (YY <= 290)
both = A & np.isfinite(DTM) & np.isfinite(skz)
dz = np.full_like(DTM, np.nan)
dz[both] = DTM[both] - skz[both]
dd = dz[both]
bands = []
for y0 in range(140, 290, 20):
    B = A & (YY >= y0) & (YY < y0 + 20)
    bb = B & both
    dbb = dz[bb]
    E = B & (XX >= 256) & both
    bands.append({
        'y0': y0, 'y1': y0 + 20, 'n': int(B.sum()),
        'wood_pct': round(100 * (B & wood).sum() / max(1, B.sum()), 1),
        'road_pct': round(100 * (B & roads).sum() / max(1, B.sum()), 1),
        'walk_pct': round(100 * (B & walks).sum() / max(1, B.sum()), 1),
        'chm_gt3_pct': round(float(100 * np.nanmean(CHM[B] > 3)), 1),
        'dz_med': None if not bb.any() else round(float(np.median(dbb)), 2),
        'dz_p5': None if not bb.any() else round(float(np.percentile(dbb, 5)), 2),
        'dz_p95': None if not bb.any() else round(float(np.percentile(dbb, 95)), 2),
        'abs_dz_gt2_pct': None if not bb.any() else round(float(100 * np.mean(np.abs(dbb) > 2)), 1),
        'east_dz_med': None if not E.any() else round(float(np.median(dz[E])), 2),
    })

# Priority B
donot = (XX >= 40) & (XX <= 155) & (YY >= 245) & (YY <= 320)
B_south = YY < 215
target = B_south & wood & (CHM > 3) & ~bldg
H = np.nan_to_num(CHM, nan=0.0)
P = np.pad(H, 1, mode='edge')
Hs = sum(P[a:a + H.shape[0], b:b + H.shape[1]] for a in range(3) for b in range(3)) / 9
P2 = np.pad(Hs, 2, mode='edge')
mx = np.max(np.stack([P2[a:a + H.shape[0], b:b + H.shape[1]] for a in range(5) for b in range(5)]), axis=0)
BOX = (YY < 215) & (YY >= 140) & (XX >= 137) & (XX <= 206)
ismax = (Hs >= mx - 1e-9) & (Hs >= 4) & BOX & wood & ~bldg & ~roads & (H >= 4)
tops = []
for j, i in zip(*np.where(ismax)):
    h = float(Hs[j, i] + (H[j, i] - Hs[j, i]) * 0.5)
    tops.append((float(xs[i]), float(ys[j]), h, int(cov[j, i]), float(H[j, i])))
sel = []
for x, y, h, cv, hr in sorted(tops, key=lambda t: -t[2]):
    if any((x - a) ** 2 + (y - b) ** 2 < 4.5 ** 2 for a, b, *_ in sel):
        continue
    sel.append((x, y, h, cv, hr))

cov_of_target = Counter(int(v) for v in cov[target].tolist()) if target.any() else {}
rep = {
    'choice': 'B',
    'reason': (
        'A skipped: 0% OSM wood; Valley Road + service 843003380 + footway 1504781934 occupy y240-290 '
        '(same occupied-ground class as the Richardson band); y160-220 DTM is +2 to +3 m above 3DEP '
        'while the grid ends at x260 and east-edge dz shrinks, so a 15 m stripe would read as a N-S '
        'terrace ramping down to 3DEP. B: y<215 south of Stone is real OSM wood 315835594 with 1270 '
        'wood∧CHM>3 cells, 0 buildings/roads/walks on those cells, and ALL already on modelled LiDAR '
        '(Terrain_LiDAR / QG / QH / QI) — so plant CHM local-max trees on existing ground, no new patch.'
    ),
    'priority_A': {
        'box': [245, 260, 140, 290],
        'cells': int(A.sum()),
        'cov0': int((A & (cov == 0)).sum()),
        'wood_pct': round(100 * (A & wood).sum() / A.sum(), 1),
        'bldg': int((A & bldg).sum()),
        'road_pct': round(100 * (A & roads).sum() / A.sum(), 1),
        'walk_pct': round(100 * (A & walks).sum() / A.sum(), 1),
        'valley_rd_lt5m': int((A & (vr < 5)).sum()),
        'svc_843003380_lt5m': int((A & (svc < 5)).sum()),
        'footway_1504781934_lt3m': int((A & (fw < 3)).sum()),
        'chm_gt3_pct': round(float(100 * np.nanmean(CHM[A] > 3)), 1),
        'dtm_minus_skirt': {
            'n': int(both.sum()),
            'mean': round(float(dd.mean()), 2),
            'med': round(float(np.median(dd)), 2),
            'p5': round(float(np.percentile(dd, 5)), 2),
            'p95': round(float(np.percentile(dd, 95)), 2),
            'min': round(float(dd.min()), 2),
            'max': round(float(dd.max()), 2),
            'abs_gt1_pct': round(float(100 * np.mean(np.abs(dd) > 1)), 1),
            'abs_gt2_pct': round(float(100 * np.mean(np.abs(dd) > 2)), 1),
        },
        'y_bands': bands,
        'skip': True,
    },
    'priority_B': {
        'search': 'OSM wood 315835594 ∧ CHM>3 ∧ ~bldg, y<215 and/or x<120, excluding Richardson band',
        'x_lt_120_wood_chm3': int(((XX < 120) & wood & (CHM > 3)).sum()),
        'south_y_lt_215': {
            'cells': int(B_south.sum()),
            'wood': int((B_south & wood).sum()),
            'wood_chm3_nobldg': int(target.sum()),
            'wood_chm3_bbox': (
                [float(XX[target].min()), float(XX[target].max()),
                 float(YY[target].min()), float(YY[target].max())]
                if target.any() else None
            ),
            'wood_chm3_cov': {str(k): int(v) for k, v in sorted(cov_of_target.items())},
            'wood_chm3_cov0': int((target & (cov == 0)).sum()),
            'wood_chm3_roads': int((target & roads).sum()),
            'wood_chm3_walks': int((target & walks).sum()),
        },
        'maxima_box': [137, 206, 140, 215],
        'n_maxima_rawH_ge4': len(tops),
        'n_spaced_4_5m': len(sel),
        'sel': [{'x': round(x, 2), 'y': round(y, 2), 'h': round(h, 2),
                 'cov': int(cv), 'raw_chm': round(hr, 2)} for x, y, h, cv, hr in sel],
        'lidar_already_present': True,
    },
}
json.dump(rep, open(f'{ROOT}/data/wq/probe.json', 'w'), indent=1)
print('CHOICE', rep['choice'])
print('A skip wood%', rep['priority_A']['wood_pct'], 'road%', rep['priority_A']['road_pct'],
      'dz med', rep['priority_A']['dtm_minus_skirt']['med'])
print('B south wood∧CHM>3', int(target.sum()), 'cov0', int((target & (cov == 0)).sum()),
      'maxima', len(tops), 'spaced', len(sel))
