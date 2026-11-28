# ws276 probe276a (modifiers off, no save): Sprague Library east side at the ofj-ceinteriors door 1 (-50.20, 34.99, sill 137.90,
# facing 103 deg). Lists every object whose world bbox meets x -60..-36, y 24..46, and for meshes the east/west-facing faces
# (|n.x| > 0.6) that cross the door line y 34..36 between z 137.5 and 141: x, z range, area, material.
import bpy, os, json
from bpy.app.handlers import persistent
from mathutils import Vector
@persistent
def _off(*a):
    for o in bpy.data.objects:
        for m in o.modifiers: m.show_viewport = False
bpy.app.handlers.load_post.append(_off)
bpy.ops.wm.open_mainfile(filepath=os.environ['INF'])
X0, X1, Y0, Y1 = -60, -36, 24, 46
out = []
for o in bpy.data.objects:
    if o.type not in ('MESH', 'CURVE', 'FONT', 'EMPTY'): continue
    bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
    lo = [min(v[i] for v in bb) for i in range(3)]; hi = [max(v[i] for v in bb) for i in range(3)]
    if hi[0] < X0 or lo[0] > X1 or hi[1] < Y0 or lo[1] > Y1 or o.type == 'EMPTY': continue
    if hi[0] - lo[0] > 400 or hi[1] - lo[1] > 400: continue  # terrain, skirt
    rec = {'name': o.name, 'type': o.type, 'lo': [round(v, 2) for v in lo], 'hi': [round(v, 2) for v in hi],
           'hide': o.hide_render, 'colls': [c.name for c in o.users_collection]}
    if o.type == 'MESH':
        me = o.data; mw = o.matrix_world; nm = mw.to_3x3().inverted().transposed()
        rec['verts'] = len(me.vertices)
        rec['mods'] = [m.type + ':' + m.name for m in o.modifiers]
        faces = []
        for p in me.polygons:
            n = (nm @ p.normal).normalized()
            if abs(n.x) < 0.6: continue
            vs = [mw @ me.vertices[i].co for i in p.vertices]
            ys = [v.y for v in vs]; zs = [v.z for v in vs]; xs = [v.x for v in vs]
            if max(ys) < 34 or min(ys) > 36 or max(zs) < 137.5 or min(zs) > 141: continue
            mat = me.materials[p.material_index].name if me.materials and p.material_index < len(me.materials) and me.materials[p.material_index] else ''
            faces.append([p.index, round(sum(xs) / len(xs), 2), round(n.x, 2), round(min(ys), 2), round(max(ys), 2), round(min(zs), 2), round(max(zs), 2), round(p.area, 2), mat])
        rec['xfaces'] = faces[:40]; rec['nxfaces'] = len(faces)
    out.append(rec)
json.dump(out, open(os.environ['OUTJ'], 'w'), indent=1)
print('P276A objects', len(out), 'with door-line x-faces', sum(1 for r in out if r.get('nxfaces')), flush=True)
