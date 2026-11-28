# ws277 f277a (merge208 CHAIN, on ws276b): Alumni House (OSM way 232846660, university property, S of Normal Ave W at about
# x -359, y -272) as LiDAR context massing (#38 start-here item 3). Evidence: OSM outline (8 corners); 3DEP 2014 returns inside it
# (/workspace/data/alumni/lidar.npz, no class-6 points): ground 114.7 m (p50 of class-2 within 6 m), roof cells 6..8 m above
# ground over the main block (ridge ~122.7 m, running along the long side), no returns over the S wing (scan gap y -272..-275).
# Walls: the OSM outline from 113.9 (0.8 m under grade, the house stands on the coarse skirt) to eave 119.9 (UNVERIFIED), closed
# by a flat cap; a hip roof on the main block's rectangle to 122.7; a gable on the S wing to 121.5 and a hipped connector between them
# (UNVERIFIED: no returns).
# Colours: roof = NJ 2020 ortho mid-band average inside the outline (sRGB 0.24, 0.28, 0.28, linear ~0.05..0.065, lifted to
# 0.07..0.08); walls neutral cream, UNVERIFIED (no public photo found).
import bpy, bmesh
from mathutils import Vector
TAG = 'F277A'; NAME = 'WS277_Alumni_House_OSM232846660_LiDAR_massing_UNVERIFIED'
if NAME in bpy.data.objects: raise SystemExit(TAG + ' already there')
OSM = [(-364.06, -265.06), (-365.36, -271.46), (-362.94, -271.95), (-363.38, -274.12), (-358.45, -275.11), (-359.14, -278.51),
       (-355.71, -279.21), (-353.29, -267.23)]
Z0, EAVE, RIDGE, WRIDGE = 113.9, 119.9, 122.7, 121.5
p0 = Vector(OSM[0]); a = (Vector(OSM[-1]) - p0).normalized(); b = Vector((a.y, -a.x))  # a along the N side, b into the house (S)
if b.dot(Vector(OSM[2]) - p0) < 0: b = -b
L = lambda p: ((Vector(p) - p0).dot(a), (Vector(p) - p0).dot(b))
W = lambda u, v, z: (p0 + a * u + b * v).to_3d() + Vector((0, 0, z))
loc = [L(p) for p in OSM]
amax = max(u for u, v in loc); bmain = loc[1][1]  # main block: the N side to the W corner's depth
wing = [loc[5], loc[6]]; wa0, wa1 = min(u for u, v in wing), max(u for u, v in wing); wb1 = max(v for u, v in wing)
print(TAG, 'main a 0..%.2f b 0..%.2f; wing a %.2f..%.2f b %.2f..%.2f' % (amax, bmain, wa0, wa1, bmain, wb1), flush=True)
bm = bmesh.new()
def mat(name, col, rough):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name); m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF'); bs.inputs['Base Color'].default_value = col; bs.inputs['Roughness'].default_value = rough
    m.diffuse_color = col; return m
MW = mat('WS277_house_wall_cream_UNVERIFIED', (0.62, 0.58, 0.50, 1), 0.85)
MR = mat('WS277_house_roof_shingle_ortho2020_UNVERIFIED', (0.07, 0.08, 0.08, 1), 0.9)
# walls + flat cap at the eave
bot = [bm.verts.new(W(u, v, Z0)) for u, v in loc]; top = [bm.verts.new(W(u, v, EAVE)) for u, v in loc]
n = len(loc)
for i in range(n):
    j = (i + 1) % n; bm.faces.new((bot[i], bot[j], top[j], top[i])).material_index = 0
cap = bm.faces.new(top); cap.material_index = 1
cap.normal_update()
if cap.normal.z < 0: cap.normal_flip()
# hip roof on the main block (ridge along a, hips at 45 deg in plan)
h = bmain / 2
r = [W(0, 0, EAVE), W(amax, 0, EAVE), W(amax, bmain, EAVE), W(0, bmain, EAVE), W(h, h, RIDGE), W(amax - h, h, RIDGE)]
rv = [bm.verts.new(p) for p in r]
for f in ((0, 1, 5, 4), (1, 2, 5), (2, 3, 4, 5), (3, 0, 4)):
    bm.faces.new([rv[k] for k in f]).material_index = 1
# gable on the S wing (ridge along b)
wm = (wa0 + wa1) / 2
g = [W(wa0, bmain, EAVE), W(wa1, bmain, EAVE), W(wa1, wb1, EAVE), W(wa0, wb1, EAVE), W(wm, bmain + 0.01, WRIDGE), W(wm, wb1, WRIDGE)]
gv = [bm.verts.new(p) for p in g]
for f, mi in (((0, 4, 5, 3), 1), ((1, 2, 5, 4), 1), ((2, 3, 5), 0), ((0, 1, 4), 0)):
    bm.faces.new([gv[k] for k in f]).material_index = mi
# connector between the main block and the S wing (OSM corners 2..4: a %.1f..wing, b bmain..corner 4): hipped at its W end, ridge along a
# at 45 deg pitch, run 0.5 m into the wing's gable so the join is buried (Codex review: it was only the flat cap)
ca0 = min(loc[2][0], loc[3][0]); cb1 = loc[4][1]; ch = (cb1 - bmain) / 2; cz = EAVE + ch
c = [W(ca0, bmain, EAVE), W(wa0 + 0.5, bmain, EAVE), W(wa0 + 0.5, cb1, EAVE), W(ca0, cb1, EAVE), W(ca0 + ch, bmain + ch, cz), W(wa0 + 0.5, bmain + ch, cz)]
cv = [bm.verts.new(p) for p in c]
for f in ((0, 1, 5, 4), (2, 3, 4, 5), (3, 0, 4), (1, 2, 5)):
    bm.faces.new([cv[k] for k in f]).material_index = 1
print(TAG, 'connector a %.2f..%.2f b %.2f..%.2f ridge %.2f' % (ca0, wa0 + 0.5, bmain, cb1, cz), flush=True)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
me = bpy.data.meshes.new(NAME); bm.to_mesh(me); bm.free()
me.materials.append(MW); me.materials.append(MR)
o = bpy.data.objects.new(NAME, me)
col = bpy.data.collections.get('WS277_Alumni_House') or bpy.data.collections.new('WS277_Alumni_House')
if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
col.objects.link(o)
print(TAG, NAME, 'verts', len(me.vertices), 'faces', len(me.polygons), 'z', Z0, EAVE, RIDGE, WRIDGE, flush=True)
# neighbours: Void's WS172 lawn and WS173 driveway patches must stay clear of the footprint
for nm in ('WS172_frontyards_S_of_NormalAve_W_DTM2023_J5D5', 'WS173_driveway_D1_S_of_NormalAve_W_LiDAR2023_int_UNVERIFIED'):
    x = bpy.data.objects.get(nm)
    if x:
        xs = [(x.matrix_world @ v.co).x for v in x.data.vertices]
        print(TAG, nm[:40], 'min x %.2f (house max x %.2f)' % (min(xs), max(p[0] for p in OSM)), flush=True)
