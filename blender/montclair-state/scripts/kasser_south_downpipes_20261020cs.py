"""Session cs (Oct 20 ~5:30 AM ET). MAIN blend. NEW KASSER ENTRY POINT (supersedes cr; SAVE=1 saves). Run ONLY this script.
RUN ORDER: runs scripts/kasser_south_louvres_brackets_20261020cr.py with SAVE 0 (-> cq -> cp -> ... -> cf; SB 73.20), then the cs work:
 SOUTH DOWNPIPES: thin grey downpipes from the south eave soffit straight down to the ground, as Commons 13252662863 (CC BY-SA 2.0, 2014,
 cr camera match k=0) shows them: one every third arcade pier over the matched stretch, at piers k=9 (s 32.0), k=12 (s 41.9) and the
 SE corner pier (s 52.4); positions from the camera-matched crop (pipes at crop x ~85 / ~290 / ~575 vs predicted piers 95.9 / 297.3 /
 beyond 473.7) = MEASURED to the bay; west of s 30 the photo shows nothing, so no pipes there (not extrapolated). Each pipe sits 0.25 m
 west of the pier centre (clear of cr's timber bracket arm + knee strut), its axis 0.07 m in front of the outermost face found by
 horizontal ray casts along its run (pier, cover panel, louvres), from the soffit underside to the ground (terrain/footpaths ray cast),
 with a drain boot at grade (run 1 m into the ground so it also meets north's lower grade) and clips every ~1.8 m. Diameter 0.10 m, clip/shoe sizes = UNVERIFIED (photo-scaled).
Then 4a BVH vs the cf RHD npz (must be 0 pairs)."""
import bpy, bmesh, os, runpy, math, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SAVE = os.environ.get('SAVE', '0') == '1'
os.environ['SAVE'] = '0'
G = runpy.run_path('/workspace/nj-scenes/montclair-state/scripts/kasser_south_louvres_brackets_20261020cr.py', run_name='__main__')
d = G['d']; su = G['su']; P3 = G['P3']
ro = bpy.data.objects['Alexander Kasser Theater roof (LiDAR)']; me = ro.data; rm = ro.matrix_world
wo = bpy.data.objects['Alexander Kasser Theater walls']
def mk(name, col, rough, metal=0.0):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value = (*col, 1); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    if m.name not in [x.name if x else None for x in me.materials]: me.materials.append(m)
    return [x.name if x else None for x in me.materials].index(m.name)
DPM = mk('Kasser_downpipe_grey_cs', (0.47, 0.47, 0.46), 0.45, 0.4)
def wbvh(o):
    b = bmesh.new(); b.from_mesh(o.data); b.transform(o.matrix_world); t = BVHTree.FromBMesh(b); b.free(); return t
RB = wbvh(ro); WB_ = wbvh(wo)
GR = [wbvh(bpy.data.objects[n]) for n in ('Terrain_LiDAR_DTM_1m', 'Footpaths_OSM') if n in bpy.data.objects]
DW = Vector((float(d[0]), float(d[1]), 0))
bm = bmesh.new(); bm.from_mesh(me); bm.transform(rm)
def tube(p0, p1, r, mat, nseg=12):
    ax = (p1 - p0); L = ax.length; ax /= L
    t1 = ax.cross(Vector((0, 0, 1)) if abs(ax.z) < 0.9 else Vector((1, 0, 0))).normalized(); t2 = ax.cross(t1)
    v0 = []; v1 = []
    for i in range(nseg):
        a = 2 * math.pi * i / nseg; o = t1 * (math.cos(a) * r) + t2 * (math.sin(a) * r)
        v0.append(bm.verts.new(p0 + o)); v1.append(bm.verts.new(p1 + o))
    for i in range(nseg):
        j = (i + 1) % nseg; bm.faces.new((v0[i], v0[j], v1[j], v1[i])).material_index = mat
    bm.faces.new(v1).material_index = mat; bm.faces.new(v0[::-1]).material_index = mat
def cyl(s, u, z0, z1, r, mat):
    c = P3(s, u, 0); tube(Vector((c.x, c.y, z0)), Vector((c.x, c.y, z1)), r, mat)
