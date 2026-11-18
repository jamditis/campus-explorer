"""2026-10-15 az: close-up cam on the new round-2 species (main blend). Reuses the known-good open-air viewpoint of
CAM_oblique_CCOM_east_jf (ax lesson: ray_cast 'open sky' checks fail in main), lens x2.6, aimed at the nearest Norway Spruce /
Sweetgum whose crown is the first thing hit from that viewpoint. Args after --: [--save]"""
import bpy, sys, math
from mathutils import Vector
SAVE = '--save' in sys.argv
A = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
SRCS = [a for a in A if a.startswith('CAM_')] or ['CAM_oblique_CCOM_east_jf']
LENSX = float(next((a.split('=')[1] for a in A if a.startswith('lensx=')), '1.7'))
sc = bpy.context.scene; dg = bpy.context.evaluated_depsgraph_get()
cands = []
for sn in SRCS:
  src = bpy.data.objects.get(sn)
  if not src: continue
  P = src.matrix_world.translation.copy(); fwd = (src.matrix_world.to_quaternion() @ Vector((0, 0, -1))).normalized()
  for o in bpy.data.objects:
    if o.get('ax_species') in ('NorwaySpruce', 'Sweetgum') and o.get('az_src_species'):
        c = o.location + Vector((0, 0, o.dimensions.z * 0.55)); d = c - P
        if d.length > 260 or d.normalized().dot(fwd) < 0.3: continue
        hit, loc, nor, idx, ob, _ = sc.ray_cast(dg, P, d.normalized(), distance=d.length + 5)
        if hit and ob.original == o: cands.append((d.length - (40 if o['ax_species'] == 'NorwaySpruce' else 0), o, c, src, P))
cands.sort(key=lambda x: x[0])
print('CANDS', [(round(l), o.name, o['ax_species'], sr.name) for l, o, c, sr, P in cands[:10]])
# prefer one spruce and one sweetgum in frame: aim at the nearest, report the other
if cands:
    l, o, c, src, P = cands[0]
    nm = 'CAM_closeup_trees_species_az'
    cd = bpy.data.cameras.get(nm) or bpy.data.cameras.new(nm); cd.lens = src.data.lens * LENSX; cd.clip_end = 30000
    co = bpy.data.objects.get(nm) or bpy.data.objects.new(nm, cd)
    if co.name not in sc.collection.objects: sc.collection.objects.link(co)
    co.location = P; co.rotation_euler = (c - P).to_track_quat('-Z', 'Y').to_euler()
    co['az_target'] = o.name; co['az_src_cam'] = src.name
    print('CAM', nm, o.name, o['ax_species'], round(l, 1), 'lens', round(cd.lens, 1))
if SAVE:
    bpy.ops.wm.save_mainfile(); print('SAVED')
