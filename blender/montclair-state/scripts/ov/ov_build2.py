# ov (B): 'crumpled white OSM walk sheets' at eye level = long skinny OSM triangles draped to the DTM (oo) with flat shading, so every
# crease between neighbouring facets reads as a fold. Removable GN modifier OV_walk_smooth on Footpaths_OSM (after OT_follow_skirt_edge):
# Z-only Blur Attribute (8 iterations; 4 in the first pass; x/y untouched), clamped to stay >= DTM+3 cm (raycast to Terrain_LiDAR_DTM_1m), then smooth shading.
# Mesh unedited. ALL UNVERIFIED (visual smoothing, heights still from the DTM). REVERT=1 removes modifier + node group.
import bpy, os, sys
REV=os.environ.get('REVERT')=='1'; SAVE='--save' in sys.argv
GN='OV_walk_smooth'; ob=bpy.data.objects['Footpaths_OSM']; ter=bpy.data.objects['Terrain_LiDAR_DTM_1m']
m=ob.modifiers.get(GN)
if m: ob.modifiers.remove(m)
g=bpy.data.node_groups.get(GN)
if g: bpy.data.node_groups.remove(g)
if 'UNVERIFIED_ov' in ob: del ob['UNVERIFIED_ov']
if REV:
    print('REVERTED2')
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit(0)
ITER=int(os.environ.get('ITER','8'))
g=bpy.data.node_groups.new(GN,'GeometryNodeTree')
g.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry')
g.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
N=g.nodes; L=g.links
gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
pos=N.new('GeometryNodeInputPosition')
bl=N.new('GeometryNodeBlurAttribute'); bl.data_type='FLOAT_VECTOR'; bl.inputs['Iterations'].default_value=ITER
L.new(pos.outputs[0],bl.inputs[0])  # Value (vector) is the first input for FLOAT_VECTOR
sb=N.new('ShaderNodeSeparateXYZ'); L.new(bl.outputs[0],sb.inputs[0])
sp=N.new('ShaderNodeSeparateXYZ'); L.new(pos.outputs[0],sp.inputs[0])
oi=N.new('GeometryNodeObjectInfo'); oi.transform_space='RELATIVE'; oi.inputs['Object'].default_value=ter
src=N.new('ShaderNodeCombineXYZ'); L.new(sp.outputs[0],src.inputs[0]); L.new(sp.outputs[1],src.inputs[1])
up=N.new('ShaderNodeMath'); up.operation='ADD'; up.inputs[1].default_value=40.0; L.new(sb.outputs[2],up.inputs[0]); L.new(up.outputs[0],src.inputs[2])
rc=N.new('GeometryNodeRaycast'); rc.data_type='FLOAT'
L.new(oi.outputs['Geometry'],rc.inputs['Target Geometry']); L.new(src.outputs[0],rc.inputs['Source Position'])
rc.inputs['Ray Direction'].default_value=(0,0,-1); rc.inputs['Ray Length'].default_value=200.0
sh=N.new('ShaderNodeSeparateXYZ'); L.new(rc.outputs['Hit Position'],sh.inputs[0])
fl=N.new('ShaderNodeMath'); fl.operation='ADD'; fl.inputs[1].default_value=0.03; L.new(sh.outputs[2],fl.inputs[0])
# no hit -> floor = -1e4 (keep blurred z)
sw=N.new('GeometryNodeSwitch'); sw.input_type='FLOAT'; sw.inputs['False'].default_value=-1e4
L.new(rc.outputs['Is Hit'],sw.inputs['Switch']); L.new(fl.outputs[0],sw.inputs['True'])
mx=N.new('ShaderNodeMath'); mx.operation='MAXIMUM'; L.new(sb.outputs[2],mx.inputs[0]); L.new(sw.outputs[0],mx.inputs[1])
# never lift more than 15 cm above the incoming (draped) z
cap=N.new('ShaderNodeMath'); cap.operation='ADD'; cap.inputs[1].default_value=0.15; L.new(sp.outputs[2],cap.inputs[0])
mn=N.new('ShaderNodeMath'); mn.operation='MINIMUM'; L.new(mx.outputs[0],mn.inputs[0]); L.new(cap.outputs[0],mn.inputs[1])
cx=N.new('ShaderNodeCombineXYZ'); L.new(sp.outputs[0],cx.inputs[0]); L.new(sp.outputs[1],cx.inputs[1]); L.new(mn.outputs[0],cx.inputs[2])
st=N.new('GeometryNodeSetPosition'); L.new(gi.outputs[0],st.inputs['Geometry']); L.new(cx.outputs[0],st.inputs['Position'])
ss=N.new('GeometryNodeSetShadeSmooth'); L.new(st.outputs[0],ss.inputs['Geometry'])
L.new(ss.outputs[0],go.inputs[0])
md=ob.modifiers.new(GN,'NODES'); md.node_group=g
ob['UNVERIFIED_ov']='OV_walk_smooth: Z-only blur %d it, >= DTM+3cm, <= drape+15cm, smooth shading'%ITER
print('BUILT2',[m.name for m in ob.modifiers])
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
