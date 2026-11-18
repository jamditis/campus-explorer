import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def bvh(o):
    M=o.matrix_world; return BVHTree.FromPolygons([M@v.co for v in o.data.vertices],[p.vertices[:] for p in o.data.polygons])
objs=[o for o in bpy.data.objects if o.type=='MESH' and not o.hide_render and o.name.startswith(('WS163','WS162','WS186','WS187','WS167_ground','WS110_ground','WS169c','WS170b','WS190b','WS191','WS192'))]
T=[(o.name[:18],bvh(o)) for o in objs]
for y in (-234.5,-235.5,-236.5,-237.5,-238.5,-239.5,-240.5,-241.5,-242.5,-244,-246):
    row=[]
    for i in range(0,25):
        x=-315+i*0.5
        hs=[]
        for n,t in T:
            h=t.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))
            if h[0]: hs.append((h[0].z,n))
        hs.sort(reverse=True)
        row.append('%.1f:%s%.2f'%(x,hs[0][1][:9],hs[0][0]-117) if hs else '%.1f:-'%x)
    print('XS y',y,' '.join(row),flush=True)
