import bpy, os
s=bpy.context.scene; s.render.engine='CYCLES'; s.cycles.samples=8; s.render.resolution_x=480; s.render.resolution_y=270; s.render.resolution_percentage=100
s.camera=bpy.data.objects['PAT_CAM_bank_top']
o=bpy.data.objects['PA_north_strip_lawn_smooth_UNVERIFIED']
m=bpy.data.materials['PA_Ground_ortho_grass_attrUV']
mode=os.environ['MODE']
if mode=='hide': o.hide_render=True
if mode=='emit':
    nt=m.node_tree; e=nt.nodes.new('ShaderNodeEmission'); a=[n for n in nt.nodes if n.type=='ATTRIBUTE'][0]; nt.links.new(a.outputs['Vector'],e.inputs['Color']); nt.links.new(e.outputs[0],nt.nodes['Material Output'].inputs['Surface'])
s.render.filepath='//renders/wip/pa_test/diag_'+mode+'.png'; bpy.ops.render.render(write_still=True)
