# ws234 M3a step 4 (self-review of the skirt-visible WIPs, ws234e): outside the extension the skirt keeps its coarse 3DEP height,
# so the extension's ragged DTM edge stands up as a ledge over it (oblique, east of the station). Rebuild the end-of-stack GN
# WS234_skirt_under_M3a_ext: where the downward ray hits the extension -> min(z, ext - 0.35) as before; where it misses but the
# skirt point is within FEATHER m of the extension (Geometry Proximity, edges) -> blend from (nearest ext z - 0.35) at the edge to
# its own z at FEATHER m (smoothstep). Points farther away are untouched. Ground only; no paving touched.
import bpy
FEATHER=20.0
EXT=bpy.data.objects['M3a_north_LiDAR_DTM_1m_ext_y515_UNVERIFIED_seam']
sk=bpy.data.objects['Context_skirt_3DEP_ortho_4km']
m=sk.modifiers['WS234_skirt_under_M3a_ext']
ng=bpy.data.node_groups.new('WS234_skirt_under_M3a_ext_feather','GeometryNodeTree')
ng.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry')
ng.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
N=ng.nodes; L=ng.links
def node(t,**kw):
    n=N.new(t)
    for k,v in kw.items(): setattr(n,k,v)
    return n
def math(op,a=None,b=None):
    n=node('ShaderNodeMath',operation=op)
    for i,x in enumerate((a,b)):
        if x is None: continue
        if isinstance(x,(int,float)): n.inputs[i].default_value=x
        else: L.new(x,n.inputs[i])
    return n.outputs[0]
gi=node('NodeGroupInput'); go=node('NodeGroupOutput')
oi=node('GeometryNodeObjectInfo',transform_space='RELATIVE'); oi.inputs['Object'].default_value=EXT
pos=node('GeometryNodeInputPosition')
up=node('ShaderNodeVectorMath',operation='ADD'); up.inputs[1].default_value=(0,0,400); L.new(pos.outputs[0],up.inputs[0])
rc=node('GeometryNodeRaycast'); L.new(oi.outputs['Geometry'],rc.inputs['Target Geometry']); L.new(up.outputs[0],rc.inputs['Source Position'])
rc.inputs['Ray Direction'].default_value=(0,0,-1); rc.inputs['Ray Length'].default_value=2000
px=node('GeometryNodeProximity'); 
try: px.target_element='EDGES'
except Exception: pass
L.new(oi.outputs['Geometry'],px.inputs[0])
# proximity measured in XY: feed the point's position flattened to the nearest-ext height is not possible directly; use 3D distance (ext and skirt within a few m vertically, FEATHER 20 m)
spn=[s for s in px.inputs if s.name in ('Source Position','Sample Position')]
if spn: L.new(pos.outputs[0],spn[0])
sp=node('ShaderNodeSeparateXYZ'); L.new(pos.outputs[0],sp.inputs[0])
sh=node('ShaderNodeSeparateXYZ'); L.new(rc.outputs['Hit Position'],sh.inputs[0])
sn=node('ShaderNodeSeparateXYZ'); L.new(px.outputs['Position'],sn.inputs[0])
hitz=math('SUBTRACT',sh.outputs['Z'],0.35)
under=math('MINIMUM',sp.outputs['Z'],hitz)
edz=math('SUBTRACT',sn.outputs['Z'],0.35)
mr=node('ShaderNodeMapRange',interpolation_type='SMOOTHSTEP'); L.new(px.outputs['Distance'],mr.inputs['Value']); mr.inputs['From Min'].default_value=0.0; mr.inputs['From Max'].default_value=FEATHER
t=mr.outputs['Result']
# feather: edz*(1-t) + z*t
fe=math('ADD',math('MULTIPLY',edz,math('SUBTRACT',1.0,t)),math('MULTIPLY',sp.outputs['Z'],t))
sw=node('GeometryNodeSwitch',input_type='FLOAT'); L.new(rc.outputs['Is Hit'],sw.inputs['Switch']); L.new(fe,sw.inputs['False']); L.new(under,sw.inputs['True'])
cx=node('ShaderNodeCombineXYZ'); L.new(sp.outputs['X'],cx.inputs['X']); L.new(sp.outputs['Y'],cx.inputs['Y']); L.new(sw.outputs[0],cx.inputs['Z'])
st=node('GeometryNodeSetPosition'); L.new(gi.outputs[0],st.inputs['Geometry']); L.new(cx.outputs[0],st.inputs['Position']); L.new(st.outputs[0],go.inputs[0])
m.node_group=ng
print('F234H feather GN set',ng.name,'proximity inputs',[s.name for s in px.inputs],'target',getattr(px,'target_element',None),flush=True)
