import bpy
objs=len(bpy.data.objects); mats=len(bpy.data.materials)
vf=sum(1 for o in bpy.data.objects if o.get('vf_obj'))
ve=sum(1 for o in bpy.data.objects if o.get('ve_obj'))
vd=sum(1 for o in bpy.data.objects if o.get('vd_obj'))
vc=sum(1 for o in bpy.data.objects if o.get('vc_obj'))
vfm=sum(1 for m in bpy.data.materials if m.get('vf_mat'))
hid=sum(1 for o in bpy.data.objects if o.get('vf_hidden'))
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
print(f'VFSIG {objs} mats={mats} vf={vf} vfm={vfm} ve={ve} vd={vd} vc={vc} hid={hid} letter={let!r} size={sz} loc=({mx},{my},{mz}) glassA={ga}')
