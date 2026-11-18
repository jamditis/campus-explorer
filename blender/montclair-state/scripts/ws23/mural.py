"""ws23: RED HAWK COUNTRY wall vs Joe's Nov 8 photo — painted arch niches recoloured from lavender to the photo's soft warm grey
(new packed image annex_mural_arch_tile_ws23.png on the image node; old image kept), and Annex coping switched from 2016-photo red
to the wall's white paint seen in Joe's photo (new material WS23_Annex_coping_white_JoePhoto on both coping users). SAVE=1 saves."""
import bpy, os, hashlib
R='/workspace/nj-scenes/montclair-state'
m=bpy.data.materials['MI_Annex_mural_arch_paint_UNVERIFIED']
nt=m.node_tree; tex=[n for n in nt.nodes if n.type=='TEX_IMAGE'][0]
mix=[n for n in nt.nodes if n.type=='MIX'][0]
print('mix fac',mix.inputs[0].default_value, 'blend',mix.blend_type, 'old img',tex.image.name)
m['ws23_old_image']=tex.image.name
img=bpy.data.images.load(R+'/data/ws23/tex/annex_mural_arch_tile_ws23.png'); img.name='annex_mural_arch_tile_ws23.png'; img.pack()
tex.image=img
red=bpy.data.materials['MH_Annex_coping_red_metal_photo2016']
w=red.copy(); w.name='WS23_Annex_coping_white_JoePhoto'
b=w.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value=(0.74,0.72,0.73,1); b.inputs['Roughness'].default_value=0.6
n=0
for o in bpy.data.objects:
    if o.type!='MESH': continue
    for s in o.material_slots:
        if s.material==red:
            s.material=w; n+=1; print('coping slot ->white',o.name,s.link)
            o['ws23_coping_was']=red.name
red.use_fake_user=True
print('slots changed',n)
if os.environ.get('SAVE')=='1':
    bpy.ops.wm.save_mainfile(); print('SAVED')
