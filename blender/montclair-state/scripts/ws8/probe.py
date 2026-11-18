import bpy
for o in bpy.data.objects:
  if o.type=='CAMERA' and ('Cole' in o.name or 'cole' in o.name or o.name.startswith('WS')): print('CAM',o.name,[round(v,1) for v in o.location])
p=bpy.data.objects['WS5_Cole_plaza_circle_quatrefoil_20261109']
print('PLAZA mats',[m.name for m in p.data.materials])
def dump(mn):
  m=bpy.data.materials.get(mn)
  if not m: print('NOMAT',mn); return
  print('MAT',mn)
  for n in m.node_tree.nodes:
    if n.type=='VALTORGB': print('  ramp',n.name,[tuple(round(c,3) for c in e.color[:3]) for e in n.color_ramp.elements])
    if n.type=='BSDF_PRINCIPLED': print('  bsdf base',tuple(round(c,3) for c in n.inputs['Base Color'].default_value[:3]), 'linked',n.inputs['Base Color'].is_linked)
    if n.type=='RGB': print('  rgb',tuple(round(c,3) for c in n.outputs[0].default_value[:3]))
    if n.type=='MIX' and n.data_type=='RGBA': print('  mixB',tuple(round(c,3) for c in n.inputs['B'].default_value[:3]))
for mn in [m.name for m in p.data.materials]: dump(mn)
w=bpy.data.objects.get('WS3_Cole_plaza_paving_20261109')
if w:
  print('WS3 mats',[m.name for m in w.data.materials])
  for m in w.data.materials: dump(m.name)
