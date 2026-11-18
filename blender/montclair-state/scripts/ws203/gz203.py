import bpy
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
for (x,y) in [(-216,-61),(-194.6,-84.7),(-256.5,-52.8),(-72.5,-70.5),(10.6,-39.1),(-310.4,-11.2)]:
    o0=Vector((x,y,400)); 
    for _ in range(8):
        r=sc.ray_cast(dg,o0,Vector((0,0,-1)))
        if not r[0] or (not r[4].hide_render and 'tree' not in r[4].name.lower() and 'canopy' not in r[4].name.lower()): break
        o0=r[1]+Vector((0,0,-0.001))
    print('G203',x,y,round(r[1].z,2) if r[0] else None,r[4].name[:30] if r[0] else None,flush=True)
