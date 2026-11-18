# wa: move WA_CAM_eye_Bohn_S_wing_from_SW to a tree-clear eye-level station (ray visibility search)
import bpy, json, math, os
from mathutils import Vector
SAVE = os.environ.get('SAVE') == '1'
log = json.load(open('/workspace/nj-scenes/montclair-state/data/wa/apply.json'))
O = Vector((log['origin'][0], log['origin'][1], 0)); U = Vector((log['U'][0], log['U'][1], 0)); N = Vector((log['N'][0], log['N'][1], 0))
U.normalize(); N.normalize()
dg = bpy.context.evaluated_depsgraph_get(); sc = bpy.context.scene
def gz(x, y):
    for gn in ('Terrain_LiDAR_DTM_1m', 'Context_skirt_3DEP_ortho_4km'):
        go = bpy.data.objects.get(gn)
        if not go: continue
        e = go.evaluated_get(dg); iw = go.matrix_world.inverted()
        r = e.ray_cast(iw @ Vector((x, y, 400)), (iw.to_3x3() @ Vector((0, 0, -1))).normalized())
        if r[0]: return (go.matrix_world @ r[1]).z
    return None
tz = [124, 130, 137, 143, 148]; tt = [-4.0, -1.0, 2.0, 5.0]
best = None; res = []
for ti in range(-50, 6, 4):
    for ni in range(14, 70, 4):
        p = O + U * ti + N * ni; g = gz(p.x, p.y)
        if g is None: continue
        c = Vector((p.x, p.y, g + 1.7)); ok = 0; tot = 0
        for a in tt:
            for z in tz:
                q = O + U * a + N * 0.3; q = Vector((q.x, q.y, z)); d = q - c
                hit, loc, nor, idx, ob, mx = sc.ray_cast(dg, c, d.normalized(), distance=d.length + 1.0)
                tot += 1
                if hit and ob and (('Bohn' in ob.name) or ob.name.startswith(('VW_', 'WA_'))): ok += 1
        res.append((ok / tot, ti, ni, round(g, 2)))
res.sort(reverse=True)
print('WACAM top', res[:6])
sc_, ti, ni, g = res[0]
cam = bpy.data.objects['WA_CAM_eye_Bohn_S_wing_from_SW']
p = O + U * ti + N * ni; cam.location = (p.x, p.y, g + 1.7)
q = O + U * 0.0 + N * 0.0; d = Vector((q.x - p.x, q.y - p.y, 140.0 - (g + 1.7)))
cam.rotation_euler = (math.pi / 2 + math.atan2(d.z, math.hypot(d.x, d.y)), 0, math.atan2(d.y, d.x) - math.pi / 2)
cam.data.lens = 22
log['eye_cam_station'] = dict(t=ti, n=ni, ground=g, vis=sc_)
json.dump(log, open('/workspace/nj-scenes/montclair-state/data/wa/apply.json', 'w'), indent=2)
print('WACAM set', ti, ni, g, sc_)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
