import bpy
from mathutils import Vector
src=bpy.data.materials['Lawn_Varied_Oct_local_fade']
m=bpy.data.materials.get('WS70_berm_lawn_ortho_matched') or src.copy(); m.name='WS70_berm_lawn_ortho_matched'
nt=m.node_tree; b=[n for n in nt.nodes if n.type=='BSDF_PRINCIPLED'][0]
if not nt.nodes.get('WS70_match'):
    l=b.inputs['Base Color'].links[0]; fs=l.from_socket
    h=nt.nodes.new('ShaderNodeHueSaturation'); h.name='WS70_match'
    h.inputs['Hue'].default_value=0.53; h.inputs['Saturation'].default_value=0.62; h.inputs['Value'].default_value=1.25
    nt.links.new(fs,h.inputs['Color']); nt.links.new(h.outputs['Color'],b.inputs['Base Color'])
o=bpy.data.objects['WS70_gap_strip_grass_berms']; o.data.materials[0]=m
print('M70 ok')
for o in bpy.data.objects:
    if 'kasser' in o.name.lower() and o.type=='MESH':
        bb=[o.matrix_world@Vector(c) for c in o.bound_box]
        print('M70 K',o.name[:50],[round(f(v[i] for v in bb),1) for i in range(3) for f in (min,max)])
bpy.ops.wm.save_mainfile(); print('M70 saved')
