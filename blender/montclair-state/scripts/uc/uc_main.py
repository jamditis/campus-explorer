"""Session uc (Nov 5 2026 ~12:25–1:10 PM ET, MAIN): context wall-top vs roof gap audit + Finley Hall fix.

AUDIT (data/uc/): paired Buildings_context walls vs roof (LiDAR) slabs. Freeman-style open band =
rim verts ≥0.5 m below a flat/near-flat roof so eye/oblique cams see into the empty shell.
Result: after ub's Freeman fix, the only remaining clear flat-roof case is Finley Hall (all wall
tops at 145.42 while roof up-faces span 145.42–146.17, med 145.92 → open band up to ~0.75 m).
Pitched-roof buildings (Cole/Schmitt/Morehead/CCOM/…) meet eaves; multi-level (Kasser) OK.
University Hall skipped. Hero-detailed buildings left alone.

FIX: lift Finley Hall wall top verts (z>144.5) to 146.22 (roof max +0.05). Roof height MEASURED
(LiDAR); wall-top=roof UNVERIFIED. Originals in data/uc/finley_walls_orig.json.

SECONDARY: thin parapet/coping ring on Freeman Hall flat roof (bare after ub). UNVERIFIED profile.

REVERT=1 restores Finley verts + removes uc_obj meshes/cams. Tag uc_fix on Finley walls.
"""
import bpy, os, json, math
from mathutils import Vector

REV = os.environ.get('REVERT') == '1'
SAVE = os.environ.get('SAVE') == '1'
DATA = '/workspace/nj-scenes/montclair-state/data/uc'
os.makedirs(DATA, exist_ok=True)
J_FIN = os.path.join(DATA, 'finley_walls_orig.json')
TOPZ = 146.22  # Finley roof max ~146.17 + 0.05
THRESH = 144.5  # Finley top-band (wall max was 145.42; base ~137.7)


def remove_uc_objects():
    removed = 0
    for o in list(bpy.data.objects):
        if o.get('uc_obj'):
            is_cam = o.type == 'CAMERA'
            cd = o.data
            bpy.data.objects.remove(o, do_unlink=True)
            if is_cam and cd:
                bpy.data.cameras.remove(cd)
            elif cd and getattr(cd, 'users', 1) == 0:
                if hasattr(cd, 'materials'):
                    bpy.data.meshes.remove(cd)
            removed += 1
    # orphan mats
    for m in list(bpy.data.materials):
        if m.get('uc_mat') and m.users == 0:
            bpy.data.materials.remove(m)
    # empty collections
    for c in list(bpy.data.collections):
        if c.name.startswith('UC_') and len(c.objects) == 0 and len(c.children) == 0:
            bpy.data.collections.remove(c)
    return removed


def ensure_coll(name):
    c = bpy.data.collections.get(name)
    if not c:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
    return c


def fix_finley():
    o = bpy.data.objects['Finley Hall walls']
    me = o.data
    if o.get('uc_fix'):
        raise SystemExit('UC Finley already applied')
    d = {str(v.index): v.co.z for v in me.vertices if v.co.z > THRESH}
    if not os.path.exists(J_FIN):
        json.dump(d, open(J_FIN, 'w'))
    for k in d:
        me.vertices[int(k)].co.z = TOPZ
    o['uc_fix'] = 1
    me.update()
    print('UC Finley lifted', len(d), 'top verts to', TOPZ,
          'min orig', round(min(d.values()), 3), 'max', round(max(d.values()), 3))
    return len(d)


def revert_finley():
    o = bpy.data.objects['Finley Hall walls']
    me = o.data
    if not os.path.exists(J_FIN):
        print('UC no finley orig json')
        return 0
    d = json.load(open(J_FIN))
    for k, z in d.items():
        me.vertices[int(k)].co.z = z
    o.pop('uc_fix', None)
    me.update()
    print('UC Finley REVERTED', len(d))
    return len(d)


