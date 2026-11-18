"""Session ud (Nov 5 2026 ~1:25–2:10 PM ET, MAIN, day 9 polish):
(1) Normal Ave asphalt tone: UA-scoped copy of SF_asphalt_worn_UNVERIFIED →
    UD_asphalt_worn_NormalAve_UNVERIFIED (darker + slightly warmer ramp). Swap onto
    UA asphalt objects only so Lot38 / QuadRoad keep SF. Soft-end z vs Context_skirt:
    lift verts that sit under skirt+0.04 back on top (backup vert z JSON).
(2) Partridge TY walk/apron jagged edges: densify + bevel boundary of TY footways;
    remesh apron top outline with smoother along-wall sampling via a thin UD soft-edge
    rim OR in-place boundary bevel. Mesh backups in data/ud/*.json.
ALL UNVERIFIED. Tag ud_obj / ud_mat / ud_fix. REVERT=1 restores mats + meshes + removes ud objs.
"""
import bpy, bmesh, os, json, math, shutil
from mathutils import Vector

REV = os.environ.get('REVERT') == '1'
SAVE = os.environ.get('SAVE') == '1'
D = '/workspace/nj-scenes/montclair-state/'
DATA = D + 'data/ud/'
os.makedirs(DATA, exist_ok=True)
COLN = 'UD_day9_polish_UNVERIFIED'
SRC_MAT = 'SF_asphalt_worn_UNVERIFIED'
UD_MAT = 'UD_asphalt_worn_NormalAve_UNVERIFIED'
UA_ASPHALT = [
    'UA_NormalAve_CR618_583841725_727_729_UNVERIFIED',
    'UA_CollegeAve_spur_1557427669_UNVERIFIED',
    'UA_SkylineWay_south_232846698_UNVERIFIED',
]
TY_WALKS = [
    'TY_footway_313026399_to_Partridge_UNVERIFIED',
    'TY_footway_313026403_to_Partridge_UNVERIFIED',
    'TY_footway_313026404_to_Partridge_UNVERIFIED',
    'TY_footway_313026405_to_Partridge_UNVERIFIED',
    'TY_footway_313026406_to_Partridge_UNVERIFIED',
    'TY_footway_313026407_to_Partridge_UNVERIFIED',
]
TY_APRON = 'TY Partridge W areaway apron cutting lawn bank (UNVERIFIED)'
J_MAT = DATA + 'ua_mat_slots.json'
J_Z = DATA + 'ua_asphalt_z_backup.json'
J_WALK = DATA + 'ty_walk_verts_backup.json'
J_APRON = DATA + 'ty_apron_verts_backup.json'
SKIRT_LIFT = 0.04   # target clearance above Context_skirt
# Darker + warmer than SF ramp (0.05–0.11 cool grey) — visual choice UNVERIFIED
RAMP_LO = (0.032, 0.030, 0.028, 1.0)
RAMP_HI = (0.078, 0.070, 0.060, 1.0)


def remove_ud_objects():
    n = 0
    for o in list(bpy.data.objects):
        if o.get('ud_obj'):
            me = o.data; t = o.type
            bpy.data.objects.remove(o, do_unlink=True)
            if me is not None and me.users == 0:
                if t == 'MESH':
                    bpy.data.meshes.remove(me)
                elif t == 'CAMERA':
                    bpy.data.cameras.remove(me)
            n += 1
    c = bpy.data.collections.get(COLN)
    if c and len(c.objects) == 0 and len(c.children) == 0:
        bpy.data.collections.remove(c)
    for m in list(bpy.data.materials):
        if m.get('ud_mat') and m.users == 0:
            bpy.data.materials.remove(m)
        elif m.name.startswith('UD_') and m.users == 0:
            bpy.data.materials.remove(m)
    return n


def restore_mat_slots():
    if not os.path.exists(J_MAT):
        print('UD no mat slot backup')
        return 0
    d = json.load(open(J_MAT))
    n = 0
    for name, slots in d.items():
        o = bpy.data.objects.get(name)
        if not o:
            continue
        for i, mn in enumerate(slots):
            if i >= len(o.material_slots):
                break
            m = bpy.data.materials.get(mn) if mn else None
            o.material_slots[i].material = m
        if o.get('ud_fix'):
            del o['ud_fix']
        n += 1
    # drop UD mat if orphan
    m = bpy.data.materials.get(UD_MAT)
    if m and m.users == 0:
        bpy.data.materials.remove(m)
    print('UD restored mat slots', n)
    return n


