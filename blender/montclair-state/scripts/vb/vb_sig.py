import bpy, json
objs=len(bpy.data.objects); mats=len(bpy.data.materials)
vb=sum(1 for o in bpy.data.objects if o.get('vb_obj'))
uy=sum(1 for o in bpy.data.objects if o.get('uy_obj'))
uv=sum(1 for o in bpy.data.objects if o.get('uv_obj'))
uw=sum(1 for o in bpy.data.objects if o.get('uw_obj'))
vbm=sum(1 for m in bpy.data.materials if m.get('vb_mat'))
let=None
for o in bpy.data.objects:
    if o.type=='FONT' and 'FREEMAN' in o.name.upper():
        let=o.data.body
        # include matrix digest for va lettering integrity
        mw=o.matrix_world
        mx=round(mw[0][3],4); my=round(mw[1][3],4); mz=round(mw[2][3],4)
        sz=round(o.data.size,5)
        break
else:
    mx=my=mz=sz=None
print(f'VBSIG {objs} mats={mats} vb={vb} vbm={vbm} uy={uy} uv={uv} uw={uw} letter={let!r} size={sz} loc=({mx},{my},{mz})')
