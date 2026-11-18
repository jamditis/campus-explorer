import bpy,sys
m=bpy.data.materials.get('PJ_sill_drip_grime_light_UNVERIFIED')
n=m.node_tree.nodes['Math.002']; print('PJD before',n.inputs[1].default_value); n.inputs[1].default_value=0.5
print('PJD after',n.inputs[1].default_value, 'objs',len(bpy.data.objects))
if '--save' in sys.argv: bpy.ops.wm.save_mainfile()
print('PJD_DONE')
