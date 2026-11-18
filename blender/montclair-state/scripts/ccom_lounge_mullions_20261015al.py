"""2026-10-15 ~7:45 AM ET (tag 20261015al). Lounge east curtain wall: photo (refs/ccom_x/02) shows 6 narrow columns of panes with
slim dark mullions; jf model had 4 wide columns. Hide jf vertical mullions mull0-4, add 5 slimmer verticals at L/6 spacing
(same depth/z range as the jf ones). Column count from photo, UNVERIFIED +-1. Run after ccom_lounge_photo_20261015al.py.
Run: ../tools/blender_slot.sh -b montclair_state.blend --python scripts/ccom_lounge_mullions_20261015al.py -- --save"""
import bpy, bmesh, sys, math
from mathutils import Vector, Matrix
ARGV = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
TAG = '20261015al'
A = Vector((23.45, -24.78)); B = Vector((25.0, -18.76)); T = (B - A).normalized(); N = Vector((T.y, -T.x)); L = (B - A).length
col = bpy.data.collections['CCOM_lounge_photo_' + TAG]
for o in list(col.objects):
    if o.name.startswith('CCOM_lounge_mull6_'): bpy.data.objects.remove(o)
olds = [o for o in bpy.data.objects if o.name.startswith('CCOM_lounge_east_mull') and o.name.endswith('_20261014jf')]
ss, zs = [], []
for o in olds:
    vs = [o.matrix_world @ v.co for v in o.data.vertices]
    ss += [(v.xy - A).dot(N) for v in vs]; zs += [v.z for v in vs]
    o.hide_render = True; o.hide_viewport = True
s0, s1, z0, z1 = min(ss), max(ss), min(zs), max(zs)
print('OLD mullions', len(olds), 's', round(s0, 3), round(s1, 3), 'z', round(z0, 2), round(z1, 2), flush=True)
m = bpy.data.materials['CCOM_maroon_frame_20261014jf']; W = 0.085
for k in range(0, 7):   # 0 and 6 = edge frames (jf mull0/mull4 were the edges)
    c = A + T * (L * k / 6) + N * ((s0 + s1) / 2)
    me = bpy.data.meshes.new('CCOM_lounge_mull6_%d_' % k + TAG); bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Diagonal((W, s1 - s0, z1 - z0, 1))); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(me.name, me); col.objects.link(o); me.materials.append(m)
    o.matrix_world = Matrix.Translation((c.x, c.y, (z0 + z1) / 2)) @ Matrix.Rotation(math.atan2(T.y, T.x), 4, 'Z')
print('NEW mullions 7 width', W, flush=True)
if '--save' in ARGV: bpy.ops.wm.save_mainfile(); print('SAVED', bpy.data.filepath, flush=True)
