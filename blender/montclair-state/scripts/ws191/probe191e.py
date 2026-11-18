import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
out=open('/workspace/nj-scenes/montclair-state/scripts/ws191/probe191e.out','w')
TT=[]
for o in bpy.data.objects:
    if o.name.startswith(('WS163_ground_patch_W_of_WS110','WS170b_','WS162_Lot3_asphalt_OSM','WS110_ground_patch_S','WS190b_','WS191b_')):
        M=o.matrix_world
        TT.append((o.name[:6],BVHTree.FromPolygons([M@v.co for v in o.data.vertices],[p.vertices[:] for p in o.data.polygons])))
out.write('N %d\n'%len(TT))
for j in range(10):
    y=-234.2-0.4*j; line='Y %.1f '%y
    for i in range(6):
        x=-300.2+0.6*i; line+=' %.1f:'%x
        for n,t in TT:
            h=t.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))
            if h[0]: line+='%s=%.2f/'%(n,h[0].z)
    out.write(line+'\n')
out.close()
