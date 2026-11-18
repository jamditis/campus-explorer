import bpy
from mathutils import Vector
for o in sorted(bpy.data.objects,key=lambda o:o.name):
    if 'Chapin' in o.name or 'chapin' in o.name.lower():
        if o.type!='MESH': print('P', o.name, o.type); continue
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        xs=[p.x for p in bb]; ys=[p.y for p in bb]; zs=[p.z for p in bb]
        print('P %s v%d f%d x%.1f..%.1f y%.1f..%.1f z%.2f..%.2f mods=%s col=%s'%(o.name,len(o.data.vertices),len(o.data.polygons),min(xs),max(xs),min(ys),max(ys),min(zs),max(zs),[m.type for m in o.modifiers],[c.name for c in o.users_collection]))
