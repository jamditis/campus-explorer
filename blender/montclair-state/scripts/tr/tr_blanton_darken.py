# tr pass 2: further darken Blanton-only TR_Blanton_infill_cream_UNVERIFIED (still too pale vs TN frame)
import bpy, os
m=bpy.data.materials.get('TR_Blanton_infill_cream_UNVERIFIED')
assert m, 'missing TR Blanton mat'
N=m.node_tree.nodes; L=m.node_tree.links
# push base ramps darker/warmer (finished 1980s cream-grey cladding between pale precast)
for nm,c0,c1 in (
    ('Color Ramp',(0.26,0.24,0.20,1),(0.36,0.33,0.28,1)),
    ('Color Ramp.001',(0.22,0.20,0.17,1),(0.32,0.29,0.25,1)),
):
    n=N.get(nm)
    if n:
        n.color_ramp.elements[0].color=c0; n.color_ramp.elements[1].color=c1
# add an end multiply if not already tr-tagged
if 'tr_darken' not in m:
    b=N['Principled BSDF']
    src=b.inputs['Base Color'].links[0].from_socket
    mx=N.new('ShaderNodeMix'); mx.data_type='RGBA'; mx.blend_type='MULTIPLY'; mx.inputs['Factor'].default_value=1.0
    mx.inputs['B'].default_value=(0.72,0.68,0.60,1)  # warm darken
    L.new(src, mx.inputs['A']); L.new(mx.outputs['Result'], b.inputs['Base Color'])
    m['tr_darken']=1
    print('TR darken multiply added')
else:
    # strengthen existing
    for n in N:
        if n.type=='MIX' and n.blend_type=='MULTIPLY' and n.inputs['B'].default_value[0]<0.8:
            # the one we added
            pass
    print('TR darken already present; ramps updated')
print('TR Blanton darkened')
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
