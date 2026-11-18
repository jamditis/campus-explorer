"""Quick polish: stronger SE eave hole cover; lounge glass more transparent; mark chairs."""
import bpy, bmesh, math, sys, resource
from mathutils import Vector

SAVE = '--save' in sys.argv
TAG = '20261014z'
EAVE = 143.017
PARAPET = 0.45
G_WEST = 137.55

def rss():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0

def mat(name, rgba, rough=0.55):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    b = nt.nodes.new('ShaderNodeBsdfPrincipled')
    b.inputs['Base Color'].default_value = rgba
    b.inputs['Roughness'].default_value = rough
    nt.links.new(b.outputs['BSDF'], out.inputs['Surface'])
    return m

def frame_box(name, center, size, u, v, col, material):
    me = bpy.data.meshes.new(name)
    sx, sy, sz = [s / 2 for s in size]
    verts = [(-sx,-sy,-sz),(sx,-sy,-sz),(sx,sy,-sz),(-sx,sy,-sz),
             (-sx,-sy,sz),(sx,-sy,sz),(sx,sy,sz),(-sx,sy,sz)]
    me.from_pydata(verts, [], [(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)])
    me.update()
    if material: me.materials.append(material)
    ob = bpy.data.objects.new(name, me)
    ob.location = center
    ob.rotation_euler = (0, 0, math.atan2(u.y, u.x))
    col.objects.link(ob)
    return ob

col = bpy.data.collections.get(f'CCOM_east_eave_clean_{TAG}')
if not col:
    col = bpy.data.collections.new(f'CCOM_east_eave_clean_{TAG}')
    bpy.context.scene.collection.children.link(col)

# Remove prior z2 plugs if re-run
for o in list(col.objects):
    if '_z2_' in o.name or o.name.endswith('_z2'):
        bpy.data.objects.remove(o, do_unlink=True)

m_wall = mat(f'CCOM_east_wall_plug_z2_{TAG}', (0.88, 0.86, 0.80, 1), 0.55)
m_flat = mat(f'CCOM_east_flat_z2_{TAG}', (0.55, 0.54, 0.52, 1), 0.85)
m_par = mat(f'CCOM_east_par_z2_{TAG}', (0.85, 0.83, 0.78, 1), 0.6)

# SE r1 frame
wcol = bpy.data.collections.get('CCOM_windows_modelled')
se_r1 = []
for o in (wcol.objects if wcol else []):
    if not o.name.startswith('CCOM_win_'): continue
    n = o.matrix_world.to_3x3() @ Vector((0, 1, 0))
    if n.x <= 0.5: continue
    loc = o.matrix_world.translation.copy()
    row = int(o.get('row', o.name.rsplit('_r', 1)[-1]))
    if row == 1 and loc.y < 8:
        se_r1.append((loc, n.normalized()))
se_r1.sort(key=lambda t: t[0].y)
n_out = sum((t[1] for t in se_r1), Vector()); n_out.z = 0; n_out.normalize()
u = Vector((-n_out.y, n_out.x, 0)).normalized()
if u.y < 0: u = -u
v_in = -n_out
locs = [t[0] for t in se_r1]
mid_xy = sum((Vector((l.x, l.y, 0)) for l in locs), Vector()) / len(locs)
bay_u = [(l - mid_xy).dot(u) for l in locs]
U0, U1 = min(bay_u) - 2.5, max(bay_u) + 2.5
ru, cu = U1 - U0, (U0 + U1) / 2

def Pw(uu, vv, zz):
    return mid_xy + u * uu + v_in * vv + Vector((0, 0, zz))

# BIG exterior wall plug covering entire SE east face from mid-window to parapet top
# (windows stay visible via existing openings in front — this sits OUTSIDE above heads only
#  AND a second solid behind any holes at roof junction)
# 1) Cap above window heads (eave band thickened)
for o in list(col.objects):
    if 'eave_band' in o.name or 'flat_roof_clean' in o.name:
        # keep; we'll add larger overlays
        pass

# Massive flat roof plate covering SE (hides jagged LiDAR tiles from above)
deck = frame_box(f'CCOM_east_roof_plate_z2_{TAG}', Pw(cu, 5.0, EAVE + 0.05),
                 (ru + 4.0, 20.0, 0.45), u, v_in, col, m_flat)
