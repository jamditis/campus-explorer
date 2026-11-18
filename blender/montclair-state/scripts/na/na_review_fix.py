# na review fix: carpet reads too dark vs Joe's photo (mid-grey with coloured stripes) -> value x1.7 via HueSat node
import bpy, os
m=bpy.data.materials['NA_ccm_striped_carpet_generic_UNVERIFIED']; N=m.node_tree.nodes; Lk=m.node_tree.links
tx=[x for x in N if x.type=='TEX_IMAGE'][0]; b=N['Principled BSDF']
if 'na_value' not in N:
    hs=N.new('ShaderNodeHueSaturation'); hs.name='na_value'; hs.inputs['Value'].default_value=1.7; hs.inputs['Saturation'].default_value=1.15
    Lk.new(tx.outputs['Color'],hs.inputs['Color']); Lk.new(hs.outputs['Color'],b.inputs['Base Color'])
m['na_fix']='value x1.7, sat x1.15 (review)'
bpy.ops.wm.save_as_mainfile(filepath=bpy.data.filepath) if os.environ.get('NA_MODE')=='SAVE' else bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath('data/na/test.blend'),copy=True)
print("SAVED",len(bpy.data.objects))
