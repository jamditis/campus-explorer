import bpy, os
# oe: od review leftover - power-pole outlet/USB plates read too bright in the close-up -> softer warm off-white, rougher. REVERT=1 restores od values.
m=bpy.data.materials['OD_power_outlet_face_white_UNVERIFIED']
b=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
if os.environ.get('REVERT')=='1':
    b.inputs['Base Color'].default_value=(0.75,0.75,0.72,1); b.inputs['Roughness'].default_value=0.4
else:
    print('OE before',tuple(b.inputs['Base Color'].default_value),b.inputs['Roughness'].default_value)
    b.inputs['Base Color'].default_value=(0.50,0.495,0.47,1); b.inputs['Roughness'].default_value=0.6
m['oe_note']='oe: dimmed from 0.75 / rough 0.4 (od) after close-up review; UNVERIFIED'
bpy.ops.wm.save_mainfile(); print('OE_SAVED',len(bpy.data.objects))
