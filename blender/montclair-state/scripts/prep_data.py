"""Prepare day-1 GIS data: OSM -> local meters, LiDAR -> DTM/DSM grids + building stats.
CRS: NAD83(2011) / New Jersey (ftUS), EPSG:6527 (same as NJ LiDAR). Blender = (ft - origin) * US survey foot."""
import json, xml.etree.ElementTree as ET
import numpy as np, laspy
from pyproj import Transformer
from shapely.geometry import Polygon, LineString, Point
from shapely import contains_xy
FT = 1200/3937  # US survey foot in meters
tr = Transformer.from_crs("EPSG:4326", "EPSG:6527", always_xy=True)
c_e, c_n = tr.transform(-74.19720, 40.86000)
E0, N0 = round(c_e, -1), round(c_n, -1)
HALF = 250.0  # meters half-extent of terrain tile
def loc(lon, lat):
    e, n = tr.transform(lon, lat); return ((e-E0)*FT, (n-N0)*FT)
r = ET.parse('data/msu_osm.xml').getroot()
nodes = {n.get('id'): (float(n.get('lon')), float(n.get('lat'))) for n in r.iter('node')}
feats = []
for w in r.iter('way'):
    t = {x.get('k'): x.get('v') for x in w.findall('tag')}
    pts = [loc(*nodes[x.get('ref')]) for x in w.findall('nd') if x.get('ref') in nodes]
    if len(pts) < 2: continue
    if not any(abs(x) < HALF+60 and abs(y) < HALF+60 for x, y in pts): continue
    keys = ('building','highway','landuse','leisure','natural','amenity','barrier','area:highway','surface','footway','parking')
    if not any(k in t for k in keys): continue
    feats.append({'id': w.get('id'), 'tags': t, 'pts': pts, 'closed': w.findall('nd')[0].get('ref') == w.findall('nd')[-1].get('ref')})
tree_nodes = []
for n in r.iter('node'):
    t = {x.get('k'): x.get('v') for x in n.findall('tag')}
    if t.get('natural') == 'tree' or t.get('highway') in ('street_lamp',) or t.get('amenity') in ('bench',):
        x, y = loc(float(n.get('lon')), float(n.get('lat')))
        if abs(x) < HALF and abs(y) < HALF: tree_nodes.append({'tags': t, 'xy': (x, y)})
# LiDAR
las = laspy.read('data/lpc_2023_J5D6.laz')
X = (np.asarray(las.x) - E0)*FT; Y = (np.asarray(las.y) - N0)*FT; Z = np.asarray(las.z)*FT
m = (abs(X) < HALF) & (abs(Y) < HALF)
X, Y, Z = X[m], Y[m], Z[m]
cls = np.asarray(las.classification)[m]; rn = np.asarray(las.return_number)[m]
del las
print('points in tile', m.sum(), 'classes', np.unique(cls, return_counts=True))
res = 1.0; nx = int(2*HALF/res)
ix = np.clip(((X+HALF)/res).astype(int), 0, nx-1); iy = np.clip(((Y+HALF)/res).astype(int), 0, nx-1)
def grid(sel, fn):
    g = np.full((nx, nx), np.nan)
    if fn == 'max':
        np.fmax.at(g, (iy[sel], ix[sel]), Z[sel])
    else:
        s = np.zeros((nx, nx)); c = np.zeros((nx, nx))
        np.add.at(s, (iy[sel], ix[sel]), Z[sel]); np.add.at(c, (iy[sel], ix[sel]), 1)
        g = np.where(c > 0, s/np.maximum(c, 1), np.nan)
    return g
def fill(g):
    # nearest-ish fill by iterative neighbor averaging
    g = g.copy()
    for _ in range(200):
        nanm = np.isnan(g)
        if not nanm.any(): break
        p = np.pad(g, 1, constant_values=np.nan)
        nb = np.stack([p[:-2,1:-1], p[2:,1:-1], p[1:-1,:-2], p[1:-1,2:]])
        mean = np.nanmean(np.where(np.isnan(nb), np.nan, nb), axis=0) if True else None
        g[nanm] = mean[nanm]
    return g
import warnings; warnings.filterwarnings('ignore')
dtm = fill(grid(cls == 2, 'mean'))
dsm = fill(grid(np.isin(cls, [2, 5, 6]) | (cls == 1), 'max'))
np.save('data/dtm_1m.npy', dtm.astype(np.float32)); np.save('data/dsm_1m.npy', dsm.astype(np.float32))
# building stats
bstats = {}
for f in feats:
    if 'building' not in f['tags'] or not f['closed'] or len(f['pts']) < 4: continue
    poly = Polygon(f['pts'])
    if not poly.is_valid: poly = poly.buffer(0)
    inner = poly.buffer(-1.0) if poly.area > 50 else poly
    sel = (cls == 6)
    inside = contains_xy(inner, X[sel], Y[sel])
    zb = Z[sel][inside]
    ring = poly.buffer(4).difference(poly.buffer(1))
    gsel = cls == 2
    zg = Z[gsel][contains_xy(ring, X[gsel], Y[gsel])]
    if len(zb) < 10 or len(zg) < 5: continue
    g = float(np.percentile(zg, 10))
    bstats[f['id']] = {'name': f['tags'].get('name'), 'ground_min': float(zg.min()), 'ground_p10': g, 'ground_med': float(np.median(zg)),
        'roof_p50': float(np.median(zb)), 'roof_p95': float(np.percentile(zb, 95)), 'roof_max': float(zb.max()),
        'n': int(len(zb)), 'area': poly.area}
# per-building roof height raster (building-class max)
bgrid = grid(cls == 6, 'max'); np.save('data/bldg_max_1m.npy', bgrid.astype(np.float32))
vgrid = grid(cls == 5, 'max'); np.save('data/veg_max_1m.npy', vgrid.astype(np.float32))
json.dump({'E0_ftUS': E0, 'N0_ftUS': N0, 'crs': 'EPSG:6527', 'half_m': HALF, 'res_m': res, 'features': feats, 'points': tree_nodes, 'bstats': bstats},
          open('data/scene_data.json', 'w'))
for k, v in bstats.items():
    if v['name']: print(k, v['name'], {a: round(b, 1) for a, b in v.items() if a != 'name'})
print('E0,N0', E0, N0, 'origin latlon -74.1972,40.86', 'nfeat', len(feats), 'npts', len(tree_nodes))
