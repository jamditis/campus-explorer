"""2026-10-15 ay: smaller-leaf Honey Locust on Tree_HoneyLocust_LOD1 (assets).

Real Gleditsia leaflets are tiny; LOD1 leaf cards were ~1.0 m median span (too big).
Scale leaf-material faces toward each face centroid by LEAF_SCALE, leave bark verts
alone so trunk/height (LiDAR-fit) stay valid. UNVERIFIED artistic.

Also scales LOD0 the same way for consistency of the asset library.

Idempotent via mesh['ay_small_leaf'] == LEAF_SCALE.
Args after --: [--save] [--scale=0.48]
Run only on assets/campus_assets.blend (hold assets/.lock).
After save, reload libraries in main + north so linked instances pick it up.
"""
import bpy, sys, bmesh
from mathutils import Vector
argv = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
SAVE = '--save' in argv
LEAF_SCALE = 0.48
for a in argv:
    if a.startswith('--scale='):
        LEAF_SCALE = float(a.split('=', 1)[1])
TARGETS = ('Tree_HoneyLocust_LOD1', 'Tree_HoneyLocust_LOD0')
LEAF_MAT_SUBSTR = 'Leaf_HoneyLocust'

def scale_leaf_cards(me, scale):
    if me.get('ay_small_leaf') == scale:
        print('SKIP', me.name, 'already ay_small_leaf', scale)
        return False
    # material index for leaf
    leaf_idx = None
    for i, mat in enumerate(me.materials):
        if mat and LEAF_MAT_SUBSTR in mat.name:
            leaf_idx = i
            break
    if leaf_idx is None:
        print('NO_LEAF_MAT', me.name, [m.name if m else None for m in me.materials])
        return False
    # Per-face: gather leaf faces, scale verts toward face center.
    # Shared verts between leaf faces: average the target positions.
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.faces.ensure_lookup_table()
    bm.verts.ensure_lookup_table()
    targets = {}  # vert -> list of desired positions
    n_faces = 0
    for f in bm.faces:
        if f.material_index != leaf_idx:
            continue
        n_faces += 1
        cent = f.calc_center_median()
        for v in f.verts:
            new = cent + (v.co - cent) * scale
            targets.setdefault(v.index, []).append(new.copy())
    moved = 0
    for idx, pts in targets.items():
        avg = sum(pts, Vector((0, 0, 0))) / len(pts)
        bm.verts[idx].co = avg
        moved += 1
    bm.to_mesh(me)
    bm.free()
    me['ay_small_leaf'] = scale
    me['ay_small_leaf_note'] = 'UNVERIFIED artistic; leaf cards scaled toward face centroids; bark/height unchanged'
    # measure new leaf spans (sample)
    spans = []
    for p in me.polygons:
        if p.material_index != leaf_idx:
            continue
        verts = [me.vertices[i].co for i in p.vertices]
        xs = [v.x for v in verts]; ys = [v.y for v in verts]; zs = [v.z for v in verts]
        spans.append(((max(xs) - min(xs))**2 + (max(ys) - min(ys))**2 + (max(zs) - min(zs))**2) ** 0.5)
    spans.sort()
    med = spans[len(spans)//2] if spans else 0
    zs = [v.co.z for v in me.vertices]
    print('SCALED', me.name, 'leaf_faces', n_faces, 'verts_moved', moved,
          'leaf_span_med', round(med, 4), 'z_extent', round(max(zs) - min(zs), 3),
          'scale', scale)
    return True

changed = 0
for name in TARGETS:
    me = bpy.data.meshes.get(name)
    if not me:
        print('MISSING', name)
        continue
    if scale_leaf_cards(me, LEAF_SCALE):
        changed += 1
print('CHANGED', changed, 'LEAF_SCALE', LEAF_SCALE)
if SAVE:
    bpy.ops.wm.save_mainfile()
    print('SAVED', bpy.data.filepath)
