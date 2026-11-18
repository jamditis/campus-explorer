"""ut self-review polish: apron silhouette bevel (no densify), stronger S-edge/join mat Fac, modest grass extra.
Uses existing UT_bak_* where present. REVERT still via us_main REVERT=1.
"""
import bpy, bmesh, os, json, random
from mathutils import Vector, Matrix
SAVE = os.environ.get('SAVE') == '1'
D = '/workspace/nj-scenes/montclair-state/'
rnd = random.Random(20261106 + 11)
log = {}

def ensure_bak(o):
    if any(m.get('ut_bak_of') == o.name for m in bpy.data.meshes):
        return
    orig = o.data; nm = orig.name
    cp = orig.copy(); o.data = cp
    orig.name = 'UT_bak_' + nm[:50]; orig.use_fake_user = True
    orig['ut_bak_of'] = o.name; orig['ut_orig_name'] = nm
    cp.name = nm

# --- apron: force silhouette bevel on top-band edges (not only boundary) ---
apron = bpy.data.objects.get('TY Partridge W areaway apron cutting lawn bank (UNVERIFIED)')
if apron:
    ensure_bak(apron)
    bm = bmesh.new(); bm.from_mesh(apron.data)
    bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table(); bm.faces.ensure_lookup_table()
    mw = apron.matrix_world
    zs = sorted((mw @ v.co).z for v in bm.verts)
    zref = zs[int(0.90 * (len(zs) - 1))]
    top = {v for v in bm.verts if (mw @ v.co).z > zref - 0.18}
    focus = {v for v in top if -110 < (mw @ v.co).x < -96 and 243 < (mw @ v.co).y < 258} or top
    # silhouette: edges with one face in focus-top and angley, or boundary
    eu = {}
    for f in bm.faces:
        for e in f.edges:
            eu[e] = eu.get(e, 0) + 1
    cand = []
    for e in bm.edges:
        if e.verts[0] not in focus or e.verts[1] not in focus:
            continue
        if eu.get(e, 0) == 1:
            cand.append(e); continue
        # sharp-ish edge between top faces
        if len(e.link_faces) == 2:
            n0 = e.link_faces[0].normal; n1 = e.link_faces[1].normal
            if n0.dot(n1) < 0.92:
                cand.append(e)
    # xy smooth
    for _ in range(4):
        coords = {}
        for v in focus:
            nbrs = [e.other_vert(v) for e in v.link_edges if e.other_vert(v) in top]
            if len(nbrs) < 2: continue
            avg = sum((n.co for n in nbrs), Vector()) / len(nbrs)
            nc = v.co.lerp(avg, 0.40)
            coords[v] = Vector((nc.x, nc.y, v.co.z))
        for v, c in coords.items():
            v.co = c
    n_bev = 0
    if cand:
        try:
            bmesh.ops.bevel(bm, geom=cand[:120], offset=0.032, segments=1, affect='EDGES', profile=0.5)
            n_bev = min(len(cand), 120)
        except Exception as e:
            print('UT polish apron bevel fail', e)
    bm.to_mesh(apron.data); bm.free(); apron.data.update()
    log['apron_bev'] = n_bev
    log['apron_v'] = len(apron.data.vertices)
    print('UT polish apron bev', n_bev, 'verts', log['apron_v'])

# bump edge soft Fac on paving mats
for on in ('QXP_pedestrian_area_313024781_paving_UNVERIFIED',
           'QY_plaza_rim_band_313024781_UNVERIFIED',
           'Footpaths_OSM'):
    o = bpy.data.objects.get(on)
    if not o or not o.material_slots: continue
    mat = o.material_slots[0].material
    if mat is None or mat.node_tree is None: continue
    for n in mat.node_tree.nodes:
        if (n.name.startswith('UT_edge_soft') or n.name.startswith('UR_edge_soft') or n.name.startswith('UQ_edge_soft') or n.name.startswith('UP_edge_soft') or n.name.startswith('UO_edge_soft')) and 'Fac' in n.inputs:
            n.inputs['Fac'].default_value = min(0.44, n.inputs['Fac'].default_value + 0.04)
            log.setdefault('edge_fac_bump', []).append(on)

