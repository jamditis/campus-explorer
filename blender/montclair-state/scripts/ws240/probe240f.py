# camera placement check: top surface under each candidate (all meshes in a 60 m box, evaluated) and anything overhead
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
C=[(-20,1110),(-30,1090),(-10,1030),(-140,1000),(-150,1060),(-120,940),(-332,36),(-375,-5),(-372,25),(-340,-25)]
def bb(o):
    w=[o.matrix_world@Vector(c) for c in o.bound_box]; return min(v.x for v in w),max(v.x for v in w),min(v.y for v in w),max(v.y for v in w)
objs=[o for o in bpy.data.objects if o.type=='MESH' and not o.hide_render and not o.name.startswith(('T_','Tree','gd_','ge_grass','Lawn_grass','dS_grass','BD_farfield'))]
sel=[]
for o in objs:
    b=bb(o)
    if (b[1]-b[0])*(b[3]-b[2])>4e6: continue
    if any(not(b[1]<x-30 or b[0]>x+30 or b[3]<y-30 or b[2]>y+30) for x,y in C): sel.append(o)
for o in sel:
    for m in o.modifiers: m.show_viewport=m.show_render
dg=bpy.context.evaluated_depsgraph_get(); NB=[]
for o in sel:
    e=o.evaluated_get(dg); me=e.to_mesh(); M=o.matrix_world
    if len(me.polygons): NB.append((o.name,BVHTree.FromPolygons([M@v.co for v in me.vertices],[p.vertices[:] for p in me.polygons])))
    e.to_mesh_clear()
for x,y in C:
    hs=[]
    for n,b in NB:
        h=b.ray_cast(Vector((x,y,400)),Vector((0,0,-1)))
        if h[0]: hs.append((round(h[0].z,2),n[:36]))
    hs.sort(reverse=True); print('P240F',(x,y),hs[:4],flush=True)
