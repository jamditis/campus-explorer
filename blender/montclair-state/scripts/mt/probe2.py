import bpy
from mathutils import Vector
for o in bpy.data.objects:
    if o.type=='FONT' and ('tower' in o.name.lower()):
        d=o.data
        print('L',o.name,tuple(round(x,3) for x in o.matrix_world.translation),tuple(round(x,3) for x in o.rotation_euler),tuple(round(x,3) for x in o.scale),'body',repr(d.body),'size',d.size,'ext',d.extrude,'align',d.align_x,d.align_y,'font',d.font.name if d.font else None,'mats',[m.name if m else None for m in d.materials],'hide',o.hide_render,o.hide_viewport, 'dims',tuple(round(x,3) for x in o.dimensions))
        print('  props',{k:o[k] for k in o.keys() if not k.startswith('_')})
for c in bpy.data.collections:
    if 'Day2' in c.name: print('COLL',c.name,c.hide_render)
for o in bpy.data.objects:
    if o.type=='CAMERA' and ('ccom' in o.name.lower() or 'tower' in o.name.lower()):
        print('CAM',o.name,tuple(round(x,2) for x in o.location),tuple(round(x,3) for x in o.rotation_euler),o.data.lens)
o=bpy.data.objects['CCOM tower 4a lettering COLLEGE OF']
m=o.data.materials[0] if o.data.materials else None
if m and m.node_tree:
    for n in m.node_tree.nodes:
        if n.type=='BSDF_PRINCIPLED': print('MAT',m.name,tuple(n.inputs['Base Color'].default_value),n.inputs['Roughness'].default_value)
