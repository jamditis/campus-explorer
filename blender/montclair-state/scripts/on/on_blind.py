# on: re-apply om's per-window Schmitt blind variation (om log says it was on, but the om final saved file has CCOM_win_blind on the shared blind mesh and the OM material had 0 users, so it was purged on save). REVERT=1 puts CCOM_win_blind back and drops the OM copy.
import bpy, os, sys
MB='OM_Schmitt_win_blind_var_UNVERIFIED'; SAVE='--save' in sys.argv
ob=bpy.data.objects['CCOM_Win_Wing_A_blind']; bl=ob.data  # mesh is LINKED from windows_ccom.blend -> data-level edits are not saved; use an object-level slot
if os.environ.get('REVERT')=='1':
    ob.material_slots[0].material=None if ob.material_slots[0].link=='OBJECT' else ob.material_slots[0].material; ob.material_slots[0].link='DATA'
    m=bpy.data.materials.get(MB)
    if m: bpy.data.materials.remove(m)
    print('ON_BLIND_REVERTED')
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    sys.exit(0)
if bpy.data.materials.get(MB): bpy.data.materials.remove(bpy.data.materials[MB])
# (5) blind variation
mb=bpy.data.materials['CCOM_win_blind'].copy(); mb.name=MB; nt=mb.node_tree
mr=nt.nodes['Map Range']; oi=nt.nodes['Object Info']
wn=nt.nodes.new('ShaderNodeTexWhiteNoise'); wn.noise_dimensions='3D'
sep=nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(oi.outputs['Location'],sep.inputs[0]); nt.links.new(oi.outputs['Location'],wn.inputs['Vector'])
def rng(sock,lo,hi):
    a=nt.nodes.new('ShaderNodeMath'); a.operation='GREATER_THAN'; a.inputs[1].default_value=lo; nt.links.new(sock,a.inputs[0])
    b=nt.nodes.new('ShaderNodeMath'); b.operation='LESS_THAN'; b.inputs[1].default_value=hi; nt.links.new(sock,b.inputs[0])
    m=nt.nodes.new('ShaderNodeMath'); m.operation='MULTIPLY'; nt.links.new(a.outputs[0],m.inputs[0]); nt.links.new(b.outputs[0],m.inputs[1]); return m.outputs[0]
gx=rng(sep.outputs['X'],-30,25); gy=rng(sep.outputs['Y'],108,194)
gm=nt.nodes.new('ShaderNodeMath'); gm.operation='MULTIPLY'; nt.links.new(gx,gm.inputs[0]); nt.links.new(gy,gm.inputs[1])
mxr=nt.nodes.new('ShaderNodeMix'); mxr.data_type='FLOAT'
nt.links.new(gm.outputs[0],mxr.inputs['Factor']); nt.links.new(oi.outputs['Random'],mxr.inputs[2]); nt.links.new(wn.outputs['Value'],mxr.inputs[3])
nt.links.new(mxr.outputs[0],mr.inputs['Value'])
ob.material_slots[0].link='OBJECT'; ob.material_slots[0].material=mb
print('blind var on, mesh users',bl.users)
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
