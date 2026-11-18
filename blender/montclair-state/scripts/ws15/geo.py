import bpy
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get()
for n,idx in [('Susan A. Cole Hall walls',[55,56]),('TZ_Cole_north_addition_UNVERIFIED',[3])]:
    o=bpy.data.objects[n]; me=o.evaluated_get(dg).data; mw=o.matrix_world
    for i in idx:
        p=me.polygons[i]; print('F',n,i,[tuple(round(c,2) for c in mw@me.vertices[v].co) for v in p.vertices], tuple(round(c,2) for c in (mw.to_3x3()@p.normal)))
o=bpy.data.objects['TZ_Cole_north_addition_UNVERIFIED']
bb=[o.matrix_world@Vector(c) for c in o.bound_box]; print('BB add',[round(min(v[i] for v in bb),2) for i in range(3)],[round(max(v[i] for v in bb),2) for i in range(3)])
# addition faces near x -98.4 or y -82.5 large
me=o.evaluated_get(dg).data; mw=o.matrix_world
for p in me.polygons:
    c=mw@p.center
    if p.area>4 : print('AF',p.index,tuple(round(x,2) for x in c),round(p.area,1),tuple(round(x,2) for x in mw.to_3x3()@p.normal), me.materials[p.material_index].name)
