"""2026-10-21 session dV (~10:40 AM ET). Inside CCOM's 1st-floor corridors the OSM/LiDAR building wall ("School of Communication
and Media ...") starts ~0.3 m ABOVE the dd terrazzo floors, so after the dV terrain cut the terrain step just outside the wall
showed through that gap as a green band under the south windows (dV test corrS_after4.jpg). Joe's photos 04/05 show plain
white walls down to a grey base. Fix: on every dd floor-rectangle edge where a horizontal ray at floor+0.12 m finds no wall within
0.06 m beyond the slab edge, add a vertical skirt quad 0.04 m outside the slab edge (1 cm inside the building wall face at 0.05),
floor-0.05 -> floor+0.75, using that corridor's own back-wall material. Collection CCOM_corridor_skirt_dV; idempotent (rebuilt
each run); REVERT=1 removes. SAVE=1 saves. Interior only; not visible from outside (behind the building wall)."""
import bpy, os
from mathutils import Vector
CN = 'CCOM_corridor_skirt_dV'
if CN in bpy.data.collections:
    C = bpy.data.collections[CN]
    for o in list(C.objects): me = o.data; bpy.data.objects.remove(o); bpy.data.meshes.remove(me)
    bpy.data.collections.remove(C)
if os.environ.get('REVERT') == '1': print('DVSKIRT reverted', flush=True)
else:
    P0 = bpy.data.collections['CCOM_1f_interior_full_dd']
    C = bpy.data.collections.new(CN); P0.children.link(C)
    dg = bpy.context.evaluated_depsgraph_get(); scn = bpy.context.scene; made = []
    for o in [o for o in P0.all_objects if o.type == 'MESH' and o.name.endswith('_floor_terrazzo')]:
        pre = o.name[:-len('_floor_terrazzo')]
        mat = bpy.data.objects[pre + '_back_wall'].active_material
        top = max(o.data.polygons, key=lambda p: (o.matrix_world.to_3x3() @ p.normal).z)
        P = [o.matrix_world @ o.data.vertices[i].co for i in top.vertices]; zt = max(p.z for p in P)
        R = [p.to_2d() for p in P]; c = sum(R, Vector((0, 0))) / len(R)
        for i in range(len(R)):
            a, b = R[i], R[(i + 1) % len(R)]; d = (b - a).normalized(); nrm = Vector((-d.y, d.x))
            if nrm.dot(a - c) < 0: nrm = -nrm          # outward
            gap = 0
            for t in (0.15, 0.3, 0.5, 0.7, 0.85):
                q = a + (b - a) * t - nrm * 0.5; org = Vector((q.x, q.y, zt + 0.12)); dv = Vector((nrm.x, nrm.y, 0)); wall = None
                for _ in range(8):
                    h, loc, no, idx, ob, mt = scn.ray_cast(dg, org, dv, distance=3.0)
                    if not h: break
                    if ob.name.startswith('Terrain') or 'grass' in ob.name.lower() or 'rug' in ob.name or ob.name == o.name: org = loc + dv * 1e-3; continue
                    wall = (loc.to_2d() - a).dot(nrm); break
                if wall is None or wall > 0.06: gap += 1
            if gap < 2: continue
            A = a + nrm * 0.04; B = b + nrm * 0.04
            vs = [(A.x, A.y, zt - 0.05), (B.x, B.y, zt - 0.05), (B.x, B.y, zt + 0.75), (A.x, A.y, zt + 0.75)]
            me = bpy.data.meshes.new('%s_skirt_%d_dV' % (pre, i)); me.from_pydata(vs, [], [(0, 1, 2, 3)]); me.materials.append(mat)
            ob = bpy.data.objects.new(me.name, me); C.objects.link(ob); made.append((ob.name, gap))
    print('DVSKIRT made', made, flush=True)
if os.environ.get('SAVE') == '1': bpy.ops.wm.save_mainfile(); print('DVSKIRT_SAVED', flush=True)
