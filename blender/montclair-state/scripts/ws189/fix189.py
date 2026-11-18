# ws189 fix: Lot 36 W eye foreground wedge = sliver of the far-field skirt (Context_skirt_3DEP_ortho_4km) left UNPUSHED
# between the WS163/WS167 skirt_under boxes at x -334.6..-329.4, y -232.0..-231.4 (up to +0.22 m above WS181 asphalt,
# measured on the evaluated skirt at 0.2 m, scripts/ws189/skfine189.out). Clamp skirt z below the LiDAR patches in a small
# box fully covered by WS181 asphalt / WS163 patch (tops 115.54-115.84): z = min(z, 115.35). Last modifier on the skirt.
import bpy
SKO189=bpy.data.objects['Context_skirt_3DEP_ortho_4km']
NAME='WS189_skirt_clamp_Lot36_W'
X0,X1,Y0,Y1,ZC=-337.5,-328.0,-233.2,-230.6,115.35
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
sel=AND(AND(cmp(sep.outputs[0],'GREATER_THAN',X0),cmp(sep.outputs[0],'LESS_THAN',X1)),AND(cmp(sep.outputs[1],'GREATER_THAN',Y0),cmp(sep.outputs[1],'LESS_THAN',Y1)))
mn=N.new('ShaderNodeMath'); mn.operation='MINIMUM'; L.new(sep.outputs[2],mn.inputs[0]); mn.inputs[1].default_value=ZC
cb=N.new('ShaderNodeCombineXYZ'); L.new(sep.outputs[0],cb.inputs[0]); L.new(sep.outputs[1],cb.inputs[1]); L.new(mn.outputs[0],cb.inputs[2])
sp=N.new('GeometryNodeSetPosition'); L.new(gi.outputs[0],sp.inputs['Geometry']); L.new(sel,sp.inputs['Selection']); L.new(cb.outputs[0],sp.inputs['Position'])
L.new(sp.outputs[0],go.inputs[0])
m=SKO189.modifiers.get(NAME) or SKO189.modifiers.new(NAME,'NODES'); m.node_group=g
# keep it last
while SKO189.modifiers[-1].name!=NAME: bpy.ops.object.modifier_move_down({'object':SKO189},modifier=NAME) if False else SKO189.modifiers.move(list(SKO189.modifiers).index(m),len(SKO189.modifiers)-1)
print('FIX189 modifier',NAME,'index',list(SKO189.modifiers).index(m),'of',len(SKO189.modifiers),'box',X0,X1,Y0,Y1,'zc',ZC,flush=True)
