"""un self-review: modest extra grass on bald strip patches only."""
import bpy, os, json, random
from mathutils import Vector, Matrix
SAVE = os.environ.get('SAVE') == '1'
D = '/workspace/nj-scenes/montclair-state/'
rnd = random.Random(20261105 + 24)
COLN = 'UN_Partridge_leftover_polish_UNVERIFIED'
XA, XB = -67.5, -35.5
Y_WALK, Y_PLAZA = 247.0, 251.2
src = bpy.data.objects.get('UN_Partridge_E_strip_grass_fill_UNVERIFIED')
existing = []
for gn in ('UH_Partridge_E_seam_grass_points_UNVERIFIED','UI_Partridge_E_strip_grass_points_UNVERIFIED',
           'UJ_Partridge_E_strip_grass_fill_UNVERIFIED','UK_Partridge_E_strip_grass_fill_UNVERIFIED',
           'UL_Partridge_E_strip_grass_fill_UNVERIFIED','UM_Partridge_E_strip_grass_fill_UNVERIFIED',
           'UN_Partridge_E_strip_grass_fill_UNVERIFIED'):
    go = bpy.data.objects.get(gn)
    if go: existing.extend(tuple(v.co) for v in go.data.vertices)
ugo2 = bpy.data.objects['UG_Partridge_E_seam_fill_lawn_UNVERIFIED']
umw2 = ugo2.matrix_world
dg = bpy.context.evaluated_depsgraph_get()
uge = ugo2.evaluated_get(dg)
FP = [tuple(p) for p in json.load(open(D + 'data/tx/nursing_geom.json'))['footprint']]
def inside(x, y):
    c = False; n = len(FP)
    for i in range(n):
        x1,y1 = FP[i]; x2,y2 = FP[(i+1)%n]
        if (y1>y)!=(y2>y) and x < (x2-x1)*(y-y1)/(y2-y1+1e-12)+x1: c = not c
    return c
blk_names = ['QXP_pedestrian_area_313024781_paving_UNVERIFIED','QY_plaza_rim_band_313024781_UNVERIFIED',
             'Footpaths_OSM','TY_footway_313026406_to_Partridge_UNVERIFIED',
             'TY_footway_313026407_to_Partridge_UNVERIFIED','TY_footway_313026405_to_Partridge_UNVERIFIED',
             'TY Partridge entrance steps+landings (UNVERIFIED)']
blk = []
for n in blk_names:
    o = bpy.data.objects.get(n)
    if o: blk.append((o.evaluated_get(dg), o.matrix_world))
def hit_blk(x,y,z):
    for e,mw in blk:
        iw = mw.inverted(); o0 = iw@Vector((x,y,z+40)); o1 = iw@Vector((x,y,z-0.05)); d=o1-o0
        if d.length < 1e-6: continue
        if e.ray_cast(o0, d.normalized(), distance=d.length)[0]: return True
    return False
pts = list(existing); new_pts=[]; added=0
for _ in range(1200):
    if rnd.random() < 0.55:
        x = -62.0 + rnd.random()*18.0; y = 247.6 + rnd.random()*3.0
    else:
        x = XA + rnd.random()*(XB-XA); y = Y_WALK + 0.25 + rnd.random()*(Y_PLAZA-Y_WALK-0.4)
    if inside(x,y): continue
    if any((x-p[0])**2+(y-p[1])**2 < 0.28**2 for p in pts[::max(1,len(pts)//90)] + pts[-160:]):
        continue
    r = uge.ray_cast(ugo2.matrix_world.inverted()@Vector((x,y,400)),
                     (ugo2.matrix_world.inverted().to_3x3()@Vector((0,0,-1))).normalized())
    if not r[0]: continue
    z = (umw2@r[1]).z
    if hit_blk(x,y,z): continue
    new_pts.append((x,y,z-0.004)); pts.append(new_pts[-1]); added += 1
    if added >= 120: break
log = {'grass_extra': added}
if added and src:
    me = src.data
    # append verts to existing UN grass mesh
    import bmesh
    bm = bmesh.new(); bm.from_mesh(me)
    for p in new_pts:
        bm.verts.new(p)
    bm.to_mesh(me); bm.free(); me.update()
    log['un_grass_total'] = len(me.vertices)
    print('UN grass_extra added', added, 'total', log['un_grass_total'])
else:
    print('UN grass_extra none', added, bool(src))
json.dump(log, open(D+'data/un/un_grass_extra.json','w'), indent=1)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
