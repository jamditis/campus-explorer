# pl: the PK west DTM fill's ortho grass reads pale/whitish (ortho texels over the NW slope). Object-level material copy on
# PK_Feliciano_west_DTM_fill_UNVERIFIED only: Multiply toward lawn green on the BSDF Base Color, faded in from the DTM
# edge (x -246 -> -256) so there is no tone seam. REVERT=1 restores the original slot and removes the copy. UNVERIFIED.
import bpy, os, sys
REV=os.environ.get('REVERT')=='1'; MN='PL_Feliciano_fill_grass_tone_UNVERIFIED'
o=bpy.data.objects['PK_Feliciano_west_DTM_fill_UNVERIFIED']
if 'pl_prev_mat' in o:
    o.material_slots[0].link='OBJECT'; o.material_slots[0].material=None; o.material_slots[0].link='DATA'; del o['pl_prev_mat']
if MN in bpy.data.materials: bpy.data.materials.remove(bpy.data.materials[MN])
if not REV:
    base=o.material_slots[0].material; m=base.copy(); m.name=MN; nt=m.node_tree; N=nt.nodes; L=nt.links.new
    bs=[n for n in N if n.type=='BSDF_PRINCIPLED'][0]; inp=bs.inputs['Base Color']; src=inp.links[0].from_socket if inp.links else None
    mx=N.new('ShaderNodeMix'); mx.data_type='RGBA'; mx.blend_type='MULTIPLY'; mx.clamp_result=True
    g=os.environ.get('GREEN','0.62,0.78,0.50').split(','); mx.inputs[7].default_value=(float(g[0]),float(g[1]),float(g[2]),1)
    if src: L(src,mx.inputs[6])
    else: mx.inputs[6].default_value=inp.default_value
    geo=N.new('ShaderNodeNewGeometry'); sx=N.new('ShaderNodeSeparateXYZ'); L(geo.outputs['Position'],sx.inputs[0])
    mr=N.new('ShaderNodeMapRange'); L(sx.outputs['X'],mr.inputs['Value']); mr.inputs['From Min'].default_value=-246; mr.inputs['From Max'].default_value=-256
    mr.inputs['To Min'].default_value=0; mr.inputs['To Max'].default_value=float(os.environ.get('FAC','1.0')); mr.clamp=True
    L(mr.outputs['Result'],mx.inputs['Factor']); L(mx.outputs[2],inp)
    o['pl_prev_mat']=base.name; o.material_slots[0].link='OBJECT'; o.material_slots[0].material=m
    print('PL_TONE base',base.name,'src',src.node.name if src else None)
else: print('REVERTED_PL_TONE')
if os.environ.get('SAVEAS'): bpy.ops.wm.save_as_mainfile(filepath=os.environ['SAVEAS'],copy=True); print('SAVED_AS')
if '--save' in sys.argv: bpy.ops.wm.save_mainfile(); print('SAVED')
