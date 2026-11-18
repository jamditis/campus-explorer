"""2026-10-16 session bi: DRY diagnose — main montclair_state.blend terrain vs LiDAR DTM near CCOM/Morehead/Life.
Main terrain is NOT the north zfill path (build_scene/prep_geom use raw dtm_1m as terrain_z). This probe samples
Terrain_LiDAR_DTM_1m (or renamed 'terrain' mesh) Z vs data/dtm_1m.npy within ~0.8–1.5 m of footprints and reports
band verts >0.3 m below measured grade. Env: REPORT_ONLY default; writes JSON under data/. No SAVE."""
import bpy, json, os, sys, resource, numpy as np
sys.path.append('/workspace/nj-scenes/blender_pylib')
from shapely.geometry import Polygon, Point
R0 = '/workspace/nj-scenes/montclair-state'
HALF = 250.0
dtm = np.load(R0 + '/data/dtm_1m.npy')  # (500,500) cell centres at -H+0.5..
ny, nx = dtm.shape
assert ny == 500 and nx == 500
def gz(x, y):
    """Bilinear sample of LiDAR DTM at scene xy (m)."""
    fx = np.clip(x - (-HALF + 0.5), 0, nx - 1.001)
    fy = np.clip(y - (-HALF + 0.5), 0, ny - 1.001)
    j, i = int(fx), int(fy); a, b = fx - j, fy - i
    return float(dtm[i, j] * (1 - a) * (1 - b) + dtm[i, j + 1] * a * (1 - b)
                 + dtm[i + 1, j] * (1 - a) * b + dtm[i + 1, j + 1] * a * b)

# footprints: prefer OSM extract written by session (CCOM / Morehead / Life)
fps_path = '/tmp/bi_fps.json'
if not os.path.exists(fps_path):
    # rebuild quickly from msu_osm
    import xml.etree.ElementTree as ET
    from pyproj import Transformer
    E0, N0 = 575880.0, 738340.0; FT = 1200 / 3937
    tr = Transformer.from_crs('EPSG:4326', 'EPSG:6527', always_xy=True)
    want = {1188721159, 312933183, 313021866}
    root = ET.parse(R0 + '/data/msu_osm.xml').getroot()
    nodes = {int(n.get('id')): (float(n.get('lon')), float(n.get('lat'))) for n in root.findall('node')}
    fps = {}
    for w in root.findall('way'):
        wid = int(w.get('id'))
        if wid not in want: continue
        tags = {t.get('k'): t.get('v') for t in w.findall('tag')}
        pts = []
        for nd in w.findall('nd'):
            lon, lat = nodes[int(nd.get('ref'))]; e, n = tr.transform(lon, lat)
            pts.append([(e - E0) * FT, (n - N0) * FT])
        fps[str(wid)] = dict(name=tags.get('name'), pts=pts)
    json.dump(fps, open(fps_path, 'w'))
else:
    fps = json.load(open(fps_path))

BLD = []
for wid, d in fps.items():
    pts = d['pts']
    if pts and pts[0] != pts[-1]:
        pts = pts + [pts[0]]
    P = Polygon(pts).buffer(0)
    if not P.is_empty:
        BLD.append((d.get('name') or wid, P, wid))

# locate terrain object
ter = bpy.data.objects.get('Terrain_LiDAR_DTM_1m') or bpy.data.objects.get('terrain')
if ter is None:
    cands = [o for o in bpy.data.objects if o.type == 'MESH' and ('terrain' in o.name.lower() or 'dtm' in o.name.lower())]
    print('TERRAIN CANDIDATES', [c.name for c in cands], flush=True)
    ter = cands[0] if cands else None
