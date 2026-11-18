"""Session dS (~7:36 AM ET Oct 21). MAIN: eye-level lawn grass around CCOM (the lawns between CCOM, Life Hall, Morehead's west/north
front and the strip along CCOM's east wall before the wood), where the cx/3g grass stops (cx ends at x -13.4).
Same clumps + GN group as cx_grass_points (cx_grass_instancer). Mask data/dS/lawn_mask_ccom_dS.npy (OSM + NJ 2020 ortho; wood, parking,
buildings, walks/steps/service buffered out). Only 0.5 m cells where existing grass (cx, cx fill) has < 25 % of FILL.
Ground z MEASURED (main Terrain_ etc.), points under any non-ground mesh within 1 m dropped (walk slabs, steps, kerbs, building skirts).
Idempotent (object dS_grass_ccom_points). Env: SAVE=1, FILL (45). REVERT=1 SAVE=1 removes it."""
import bpy, os, re, time
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
t0 = time.time(); SAVE = os.environ.get('SAVE', '0') == '1'
FILL = float(os.environ.get('FILL', '45'))
RX0, RX1, RY0, RY1 = -45.0, 75.0, -85.0, 65.0
M = np.load('/workspace/nj-scenes/montclair-state/data/dS/lawn_mask_ccom_dS.npy').astype(np.float32) / 255.0
MX0, MY1, MRES = RX0, RY1, 0.2; H_, W_ = M.shape
sc = bpy.context.scene
old = bpy.data.objects.get('dS_grass_ccom_points')
if old: me_old = old.data; bpy.data.objects.remove(old, do_unlink=True); bpy.data.meshes.remove(me_old); print('dS: removed old')
if os.environ.get('REVERT') == '1':
    if SAVE: bpy.ops.wm.save_mainfile(); print('dS: REVERTED+SAVED', time.strftime('%H:%M:%S'))
    raise SystemExit
ng = bpy.data.node_groups['cx_grass_instancer']
C = 0.5; gx = int((RX1 - RX0) / C) + 1; gy = int((RY1 - RY0) / C) + 1
cnt = np.zeros((gy, gx), np.int32)
for nm in ('cx_grass_points', 'cx_grass_fill_points'):
    po = bpy.data.objects[nm]; n = len(po.data.vertices); E = np.zeros(n * 3, np.float32); po.data.vertices.foreach_get('co', E); E = E.reshape(-1, 3)
    Wm = np.array(po.matrix_world, np.float32); E = E @ Wm[:3, :3].T + Wm[:3, 3]
    k = (E[:, 0] >= RX0) & (E[:, 0] < RX1) & (E[:, 1] >= RY0) & (E[:, 1] < RY1)
    np.add.at(cnt, (((E[k, 1] - RY0) / C).astype(int), ((E[k, 0] - RX0) / C).astype(int)), 1)
rng = np.random.default_rng(20261021)
N = int(FILL * (RX1 - RX0) * (RY1 - RY0))
P = np.stack([rng.uniform(RX0, RX1, N), rng.uniform(RY0, RY1, N)], 1)
ix = ((P[:, 0] - MX0) / MRES).astype(int); iy = ((MY1 - P[:, 1]) / MRES).astype(int)
ok = (ix >= 0) & (ix < W_) & (iy >= 0) & (iy < H_)
mv = np.zeros(N, np.float32); mv[ok] = M[iy[ok], ix[ok]]
acc = rng.random(N) < np.clip((mv - 0.35) / 0.4, 0, 1)
ci = ((P[:, 1] - RY0) / C).astype(int).clip(0, gy - 1); cj = ((P[:, 0] - RX0) / C).astype(int).clip(0, gx - 1)
acc &= cnt[ci, cj] < 0.25 * FILL * C * C
P = P[acc]; print('dS candidates', N, 'accepted (mask, uncovered)', len(P), flush=True)
dg = bpy.context.evaluated_depsgraph_get()
GRE = re.compile(r'^(Terrain_|Lawn_worn_edge|Context_skirt|BD_farfield)'); IGN = re.compile(r'(?i)^(Lawn_grass_instanced|cx_grass|cd_grass|dS_grass)|^CAM')
ground, occl = [], []
for o in sc.objects:
    if o.type != 'MESH' or o.hide_render or not o.visible_get() or IGN.search(o.name): continue
    cs = [o.matrix_world @ Vector(c) for c in o.bound_box]
    if max(c.x for c in cs) < RX0 or min(c.x for c in cs) > RX1 or max(c.y for c in cs) < RY0 or min(c.y for c in cs) > RY1: continue
    if min(c.z for c in cs) > 165: continue
    (ground if GRE.search(o.name) else occl).append(o)
def merged(objs):
    V, F, off = [], [], 0
    for o in objs:
        oe = o.evaluated_get(dg); me = oe.to_mesh(); kk = len(me.vertices)
        if kk == 0 or not len(me.polygons): oe.to_mesh_clear(); continue
        c = np.zeros(kk * 3, np.float32); me.vertices.foreach_get('co', c); c = c.reshape(-1, 3)
        Wm = np.array(o.matrix_world, np.float32); c = c @ Wm[:3, :3].T + Wm[:3, 3]
        F += [tuple(i + off for i in p.vertices) for p in me.polygons]; oe.to_mesh_clear(); V.append(c); off += kk
    return BVHTree.FromPolygons(np.concatenate(V).tolist(), F) if F else None
GB = [merged([o]) for o in ground]; GB = [g for g in GB if g]; OT = merged(occl)
print('dS ground', [o.name for o in ground], 'occluders', len(occl), '%.1fs' % (time.time() - t0), flush=True)
down = Vector((0, 0, -1)); verts = []; miss = occ = 0
for x, y in P:
    zs = [h[0].z for h in (t.ray_cast(Vector((float(x), float(y), 400.0)), down) for t in GB) if h[0] is not None]
    if not zs: miss += 1; continue
    z = max(zs)
    if OT and OT.ray_cast(Vector((float(x), float(y), z + 1.0)), down, 1.15)[0] is not None: occ += 1; continue
    verts.append((float(x), float(y), z - 0.004))
print('dS kept', len(verts), 'miss', miss, 'occluded', occ, flush=True)
me = bpy.data.meshes.new('dS_grass_ccom_points'); me.from_pydata(verts, [], [])
fo = bpy.data.objects.new('dS_grass_ccom_points', me); bpy.data.collections['Main_grass_cx'].objects.link(fo)
md = fo.modifiers.new('cx_grass', 'NODES'); md.node_group = ng
fo['dS_source'] = 'uniform %.0f/m2 on dS CCOM lawn mask (OSM + 2020 ortho), uncovered cells only; z MEASURED on main' % FILL
print('dS: done %.1fs' % (time.time() - t0), flush=True)
if SAVE: bpy.ops.wm.save_mainfile(); print('dS: SAVED', time.strftime('%H:%M:%S'), flush=True)
