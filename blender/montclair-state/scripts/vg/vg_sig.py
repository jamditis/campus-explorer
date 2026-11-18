import bpy
objs=len(bpy.data.objects); mats=len(bpy.data.materials)
vg=sum(1 for o in bpy.data.objects if o.get('vg_obj'))
vf=sum(1 for o in bpy.data.objects if o.get('vf_obj'))
ve=sum(1 for o in bpy.data.objects if o.get('ve_obj'))
vd=sum(1 for o in bpy.data.objects if o.get('vd_obj'))
vgm=sum(1 for m in bpy.data.materials if m.get('vg_mat'))
hid=sum(1 for o in bpy.data.objects if o.get('vg_hidden'))
let=None; mx=my=mz=sz=None
for o in bpy.data.objects:
    if o.type=='FONT' and 'FREEMAN' in o.name.upper():
        let=o.data.body
        mw=o.matrix_world
        mx=round(mw[0][3],4); my=round(mw[1][3],4); mz=round(mw[2][3],4)
        sz=round(o.data.size,5)
        break
g=bpy.data.materials.get('VD_Freeman_W_glass_pane_UNVERIFIED')
ga=None
if g and g.use_nodes:
    b=g.node_tree.nodes.get('Principled BSDF')
    if b: ga=round(b.inputs['Alpha'].default_value,3)
sg=bpy.data.materials.get('VG_Freeman_SE_glass_pane_UNVERIFIED')
sga=None
if sg and sg.use_nodes:
    b=sg.node_tree.nodes.get('Principled BSDF')
    if b: sga=round(b.inputs['Alpha'].default_value,3)
s=bpy.data.objects.get('VG_Freeman_S_pane_grid_UNVERIFIED')
e=bpy.data.objects.get('VG_Freeman_E_pane_grid_UNVERIFIED')
print(f'VGSIG {objs} mats={mats} vg={vg} vgm={vgm} vf={vf} ve={ve} vd={vd} hid={hid} letter={let!r} size={sz} loc=({mx},{my},{mz}) glassA={ga} SEglassA={sga} Sgrid={bool(s)} Egrid={bool(e)}')