def restore_verts(path, tag):
    if not os.path.exists(path):
        print('UD no vert backup', path)
        return 0
    d = json.load(open(path))
    n = 0
    for name, verts in d.items():
        o = bpy.data.objects.get(name)
        if not o or o.type != 'MESH':
            continue
        me = o.data
        if len(me.vertices) != len(verts):
            print('UD WARN vert count mismatch', name, len(me.vertices), len(verts),
                  '— skip restore (caller should have replaced mesh)')
            continue
        for i, co in enumerate(verts):
            me.vertices[i].co = co
        me.update()
        if o.get(tag):
            del o[tag]
        n += 1
    print('UD restored verts', n, 'from', os.path.basename(path))
    return n


def restore_meshes_from_backup():
    """Restore original mesh datablocks parked on UD_bak_* objects."""
    n = 0
    for o in list(bpy.data.objects):
        if not o.name.startswith('UD_bak_'):
            continue
        target = o.get('ud_bak_for')
        if not target:
            bpy.data.objects.remove(o, do_unlink=True)
            continue
        tgt = bpy.data.objects.get(target)
        if tgt and tgt.type == 'MESH' and o.type == 'MESH' and o.data:
            work = tgt.data
            me_orig = o.data
            tgt.data = me_orig
            # ensure original name (Blender may have renamed on conflicts)
            want = o.get('ud_orig_mesh_name') or me_orig.name
            if me_orig.name != want and want:
                # free the name if a leftover work mesh holds it
                clash = bpy.data.meshes.get(want)
                if clash and clash != me_orig:
                    clash.name = (want + '_ud_stale')[:60]
                me_orig.name = want
            o.data = None
            bpy.data.objects.remove(o, do_unlink=True)
            if work and work.users == 0:
                bpy.data.meshes.remove(work)
            if tgt.get('ud_fix'):
                del tgt['ud_fix']
            n += 1
            print('UD restored mesh from bak for', target, 'mesh', me_orig.name)
        else:
            bpy.data.objects.remove(o, do_unlink=True)
    return n


def revert():
    # restore mat slots first (before removing UD mat users)
    restore_mat_slots()
    # restore z-lifted verts (topology unchanged)
    restore_verts(J_Z, 'ud_fix')
    # restore mesh topology from bak objects (walks/apron)
    restore_meshes_from_backup()
    # also restore vert-only walk backups if any remain (no bak)
    restore_verts(J_WALK, 'ud_fix')
    restore_verts(J_APRON, 'ud_fix')
    n = remove_ud_objects()
    print('UD REVERTED objs_removed', n)


revert()
if REV:
    if SAVE:
        bpy.ops.wm.save_mainfile()
        print('SAVED')
    raise SystemExit


def ensure_coll(name):
    c = bpy.data.collections.get(name)
    if not c:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
    return c


def make_ud_asphalt():
    src = bpy.data.materials.get(SRC_MAT)
    if src is None:
        raise SystemExit('missing ' + SRC_MAT)
    # remove stale copy if re-running after partial
    old = bpy.data.materials.get(UD_MAT)
    if old:
        bpy.data.materials.remove(old)
    m = src.copy()
    m.name = UD_MAT
    m['ud_mat'] = 1
    m['UNVERIFIED'] = 'UA/UD Normal Ave asphalt tone — darker/warmer than SF campus asphalt; visual choice'
    # adjust color ramp
    ramp = None
    for n in m.node_tree.nodes:
        if n.type == 'VALTORGB':
            ramp = n
            break
    if ramp and len(ramp.color_ramp.elements) >= 2:
        ramp.color_ramp.elements[0].color = RAMP_LO
        ramp.color_ramp.elements[-1].color = RAMP_HI
        # nudge positions slightly for more mid-dark
        ramp.color_ramp.elements[0].position = 0.40
        ramp.color_ramp.elements[-1].position = 0.82
    # slightly higher roughness
    b = m.node_tree.nodes.get('Principled BSDF')
    if b:
        b.inputs['Roughness'].default_value = 0.96
    print('UD made', UD_MAT, 'ramp', RAMP_LO[:3], '->', RAMP_HI[:3])
    return m


