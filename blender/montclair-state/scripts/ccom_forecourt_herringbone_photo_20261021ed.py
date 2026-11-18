# Session ed (Oct 21 2026 ~6:35 PM ET): CCOM west-entrance brick forecourt read as a flat tan slab at eye level
# (PavingStones126A at 1.2 m repeat, darkened 50%). Replace its image set with a generated herringbone paver tile
# (20x10 cm units, 4 mm joints, 3.2 m seamless; textures/HerringbonePaver_ed/, data/ed/make_herringbone_ed.py),
# colours by eye from Commons 'School of Communications.jpg' (2021, CC BY-SA 4.0). Pattern turned 45 deg off the old mapping.
# SAVE=1 saves; REVERT=1 restores the originals kept as custom props on the material.
import bpy, os, math
mat=bpy.data.materials['Brick_forecourt_herringbone']; nt=mat.node_tree; N=nt.nodes
tex={'Image Texture':'herringbone_color_ed.png','Image Texture.001':'herringbone_rough_ed.png','Image Texture.002':'herringbone_normalGL_ed.png'}
mp=N['Mapping']; mix=N['Mix']; nm=N['Normal Map']; mth=N['Math']
if os.environ.get('REVERT')=='1':
    if 'ed_orig' in mat:
        o=mat['ed_orig']
        for k,v in tex.items(): N[k].image=bpy.data.images[o[k]]
        mp.inputs['Rotation'].default_value[2]=o['rot']; s=o['scale']; mp.inputs['Scale'].default_value=(s,s,s)
        mix.inputs[0].default_value=o['fac']; nm.inputs['Strength'].default_value=o['nstr']
        del mat['ed_orig']; print('ED_REVERTED')
else:
    if 'ed_orig' not in mat:
        mat['ed_orig']={**{k:N[k].image.name for k in tex},'rot':mp.inputs['Rotation'].default_value[2],'scale':mp.inputs['Scale'].default_value[0],
                        'fac':mix.inputs[0].default_value,'nstr':nm.inputs['Strength'].default_value}
    rot0=mat['ed_orig']['rot']
    for k,f in tex.items():
        im=bpy.data.images.load('//textures/HerringbonePaver_ed/'+f, check_existing=True)
        if k!='Image Texture': im.colorspace_settings.name='Non-Color'
        N[k].image=im; N[k].interpolation='Cubic'
    mp.inputs['Rotation'].default_value[2]=rot0+math.pi/4
    mp.inputs['Scale'].default_value=(1/3.2,1/3.2,1/3.2)
    mix.inputs[0].default_value=0.12   # only a slight darkening toward the photo's tone
    nm.inputs['Strength'].default_value=0.8
    print('ED_APPLIED rot',rot0+math.pi/4)
if os.environ.get('SAVE')=='1':
    bpy.ops.wm.save_mainfile(); print('ED_SAVED')
