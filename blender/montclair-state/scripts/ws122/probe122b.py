import bpy
from mathutils import Vector
X0,X1,Y0,Y1=-240,-150,-245,-140
for o in sorted(bpy.data.objects,key=lambda o:o.name):
    if o.type!='MESH': continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    xs=[p.x for p in bb]; ys=[p.y for p in bb]; zs=[p.z for p in bb]
    if max(xs)<X0 or min(xs)>X1 or max(ys)<Y0 or min(ys)>Y1: continue
    if o.name.startswith(('WS107_Chapin','WS108_Chapin')): continue
    print('N %s f%d z%.1f..%.1f vis=%s mods=%s'%(o.name,len(o.data.polygons),min(zs),max(zs),not o.hide_render,[m.type for m in o.modifiers]))