def swap_ua_mats(ud_mat):
    slots_bak = {}
    for name in UA_ASPHALT:
        o = bpy.data.objects.get(name)
        if not o:
            print('UD missing', name); continue
        slots_bak[name] = [s.material.name if s.material else None for s in o.material_slots]
        for i, s in enumerate(o.material_slots):
            if s.material and s.material.name == SRC_MAT:
                o.material_slots[i].material = ud_mat
        o['ud_fix'] = 1
        o['ud_mat_swap'] = SRC_MAT
    json.dump(slots_bak, open(J_MAT, 'w'), indent=2)
    print('UD swapped mats on', list(slots_bak.keys()))
    return slots_bak


def lift_ua_over_skirt():
    """Lift UA asphalt verts that sit under Context_skirt + SKIRT_LIFT."""
    skirt = bpy.data.objects.get('Context_skirt_3DEP_ortho_4km')
    if not skirt:
        print('UD no Context_skirt — skip z lift')
        return
    dg = bpy.context.evaluated_depsgraph_get()
    ev = skirt.evaluated_get(dg)
    mw = skirt.matrix_world
    iw = mw.inverted()
    down = (iw.to_3x3() @ Vector((0, 0, -1))).normalized()
    bak = {}
    lifted = 0
    for name in UA_ASPHALT:
        o = bpy.data.objects.get(name)
        if not o or o.type != 'MESH':
            continue
        me = o.data
        omw = o.matrix_world
        oiw = omw.inverted()
        coords = []
        for v in me.vertices:
            coords.append(list(v.co))
        bak[name] = coords
        for v in me.vertices:
            w = omw @ v.co
            r = ev.ray_cast(iw @ Vector((w.x, w.y, 400.0)), down)
            if not r[0]:
                continue
            sz = (mw @ r[1]).z
            need = sz + SKIRT_LIFT
            if w.z < need:
                w.z = need
                v.co = oiw @ w
                lifted += 1
        me.update()
        o['ud_fix'] = 1
    json.dump(bak, open(J_Z, 'w'))
    print('UD skirt-lift verts', lifted, 'clearance', SKIRT_LIFT)


def stash_mesh_backup(o, key_prefix):
    """Park the ORIGINAL mesh datablock on a hidden bak object; give o a working copy.
    Preserves original mesh name so REVERT_EXACT mesh-name hash matches.
    """
    orig_me = o.data
    work = orig_me.copy()
    # keep work name temporary; will be discarded on revert
    work.name = (('UD_work_' + o.name)[:60])
    o.data = work
    bak = bpy.data.objects.new(('UD_bak_' + o.name)[:60], orig_me)
    bak['ud_obj'] = 1
    bak['ud_bak_for'] = o.name
    bak['ud_orig_mesh_name'] = orig_me.name
    bak.hide_viewport = True
    bak.hide_render = True
    col = ensure_coll(COLN)
    col.objects.link(bak)
    return bak


def soften_walk(o):
    """Densify + bevel boundary edges of a TY footway ribbon (in place)."""
    stash_mesh_backup(o, 'walk')
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.edges.ensure_lookup_table()
    bm.verts.ensure_lookup_table()
    # Subdivide long boundary edges once for denser outline
    long_bnd = [e for e in bm.edges if e.is_boundary and e.calc_length() > 0.55]
    if long_bnd:
        bmesh.ops.subdivide_edges(bm, edges=long_bnd, cuts=1)
        bm.edges.ensure_lookup_table()
    # Bevel boundary edges lightly
    bnds = [e for e in bm.edges if e.is_boundary]
    if bnds:
        try:
            bmesh.ops.bevel(bm, geom=bnds, offset=0.08, segments=2,
                            affect='EDGES', profile=0.5)
        except Exception as e:
            print('UD bevel fail', o.name, e)
    # Mild smooth on boundary verts
    bm.verts.ensure_lookup_table()
    bverts = [v for v in bm.verts if any(e.is_boundary for e in v.link_edges)]
    for _ in range(2):
        coords = {}
        for v in bverts:
            nbrs = [e.other_vert(v).co for e in v.link_edges if e.is_boundary]
            if len(nbrs) >= 2:
                avg = sum(nbrs, Vector()) / len(nbrs)
                coords[v] = v.co.lerp(avg, 0.35)
        for v, c in coords.items():
            # keep z (drape) — only xy smooth
            v.co.x = c.x
            v.co.y = c.y
    bm.to_mesh(o.data)
    bm.free()
    o.data.update()
    o['ud_fix'] = 1
    o['UNVERIFIED_ud'] = 'boundary bevel+xy smooth UNVERIFIED; original mesh in UD_bak_*'
    print('UD softened walk', o.name, 'verts now', len(o.data.vertices))


