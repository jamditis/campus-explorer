import bpy, os
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
ter=bpy.data.objects['Terrain_LiDAR_DTM_1m']
pts=[tuple(map(float,p.split(':'))) for p in os.environ['PTS'].split(',')]
for x,y in pts:
    o=Vector((x,y,250)); hits=[]; 
    for i in range(8):
        h=sc.ray_cast(dg,o,Vector((0,0,-1)))
        if not h[0]: break
        hits.append('%s@%.2f'%(h[4].name[:38],h[1].z)); o=h[1]-Vector((0,0,0.002))
    print('PT',x,y,' | '.join(hits))
