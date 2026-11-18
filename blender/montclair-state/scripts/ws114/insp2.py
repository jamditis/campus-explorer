import bpy, numpy as np
dg=bpy.context.evaluated_depsgraph_get()
for n in [o.name for o in bpy.data.objects if o.name.startswith(('Footpaths','OZ_walk'))]:
    o=bpy.data.objects[n]; e=o.evaluated_get(dg); me=e.to_mesh(); mw=o.matrix_world
    c=[(mw@f.center) for f in me.polygons]
    sel=[v for v in c if -245<v.x<-225 and -242<v.y<-228]
    print('I2',n,o.hide_render,o.hide_get(),o.visible_get(),[m.name for m in o.modifiers][:3],len(me.polygons),'in box',len(sel))
    for v in sel[:40]: print('I2f %.2f %.2f %.3f'%tuple(v))
    e.to_mesh_clear()
