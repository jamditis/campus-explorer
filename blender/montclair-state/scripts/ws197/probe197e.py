import bpy,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
cam=Vector((-233.0,-79.8,128.4)); tg=Vector((-223.5,-76.0,126.9)); f=(tg-cam).normalized()
r=f.cross(Vector((0,0,1))).normalized(); u=r.cross(f)
objs=[]
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    if max(b.x for b in bb)<-232 or min(b.x for b in bb)>-205 or max(b.y for b in bb)<-95 or min(b.y for b in bb)>-70 or min(b.z for b in bb)>129: continue
    if len(o.data.vertices)>300000: continue
    mw=o.matrix_world; objs.append((o.name,BVHTree.FromPolygons([mw@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])))
for px,py in ((570,265),(580,275),(585,290),(575,300),(590,310)):
    a=(px-352)/352*18/26; b=-(py-198)/352*18/26
    d=(f+r*a+u*b).normalized(); hits=[]
    for n,T in objs:
        h=T.ray_cast(cam,d)
        if h[0]: hits.append((round(h[3],2),n,tuple(round(c,2) for c in h[0])))
    hits.sort(); print('P197e',px,py,hits[:4],flush=True)