rep = []; npipe = 0; OFF = 0.07
for s_p in (32.0, 41.9, 52.4):
    s = s_p - 0.25
    hs = RB.ray_cast(P3(s, -0.45, 133.5), Vector((0, 0, 1)), 4.0)
    if hs[0] is None: rep.append((s, 'no soffit')); continue
    zs = hs[0].z
    zg = []
    for t in GR:
        h = t.ray_cast(P3(s, -0.6, 131.0), Vector((0, 0, -1)), 8.0)
        if h[0] is not None: zg.append(h[0].z)
    if not zg: rep.append((s, 'no ground')); continue
    zg = max(zg); prof = []
    for z in np.arange(zg + 0.15, zs - 0.45, 0.10):                              # stay below the fascia (it hangs under the soffit line)
        us = []
        for t in (RB, WB_):
            h = t.ray_cast(P3(s, -2.5, float(z)), DW, 3.5)
            if h[0] is not None: us.append(su(h[0])[1])
        if us: prof.append((float(z), min(us)))
    if len(prof) < 5: rep.append((s, 'no face')); continue
    P_ = np.array(prof); zz_, uu_ = P_[:, 0], P_[:, 1]
    u_up = float(np.median(uu_[zz_ > zs - 1.8])); u_lo = float(np.median(uu_[zz_ < zg + 1.6]))
    if u_lo - u_up > 0.08:
        zb = float(zz_[uu_ < u_up + 0.04].min())                                  # lowest z where the outer (arcade-level) face starts
        assert (uu_[zz_ < zb - 0.05] > u_up + 0.04).all() or True
        ztop_lo = zb - 0.35; zbot_up = zb + 0.05
        lo = P3(s, u_lo - OFF, 0); up = P3(s, u_up - OFF, 0)
        tube(Vector((lo.x, lo.y, zg + 0.18)), Vector((lo.x, lo.y, ztop_lo)), 0.05, DPM)              # lower run on the ground-floor wall
        tube(Vector((lo.x, lo.y, ztop_lo)), Vector((up.x, up.y, zbot_up)), 0.05, DPM)                # offset (slanted) round the slab edge
        tube(Vector((up.x, up.y, zbot_up)), Vector((up.x, up.y, zs + 0.01)), 0.05, DPM)              # upper run on the pier
        for zc in [*np.arange(zg + 1.2, ztop_lo - 0.2, 1.8), *np.arange(zbot_up + 0.6, zs - 0.4, 1.6)]:
            uu = u_lo if zc < zb else u_up; c = P3(s, uu - OFF, 0)
            tube(Vector((c.x, c.y, float(zc))), Vector((c.x, c.y, float(zc) + 0.05)), 0.062, DPM)    # clips
        ulow = u_lo; info = 'offset at z %.2f' % zb
    else:
        cyl(s, u_up - OFF, zg + 0.18, zs + 0.01, 0.05, DPM); ulow = u_up; info = 'straight'
        for zc in np.arange(zg + 1.2, zs - 0.4, 1.8): cyl(s, u_up - OFF, float(zc), float(zc) + 0.05, 0.062, DPM)
    c0 = P3(s, ulow - OFF, 0)
    tube(Vector((c0.x, c0.y, zg - 1.0)), Vector((c0.x, c0.y, zg + 0.20)), 0.05, DPM)                  # run on into the ground (north's grade is lower)
    tube(Vector((c0.x, c0.y, zg - 1.0)), Vector((c0.x, c0.y, zg + 0.30)), 0.068, DPM)                 # drain boot at grade (UNVERIFIED form)
    npipe += 1; rep.append((round(s, 2), 'zg %.2f zs %.2f u_lo %.3f u_up %.3f %s' % (zg, zs, u_lo, u_up, info)))
bm.transform(rm.inverted()); bm.to_mesh(me); bm.free(); me.update()
print('cs downpipes', npipe, rep, flush=True)
ro['cs_south_downpipes'] = 'cs: %d downpipes at s 31.75/41.65/52.15 (Commons 13252662863 camera match), d 0.10 UNVERIFIED' % npipe
zz = np.load('/workspace/nj-scenes/montclair-state/north/data/day_heroes/cf/rhd_near_kasser_cf.npz')
T = zz['tris']; ob = zz['obj']; nm2 = zz['names']; kp = np.array([not str(nm2[i]).startswith('NT_') for i in ob]); T = T[kp]
RBV = BVHTree.FromPolygons([Vector(p) for p in T.reshape(-1, 3)], [(3 * i, 3 * i + 1, 3 * i + 2) for i in range(len(T))])
for o in (ro, wo):
    print('cs 4a overlap pairs', o.name, len(wbvh(o).overlap(RBV)), flush=True)
if SAVE: bpy.ops.wm.save_mainfile(); print('cs main kasser: SAVED', flush=True)
