import bpy
objs=len(bpy.data.objects); mats=len(bpy.data.materials)
vc=sum(1 for o in bpy.data.objects if o.get('vc_obj'))
vb=sum(1 for o in bpy.data.objects if o.get('vb_obj'))
uy=sum(1 for o in bpy.data.objects if o.get('uy_obj'))
uv=sum(1 for o in bpy.data.objects if o.get('uv_obj'))
vcm=sum(1 for m in bpy.data.materials if m.get('vc_mat'))
let=None; mx=my=mz=sz=None
for o in bpy.data.objects:
    if o.type=='FONT' and 'FREEMAN' in o.name.upper():
        let=o.data.body
        mw=o.matrix_world
        mx=round(mw[0][3],4); my=round(mw[1][3],4); mz=round(mw[2][3],4)
        sz=round(o.data.size,5)
        break
print(f'VCSIG {objs} mats={mats} vc={vc} vcm={vcm} vb={vb} uy={uy} uv={uv} letter={let!r} size={sz} loc=({mx},{my},{mz})')
