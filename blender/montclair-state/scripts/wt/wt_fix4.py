"""wt fix4 (review): gate the WT skirt GN Set Position on Raycast Attribute (wt_in) > 0.001 so skirt verts within 4.5 m of an
open (skirt-facing) patch edge are left exactly as before; the patch edge equals that skirt, so no step at x=80. Same material on both."""
import bpy, json
ng=bpy.data.node_groups['WT_skirt_under_richardson_west']; N=ng.nodes; Lk=ng.links
rc=N['Raycast']; b4=N['Boolean Math.004']; sp=N['Set Position']
c=N.new('FunctionNodeCompare'); c.name='WT_gate_cmp'; c.data_type='FLOAT'; c.operation='GREATER_THAN'; c.inputs[1].default_value=0.001
Lk.new(rc.outputs['Attribute'],c.inputs[0])
a=N.new('FunctionNodeBooleanMath'); a.name='WT_gate_and'; a.operation='AND'
Lk.new(b4.outputs[0],a.inputs[0]); Lk.new(c.outputs[0],a.inputs[1]); Lk.new(a.outputs[0],sp.inputs['Selection'])
print('GATED',[ (l.from_node.name,l.to_node.name) for l in Lk if l.to_node==sp])
bpy.ops.wm.save_mainfile(); print('SAVED')
