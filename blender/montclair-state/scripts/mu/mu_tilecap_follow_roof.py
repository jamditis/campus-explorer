# Session mu: rebuild the eave-return tile caps so their top follows the main roof (LiDAR) profile sampled just outside the trimmed band (+2 cm),
# instead of a guessed 0.59 slope that stood ~proud of the roof on the S side.
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
n=Vector((-0.972,0.232,0)).normalized(); t=Vector((0.232,0.972,0)).normalized()
def P(u,z,w): v=t*u+n*w; return Vector((v.x,v.y,z))
roof=bpy.data.objects['School of Communication and Media roof (LiDAR)']; mw=roof.matrix_world
T=BVHTree.FromPolygons([mw@v.co for v in roof.data.vertices],[list(p.vertices) for p in roof.data.polygons])
def rz(u,w):
    h=T.ray_cast(P(u,160,w),Vector((0,0,-1)),30); return h[0].z if h[0] else None
U0,U1,US,UN=3.197,10.397,2.361,12.085
WS=[21.40,21.70,22.00,22.30,22.55,22.73,22.90,23.06]
for s,uref,ua,ub in (('S',2.30,US-0.004,U0-0.006),('N',12.15,U1+0.006,UN+0.004)):
    prof=[]
    for w in WS:
        zz=[z for z in (rz(uref,w),rz(uref-0.1 if s=='S' else uref+0.1,w)) if z is not None]
        prof.append((w,max(zz)+0.02 if zz else None))
    print('PROF',s,[(w,round(z,3) if z else None) for w,z in prof])
    good=[(w,z) for w,z in prof if z is not None]
    # top polyline back->front, ensure front top >= 147.10 (covers tile course)
    top=[(w,max(z,147.10)) for w,z in good]
    poly=[(good[0][0],146.985),(good[-1][0],146.985)]+[(w,z) for w,z in reversed(top)]
    o=bpy.data.objects['CCOM gable eave return %s tile cap (mu)'%s]
    k=len(poly); vs=[P(ua,z,w) for w,z in poly]+[P(ub,z,w) for w,z in poly]
    fs=[list(range(k))[::-1],list(range(k,2*k))]+[[i,(i+1)%k,k+(i+1)%k,k+i] for i in range(k)]
    me=o.data; me.clear_geometry(); me.from_pydata([tuple(v) for v in vs],[],fs); me.update()
    bm=bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth=False
        p.material_index=1 if abs((o.matrix_world.to_3x3()@p.normal).normalized().dot(t))>0.9 else 0
    print('REBUILT',o.name,len(me.polygons),[m.name for m in me.materials])
print('COUNT',len(bpy.data.objects)); bpy.ops.wm.save_mainfile(); print('SAVED')