def freeman_parapet():
    """Thin UNVERIFIED coping ring on Freeman flat roof perimeter."""
    if bpy.data.objects.get('UC_Freeman_parapet_coping_UNVERIFIED'):
        print('UC parapet exists')
        return
    ro = bpy.data.objects['Freeman Hall roof (LiDAR)']
    rmw = ro.matrix_world
    # Collect rim: boundary edges of up-faces, or convex hull of roof verts in XY at roof z
    # Simpler: ordered outline via angle sort around centroid of roof verts
    pts = [rmw @ v.co for v in ro.data.vertices]
    if not pts:
        return
    cx = sum(p.x for p in pts) / len(pts)
    cy = sum(p.y for p in pts) / len(pts)
    rz = pts[0].z  # flat
    # unique-ish rim via angular bins of outermost points
    import math as _m
    bins = {}
    for p in pts:
        ang = _m.atan2(p.y - cy, p.x - cx)
        k = int(_m.floor(ang / (2 * _m.pi) * 64)) % 64
        dist = (p.x - cx) ** 2 + (p.y - cy) ** 2
        if k not in bins or dist > bins[k][0]:
            bins[k] = (dist, p.x, p.y)
    keys = sorted(bins)
    ring = [(bins[k][1], bins[k][2]) for k in keys]
    if len(ring) < 4:
        print('UC parapet ring too small', len(ring))
        return
    # close
    ring.append(ring[0])

    H = 0.28   # parapet height UNVERIFIED
    W = 0.22   # width UNVERIFIED
    inset = 0.05
    # Build box-section ring: outer + inner footprints
    def offset_ring(poly, dist):
        # simple outward normal offset in XY
        out = []
        n = len(poly) - 1
        for i in range(n):
            x0, y0 = poly[i]
            x1, y1 = poly[(i + 1) % n]
            xm, ym = poly[(i - 1) % n]
            # edge normals (outward approx from centroid)
            e1x, e1y = x1 - x0, y1 - y0
            # inward toward centroid
            tx, ty = cx - x0, cy - y0
            # perpendicular
            nx, ny = -e1y, e1x
            ln = _m.hypot(nx, ny) or 1
            nx, ny = nx / ln, ny / ln
            # flip if pointing toward centroid
            if nx * tx + ny * ty > 0:
                nx, ny = -nx, -ny
            out.append((x0 + nx * dist, y0 + ny * dist))
        out.append(out[0])
        return out

    outer = offset_ring(ring, 0.02)  # slight out past roof edge
    inner = offset_ring(ring, -(W))  # inward by width

    # Mesh: for each segment, a box (outer-inner) extruded H above roof
    verts = []
    faces = []
    nseg = len(outer) - 1
    for i in range(nseg):
        o0, o1 = outer[i], outer[i + 1]
        i0, i1 = inner[i], inner[i + 1]
        z0 = rz
        z1 = rz + H
        base = len(verts)
        # 8 verts of segment box
        verts += [
            (o0[0], o0[1], z0), (o1[0], o1[1], z0), (i1[0], i1[1], z0), (i0[0], i0[1], z0),
            (o0[0], o0[1], z1), (o1[0], o1[1], z1), (i1[0], i1[1], z1), (i0[0], i0[1], z1),
        ]
        faces += [
            (base, base+1, base+5, base+4),  # outer
            (base+3, base+7, base+6, base+2),  # inner
            (base+4, base+5, base+6, base+7),  # top
            (base, base+3, base+2, base+1),  # bottom
            (base, base+4, base+7, base+3),  # start cap
            (base+1, base+2, base+6, base+5),  # end cap
        ]

    me = bpy.data.meshes.new('UC_Freeman_parapet_coping_UNVERIFIED')
    me.from_pydata(verts, [], faces)
    me.update()
    obj = bpy.data.objects.new('UC_Freeman_parapet_coping_UNVERIFIED', me)
    obj['uc_obj'] = 1
    obj['UNVERIFIED'] = 1
    coll = ensure_coll('UC_Freeman_parapet_UNVERIFIED')
    coll.objects.link(obj)

    mat = bpy.data.materials.get('UC_Freeman_coping_UNVERIFIED')
    if not mat:
        mat = bpy.data.materials.new('UC_Freeman_coping_UNVERIFIED')
        mat.use_nodes = True
        mat['uc_mat'] = 1
        nt = mat.node_tree
        nt.nodes.clear()
        out = nt.nodes.new('ShaderNodeOutputMaterial')
        bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
        bsdf.inputs['Base Color'].default_value = (0.22, 0.22, 0.24, 1)
        bsdf.inputs['Roughness'].default_value = 0.55
        nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
    print('UC Freeman parapet: segs', nseg, 'H', H, 'W', W, 'z', rz)
    return obj



def make_cams():
    """UC cams aimed at Finley Hall (x[-64,-15] y[88,125])."""
    from mathutils import Vector
    fin = bpy.data.objects['Finley Hall walls']
    mw = fin.matrix_world
    xs=[]; ys=[]; zs=[]
    for v in fin.data.vertices:
        c = mw @ v.co; xs.append(c.x); ys.append(c.y); zs.append(c.z)
    cx=(min(xs)+max(xs))/2; cy=(min(ys)+max(ys))/2; cz=max(zs)
    specs = {
        'UC_CAM_oblique_Finley_area_from_SW': ((cx-55, cy-70, cz+35), (cx, cy, cz-1), 32),
        'UC_CAM_eye_Finley_from_S': ((cx, cy-35, 141.5), (cx, cy, 145.5), 35),
        'UC_CAM_eye_Finley_from_E': ((cx+40, cy, 142.0), (cx, cy, 145.5), 35),
        'UC_CAM_closeup_Finley_wall_top': ((max(xs)+8, min(ys)-5, cz+4), (max(xs)-2, min(ys)+8, cz), 45),
    }
    # Freeman parapet closeup (secondary)
    fr = bpy.data.objects['Freeman Hall roof (LiDAR)']
    fx=[(fr.matrix_world@v.co).x for v in fr.data.vertices]
    fy=[(fr.matrix_world@v.co).y for v in fr.data.vertices]
    fz=(fr.matrix_world@fr.data.vertices[0].co).z
    fcx,fcy=(min(fx)+max(fx))/2,(min(fy)+max(fy))/2
    specs['UC_CAM_closeup_Freeman_parapet'] = ((fcx-25, fcy-30, fz+8), (fcx, fcy, fz+0.3), 40)
    coll = ensure_coll('UC_cams')
    for name, (loc, target, lens) in specs.items():
        if name in bpy.data.objects:
            obj = bpy.data.objects[name]
        else:
            cam = bpy.data.cameras.new(name)
            obj = bpy.data.objects.new(name, cam)
            coll.objects.link(obj)
        # also ensure in UC_cams
        if obj.name not in coll.objects:
            try: coll.objects.link(obj)
            except: pass
        obj.location = loc
        obj.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
        obj.data.lens = lens
        obj['uc_obj'] = 1
        print('UC cam', name)


if REV:
    n = revert_finley()
    r = remove_uc_objects()
    print('UC REVERT done finley', n, 'removed_uc', r)
else:
    fix_finley()
    freeman_parapet()
    make_cams()
    print('UC apply done')

if SAVE:
    bpy.ops.wm.save_mainfile()
    print('SAVED')
