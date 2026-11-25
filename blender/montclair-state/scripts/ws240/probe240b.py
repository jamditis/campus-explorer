# W12c camera-ray probe: what surface is the dark lip at the apron's E end in the SW eye view (ws209 camera)?
import bpy, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
X0,X1,Y0,Y1=-5,30,-50,-20
def bb(o):
    w=[o.matrix_world@Vector(c) for c in o.bound_box]; return min(v.x for v in w),max(v.x for v in w),min(v.y for v in w),max(v.y for v in w)
loc=[o for o in bpy.data.objects if o.type=='MESH' and not o.hide_render and not o.name.startswith(('T_','Tree','WQ_','gd_','ge_','Lawn_grass','dS_grass','WS48')) and (lambda b: not(b[1]<X0 or b[0]>X1 or b[3]<Y0 or b[2]>Y1))(bb(o))]
loc=[o for o in loc if (lambda b:(b[1]-b[0])*(b[3]-b[2]))(bb(o))<4e6]
for o in loc:
    for m in o.modifiers: m.show_viewport=m.show_render
dg=bpy.context.evaluated_depsgraph_get(); NB=[]
for o in loc:
    e=o.evaluated_get(dg); me=e.to_mesh(); M=o.matrix_world
    if len(me.polygons): NB.append((o.name,BVHTree.FromPolygons([M@v.co for v in me.vertices],[p.vertices[:] for p in me.polygons])))
    e.to_mesh_clear()
C=Vector((0.5,-44.5,136.4)); f=(Vector((7.5,-37.5,135.3))-C).normalized(); r=f.cross(Vector((0,0,1))).normalized(); u=r.cross(f)
W,H=704,396; t=math.tan(math.atan(18/35))
for px,py in [(470,180),(500,178),(530,180),(560,182),(585,178),(540,170),(600,185),(620,200),(650,240),(560,205)]:
    d=(f+r*((px/W-0.5)*2*t)+u*(-(py/H-0.5)*2*t*H/W)).normalized()
    hs=[]
    for n,b in NB:
        h=b.ray_cast(C,d)
        if h[0] is not None: hs.append((round(h[3],2),n[:40],tuple(round(c,2) for c in h[0]),round(h[1].z,2)))
    hs.sort(); print('P240B',px,py,hs[:3],flush=True)
