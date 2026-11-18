import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
X0,X1,Y0,Y1=-285,-180,140,240
def mk(name):
    T=bpy.data.objects[name]; tm=T.matrix_world; tv=[tm@v.co for v in T.data.vertices]
    ins=[X0-5<=v.x<=X1+5 and Y0-5<=v.y<=Y1+5 for v in tv]
    polys=[list(p.vertices) for p in T.data.polygons if any(ins[i] for i in p.vertices)]
    used=sorted({i for p in polys for i in p}); rm={o:n for n,o in enumerate(used)}
    return BVHTree.FromPolygons([tv[i] for i in used],[[rm[i] for i in p] for p in polys])
bt=mk('Terrain_LiDAR_DTM_1m'); bs=mk('Context_skirt_3DEP_ortho_4km')
w=bpy.data.objects['Feliciano School of Business walls']; mw=w.matrix_world
bw=BVHTree.FromPolygons([mw@v.co for v in w.data.vertices],[list(p.vertices) for p in w.data.polygons])
D=Vector((0,0,-1))
for y in range(Y1,Y0,-3):
    row=''
    for x in range(X0,X1,2):
        t=bt.ray_cast(Vector((x,y,300)),D,400); s=bs.ray_cast(Vector((x,y,300)),D,400)
        # inside building? cast ray along +x count crossings
        if t[0] is not None: row+='T'
        elif s[0] is not None: row+='s' if s[0].z<132.5 else 'S'
        else: row+='.'
    print(y,row)
