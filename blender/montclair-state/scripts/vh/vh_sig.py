import bpy
objs=len(bpy.data.objects); mats=len(bpy.data.materials)
vh=sum(1 for o in bpy.data.objects if o.get('vh_obj'))
vg=sum(1 for o in bpy.data.objects if o.get('vg_obj'))
vf=sum(1 for o in bpy.data.objects if o.get('vf_obj'))
vhm=sum(1 for m in bpy.data.materials if m.get('vh_mat'))
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
        if b: return round(b.inputs['Alpha'].default_value,3)
    return None
print(f'VHSIG {objs} mats={mats} vh={vh} vhm={vhm} vg={vg} vf={vf} letter={let!r} size={sz} loc=({mx},{my},{mz}) WglassA={ga("VD_Freeman_W_glass_pane_UNVERIFIED")} SEglassA={ga("VG_Freeman_SE_glass_pane_UNVERIFIED")} sky={bool(bpy.data.objects.get("VF_Freeman_W_sky_tint_continuous_UNVERIFIED"))}')
