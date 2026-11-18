# qj: BD_farfield_3DEP_ortho (coarse far-field backdrop) poked up through the NE terrain/skirt seam (grey untextured sheet at
# z~104-105 over x 212-235, y 180-215). Removable GN 'QJ_farfield_under_skirt' keeps every far-field vertex at least 0.4 m
# under the evaluated Terrain_LiDAR_DTM_1m + Context_skirt_3DEP_ortho_4km wherever those exist. REVERT=1 removes it.
import bpy, os
REV=os.environ.get('REVERT')=='1'
F=bpy.data.objects['BD_farfield_3DEP_ortho']; MODN='QJ_farfield_under_skirt'
m=F.modifiers.get(MODN)
if m:
    ng=m.node_group; F.modifiers.remove(m)
    if ng and ng.users==0: bpy.data.node_groups.remove(ng)
if not REV:
    ng=bpy.data.node_groups.new(MODN+'_GN','GeometryNodeTree')
    ng.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry'); ng.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
    N=ng.nodes; L=ng.links; gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
    jn=N.new('GeometryNodeJoinGeometry')
    for nm in ('Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km'):
        oi=N.new('GeometryNodeObjectInfo'); oi.inputs['Object'].default_value=bpy.data.objects[nm]; oi.transform_space='RELATIVE'; L.new(oi.outputs['Geometry'],jn.inputs[0])
    pos=N.new('GeometryNodeInputPosition'); sep=N.new('ShaderNodeSeparateXYZ'); L.new(pos.outputs[0],sep.inputs[0])
    comb=N.new('ShaderNodeCombineXYZ'); comb.inputs['Z'].default_value=1000; L.new(sep.outputs[0],comb.inputs[0]); L.new(sep.outputs[1],comb.inputs[1])
    rc=N.new('GeometryNodeRaycast'); rc.inputs['Ray Direction'].default_value=(0,0,-1); rc.inputs['Ray Length'].default_value=3000
    L.new(jn.outputs[0],rc.inputs['Target Geometry']); L.new(comb.outputs[0],rc.inputs['Source Position'])
    hs=N.new('ShaderNodeSeparateXYZ'); L.new(rc.outputs['Hit Position'],hs.inputs[0])
    sub=N.new('ShaderNodeMath'); sub.operation='SUBTRACT'; sub.inputs[1].default_value=0.4; L.new(hs.outputs[2],sub.inputs[0])
    gt=N.new('ShaderNodeMath'); gt.operation='GREATER_THAN'; L.new(sep.outputs[2],gt.inputs[0]); L.new(sub.outputs[0],gt.inputs[1])
    an=N.new('FunctionNodeBooleanMath'); an.operation='AND'; L.new(rc.outputs['Is Hit'],an.inputs[0]); L.new(gt.outputs[0],an.inputs[1])
    c2=N.new('ShaderNodeCombineXYZ'); L.new(sep.outputs[0],c2.inputs[0]); L.new(sep.outputs[1],c2.inputs[1]); L.new(sub.outputs[0],c2.inputs[2])
    sp=N.new('GeometryNodeSetPosition'); L.new(gi.outputs[0],sp.inputs['Geometry']); L.new(an.outputs[0],sp.inputs['Selection']); L.new(c2.outputs[0],sp.inputs['Position'])
    # + delete far-field faces whose centre lies well inside the 4 km skirt (skirt always covers them; holes are filled by QJ fill)
    from mathutils import Vector as V_
    SK=bpy.data.objects['Context_skirt_3DEP_ortho_4km']; bb=[SK.matrix_world@V_(c) for c in SK.bound_box]
    X0=min(v.x for v in bb)+300; X1=max(v.x for v in bb)-300; Y0=min(v.y for v in bb)+300; Y1=max(v.y for v in bb)-300; print('FARFIELD delete box',round(X0),round(X1),round(Y0),round(Y1))
    p2=N.new('GeometryNodeInputPosition'); s3=N.new('ShaderNodeSeparateXYZ'); L.new(p2.outputs[0],s3.inputs[0]); acc=None
    for out,lo,hi in ((0,X0,X1),(1,Y0,Y1)):
        a=N.new('ShaderNodeMath'); a.operation='GREATER_THAN'; a.inputs[1].default_value=lo; L.new(s3.outputs[out],a.inputs[0])
        b=N.new('ShaderNodeMath'); b.operation='LESS_THAN'; b.inputs[1].default_value=hi; L.new(s3.outputs[out],b.inputs[0])
        for t in (a,b):
            if acc is None: acc=t.outputs[0]
            else: an2=N.new('FunctionNodeBooleanMath'); an2.operation='AND'; L.new(acc,an2.inputs[0]); L.new(t.outputs[0],an2.inputs[1]); acc=an2.outputs[0]
    dl=N.new('GeometryNodeDeleteGeometry'); dl.domain='FACE'; L.new(sp.outputs[0],dl.inputs['Geometry']); L.new(acc,dl.inputs['Selection'])
    L.new(dl.outputs[0],go.inputs[0]); md=F.modifiers.new(MODN,'NODES'); md.node_group=ng
    dg=bpy.context.evaluated_depsgraph_get(); Fe=F.evaluated_get(dg)
    import numpy as np
    a=np.zeros(len(F.data.vertices)*3); F.data.vertices.foreach_get('co',a); print('FARFIELD faces',len(F.data.polygons),'->',len(Fe.data.polygons)); b=None
