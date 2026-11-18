# vv polish: rebuild path links with stronger soft-butt onto walk (door 1 had ~0.84 m residual).
# Idempotent: removes prior vv path_link meshes/cams collection objs tagged vv_obj then rebuilds via vv_main logic inline.
import bpy, bmesh, os, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree

SAVE = os.environ.get('SAVE') == '1'
sc = bpy.context.scene
dg = bpy.context.evaluated_depsgraph_get()

# remove only path_link objects (keep cams)
for o in [o for o in bpy.data.objects if 'vv_obj' in o and 'path_link' in o.name]:
    me = o.data
    bpy.data.objects.remove(o)
    if me and me.users == 0 and hasattr(me, 'vertices'):
        bpy.data.meshes.remove(me)

GN = ['Terrain_LiDAR_DTM_1m', 'Context_skirt_3DEP_ortho_4km', 'RZ2_SC_LiDAR_ground_patch',
      'QW_DTM_north_edge_ramp_UNVERIFIED', 'SA_ground_lower_patch_UNVERIFIED']
gnd = [(bpy.data.objects[n].evaluated_get(dg), bpy.data.objects[n].matrix_world)
       for n in GN if n in bpy.data.objects]

def hit(x, y):
    best = None
    for e, mw in gnd:
        iw = mw.inverted()
        r = e.ray_cast(iw @ Vector((x, y, 400)), (iw.to_3x3() @ Vector((0, 0, -1))).normalized())
        if r[0]:
            z = (mw @ r[1]).z
            if best is None or z > best:
                best = z
    return best

WALK_ALT = {
    0: ['TJ_walk_313029110_UNVERIFIED'],
    1: ['TJ_walk_313029908_UNVERIFIED'],
    2: ['TJ_walk_313029909_UNVERIFIED', 'TJ_walk_313029910_UNVERIFIED'],
}

def door_basis(k):
    G = bpy.data.objects['TJ_Blanton_entrance_%d_glass_UNVERIFIED' % k]
    gv = [G.matrix_world @ v.co for v in G.data.vertices]
    gc = sum(gv, Vector()) / len(gv)
    best = None
    for i in range(len(gv)):
        for j in range(i + 1, len(gv)):
            d = gv[j] - gv[i]; d.z = 0
            if best is None or d.length > best.length:
                best = d
    u = best.normalized(); n = Vector((-u.y, u.x, 0))
    BC = Vector((141.6, 450.4, 0))
    if (gc - BC).to_2d().dot(n.to_2d()) < 0:
        n = -n
    return gc, u, n

def walk_data(nm):
    o = bpy.data.objects.get(nm)
    if not o: return None
    bm = bmesh.new(); bm.from_object(o, dg); bm.transform(o.matrix_world)
    verts = [v.co.copy() for v in bm.verts]
    bvh = BVHTree.FromBMesh(bm) if bm.faces else None
    bm.free()
    return o, verts, bvh

wm = None
for nm in ('TJ_walk_313029110_UNVERIFIED', 'TJ_walk_313029908_UNVERIFIED'):
    o = bpy.data.objects.get(nm)
    if o and o.data.materials:
        wm = o.data.materials[0]; break

col = bpy.data.collections.get('VV_Blanton_landing_path_join_UNVERIFIED')
if col is None:
    col = bpy.data.collections.new('VV_Blanton_landing_path_join_UNVERIFIED')
    sc.collection.children.link(col)

