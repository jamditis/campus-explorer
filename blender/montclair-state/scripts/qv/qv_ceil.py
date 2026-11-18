# qv (qu Not-fixed: Richardson interior ceiling plane looks dim between the light panels): add a faint 0.22 emission floor to the
# ceiling tile between the panels (fakes bounce light off the floors), shader-only. UNVERIFIED. REVERT=1 restores the original link.
import bpy,os
m=bpy.data.materials['QU_int_ceiling_panels_UNVERIFIED']; N=m.node_tree.nodes; L=m.node_tree.links; P=N['Principled BSDF']; I=P.inputs['Emission Strength']
if 'qv_prev_es_node' in m:
    L.new(N[m['qv_prev_es_node']].outputs[m['qv_prev_es_out']],I); del m['qv_prev_es_node']; del m['qv_prev_es_out']
for n in [n for n in N if n.name.startswith('QV_')]: N.remove(n)
print('QVC reverted')
if os.environ.get('REVERT')!='1':
    s=I.links[0].from_socket; m['qv_prev_es_node']=s.node.name; m['qv_prev_es_out']=list(s.node.outputs).index(s)
    a=N.new('ShaderNodeMath'); a.name='QV_ceiling_bounce_floor'; a.operation='MAXIMUM'; L.new(s,a.inputs[0]); a.inputs[1].default_value=float(os.environ.get('CEIL','0.22')); L.new(a.outputs[0],I)
    print('QVC bounce floor', a.inputs[1].default_value, 'prev', m['qv_prev_es_node'])
if os.environ.get('QVSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
