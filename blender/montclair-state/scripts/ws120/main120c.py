# ws120: GN edge-grade (WS113) lifts lawn 0.2-0.4 m over the apron at the S-wing face; retire the terrain/fill faces under the apron there
import bpy, bmesh
def ob(p): return next(o for o in bpy.data.objects if o.name.startswith(p))
for nm in ('Terrain_LiDAR_DTM_1m','WS113_terrain_fan_fill'):
    o=ob(nm); mw=o.matrix_world; b=bmesh.new(); b.from_mesh(o.data)
    k=[f for f in b.faces if (lambda c: -216.6<=c.x<=-215.0 and -202.9<=c.y<=-201.35)(mw@f.calc_center_median())]
    bmesh.ops.delete(b,geom=k,context='FACES'); b.to_mesh(o.data); b.free(); o.data.update(); print('M120c',nm,'retired',len(k))
bpy.ops.wm.save_mainfile(); print('M120c SAVED main')
