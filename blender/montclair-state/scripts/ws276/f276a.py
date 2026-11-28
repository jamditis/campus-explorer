# ws276 f276a (merge208 CHAIN, on ws274e): Sprague Library east doorway for the rough interiors (ofj-ceinteriors door list,
# door 1: centre -50.20, 34.99 on the shell's outer face, sill 137.90, 2.0 x 2.4 m, facing 103 deg; evidence
# library-main-level-map, inside.montclair.edu). Cuts the opening out of 'Sprague Library L0' (the visible LiDAR mass; the
# stucco 'Sprague Library walls' are hidden and not exported) with an EXACT boolean box running from 0.5 m outside the face to
# DIN m inside it (past the back of the 0.6 m recess at y 33.4..35.7), then deletes the faces the box leaves on its back plane,
# so the opening reaches the interior plan's lining instead of ending in a niche. Only faces inside the box change.
import bpy, bmesh, math, os
from mathutils import Vector
TAG = 'F276A'; OB = bpy.data.objects
C = Vector((-50.20, 34.99)); FACING = 103.0; W = 2.0; SILL = 137.90; H = 2.4; DOUT = 0.5; DIN = 1.2
n = Vector((math.sin(math.radians(FACING)), math.cos(math.radians(FACING))))  # outward normal (x east, y north)
t = Vector((-n.y, n.x))                                                         # along the face
def local(p):  # world point -> (u along face, d outward, z)
    q = Vector((p.x, p.y)) - C
    return q.dot(t), q.dot(n), p.z
o = next(x for x in OB if x.name.startswith('Sprague Library L0 (LiDAR 141.8 m east strip'))  # 63-char name, truncated
me = o.data; mw = o.matrix_world.copy()
inbox = lambda u, d, z, e=0.0: abs(u) <= W / 2 + e and -DIN - e <= d <= DOUT + e and SILL - e <= z <= SILL + H + e
before = [tuple(round(c, 4) for c in (mw @ v.co)) for v in me.vertices]
keep = sorted(p for p in before if not inbox(*local(Vector(p)), e=0.01))
print(TAG, o.name, 'verts', len(me.vertices), 'faces', len(me.polygons), 'verts in box', len(before) - len(keep), flush=True)
# cutter box in world space
bm = bmesh.new()
corners = []
for d in (-DIN, DOUT):
    for u in (-W / 2, W / 2):
        for z in (SILL, SILL + H):
            xy = C + t * u + n * d; corners.append(Vector((xy.x, xy.y, z)))
bmesh.ops.convex_hull(bm, input=[bm.verts.new(c) for c in corners])
cm = bpy.data.meshes.new('WS276_cutter'); bm.to_mesh(cm); bm.free()
cut = bpy.data.objects.new('WS276_cutter', cm); bpy.context.scene.collection.objects.link(cut)
md = o.modifiers.new('WS276_door', 'BOOLEAN'); md.operation = 'DIFFERENCE'; md.solver = 'EXACT'; md.object = cut
md.use_hole_tolerant = True; md.show_viewport = True
dg = bpy.context.evaluated_depsgraph_get(); dg.update()
new = bpy.data.meshes.new_from_object(o.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)
o.modifiers.remove(md); bpy.data.objects.remove(cut); bpy.data.meshes.remove(cm)
# open the back: faces on the box's back plane (d = -DIN) inside the opening rectangle
bm = bmesh.new(); bm.from_mesh(new)
print(TAG, 'materials', [(i, m.name) for i, m in enumerate(new.materials)], flush=True)
BRICK = [m.name for m in new.materials].index('North_wall_Sprague_brick_buff_UNVERIFIED')
PAVE = bpy.data.materials.get(os.environ.get('PAVE', 'bx_patio_curb_precast'))
if PAVE.name not in [m.name for m in new.materials]: new.materials.append(PAVE)
PI = [m.name for m in new.materials].index(PAVE.name)
HIDE = [m.name for m in new.materials].index('North_CafeDiem_L0hide_bt'); UPIER = 0.55
back = []; rev = {}
for f in bm.faces:
    ps = [local(mw @ v.co) for v in f.verts]
    if all(abs(d + DIN) < 0.005 for u, d, z in ps) and all(inbox(u, d, z, e=0.005) for u, d, z in ps):
        back.append(f); continue
    if not all(inbox(u, d, z, e=0.005) for u, d, z in ps): continue
    # reveal faces the box made: jambs (u = +-W/2), head (z = SILL+H), threshold (z = SILL)
    # North of the brick pier's N edge (u > UPIER, the recess corner at -50.28, 35.57) the L0 mass is the hidden Cafe Diem strip
    # (North_CafeDiem_L0hide_bt); reveal faces there get the same hide material, or they stand as a fin in front of the cafe glass.
    cu = sum(p[0] for p in ps) / len(ps)
    if all(abs(abs(u) - W / 2) < 0.005 for u, d, z in ps) or all(abs(z - SILL - H) < 0.005 for u, d, z in ps):
        f.material_index = HIDE if cu > UPIER else BRICK; rev['hide' if cu > UPIER else 'brick'] = rev.get('hide' if cu > UPIER else 'brick', 0) + 1
    elif all(abs(z - SILL) < 0.005 for u, d, z in ps):
        f.material_index = HIDE if cu > UPIER else PI; rev['hide' if cu > UPIER else 'sill'] = rev.get('hide' if cu > UPIER else 'sill', 0) + 1
