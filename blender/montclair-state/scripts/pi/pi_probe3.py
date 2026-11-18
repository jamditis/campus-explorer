import bpy
r=bpy.data.objects['Feliciano School of Business roof (LiDAR)']
print('PROP','pi_prev_mi' in r, r.hide_render, [m.type for m in r.modifiers], len(r.material_slots))
w=bpy.data.objects['Feliciano School of Business walls']; mw=w.matrix_world; R=mw.to_3x3()
print('WMOD',[m.type for m in w.modifiers])
for p in w.data.polygons:
    c=mw@p.center
    if -224<c.x<-204 and 170<c.y<200 and c.z>148:
        n=(R@p.normal).normalized()
        zs=[(mw@w.data.vertices[v].co).z for v in p.vertices]
        print('W',p.index,round(c.x,1),round(c.y,1),round(min(zs),1),round(max(zs),1),[round(x,2) for x in n],round(p.area,1),w.material_slots[p.material_index].material.name)