# bump UG/SA join soft Fac further
for on in ('UG_Partridge_E_seam_fill_lawn_UNVERIFIED', 'SA_ground_lower_patch_UNVERIFIED'):
    o = bpy.data.objects.get(on)
    if not o or not o.material_slots: continue
    mat = o.material_slots[0].material
    if mat is None or mat.node_tree is None: continue
    for n in mat.node_tree.nodes:
        if (n.name.startswith(('UT_join_soft','UR_join_soft','UQ_join_soft','UP_join_soft','UO_join_soft','UN_join_soft','UM_join_soft','UL_join_soft','UK_join_soft'))
                and 'Fac' in n.inputs):
            n.inputs['Fac'].default_value = min(0.48, n.inputs['Fac'].default_value + 0.04)
            log.setdefault('join_fac_bump', []).append((on, n.name, n.inputs['Fac'].default_value))

# modest grass extra onto UQ grass mesh
COLN = 'UT_Partridge_E_strip_grass_fill_UNVERIFIED'
src = bpy.data.objects.get(COLN)
XA, XB = -67.5, -35.5
Y_WALK, Y_PLAZA = 247.0, 251.2
existing = []
for gn in ('UH_Partridge_E_seam_grass_points_UNVERIFIED','UI_Partridge_E_strip_grass_points_UNVERIFIED',
           'UJ_Partridge_E_strip_grass_fill_UNVERIFIED','UK_Partridge_E_strip_grass_fill_UNVERIFIED',
           'UL_Partridge_E_strip_grass_fill_UNVERIFIED','UM_Partridge_E_strip_grass_fill_UNVERIFIED',
           'UN_Partridge_E_strip_grass_fill_UNVERIFIED','UO_Partridge_E_strip_grass_fill_UNVERIFIED',
           'UP_Partridge_E_strip_grass_fill_UNVERIFIED',
           'UQ_Partridge_E_strip_grass_fill_UNVERIFIED',
           'UR_Partridge_E_strip_grass_fill_UNVERIFIED',
           'US_Partridge_E_strip_grass_fill_UNVERIFIED',
           'UT_Partridge_E_strip_grass_fill_UNVERIFIED'):
    go = bpy.data.objects.get(gn)
    if go: existing.extend(tuple(v.co) for v in go.data.vertices)
added = 0
if src:
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
    blk = [(o.evaluated_get(dg), o.matrix_world) for n in blk_names if (o:=bpy.data.objects.get(n))]
    def hit_blk(x,y,z):
        for e,mw in blk:
            iw = mw.inverted(); o0 = iw@Vector((x,y,z+40)); o1 = iw@Vector((x,y,z-0.05)); d=o1-o0
            if d.length < 1e-6: continue
            if e.ray_cast(o0, d.normalized(), distance=d.length)[0]: return True
        return False
    pts = list(existing); new_pts=[]
    for _ in range(1000):
        if rnd.random() < 0.55:
            x = -62.0 + rnd.random()*18.0; y = 247.6 + rnd.random()*3.0
        else:
            x = XA + rnd.random()*(XB-XA); y = Y_WALK + 0.25 + rnd.random()*(Y_PLAZA-Y_WALK-0.4)
        if inside(x,y): continue
        if any((x-p[0])**2+(y-p[1])**2 < 0.26**2 for p in pts[::max(1,len(pts)//90)] + pts[-160:]):
            continue
        r = uge.ray_cast(ugo2.matrix_world.inverted()@Vector((x,y,400)),
                         (ugo2.matrix_world.inverted().to_3x3()@Vector((0,0,-1))).normalized())
        if not r[0]: continue
        z = (umw2@r[1]).z
        if hit_blk(x,y,z): continue
        new_pts.append((x,y,z-0.004)); pts.append(new_pts[-1]); added += 1
        if added >= 40: break
    if added:
        bm = bmesh.new(); bm.from_mesh(src.data)
        for p in new_pts: bm.verts.new(p)
        bm.to_mesh(src.data); bm.free(); src.data.update()
        log['grass_extra'] = added
        log['uq_grass_total'] = len(src.data.vertices)
        print('UT polish grass_extra', added, 'total', log['uq_grass_total'])
    else:
        log['grass_extra'] = 0

json.dump(log, open(D+'data/ut/ut_polish.json','w'), indent=1)
print('UT polish LOG', log)
print('UT objects', len(bpy.data.objects))
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
