# qk (Nov 2 2026): Roads_OSM / Footpaths_OSM ends at the NE edge (x~205-228, y 195-215) stood ~2.7 m above the qj fill:
# there neither the terrain (lowered by QJ_NE_seam_ramp) nor the skirt (cut under the terrain) is hit, so OP/OO/OT drapes
# left them at a stale z (105.93) and the side faces read as dark jagged curtains. Removable GN 'QK_NE_end_drape' (last
# modifier on both) raycasts terrain + QJ fill + skirt and lowers verts in the NE box that sit >0.02 m above that ground
# to ground + offset (road +3 cm, walk +5 cm, same as op/oo). Only lowers. APPROXIMATE (ground there is the qj ramp/fill).
# REVERT=1 -> removes the modifiers + node group (exact pre-qk).
import bpy, os
REV=os.environ.get('REVERT')=='1'
MN='QK_NE_end_drape'; GN='QK_NE_end_drape_GN'
OBJ={'Roads_OSM':0.03,'Footpaths_OSM':0.05}
for n in OBJ:
    o=bpy.data.objects[n]; m=o.modifiers.get(MN)
    if m: o.modifiers.remove(m)
    if 'UNVERIFIED_qk' in o: del o['UNVERIFIED_qk']
g=bpy.data.node_groups.get(GN)
if g: bpy.data.node_groups.remove(g)
if REV: print('QK roads reverted')
else:
    T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; F=bpy.data.objects['QJ_NE_seam_fill_UNVERIFIED']; S=bpy.data.objects['Context_skirt_3DEP_ortho_4km']
    ng=bpy.data.node_groups.new(GN,'GeometryNodeTree')
    ng.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry')
    so=ng.interface.new_socket('Offset',in_out='INPUT',socket_type='NodeSocketFloat'); so.default_value=0.03
    ng.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
    N=ng.nodes; L=ng.links.new; gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
    j=N.new('GeometryNodeJoinGeometry')
    for ob in (T,F,S):
        oi=N.new('GeometryNodeObjectInfo'); oi.inputs['Object'].default_value=ob; oi.transform_space='RELATIVE'; L(oi.outputs['Geometry'],j.inputs[0])
    pos=N.new('GeometryNodeInputPosition'); sp=N.new('ShaderNodeSeparateXYZ'); L(pos.outputs[0],sp.inputs[0])
    # ground = max of 5 rays (centre + 4 at 0.6 m) so coarse road/walk faces clear the steep QJ fill cells between verts
    src=N.new('ShaderNodeCombineXYZ'); src.inputs['Z'].default_value=400; L(sp.outputs[0],src.inputs[0]); L(sp.outputs[1],src.inputs[1])
    mx=None; rc=None
    for ox,oy in ((0,0),(0.6,0),(-0.6,0),(0,0.6),(0,-0.6)):
        ad=N.new('ShaderNodeVectorMath'); ad.operation='ADD'; L(src.outputs[0],ad.inputs[0]); ad.inputs[1].default_value=(ox,oy,0)
        r=N.new('GeometryNodeRaycast'); r.inputs['Ray Direction'].default_value=(0,0,-1); r.inputs['Ray Length'].default_value=1000
        L(j.outputs[0],r.inputs['Target Geometry']); L(ad.outputs[0],r.inputs['Source Position'])
        h=N.new('ShaderNodeSeparateXYZ'); L(r.outputs['Hit Position'],h.inputs[0])
        sw=N.new('GeometryNodeSwitch'); sw.input_type='FLOAT'; L(r.outputs['Is Hit'],sw.inputs['Switch']); sw.inputs['False'].default_value=-1e4; L(h.outputs[2],sw.inputs['True'])
        if rc is None: rc=r; mx=sw.outputs[0]
        else: m=N.new('ShaderNodeMath'); m.operation='MAXIMUM'; L(mx,m.inputs[0]); L(sw.outputs[0],m.inputs[1]); mx=m.outputs[0]
    nz=N.new('ShaderNodeMath'); nz.operation='ADD'; L(mx,nz.inputs[0]); L(gi.outputs['Offset'],nz.inputs[1])
    dz=N.new('ShaderNodeMath'); dz.operation='SUBTRACT'; L(sp.outputs[2],dz.inputs[0]); L(nz.outputs[0],dz.inputs[1])
    gt=N.new('FunctionNodeCompare'); gt.data_type='FLOAT'; gt.operation='GREATER_THAN'; L(dz.outputs[0],gt.inputs[0]); gt.inputs[1].default_value=0.02
    def cmp(sock,op,v):
        c=N.new('FunctionNodeCompare'); c.data_type='FLOAT'; c.operation=op; L(sock,c.inputs[0]); c.inputs[1].default_value=v; return c.outputs[0]
    sel=rc.outputs['Is Hit']
    for s in (gt.outputs[0],cmp(sp.outputs[0],'GREATER_THAN',195.0),cmp(sp.outputs[0],'LESS_THAN',250.0),cmp(sp.outputs[1],'GREATER_THAN',135.0),cmp(sp.outputs[1],'LESS_THAN',258.0)):
        a=N.new('FunctionNodeBooleanMath'); a.operation='AND'; L(sel,a.inputs[0]); L(s,a.inputs[1]); sel=a.outputs[0]
    np_=N.new('ShaderNodeCombineXYZ'); L(sp.outputs[0],np_.inputs[0]); L(sp.outputs[1],np_.inputs[1]); L(nz.outputs[0],np_.inputs[2])
    st=N.new('GeometryNodeSetPosition'); L(gi.outputs[0],st.inputs['Geometry']); L(sel,st.inputs['Selection']); L(np_.outputs[0],st.inputs['Position'])
    L(st.outputs[0],go.inputs[0])
    for n,off in OBJ.items():
        o=bpy.data.objects[n]; m=o.modifiers.new(MN,'NODES'); m.node_group=ng
        m[ng.interface.items_tree['Offset'].identifier]=off
        o['UNVERIFIED_qk']='qk: NE-edge ends lowered onto terrain/QJ fill/skirt + offset (GN QK_NE_end_drape)'
    print('QK roads drape added')
