"""Session cf (Oct 19 ~4:30 PM ET). MAIN blend (Kasser's owner). Idempotent (restores the cf_orig_* mesh copies first), SAVE=1 saves.
Rule 4a fix for linking Kasser into the north blend: Red Hawk Deck OWNS the shared OSM wall (RHD east = Kasser west,
nodes A(-250.1,-46.7) B(-237.3,3.8)). Kasser's west wall is pulled back INSET (0.25 m) into Kasser (no coplanar face), and around
the RHD SE stair core (which reaches up to 1.54 m past the OSM edge over u -0.39..9.81 along A->B, from north-blend geometry
north/data/day_heroes/cf/rhd_near_kasser_cf.npz) it steps back to NOTCH_S (1.80 m). Kasser roof / eave soffit+fascia / eave course
faces west of those lines are cut (bisect + delete) so nothing runs into the deck or its cores. Kasser wall base is extended 3.6 m down by an
extruded strip (below main's ground; closes the gap over north's lower RHD push-down ground). Overlap check vs the RHD triangles printed."""
import bpy, bmesh, os, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SAVE = os.environ.get('SAVE', '0') == '1'
INSET = float(os.environ.get('INSET', '0.25')); NOTCH_S = float(os.environ.get('NOTCH_S', '1.80'))
U0, U1 = -0.70, 10.10; DROP = float(os.environ.get('DROP', '3.6'))
A = np.array([-250.1, -46.7]); B = np.array([-237.3, 3.8]); d = (B - A) / np.linalg.norm(B - A); n = np.array([d[1], -d[0]])
NAMES = ['Alexander Kasser Theater walls', 'Alexander Kasser Theater roof (LiDAR)', 'Alexander Kasser Theater eave soffit + fascia + rafter tails', 'Alexander Kasser Theater barrel tile eave course']
def su(co): p = np.array([co.x, co.y]) - A; return float(p @ n), float(p @ d)
def plane(sval=None, uval=None):
    if sval is not None: c = A + n * sval; return Vector((c[0], c[1], 0)), Vector((n[0], n[1], 0))
    c = A + d * uval; return Vector((c[0], c[1], 0)), Vector((d[0], d[1], 0))
def target(u): return NOTCH_S if U0 <= u <= U1 else INSET
z = np.load('/workspace/nj-scenes/montclair-state/north/data/day_heroes/cf/rhd_near_kasser_cf.npz')
T = z['tris']; ob = z['obj']; nm = z['names']
keep = np.array([not str(nm[i]).startswith('NT_') for i in ob])
T = T[keep]; ob = ob[keep]
RV = [Vector(p) for p in T.reshape(-1, 3)]; RF = [(3*i, 3*i+1, 3*i+2) for i in range(len(T))]
RB = BVHTree.FromPolygons(RV, RF)
for name in NAMES:
    o = bpy.data.objects.get(name)
    if o is None: print('cf MISSING', name); continue
    on = 'cf_orig_' + name[:50]
    orig = bpy.data.meshes.get(on)
    if orig is None:
        orig = o.data.copy(); orig.name = on; orig.use_fake_user = True
    old = o.data; o.data = orig.copy(); o.data.name = name[:40] + '_cf'
    if old.users == 0 and old is not orig: bpy.data.meshes.remove(old)
    M = o.matrix_world.copy(); Mi = M.inverted()
    bm = bmesh.new(); bm.from_mesh(o.data); bm.transform(M)
    nv0, nf0 = len(bm.verts), len(bm.faces)
    if name.endswith('walls'):
        for uv in (U1, U1 + 0.10):
            co, no = plane(uval=uv); bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-4, plane_co=co, plane_no=no)
        zb = min(v.co.z for v in bm.verts); moved = 0; dropped = 0
        # bottom verts = no neighbour lower (>5 cm) and a neighbour at least 1 m higher (lower end of a wall edge)
        bot = [v for v in bm.verts if all(e.other_vert(v).co.z > v.co.z - 0.05 for e in v.link_edges) and any(e.other_vert(v).co.z > v.co.z + 1.0 for e in v.link_edges)]
        for v in bm.verts:
            s, u = su(v.co); t = target(u)
            if s < t and -2 < u < 58:
                v.co.x += float(n[0] * (t - s)); v.co.y += float(n[1] * (t - s)); moved += 1
        # extend the base DOWN with new faces (extrude bottom edges) instead of moving the original bottom verts: moving them
        # stretched the facade UVs (slanted windows in the first cf test). New strip faces keep the bottom-edge UVs.
        bset = set(bot)
        bed = [e for e in bm.edges if e.verts[0] in bset and e.verts[1] in bset and e.link_faces and abs(e.verts[0].co.z - e.verts[1].co.z) < 3.0]
        ret = bmesh.ops.extrude_edge_only(bm, edges=bed)
        for v in [g for g in ret['geom'] if isinstance(g, bmesh.types.BMVert)]: v.co.z -= DROP; dropped += 1
        print('cf walls base edges extruded', len(bed), flush=True)
        print('cf walls', name, 'moved', moved, 'dropped', dropped, 'zb', round(zb, 2), flush=True)
    else:
        for sv in (INSET, NOTCH_S):
            co, no = plane(sval=sv); bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-4, plane_co=co, plane_no=no)
        for uv in (U0, U1):
            co, no = plane(uval=uv); bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], dist=1e-4, plane_co=co, plane_no=no)
        kill = []
        for f in bm.faces:
            c = f.calc_center_median(); s, u = su(c)
            if -3 < u < 60 and s < target(u) - 1e-3: kill.append(f)
        bmesh.ops.delete(bm, geom=kill, context='FACES')
        loose = [v for v in bm.verts if not v.link_faces]; bmesh.ops.delete(bm, geom=loose, context='VERTS')
        print('cf cut', name, 'faces deleted', len(kill), flush=True)
    # overlap check (world)
    bm.verts.ensure_lookup_table()
    KB = BVHTree.FromBMesh(bm)
    ov = KB.overlap(RB); per = {}
    for a, b in ov: k = str(nm[ob[b]]); per[k] = per.get(k, 0) + 1
    print('cf 4a', name[:40], 'v', nv0, '->', len(bm.verts), 'f', nf0, '->', len(bm.faces), 'overlap pairs', len(ov), {k[:28]: v for k, v in per.items()}, flush=True)
    bm.transform(Mi); bm.to_mesh(o.data); bm.free(); o.data.update()
o0 = bpy.data.objects.get(NAMES[0])
if o0: o0['cf_kasser_rhd_trim'] = f'INSET {INSET} NOTCH_S {NOTCH_S} U {U0}..{U1} DROP {DROP}'
if SAVE: bpy.ops.wm.save_mainfile(); print('cf main: SAVED', flush=True)
