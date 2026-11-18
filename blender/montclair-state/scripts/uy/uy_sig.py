import bpy
objs=len(bpy.data.objects); mats=len(bpy.data.materials)
uy=sum(1 for o in bpy.data.objects if o.get('uy_obj'))
uv=sum(1 for o in bpy.data.objects if o.get('uv_obj'))
uw=sum(1 for o in bpy.data.objects if o.get('uw_obj'))
let=None
for o in bpy.data.objects:
    if o.type=='FONT' and 'FREEMAN' in o.name.upper():
        let=o.data.body; break
print(f'UYSIG {objs} mats={mats} uy={uy} uv={uv} uw={uw} letter={let!r}')
