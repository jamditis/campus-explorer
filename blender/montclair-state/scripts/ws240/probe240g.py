# what is the brownish horizontal bar in the RHD SE close-up (cam -261,-51.5,126.3 -> -266.5,-42,127.6, 35 mm)?
import bpy, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def bb(o):
    w=[o.matrix_world@Vector(c) for c in o.bound_box]; return min(v.x for v in w),max(v.x for v in w),min(v.y for v in w),max(v.y for v in w)
bpy.context.view_layer.update()
sel=[o for o in bpy.data.objects if o.type=='MESH' and not o.hide_render and (lambda b: not(b[1]<-285 or b[0]>-245 or b[3]<-60 or b[2]>-20))(bb(o)) and (lambda b:(b[1]-b[0])*(b[3]-b[2]))(bb(o))<4e5]
NB=[]
for o in sel:
    M=o.matrix_world; me=o.data
    if len(me.polygons): NB.append((o,BVHTree.FromPolygons([M@v.co for v in me.vertices],[p.vertices[:] for p in me.polygons])))
C=Vector((-261,-51.5,126.3)); f=(Vector((-266.5,-42,127.6))-C).normalized(); r=f.cross(Vector((0,0,1))).normalized(); u=r.cross(f)
W,H=704,396; t=math.tan(math.atan(18/35))
for px,py in [(300,248),(250,250),(380,245),(200,255)]:
    d=(f+r*((px/W-0.5)*2*t)+u*(-(py/H-0.5)*2*t*H/W)).normalized(); hs=[]
    for o,b in NB:
        h=b.ray_cast(C,d)
        if h[0] is not None:
            mi=o.data.polygons[h[2]].material_index if h[2] is not None and h[2]<len(o.data.polygons) else 0
            mat=o.material_slots[mi].material.name if len(o.material_slots)>mi and o.material_slots[mi].material else None
            hs.append((round(h[3],2),o.name[:50],mat,o.material_slots[mi].link if len(o.material_slots)>mi else None))
    hs.sort(); print('P240G',px,py,hs[:3],flush=True)
