import bpy
from mathutils import Vector
for o in bpy.context.scene.objects:
    if o.hide_render: continue
    mods=[(m.type,m.name) for m in o.modifiers if m.type in ('NODES','PARTICLE_SYSTEM')] if hasattr(o,'modifiers') else []
    if not mods: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    if min(p.x for p in bb)<5<max(p.x for p in bb) and min(p.y for p in bb)<-34<max(p.y for p in bb):
        print('GN',o.name,mods)
