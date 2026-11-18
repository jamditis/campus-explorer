import bpy
objs=len(bpy.data.objects); mats=len(bpy.data.materials)
ve=sum(1 for o in bpy.data.objects if o.get('ve_obj'))
vd=sum(1 for o in bpy.data.objects if o.get('vd_obj'))
vc=sum(1 for o in bpy.data.objects if o.get('vc_obj'))
vb=sum(1 for o in bpy.data.objects if o.get('vb_obj'))
vem=sum(1 for m in bpy.data.materials if m.get('ve_mat'))
hid=sum(1 for o in bpy.data.objects if o.get('ve_hidden'))
let=None; mx=my=mz=sz=None
for o in bpy.data.objects:
    if o.type=='FONT' and 'FREEMAN' in o.name.upper():
        let=o.data.body
        mw=o.matrix_world
        mx=round(mw[0][3],4); my=round(mw[1][3],4); mz=round(mw[2][3],4)
        sz=round(o.data.size,5)
        break
wsoft=bpy.data.objects.get('UY_Freeman_W_cream_brick_skin_UNVERIFIED')
wmat=wsoft.material_slots[0].material.name if wsoft and wsoft.material_slots and wsoft.material_slots[0].material else None
print(f'VESIG {objs} mats={mats} ve={ve} vem={vem} vd={vd} vc={vc} vb={vb} hid={hid} letter={let!r} size={sz} loc=({mx},{my},{mz}) Wmat={wmat}')
