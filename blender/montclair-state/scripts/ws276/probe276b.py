# ws276 probe276b (modifiers off, no save): horizontal section at z 139.0 of the Sprague L0 mass, the hidden Sprague walls and the
# Cafe Diem pieces within x -60..-36, y 24..46: each crossed face's segment (x0,y0)-(x1,y1), normal and material.
import bpy, os
from bpy.app.handlers import persistent
@persistent
def _off(*a):
    for o in bpy.data.objects:
        for m in o.modifiers: m.show_viewport = False
bpy.app.handlers.load_post.append(_off)
bpy.ops.wm.open_mainfile(filepath=os.environ['INF'])
Z = float(os.environ.get('ZS', '139.0'))
for o in bpy.data.objects:
    if o.type != 'MESH' or not any(k in o.name for k in ('Sprague Library', 'CafeDiem', 'Cafe Diem', 'bt ', 'bt_', 'bu ', 'bv ', 'bw ')): continue
    me = o.data; mw = o.matrix_world; nm = mw.to_3x3().inverted().transposed()
    for p in me.polygons:
        vs = [mw @ me.vertices[i].co for i in p.vertices]
        if min(v.z for v in vs) > Z or max(v.z for v in vs) < Z: continue
        pts = []
        for a, b in zip(vs, vs[1:] + vs[:1]):
            if (a.z - Z) * (b.z - Z) < 0 or a.z == Z:
                t = 0 if a.z == Z else (Z - a.z) / (b.z - a.z); pts.append(a.lerp(b, t))
        if len(pts) < 2: continue
        x0, y0, x1, y1 = pts[0].x, pts[0].y, pts[1].x, pts[1].y
        if max(x0, x1) < -60 or min(x0, x1) > -36 or max(y0, y1) < 24 or min(y0, y1) > 46: continue
        n = (nm @ p.normal).normalized()
        mat = me.materials[p.material_index].name if me.materials and me.materials[p.material_index] else ''
        print('S276B', o.name[:40], p.index, '(%.2f,%.2f)-(%.2f,%.2f)' % (x0, y0, x1, y1), 'n %.2f %.2f' % (n.x, n.y), mat, 'hide' if o.hide_render else '', flush=True)