print(TAG, 'reveal faces', rev, flush=True)
# Brick UVs: the boolean leaves its faces (and Void's older recess faces here) without a brick mapping, so they render flat grey.
# Fit uv = A (s, z) + b on the L0 front brick faces near the door (s = along the face), then project every brick face in the door
# region that is not a front face with the same scale on its own plane (jambs: depth, z; head/sill: s, depth).
uvl = bm.loops.layers.uv.active
rows = []
for f in bm.faces:
    if f.material_index != BRICK: continue
    nn = (mw.to_3x3() @ f.normal).normalized()
    if Vector((nn.x, nn.y)).dot(n) < 0.95: continue
    ps = [local(mw @ v.co) for v in f.verts]
    if not all(-6 < u < 3 and -0.5 < d < 0.5 for u, d, z in ps): continue
    for l in f.loops:
        u, d, z = local(mw @ l.vert.co); rows.append((u, z, l[uvl].uv.x, l[uvl].uv.y))
import numpy as np
R = np.array(rows); X = np.c_[R[:, 0], R[:, 1], np.ones(len(R))]
cu_, res_u = np.linalg.lstsq(X, R[:, 2], rcond=None)[:2]; cv_, res_v = np.linalg.lstsq(X, R[:, 3], rcond=None)[:2]
fit = float(np.abs(X @ cu_ - R[:, 2]).max() + np.abs(X @ cv_ - R[:, 3]).max())
print(TAG, 'brick uv fit loops', len(R), 'max residual %.4f' % fit, flush=True)
nuv = 0
if fit < 0.01:
    for f in bm.faces:
        if f.material_index != BRICK: continue
        ps = [local(mw @ v.co) for v in f.verts]
        if not all(abs(u) < W / 2 + 1.5 and -DIN - 0.1 < d < DOUT and SILL - 0.1 < z < SILL + H + 1.0 for u, d, z in ps): continue
        nn = (mw.to_3x3() @ f.normal).normalized(); a = (abs(Vector((nn.x, nn.y)).dot(t)), abs(Vector((nn.x, nn.y)).dot(n)), abs(nn.z))
        if Vector((nn.x, nn.y)).dot(n) >= 0.95: continue  # front faces keep Void's mapping; recess backs (normal -n) are re-mapped
        for l in f.loops:
            u, d, z = local(mw @ l.vert.co)
            p, q = (d, z) if a[0] == max(a) else (u, d) if a[2] == max(a) else (u, z)
            l[uvl].uv = (cu_[0] * p + cu_[1] * q + cu_[2], cv_[0] * p + cv_[1] * q + cv_[2])
        nuv += 1
print(TAG, 'brick faces re-mapped', nuv, flush=True)
area = sum(f.calc_area() for f in back)
bmesh.ops.delete(bm, geom=back, context='FACES')
bm.to_mesh(new); bm.free()
after = [tuple(round(c, 4) for c in (mw @ v.co)) for v in new.vertices]
keep2 = sorted(p for p in after if not inbox(*local(Vector(p)), e=0.01))
mats_ok = [m.name for m in new.materials][:len(me.materials)] == [m.name for m in me.materials]
print(TAG, 'back faces removed', len(back), 'area %.2f m2 (opening %.2f)' % (area, W * H), 'verts', len(new.vertices), 'faces', len(new.polygons),
      'outside-box verts identical', keep == keep2, 'materials kept', mats_ok, flush=True)
if not back or keep != keep2 or not mats_ok:
    raise SystemExit(TAG + ' refused: cut not local or back not opened')
old = o.data; o.data = new; new.name = old.name; bpy.data.meshes.remove(old)
# other visible meshes reaching into the opening above the sill (paving tops at the sill are fine)
for x in OB:
    if x.type != 'MESH' or x is o or x.hide_render: continue
    bb = [x.matrix_world @ Vector(c) for c in x.bound_box]
    if max(v.z for v in bb) < SILL + 0.05 or min(v.z for v in bb) > SILL + H: continue
    if not any(inbox(*local(v), e=0.5) for v in bb) and not (min(v.x for v in bb) < C.x < max(v.x for v in bb) and min(v.y for v in bb) < C.y < max(v.y for v in bb)): continue
    k = sum(1 for v in x.data.vertices if (lambda p: inbox(*local(p)) and p.z > SILL + 0.05)(x.matrix_world @ v.co))
    if k: print(TAG, 'other mesh in opening', x.name, k, flush=True)
