import bpy
objs=len(bpy.data.objects); mats=len(bpy.data.materials)
vd=sum(1 for o in bpy.data.objects if o.get('vd_obj'))
vc=sum(1 for o in bpy.data.objects if o.get('vc_obj'))
vb=sum(1 for o in bpy.data.objects if o.get('vb_obj'))
uy=sum(1 for o in bpy.data.objects if o.get('uy_obj'))
vdm=sum(1 for m in bpy.data.materials if m.get('vd_mat'))
hid=sum(1 for o in bpy.data.objects if o.get('vd_hidden'))
let=None; mx=my=mz=sz=None
for o in bpy.data.objects:
    if o.type=='FONT' and 'FREEMAN' in o.name.upper():
        let=o.data.body
        mw=o.matrix_world
        mx=round(mw[0][3],4); my=round(mw[1][3],4); mz=round(mw[2][3],4)
        sz=round(o.data.size,5)
        break
print(f'VDSIG {objs} mats={mats} vd={vd} vdm={vdm} vc={vc} vb={vb} uy={uy} hid={hid} letter={let!r} size={sz} loc=({mx},{my},{mz})')
