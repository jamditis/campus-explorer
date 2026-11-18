import bpy
# dump SF_asphalt node tree
m = bpy.data.materials.get('SF_asphalt_worn_UNVERIFIED')
print('MAT', m.name, 'users', m.users)
for n in m.node_tree.nodes:
    print(' NODE', n.type, n.name, getattr(n, 'bl_idname', ''))
    if n.type == 'BSDF_PRINCIPLED':
        for inp in ['Base Color','Roughness','Specular IOR Level','Metallic']:
            try:
                s = n.inputs[inp]
                print('  ', inp, 'default', list(s.default_value) if hasattr(s.default_value,'__iter__') else s.default_value, 'links', len(s.links))
            except: pass
    if n.type == 'VALTORGB':
        for i,e in enumerate(n.color_ramp.elements):
            print('  ramp', i, 'pos', e.position, 'col', list(e.color))
    if n.type == 'TEX_NOISE':
        for inp in ['Scale','Detail','Roughness','Distortion']:
            try: print('  ', inp, n.inputs[inp].default_value)
            except: pass
print('LINKS:')
for l in m.node_tree.links:
    print(f'  {l.from_node.name}.{l.from_socket.name} -> {l.to_node.name}.{l.to_socket.name}')

# TY footway 404 detail - sample boundary verts xy
import bmesh
from mathutils import Vector
o = bpy.data.objects.get('TY_footway_313026404_to_Partridge_UNVERIFIED')
bm = bmesh.new(); bm.from_mesh(o.data); bm.edges.ensure_lookup_table(); bm.verts.ensure_lookup_table()
bnds = [e for e in bm.edges if e.is_boundary]
print('\nTY404 boundary edges', len(bnds), 'faces', len(bm.faces))
# find corner verts (boundary verts with 2 boundary edges forming sharp angle)
from collections import defaultdict
bv = defaultdict(list)
for e in bnds:
    bv[e.verts[0]].append(e)
    bv[e.verts[1]].append(e)
sharp = 0
for v, es in bv.items():
    if len(es) != 2: continue
    # vectors of the two edges
    dirs = []
    for e in es:
        other = e.verts[1] if e.verts[0]==v else e.verts[0]
        d = (other.co - v.co).normalized()
        dirs.append(d)
    ang = dirs[0].angle(dirs[1])
    # exterior: if ang much less than pi, sharp corner
    import math
    deg = math.degrees(ang)
    if deg < 150:  # interior turn of boundary path
        sharp += 1
        if sharp <= 8:
            w = o.matrix_world @ v.co
            print(f'  sharp corner deg={deg:.1f} world=({w.x:.2f},{w.y:.2f},{w.z:.2f})')
print('sharp corners (<150 deg turn)', sharp)
# apron
o2 = bpy.data.objects.get('TY Partridge W areaway apron cutting lawn bank (UNVERIFIED)')
bm2 = bmesh.new(); bm2.from_mesh(o2.data)
print('\nApron faces', len(bm2.faces), 'verts', len(bm2.verts), 'is_manifold', all(e.is_manifold for e in bm2.edges) if bm2.edges else None)
# top face outline
import mathutils
zs = [v.co.z for v in bm2.verts]
print('apron local z range', min(zs), max(zs))
bm.free(); bm2.free()

# check Context_skirt under Normal Ave for z-fight note
ua = bpy.data.objects.get('UA_NormalAve_CR618_583841725_727_729_UNVERIFIED')
print('\nUA NormalAve z range', min((ua.matrix_world@v.co).z for v in ua.data.vertices), max((ua.matrix_world@v.co).z for v in ua.data.vertices))
print('UA OFF notes', ua.get('UNVERIFIED_ua'))
# sample a few verts vs skirt
skirt = bpy.data.objects.get('Context_skirt_3DEP_ortho_4km')
dg = bpy.context.evaluated_depsgraph_get()
ev = skirt.evaluated_get(dg)
mw = skirt.matrix_world; iw = mw.inverted()
diffs = []
for i,v in enumerate(ua.data.vertices):
    if i % 40: continue
    w = ua.matrix_world @ v.co
    r = ev.ray_cast(iw @ Vector((w.x,w.y,400)), (iw.to_3x3()@Vector((0,0,-1))).normalized())
    if r[0]:
        sz = (mw @ r[1]).z
        diffs.append(w.z - sz)
print('UA vs skirt z-diff samples n=', len(diffs), 'min', min(diffs) if diffs else None, 'max', max(diffs) if diffs else None, 'mean', sum(diffs)/len(diffs) if diffs else None)
