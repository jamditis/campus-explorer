# mv: which geometry pokes forward (+w) of the S eave-return box front (w 23.005) near the S gable corner
import bpy
from mathutils import Vector
n=Vector((-0.972,0.232,0)).normalized(); t=Vector((0.232,0.972,0)).normalized()
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    if max(v.dot(n) for v in bb)<22.9: continue
    if max(v.z for v in bb)<146.2 or min(v.z for v in bb)>147.4: continue
    if min(v.dot(t) for v in bb)>3.6 or max(v.dot(t) for v in bb)<1.5: continue
    mw=o.matrix_world
    for p in o.data.polygons:
        vs=[mw@o.data.vertices[i].co for i in p.vertices]
        c=sum(vs,Vector())/len(vs)
        if 1.8<c.dot(t)<3.6 and 146.2<c.z<147.4 and c.dot(n)>22.0:
            print('F',o.name[:50],p.index,'u',[round(v.dot(t),2) for v in vs],'w',[round(v.dot(n),2) for v in vs],'z',[round(v.z,2) for v in vs])
