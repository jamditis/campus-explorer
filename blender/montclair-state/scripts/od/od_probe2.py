import bpy
o=bpy.data.objects['NG atrium wide stair wood clad']; mw=o.matrix_world; me=o.data
print('MAT',[m.name for m in me.materials], tuple(round(x,3) for x in mw.translation), tuple(round(x,3) for x in mw.to_euler()))
for p in me.polygons:
    n=(mw.to_3x3()@p.normal)
    if n.z>0.9:
        vs=[mw@me.vertices[i].co for i in p.vertices]
        print('T',p.material_index,round(min(v.x for v in vs),3),round(max(v.x for v in vs),3),round(min(v.y for v in vs),3),round(max(v.y for v in vs),3),round(vs[0].z,3))
for n in ('NG stair S glass rail','NG stair S handrail','NG stair N wall handrail'):
    ob=bpy.data.objects[n]; print('R',n,[tuple(round(c,3) for c in (ob.matrix_world@v.co)) for v in ob.data.vertices])