deck['ccom_pass'] = TAG; deck['note'] = 'z2 roof plate covers collapsed SE LiDAR tiles'

# Exterior vertical face plug: from just above r1 heads to parapet, OUTSIDE
plug = frame_box(f'CCOM_east_face_plug_z2_{TAG}', Pw(cu, -0.25, EAVE + PARAPET / 2),
                 (ru + 1.0, 0.55, PARAPET + 0.35), u, v_in, col, m_par)
plug['ccom_pass'] = TAG

# Fill the hole region visible in closeup: larger vertical wall behind eave junction
# covering z from ~142.2 to EAVE+parapet, depth into building
fill = frame_box(f'CCOM_east_junction_fill_z2_{TAG}', Pw(cu, 1.2, EAVE + 0.1),
                 (ru + 2.0, 3.5, PARAPET + 0.8), u, v_in, col, m_wall)
fill['ccom_pass'] = TAG; fill['note'] = 'fills SE eave junction holes from y-collapse'

# Hide SE-region of barrel/hip/eave LiDAR pieces that read as jagged (render+viewport)
# by shrinking visibility: hide entire objects if mostly SE-flattened, else leave
# Safer: hide only if name matches and we have replacement plate
for rnm in [
    'School of Communication and Media barrel tile eave course',
    'School of Communication and Media hip + ridge cap tiles',
    'School of Communication and Media eave soffit + fascia + rafter',
]:
    ro = bpy.data.objects.get(rnm)
    if not ro: continue
    # Don't hide whole object (affects west/NE). Instead mask SE verts by moving them
    # below terrain / into deck — already at 143.097. Leave; plate covers from above.
    print(f'keep {rnm} (covered by roof plate)')

# --- Lounge glass: force high transmission / low alpha on lounge glass mats
for mname in (f'CCOM_lounge_glass_{TAG}',):
    m = bpy.data.materials.get(mname)
    if not m or not m.use_nodes: continue
    for n in m.node_tree.nodes:
        if n.type == 'BSDF_PRINCIPLED':
            if 'Transmission Weight' in n.inputs:
                n.inputs['Transmission Weight'].default_value = 0.98
            n.inputs['Alpha'].default_value = 0.05
            n.inputs['Roughness'].default_value = 0.02
            n.inputs['Base Color'].default_value = (0.85, 0.92, 0.98, 1)
    m.blend_method = 'HASHED'
    print('tuned lounge glass', mname)

# Also lighten atrium glass material if opaque
ag = bpy.data.objects.get('CCOM atrium glass (arched, 7x10 grid)')
if ag and ag.data and ag.data.materials:
    for m in ag.data.materials:
        if not m or not m.use_nodes: continue
        for n in m.node_tree.nodes:
            if n.type == 'BSDF_PRINCIPLED':
                if 'Transmission Weight' in n.inputs:
                    n.inputs['Transmission Weight'].default_value = max(
                        n.inputs['Transmission Weight'].default_value, 0.9)
                if n.inputs['Alpha'].default_value < 0.2:
                    pass  # already transparent-ish
                else:
                    n.inputs['Alpha'].default_value = 0.15
        print('tuned atrium mat', m.name)

# Raise terrazzo floor slightly + ensure lounge chairs above it; hide green ground under lounge
floor = bpy.data.objects.get(f'CCOM_lounge_floor_terrazzo_{TAG}')
if floor:
    floor.location.z = G_WEST + 0.02
    # thicken
    print('terrazzo z', floor.location.z)

# Soften lounge fill lights up for readability
m_fill = bpy.data.materials.get(f'CCOM_lounge_fill_light_{TAG}')
if m_fill and m_fill.use_nodes:
    for n in m_fill.node_tree.nodes:
        if n.type == 'BSDF_PRINCIPLED' and 'Emission Strength' in n.inputs:
            n.inputs['Emission Strength'].default_value = 4.0
            print('lounge fill strength -> 4')

print(f'polish z2 plugs in col: {[o.name for o in col.objects if "z2" in o.name]} rss={rss():.0f}')
if SAVE:
    bpy.ops.wm.save_mainfile()
    print('SAVED')
else:
    print('dry-run')
print('DONE')
