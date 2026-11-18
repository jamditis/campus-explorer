import bpy
o=bpy.data.objects['TZ_Cole_north_addition_UNVERIFIED']; M=o.matrix_world
print('mods',[m.type for m in o.modifiers], 'matrix ident', M.is_identity if hasattr(M,'is_identity') else M)
for i,s in enumerate(o.material_slots): print('SLOT',i,s.material.name)
for p in o.data.polygons:
    c=M@p.center; n=(M.to_3x3()@p.normal).normalized()
    if n.x>0.8 or (c.x>-97 and abs(n.z)<0.3):
        vs=[M@o.data.vertices[v].co for v in p.vertices]
        ys=[v.y for v in vs]; zs=[v.z for v in vs]; xs=[v.x for v in vs]
        print('F',p.index,o.material_slots[p.material_index].material.name,[round(v,2) for v in c],[round(v,2) for v in n],'x',round(min(xs),2),round(max(xs),2),'y',round(min(ys),2),round(max(ys),2),'z',round(min(zs),2),round(max(zs),2))