assert ter is not None, 'no terrain object'
print('terrain obj', ter.name, 'verts', len(ter.data.vertices), 'mw identity?', ter.matrix_world == __import__('mathutils').Matrix.Identity(4), flush=True)
me = ter.data
# world coords
import mathutils
mw = ter.matrix_world
N = len(me.vertices)
Vloc = np.zeros(N * 3, dtype=np.float64); me.vertices.foreach_get('co', Vloc); Vloc = Vloc.reshape(-1, 3)
if mw == mathutils.Matrix.Identity(4):
    V = Vloc.copy()
else:
    V = np.array([mw @ mathutils.Vector(c) for c in Vloc], dtype=np.float64)

report = dict(session='20261016bi', terrain=ter.name, n_verts=N, buildings={}, totals={})
band_out_gt03 = 0; band_in_gt03 = 0; all_out = []; all_in = []
for name, P, wid in BLD:
    x0, y0, x1, y1 = P.buffer(1.6).bounds
    # clip to main tile roughly
    idx = np.nonzero((V[:, 0] > x0) & (V[:, 0] < x1) & (V[:, 1] > y0) & (V[:, 1] < y1))[0]
    out_dz = []; in_dz = []; out_deep = 0; in_deep = 0
    for k in idx:
        x, y, z = V[k]
        pt = Point(x, y)
        ins = P.contains(pt); d = P.exterior.distance(pt)
        if not ins and d > 1.5: continue
        if ins and d > 1.5: continue
        g = gz(x, y); dz = g - z  # positive = terrain below LiDAR grade
        if not ins and d <= 0.8:
            out_dz.append(dz)
            if dz > 0.3: out_deep += 1
        elif not ins and d <= 1.5:
            out_dz.append(dz)
            if dz > 0.3: out_deep += 1
        elif ins and d <= 1.5:
            in_dz.append(dz)
            if dz > 0.3: in_deep += 1
    def stats(arr):
        if not arr: return dict(n=0)
        a = np.array(arr)
        return dict(n=int(len(a)), med=round(float(np.median(a)), 3), mean=round(float(np.mean(a)), 3),
                    max=round(float(np.max(a)), 3), min=round(float(np.min(a)), 3),
                    gt03=int(np.sum(a > 0.3)), gt05=int(np.sum(a > 0.5)), gt1=int(np.sum(a > 1.0)))
    rec = dict(osm_id=wid, outside_band_0_1p5m=stats(out_dz), inside_band_1p5m=stats(in_dz),
               outside_gt03=out_deep, inside_gt03=in_deep)
    report['buildings'][name] = rec
    band_out_gt03 += out_deep; band_in_gt03 += in_deep
    all_out.extend(out_dz); all_in.extend(in_dz)
    print('BLD', name[:40], 'out', rec['outside_band_0_1p5m'], 'in', rec['inside_band_1p5m'], flush=True)

report['totals'] = dict(outside_gt03=band_out_gt03, inside_gt03=band_in_gt03,
                        outside_stats=dict(n=len(all_out), gt03=int(np.sum(np.array(all_out) > 0.3)) if all_out else 0,
                                           max=round(float(np.max(all_out)), 3) if all_out else None),
                        inside_stats=dict(n=len(all_in), gt03=int(np.sum(np.array(all_in) > 0.3)) if all_in else 0,
                                          max=round(float(np.max(all_in)), 3) if all_in else None),
                        significant_trough=bool(band_out_gt03 >= 50 or (all_out and np.sum(np.array(all_out) > 0.5) >= 20)),
                        note='Main prep_geom terrain_z == raw dtm_1m (no north-style zfill). Significant trough only if mesh was later carved.')
outp = R0 + '/data/ccom_wallbase_probe_20261016bi.json'
json.dump(report, open(outp, 'w'), indent=1)
print('WROTE', outp, 'significant_trough', report['totals']['significant_trough'],
      'outside_gt03', band_out_gt03, flush=True)
print('maxrss MB', resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024, flush=True)
# stash custom props for visibility
ter['bi_wallbase_probe'] = '20261016bi outside_gt03=%d significant=%s' % (band_out_gt03, report['totals']['significant_trough'])
