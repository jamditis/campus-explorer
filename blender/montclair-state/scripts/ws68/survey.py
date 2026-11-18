import bpy
from mathutils import Vector
c=bpy.data.collections['WS66_RedHawkDeck_from_north']
for o in sorted(c.all_objects,key=lambda o:o.name):
    if o.type!='MESH': print('S68',o.name,o.type);continue
    bb=[o.matrix_world@Vector(v) for v in o.bound_box]
    xs=[p.x for p in bb];ys=[p.y for p in bb];zs=[p.z for p in bb]
    mats=','.join(m.name[:18] for m in o.data.materials if m)[:60]
    print('S68 %-48s f=%6d x%7.1f..%7.1f y%7.1f..%7.1f z%6.1f..%6.1f mods=%s m=%s'%(o.name[:48],len(o.data.polygons),min(xs),max(xs),min(ys),max(ys),min(zs),max(zs),','.join(m.type for m in o.modifiers),mats))