log = []
for k in range(3):
    gc, u, n = door_basis(k)
    L = bpy.data.objects['TU_Blanton_entrance_%d_landing_UNVERIFIED' % k]
    lv = [L.matrix_world @ v.co for v in L.data.vertices]
    zhi = max(p.z for p in lv)
    top = [p for p in lv if p.z > zhi - 0.1]
    door_front = [p for p in top if abs((p - gc).dot(u)) < 1.6] or top
    door_front.sort(key=lambda p: (p - gc).dot(n))
    outer_band = door_front[max(0, len(door_front)*2//3):]
    start = sum(outer_band, Vector()) / len(outer_band)

    cands = []
    for nm in WALK_ALT[k]:
        wd = walk_data(nm)
        if not wd: continue
        o, verts, bvh = wd
        # average of 12 nearest verts = more interior walk target
        nearest = sorted(verts, key=lambda q: (q.x-start.x)**2+(q.y-start.y)**2)[:12]
        wpt = sum(nearest, Vector()) / len(nearest)
        xy = ((wpt.x-start.x)**2+(wpt.y-start.y)**2)**0.5
        cands.append((xy, nm, o, verts, bvh, wpt))
    cands.sort(key=lambda t: t[0])
    gap, wnm, wo, wverts, wbvh, wpt = cands[0]

    direction = wpt - start; direction.z = 0
    length = direction.length
    dhat = direction.normalized()
    side = Vector((-dhat.y, dhat.x, 0))
    if side.dot(u) < 0: side = -side

    # Overshoot slightly INTO the walk (0.25 m past averaged wpt) so soft butt lands on surface
    end = start + dhat * (length + 0.25)
    HALF_W = 0.95
    N = max(4, int((length + 0.25) / 0.4) + 1)
    bm = bmesh.new(); rows = []; g0 = hit(start.x, start.y) or start.z - 0.06
    for i in range(N + 1):
        t = i / N
        c = start.lerp(end, t)
        hw = HALF_W * (1.0 - 0.05 * t)
        tops = []
        for s in (-hw, hw):
            q = c + side * s
            z = hit(q.x, q.y) or g0
            z_final = z + 0.06
            if t > 0.55 and wbvh:
                loc, normal, idx, dist = wbvh.find_nearest(Vector((q.x, q.y, z + 0.06)))
                if loc is not None and dist < 2.0:
                    # sit 8 mm above walk when over it; else keep ground+6cm
                    z_final = max(z + 0.06, loc.z + 0.008)
            tops.append(bm.verts.new((q.x, q.y, z_final)))
        row = ([bm.verts.new((tops[0].co.x, tops[0].co.y, tops[0].co.z - 0.22))]
               + tops
               + [bm.verts.new((tops[1].co.x, tops[1].co.y, tops[1].co.z - 0.22))])
        rows.append(row)
    for a, b in zip(rows, rows[1:]):
        for j in range(len(a)-1):
            try: bm.faces.new((a[j], a[j+1], b[j+1], b[j]))
            except ValueError: pass
    for row, rev in ((rows[0], False), (rows[-1], True)):
        try: bm.faces.new(list(reversed(row)) if rev else row)
        except ValueError: pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    me = bpy.data.meshes.new('VV_Blanton_entrance_%d_path_link_UNVERIFIED' % k)
    bm.to_mesh(me); bm.free()
    if wm: me.materials.append(wm)
    ob = bpy.data.objects.new(me.name, me); col.objects.link(ob)
    ob['vv_obj'] = 1
    ob['UNVERIFIED'] = 'short draped concrete link from TU Blanton door %d landing to OSM walk %s (vv polish butt)' % (k, wnm)
    # measure residual
    end_verts = [v.co for v in me.vertices]
    # world = identity for these
    residuals = []
    for p in end_verts:
        nv = min(wverts, key=lambda q: (q.x-p.x)**2+(q.y-p.y)**2)
        residuals.append(((nv.x-p.x)**2+(nv.y-p.y)**2)**0.5)
    entry = dict(k=k, walk=wnm, gap0=round(gap,3), length=round(length+0.25,3),
                 link_to_walk_min=round(min(residuals),3), link_to_walk_med=round(sorted(residuals)[len(residuals)//2],3))
    log.append(entry)
    print('POLISH', entry)

json.dump(log, open('data/vv/polish.json','w'), indent=1)
print('OBJS', len(bpy.data.objects))
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED')
