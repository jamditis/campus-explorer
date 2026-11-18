"""2026-10-15 ax (rev2: 18 m up, open-sky check so the cam is never inside a building/room box): re-place CAM_closeup_trees_variety_ax (first placement landed inside foliage -> black frame).
Elevated 'tree-height' close view of a mixed cluster: cam ~8 m above the cluster base, 40-60 m out, clear line of sight."""
import bpy, math, sys
from mathutils import Vector
sc = bpy.context.scene; dg = bpy.context.evaluated_depsgraph_get()
trees = [o for o in bpy.data.objects if o.get('ax_var') and o.get('ax_species')]
best, bc = None, -1
for o in trees[::2]:
    near = [p for p in trees if (p.location.xy - o.location.xy).length < 30]
    sps = {p['ax_species'] for p in near}
    sc_ = len(sps) * 100 + len(near)
    if sc_ > bc: best, bc = o, sc_
tgt = best.location + Vector((0, 0, 6.0)); camloc = None
for d in (45, 55, 60, 40):
    for k in range(24):
        a = 2 * math.pi * k / 24
        L = best.location + Vector((d * math.cos(a), d * math.sin(a), 18.0))
        v = tgt - L
        hit, loc, nrm, idx, ob, mw = sc.ray_cast(dg, L, v.normalized(), distance=v.length)
        # want the first hit to be a tree near the target (not a building / terrain in between)
        if hit and ob is not None and ob.get('ax_species') and (loc - tgt).length < 22:
            # also make sure the camera isn't inside something: short rays in 4 dirs must not hit within 1.5 m
            ok = True
            for dvec, dd in ((Vector((0,0,1)), 2000.0), (Vector((1,0,0)), 3.0), (Vector((-1,0,0)), 3.0), (Vector((0,1,0)), 3.0), (Vector((0,-1,0)), 3.0)):
                h2, *_ = sc.ray_cast(dg, L, dvec, distance=dd)
                if h2: ok = False; break
            if ok: camloc = L; break
    if camloc: break
nm = 'CAM_closeup_trees_variety_ax'
co = bpy.data.objects[nm]
co.location = camloc if camloc else best.location + Vector((50, 0, 12))
co.rotation_euler = (tgt - co.location).to_track_quat('-Z', 'Y').to_euler(); co.data.lens = 35
print('CAMFIX', best.name, bc, tuple(round(x, 1) for x in co.location), 'found' if camloc else 'fallback')
bpy.ops.wm.save_mainfile(); print('SAVED')