def soften_apron(o):
    """Soften apron jagged segment joints by xy-smoothing top-edge verts + light bevel."""
    stash_mesh_backup(o, 'apron')
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bm.faces.ensure_lookup_table()
    bm.verts.ensure_lookup_table()
    # Identify top verts (upper z band)
    zs = [v.co.z for v in bm.verts]
    zmax = max(zs)
    top = [v for v in bm.verts if v.co.z > zmax - 0.08]
    # Also outer verts (min x for west apron — outward is -X)
    # Smooth top verts along their neighbours
    for _ in range(3):
        coords = {}
        for v in top:
            nbrs = [e.other_vert(v).co for e in v.link_edges
                    if e.other_vert(v) in top or e.other_vert(v).co.z > zmax - 0.08]
            if len(nbrs) >= 2:
                avg = sum(nbrs, Vector()) / len(nbrs)
                coords[v] = v.co.lerp(avg, 0.40)
        for v, c in coords.items():
            v.co.x = c.x
            v.co.y = c.y
            # keep z
    # Bevel sharp edges on top faces
    top_edges = [e for e in bm.edges
                 if all(v.co.z > zmax - 0.08 for v in e.verts) and e.calc_length() > 0.3]
    # subdivide long top edges
    if top_edges:
        long = [e for e in top_edges if e.calc_length() > 0.7]
        if long:
            bmesh.ops.subdivide_edges(bm, edges=long, cuts=1)
            bm.edges.ensure_lookup_table()
        # re-collect
        top_edges = [e for e in bm.edges
                     if all(v.co.z > zmax - 0.08 for v in e.verts)]
        # slight bevel on outer-ish edges (those with a face normal pointing out)
        try:
            bmesh.ops.bevel(bm, geom=top_edges[:], offset=0.05, segments=1,
                            affect='EDGES', profile=0.45)
        except Exception as e:
            print('UD apron bevel fail', e)
    bm.to_mesh(o.data)
    bm.free()
    o.data.update()
    o['ud_fix'] = 1
    o['UNVERIFIED_ud'] = 'apron top xy-smooth + light bevel UNVERIFIED; bak in UD_bak_*'
    print('UD softened apron', o.name, 'verts now', len(o.data.vertices))


def add_cams(col):
    """Reuse UA/TY cams; add one UD close-up of asphalt tone + one of walk edge."""
    def cam(name, loc, target, lens=35):
        if bpy.data.objects.get(name):
            return
        c = bpy.data.cameras.new(name)
        c.lens = lens
        o = bpy.data.objects.new(name, c)
        o.location = loc
        # aim
        direction = Vector(target) - Vector(loc)
        o.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
        o['ud_obj'] = 1
        col.objects.link(o)
        return o
    # asphalt close-up near Normal Ave centre
    cam('UD_CAM_closeup_NormalAve_asphalt',
        (-170.0, -285.0, 120.5), (-165.0, -295.0, 117.5), lens=50)
    # Partridge walk edge close-up (W apron / 404)
    cam('UD_CAM_closeup_Partridge_walk_edge',
        (-108.0, 249.5, 141.0), (-100.0, 249.5, 139.6), lens=45)
    # combined oblique day-9 polish overview
    cam('UD_CAM_oblique_day9_polish_from_SW',
        (-220.0, -50.0, 210.0), (-120.0, 50.0, 140.0), lens=28)
    print('UD cams ready')


# ---- apply ----
col = ensure_coll(COLN)
ud_mat = make_ud_asphalt()
swap_ua_mats(ud_mat)
lift_ua_over_skirt()
for wn in TY_WALKS:
    o = bpy.data.objects.get(wn)
    if o:
        soften_walk(o)
    else:
        print('UD missing walk', wn)
ap = bpy.data.objects.get(TY_APRON)
if ap:
    soften_apron(ap)
else:
    print('UD missing apron')
add_cams(col)

if SAVE:
    bpy.ops.wm.save_mainfile()
    print('SAVED')
print('UD DONE')
