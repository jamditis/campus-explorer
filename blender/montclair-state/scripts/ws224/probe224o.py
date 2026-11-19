import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def ob(n): return [o for o in bpy.data.objects if o.name.startswith(n)][0]
A=ob('WS71_Kasser_S_sidewalk_ortho'); B=ob('WS72b_Kasser_S_sidewal')
print('P224',A.name,'|',B.name,[m.type for m in A.modifiers],[m.type for m in B.modifiers])
def tree(o):
    M=o.matrix_world; R=M.to_3x3()
    return BVHTree.FromPolygons([M@v.co for v in o.data.vertices],[p.vertices[:] for p in o.data.polygons if (R@p.normal).z>0.3])
TA,TB=tree(A),tree(B)
for y in [-56.0-0.4*i for i in range(0,8)]:
    row=[]
    for x in [-223.5+0.25*j for j in range(0,13)]:
        ha=TA.ray_cast(Vector((x,y,140)),Vector((0,0,-1))); hb=TB.ray_cast(Vector((x,y,140)),Vector((0,0,-1)))
        row.append('%s/%s'%('%.3f'%(ha[0].z-125) if ha[0] else '-----','%.3f'%(hb[0].z-125) if hb[0] else '-----'))
    print('P224 y%.1f '%y+' '.join(row))
MB=B.matrix_world; xs=[(MB@v.co).x for v in B.data.vertices]; print('P224 B xmin %.3f xmax %.3f nv %d'%(min(xs),max(xs),len(xs)))
MA=A.matrix_world; xs=[(MA@v.co).x for v in A.data.vertices]; print('P224 A xmin %.3f xmax %.3f nv %d'%(min(xs),max(xs),len(xs)))
