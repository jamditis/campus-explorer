import bpy
objs=len(bpy.data.objects); mats=len(bpy.data.materials)
vi=sum(1 for o in bpy.data.objects if o.get('vi_obj'))
vh=sum(1 for o in bpy.data.objects if o.get('vh_obj'))
vg=sum(1 for o in bpy.data.objects if o.get('vg_obj'))
vim=sum(1 for m in bpy.data.materials if m.get('vi_mat'))
let=None; mx=my=mz=sz=None
for o in bpy.data.objects:
    if o.type=='FONT' and 'FREEMAN' in o.name.upper():
        let=o.data.body
        mw=o.matrix_world
        mx=round(mw[0][3],4); my=round(mw[1][3],4); mz=round(mw[2][3],4)
        sz=round(o.data.size,5)
        break
def ga(name):
    g=bpy.data.materials.get(name)
    if g and g.use_nodes:
        b=g.node_tree.nodes.get('Principled BSDF')
        if b:
            a=round(b.inputs['Alpha'].default_value,3)
            cw=round(b.inputs['Coat Weight'].default_value,3) if 'Coat Weight' in b.inputs else None
            si=round(b.inputs['Specular IOR Level'].default_value,3) if 'Specular IOR Level' in b.inputs else None
            return f'A={a}/Coat={cw}/Spec={si}'
    return None
print(f'VISIG {objs} mats={mats} vi={vi} vim={vim} vh={vh} vg={vg} letter={let!r} size={sz} loc=({mx},{my},{mz}) Wglass={ga("VD_Freeman_W_glass_pane_UNVERIFIED")} SEglass={ga("VG_Freeman_SE_glass_pane_UNVERIFIED")} sky={bool(bpy.data.objects.get("VF_Freeman_W_sky_tint_continuous_UNVERIFIED"))}')
