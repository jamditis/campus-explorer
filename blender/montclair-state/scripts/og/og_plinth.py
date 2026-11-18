"""Session og (Oct 31 2026 ~8:50 AM ET), MAIN, Schmitt Hall: the LiDAR terrain falls ~5 m from S (138.6) to N/NE (133.1) outside
the footprint, but the wall bottoms sat at 137.8-138.2 -> the N half floated over a dark void. Wall-bottom verts (z < 138.3) are
dropped to (min terrain within 0.8 m) - 0.3 m, so the stucco runs down to grade (exposed lower storey on the slope; its windows
are UNVERIFIED and not added yet). Run AFTER og_schmitt_windows.py and og_build.py. REVERT=1 restores the pre-plinth mesh."""
import bpy, os, sys, json
from mathutils import Vector
wo = bpy.data.objects['Schmitt Hall walls']; PRE = 'Schmitt walls (pre-og-plinth)'
if os.environ.get('REVERT') == '1':
    pm = bpy.data.meshes.get(PRE)
    if pm:
        old = wo.data; wo.data = pm.copy(); wo.data.name = 'Schmitt Hall walls'; bpy.data.meshes.remove(old); bpy.data.meshes.remove(pm)
    if 'og_plinth' in wo: del wo['og_plinth']
    print('REVERTED'); bpy.ops.wm.save_mainfile() if '--save' in sys.argv else None; raise SystemExit(0)
pm = bpy.data.meshes.get(PRE)
if pm is not None and wo.get('og_plinth'):
    old = wo.data; wo.data = pm.copy(); wo.data.name = 'Schmitt Hall walls'; bpy.data.meshes.remove(old)
else:
    pm = wo.data.copy(); pm.name = PRE; pm.use_fake_user = True
ter = bpy.data.objects['Terrain_LiDAR_DTM_1m']; ti = ter.matrix_world.inverted()
def tz(x, y):
    h, l, n, i = ter.ray_cast(ti @ Vector((x, y, 400)), (0, 0, -1))
    return (ter.matrix_world @ l).z if h else None
me = wo.data; mw = wo.matrix_world; mi = mw.inverted()
moved = 0; mx = 0.0
for v in me.vertices:
    p = mw @ v.co
    if p.z >= 138.3: continue
    zs = [tz(p.x + dx, p.y + dy) for dx, dy in ((0, 0), (0.8, 0), (-0.8, 0), (0, 0.8), (0, -0.8), (0.56, 0.56), (-0.56, 0.56), (0.56, -0.56), (-0.56, -0.56))]
    zs = [z for z in zs if z is not None]
    if not zs: continue
    nz = min(zs) - 0.3
    if nz < p.z:
        mx = max(mx, p.z - nz); v.co = mi @ Vector((p.x, p.y, nz)); moved += 1
me.update()
wo['og_plinth'] = json.dumps(dict(moved=moved, max_drop=round(mx, 2)))
print('plinth verts moved', moved, 'max drop', round(mx, 2))
if '--save' in sys.argv: bpy.ops.wm.save_mainfile(); print('SAVED')
