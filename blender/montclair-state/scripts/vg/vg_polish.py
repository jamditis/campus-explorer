"""vg polish after WIP review: reframe S/E cams; punch SE spandrel terracotta; mild BP lift. SAVE=1."""
import bpy, os, json
from mathutils import Vector
SAVE = os.environ.get('SAVE') == '1'
D = '/workspace/nj-scenes/montclair-state/'
DATA = D + 'data/vg'
OSM = json.load(open(D + 'data/uv/freeman_osm_probe.json'))
GR = float(json.load(open(D + 'data/uv/uv_main.json')).get('GR', 129.053))
OUT = 0.08
log = {'session': 'vg_polish', 'fixes': []}

# A) Spandrel more terracotta (was reading taupe/dark in S closeup)
m = bpy.data.materials.get('VG_Freeman_SE_spandrel_deep_UNVERIFIED')
if m and m.use_nodes:
    b = m.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Base Color'].default_value = (0.55, 0.20, 0.11, 1.0)
        b.inputs['Roughness'].default_value = 0.72
        log['fixes'].append('SE_spandrel_terracotta_punch')

# B) Reframe S closeup — pull back, full bay height
e3 = [e for e in OSM['edges'] if e['i'] == 3][0]
U3 = Vector((e3['u'][0], e3['u'][1], 0)).normalized()
N3 = Vector((e3['n'][0], e3['n'][1], 0)).normalized()
A3 = Vector((e3['a'][0], e3['a'][1], 0))
c_s = A3 + U3 * 7.5
cam = bpy.data.objects.get('VG_CAM_closeup_Freeman_S_pane_grid')
if cam:
    cam.location = (c_s.x + N3.x * 9.0, c_s.y + N3.y * 9.0, GR + 7.5)
    direction = Vector((c_s.x + N3.x * (OUT + 0.22), c_s.y + N3.y * (OUT + 0.22), GR + 8.5)) - Vector(cam.location)
    cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    if cam.data: cam.data.lens = 40
    log['fixes'].append('S_closeup_pullback_full_bay')

# C) E eye — slide south along facade to clear NW tree, still show pane grid
e5 = [e for e in OSM['edges'] if e['i'] == 5][0]
U5 = Vector((e5['u'][0], e5['u'][1], 0)).normalized()
N5 = Vector((e5['n'][0], e5['n'][1], 0)).normalized()
A5 = Vector((e5['a'][0], e5['a'][1], 0))
L5 = e5['len']
# pick bay ~0.55 along edge (further from N trees)
c_e = A5 + U5 * (L5 * 0.55)
cam2 = bpy.data.objects.get('VG_CAM_eye_Freeman_E_pane_grid')
if cam2:
    cam2.location = (c_e.x + N5.x * 16.0, c_e.y + N5.y * 16.0, GR + 5.0)
    direction = Vector((c_e.x, c_e.y, GR + 8.5)) - Vector(cam2.location)
    cam2.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    if cam2.data: cam2.data.lens = 32
    log['fixes'].append('E_eye_slide_clear_tree')

cam3 = bpy.data.objects.get('VG_CAM_closeup_Freeman_E_pane_grid')
if cam3:
    cam3.location = (c_e.x + N5.x * 6.0, c_e.y + N5.y * 6.0, GR + 6.5)
    direction = Vector((c_e.x + N5.x * (OUT + 0.22), c_e.y + N5.y * (OUT + 0.22), GR + 8.0)) - Vector(cam3.location)
    cam3.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    if cam3.data: cam3.data.lens = 48
    log['fixes'].append('E_closeup_reframe')

# D) SE oblique — ensure good overview of S+E
cent = A3 + U3 * (e3['len'] * 0.45)
cam4 = bpy.data.objects.get('VG_CAM_oblique_Freeman_from_SE')
if cam4:
    # from SE looking NW at Freeman
    cam4.location = (cent.x + 28.0, cent.y + 18.0, GR + 28.0)
    direction = Vector((cent.x - 8.0, cent.y - 20.0, GR + 6.0)) - Vector(cam4.location)
    cam4.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
    if cam4.data: cam4.data.lens = 28
    log['fixes'].append('SE_oblique_reframe')

# lettering check
let = bpy.data.objects.get('UV_Freeman_N_lettering_GRACE_H_FREEMAN_HALL_UNVERIFIED')
if let:
    mw = let.matrix_world
    log['letter'] = {
        'body': let.data.body, 'size': round(let.data.size, 6),
        'loc': [round(mw[0][3], 4), round(mw[1][3], 4), round(mw[2][3], 4)],
    }

json.dump(log, open(DATA + '/vg_polish.json', 'w'), indent=2)
print('VG POLISH', json.dumps(log, indent=2))
print('OBJECTS', len(bpy.data.objects))
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED')
