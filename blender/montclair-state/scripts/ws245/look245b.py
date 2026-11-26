import bpy, os
from mathutils import Vector
o=bpy.data.objects['Terrain_LiDAR_DTM_1m']; M=o.matrix_world
P=[(-229,130),(-218,118),(-226,128)]
for px,py in P:
    vs=[(round((M@v.co).x,2),round((M@v.co).y,2),round((M@v.co).z,2)) for v in o.data.vertices if abs((M@v.co).x-px)<1.6 and abs((M@v.co).y-py)<1.6]
    print('LK2 base',(px,py),len(vs),vs[:12],flush=True)
for m in o.modifiers: m.show_viewport=True
dg=bpy.context.evaluated_depsgraph_get(); e=o.evaluated_get(dg); me=e.to_mesh()
for px,py in P:
    vs=[(round((M@v.co).x,2),round((M@v.co).y,2),round((M@v.co).z,2)) for v in me.vertices if abs((M@v.co).x-px)<1.6 and abs((M@v.co).y-py)<1.6]
    print('LK2 eval',(px,py),len(vs),vs[:12],flush=True)
print('LK2 mods',[(m.name,m.show_viewport) for m in o.modifiers][-3:],flush=True)
os._exit(0)
