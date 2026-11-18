# ws189c: the "dark bar" on the Lot 3 S bank (~(-311.8,-236.0..-233.0)) is NOT a cast shadow (rotating the sun 25 deg left it
# unchanged, renders/test/ws189_suntest_closeup_before_rot25.jpg) — it is a 0.2-0.3 m strip of the far-field skirt left
# unpushed 0.05-0.14 m ABOVE the UNIFY #90 bank lawn (evaluated-skirt probe scripts/ws189/skbar189.out). Drop skirt points in
# a small box there 0.40 m (whole box lies under WS186/WS187 lawn + WS162/WS163 paving). Last modifier on the skirt.
import bpy
SKO189C=bpy.data.objects['Context_skirt_3DEP_ortho_4km']
NAME='WS189c_skirt_drop_Lot3_S_bank'
BX=(-313.0,-310.6,-237.0,-232.4); DZ=-0.40
g=bpy.data.node_groups.get(NAME) or bpy.data.node_groups.new(NAME,'GeometryNodeTree')
g.nodes.clear()
if not g.interface.items_tree:
    g.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry')
    g.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
N=g.nodes; L=g.links
gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
pos=N.new('GeometryNodeInputPosition'); sep=N.new('ShaderNodeSeparateXYZ'); L.new(pos.outputs[0],sep.inputs[0])
def cmp(sock,op,val):
    c=N.new('FunctionNodeCompare'); c.data_type='FLOAT'; c.operation=op; L.new(sock,c.inputs[0]); c.inputs[1].default_value=val; return c.outputs[0]
def AND(a,b):
    n=N.new('FunctionNodeBooleanMath'); n.operation='AND'; L.new(a,n.inputs[0]); L.new(b,n.inputs[1]); return n.outputs[0]
sel=AND(AND(cmp(sep.outputs[0],'GREATER_THAN',BX[0]),cmp(sep.outputs[0],'LESS_THAN',BX[1])),AND(cmp(sep.outputs[1],'GREATER_THAN',BX[2]),cmp(sep.outputs[1],'LESS_THAN',BX[3])))
sp=N.new('GeometryNodeSetPosition'); L.new(gi.outputs[0],sp.inputs['Geometry']); L.new(sel,sp.inputs['Selection']); sp.inputs['Offset'].default_value=(0,0,DZ)
L.new(sp.outputs[0],go.inputs[0])
mc=SKO189C.modifiers.get(NAME) or SKO189C.modifiers.new(NAME,'NODES'); mc.node_group=g
SKO189C.modifiers.move(list(SKO189C.modifiers).index(mc),len(SKO189C.modifiers)-1)
print('FIX189C modifier',NAME,'index',list(SKO189C.modifiers).index(mc),'of',len(SKO189C.modifiers),'box',BX,'dz',DZ,flush=True)
