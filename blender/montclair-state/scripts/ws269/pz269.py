import bpy
from mathutils import Vector
o=bpy.data.objects['WS268_W72_CollegeAve_Lot33_paving_UNVERIFIED']
for x,y in [(-385,-28),(-375,-30),(-357,-36.6),(-346,-38.7),(-334,-41),(-322,-36),(-320,-45),(-350,-30),(-340,-46)]:
    zs=[(o.matrix_world@v.co).z for v in o.data.vertices if abs((o.matrix_world@v.co).x-x)<1 and abs((o.matrix_world@v.co).y-y)<1]
    print('PZ269',x,y,round(max(zs),2) if zs else None)
