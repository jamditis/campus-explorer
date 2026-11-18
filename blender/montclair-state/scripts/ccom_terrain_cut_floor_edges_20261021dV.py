"""2026-10-21 session dV (~10:40 AM ET). Footprint cut of the LiDAR DTM under CCOM's 1st-floor interior floors.
dU2 lowered only the terrain VERTICES under the dd floors; 1 m DTM triangles that span a corridor wall still rose from the
lowered vertex to the outside grade, so grass slivers showed inside the south corridor along both walls (dU2 test corr2b).
Fix: restore dU2's original z; for every floor-rectangle edge measure where the wall face actually is (horizontal ray at floor+0.5,
terrain/grass ignored); BISECT the terrain on two lines just BEHIND that wall face (+0.02 m and +0.08 m beyond it), then lower every
vertex inside the rectangle grown out to the first line to 0.12 m under that floor. (First try at -/+0.03 m about the slab edge left
a near-vertical green band showing in front of the walls, dV test corrS_after.jpg.) The rise now happens in a 6 cm band at the wall
plane (hidden by the wall from outside, below the floor from inside); outside the walls the lawn surface is unchanged.
Idempotent: the untouched terrain mesh is kept as datablock 'Terrain_LiDAR_DTM_1m_pre_dV' (fake user); a rerun or REVERT=1
swaps it back first. SAVE=1 saves. Replaces dU2's terrain script in the rerun order (dU2 lowering is folded in)."""
import bpy, bmesh, os
from mathutils import Vector
T = bpy.data.objects['Terrain_LiDAR_DTM_1m']; assert T.library is None
mw = T.matrix_world; mi = mw.inverted()
ORIG = 'Terrain_LiDAR_DTM_1m_pre_dV'
if ORIG in bpy.data.meshes:            # restore first (idempotent)
    cur = T.data; T.data = bpy.data.meshes[ORIG]; T.data.use_fake_user = True
    if cur.users == 0: bpy.data.meshes.remove(cur)
    T['dV_note'] = 'reverted'
if os.environ.get('REVERT') == '1':
    print('DVTER reverted', flush=True)
else:
    src = T.data; src.use_fake_user = True
    me = src.copy(); me.name = 'Terrain_LiDAR_DTM_1m_dV'
    A = me.attributes.get('dU2_orig_z')
    if A is not None:   # undo dU2's vertex drop so bisect interpolates the real grade
        for v, a in zip(me.vertices, A.data):
            if a.value > -1e8:
                w = mw @ v.co; w.z = a.value; v.co = mi @ w
        me.attributes.remove(A)
    # floor rectangles (top faces, world)
    fl = [o for o in bpy.data.collections['CCOM_1f_interior_full_dd'].all_objects if o.type == 'MESH' and o.name.endswith('_floor_terrazzo')]
    rects = []
    for o in fl:
        top = max(o.data.polygons, key=lambda p: (o.matrix_world.to_3x3() @ p.normal).z)
        P = [o.matrix_world @ o.data.vertices[i].co for i in top.vertices]
        rects.append((o.name, [Vector((p.x, p.y)) for p in P], max(p.z for p in P)))
    dg = bpy.context.evaluated_depsgraph_get(); scn = bpy.context.scene
    def wall_dist(a, d, nrm, L, zt):
        ds = []   # farthest wall face over 3 heights (a ledge under the south windows hides a recess at 0.5 m)
        for t in (0.2, 0.35, 0.5, 0.65, 0.8):
          for hz in (0.12, 0.5, 1.0):
            o = a + d * (L * t) + nrm * 0.6; org = Vector((o.x, o.y, zt + hz)); dirv = Vector((-nrm.x, -nrm.y, 0))
            for _ in range(8):
                hit, loc, no, idx, ob, mt = scn.ray_cast(dg, org, dirv, distance=3.0)
                if not hit: break
                if ob.name.startswith('Terrain') or 'grass' in ob.name.lower() or 'rug' in ob.name: org = loc + dirv * 1e-3; continue
                ds.append((loc.to_2d() - a).dot(-nrm)); break
        ds.sort(); return ds[int(len(ds) * 0.8)] if ds else None
    def inside(q, R, offs):
        n = len(R)
        c = sum(R, Vector((0, 0))) / n
        for i in range(n):
            a, b = R[i], R[(i + 1) % n]; e = b - a; nrm = Vector((-e.y, e.x)).normalized()
            if nrm.dot(c - a) < 0: nrm = -nrm
            if nrm.dot(q - a) < -offs[i]: return False
        return True
    bm = bmesh.new(); bm.from_mesh(me); bm.transform(mw)
    nb = 0; OFFS = {}
    for name, R, zt in rects:
        c = sum(R, Vector((0, 0))) / len(R); OFFS[name] = []
        for i in range(len(R)):
            a, b = R[i], R[(i + 1) % len(R)]; e = (b - a); L = e.length; d = e / L
            nrm = Vector((-d.y, d.x))
            if nrm.dot(c - a) < 0: nrm = -nrm
            wd = wall_dist(a, d, nrm, L, zt)   # wall face position, + = beyond the slab edge (outward)
            w = min(max(wd if wd is not None else 0.0, 0.0), 1.0) + 0.02
            OFFS[name].append(round(w, 3)); print('DVTER edge', name, i, 'wall', None if wd is None else round(wd, 3), 'cut', round(w, 3), flush=True)
            for off in (-w, -(w + 0.06)):
                geom = []
                for f in bm.faces:
                    m = f.calc_center_median(); q = Vector((m.x, m.y)) - a
                    t = q.dot(d); s = q.dot(nrm)
                    if -1.6 < t < L + 1.6 and -1.6 < s < 1.6: geom.append(f)
                if not geom: continue
                ed = set(); vs = set()
                for f in geom:
                    ed.update(f.edges); vs.update(f.verts)
                co = a + nrm * off
                bmesh.ops.bisect_plane(bm, geom=list(vs) + list(ed) + geom, dist=1e-4,
                                       plane_co=Vector((co.x, co.y, 0)), plane_no=Vector((nrm.x, nrm.y, 0)))
                nb += 1
    n = 0; mx = 0
    for v in bm.verts:
        q = Vector((v.co.x, v.co.y))
        for name, R, zt in rects:
            if inside(q, R, [o + 0.01 for o in OFFS[name]]):   # +1 cm so the verts ON the first cut line drop too
                tz = zt - 0.12
                if v.co.z > tz: mx = max(mx, v.co.z - tz); v.co.z = tz; n += 1
                break
    bm.transform(mi); bm.to_mesh(me); bm.free(); me.update()
    src.name = ORIG; T.data = me; me.name = 'Terrain_LiDAR_DTM_1m'
    T['dV_note'] = 'dV: terrain bisected on %d floor-edge lines; %d verts under 4 dd floors lowered to floor-0.12 (orig mesh %s)' % (nb, n, ORIG)
    print('DVTER rects', [(r[0], round(r[2], 2)) for r in rects], 'bisects', nb, 'lowered', n, 'max_drop', round(mx, 2),
          'verts', len(src.vertices), '->', len(me.vertices), flush=True)
if os.environ.get('SAVE') == '1': bpy.ops.wm.save_mainfile(); print('DVTER_SAVED', flush=True)
