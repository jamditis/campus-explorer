import bpy, collections
for nm in ['TZ_Cole_windows_EN_UNVERIFIED','TZ_Cole_sill_drips_EN_UNVERIFIED','Susan A. Cole Hall walls']:
    o=bpy.data.objects[nm]; me=o.data; M=o.matrix_world
    print('==',nm, 'mods',[m.type for m in o.modifiers])
    cnt=collections.Counter()
    for p in me.polygons:
        c=M@p.center
        if c.x>-80 and -100<c.y<-60:
            n=(M.to_3x3()@p.normal).normalized()
            mat=o.material_slots[p.material_index].material.name if o.material_slots else ''
            cnt[(mat,round(n.x,1),round(n.y,1),round(n.z,1))]+=1
            if nm!='TZ_Cole_windows_EN_UNVERIFIED' or cnt[(mat,round(n.x,1),round(n.y,1),round(n.z,1))]<4:
                print(' F',mat,[round(v,2) for v in c],[round(v,2) for v in n],round(p.area,3))
    print(cnt)
