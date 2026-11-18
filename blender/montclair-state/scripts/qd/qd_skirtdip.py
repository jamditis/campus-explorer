# qd (Nov 2 2026, ~6:30 AM ET): SW bank edge west of Feliciano. The context skirt and the pz feather / pk fill cross within
# 1-3 cm, so the crossing reads as a hard tone line. Removable GN modifier QD_skirt_under_pzpk (last in the skirt stack):
# subdivides only the skirt faces near the pz/pk footprint, ray-casts down onto pz+pk and, where the skirt is within
# +0.5 m / -0.06 m of them, drops it to 6 cm under them. Mesh unedited. REVERT=1 removes modifier + node group. UNVERIFIED.
import bpy, os
REV=os.environ.get('REVERT')=='1'
sk=bpy.data.objects['Context_skirt_3DEP_ortho_4km']; NM='QD_skirt_under_pzpk'
TG=['PZ_Feliciano_SW_DTM_edge_feather_UNVERIFIED','PK_Feliciano_west_DTM_fill_UNVERIFIED']
if REV:
    m=sk.modifiers.get(NM)
    if m: sk.modifiers.remove(m)
    ng=bpy.data.node_groups.get(NM)
    if ng: bpy.data.node_groups.remove(ng)
    print('QD_SKIRTDIP reverted')
else:
    assert sk.matrix_world.is_identity or True
    W=[]
    for n in TG:
        o=bpy.data.objects[n]; W+= [o.matrix_world@v.co for v in o.data.vertices]
    inv=sk.matrix_world.inverted(); W=[inv@w for w in W]
    M=float(os.environ.get('QD_MARGIN','30'))
    x0,x1=min(w.x for w in W)-M,max(w.x for w in W)+M; y0,y1=min(w.y for w in W)-M,max(w.y for w in W)+M
    print('QD bbox',round(x0,1),round(x1,1),round(y0,1),round(y1,1),'skirt polys',len(sk.data.polygons),'mods',[m.name for m in sk.modifiers])
    ng=bpy.data.node_groups.new(NM,'GeometryNodeTree')
    ng.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry')
    ng.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
    N=ng.nodes; L=ng.links
    gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
    pos=N.new('GeometryNodeInputPosition'); sxyz=N.new('ShaderNodeSeparateXYZ'); L.new(pos.outputs[0],sxyz.inputs[0])
    def cmp(sock,val,op):
        c=N.new('FunctionNodeCompare'); c.data_type='FLOAT'; c.operation=op; L.new(sock,c.inputs[0]); c.inputs[1].default_value=val; return c.outputs[0]
    def band(a,b):
        n=N.new('FunctionNodeBooleanMath'); n.operation='AND'; L.new(a,n.inputs[0]); L.new(b,n.inputs[1]); return n.outputs[0]
    sel=band(band(cmp(sxyz.outputs[0],x0,'GREATER_THAN'),cmp(sxyz.outputs[0],x1,'LESS_THAN')),band(cmp(sxyz.outputs[1],y0,'GREATER_THAN'),cmp(sxyz.outputs[1],y1,'LESS_THAN')))
    # narrower: faces whose centre is within QD_NEAR m of pz/pk (geometry proximity), AND inside the bbox
    jp=N.new('GeometryNodeJoinGeometry')
    for n in TG:
        oi=N.new('GeometryNodeObjectInfo'); oi.transform_space='RELATIVE'; oi.inputs['Object'].default_value=bpy.data.objects[n]; L.new(oi.outputs['Geometry'],jp.inputs[0])
    gp=N.new('GeometryNodeProximity'); gp.target_element='FACES'; L.new(jp.outputs[0],gp.inputs[0])
    sel=band(sel,cmp(gp.outputs['Distance'],float(os.environ.get('QD_NEAR','8')),'LESS_THAN'))
    sep=N.new('GeometryNodeSeparateGeometry'); sep.domain='FACE'; L.new(gi.outputs[0],sep.inputs[0]); L.new(sel,sep.inputs[1])
    sub=N.new('GeometryNodeSubdivideMesh'); sub.inputs['Level'].default_value=int(os.environ.get('QD_LEVEL','3')); L.new(sep.outputs[0],sub.inputs[0])
    # targets
    j=N.new('GeometryNodeJoinGeometry')
    for n in TG:
        oi=N.new('GeometryNodeObjectInfo'); oi.transform_space='RELATIVE'; oi.inputs['Object'].default_value=bpy.data.objects[n]; L.new(oi.outputs['Geometry'],j.inputs[0])
    rc=N.new('GeometryNodeRaycast'); L.new(j.outputs[0],rc.inputs['Target Geometry'])
    pos2=N.new('GeometryNodeInputPosition'); add=N.new('ShaderNodeVectorMath'); add.operation='ADD'; L.new(pos2.outputs[0],add.inputs[0]); add.inputs[1].default_value=(0,0,50)
    L.new(add.outputs[0],rc.inputs['Source Position']); rc.inputs['Ray Direction'].default_value=(0,0,-1); rc.inputs['Ray Length'].default_value=200
    hz=N.new('ShaderNodeSeparateXYZ'); L.new(rc.outputs['Hit Position'],hz.inputs[0])
    pz=N.new('ShaderNodeSeparateXYZ'); L.new(pos2.outputs[0],pz.inputs[0])
    d=N.new('ShaderNodeMath'); d.operation='SUBTRACT'; L.new(pz.outputs[2],d.inputs[0]); L.new(hz.outputs[2],d.inputs[1])  # skirt - target
    c1=cmp(d.outputs[0],-0.06,'GREATER_THAN'); c2=cmp(d.outputs[0],0.5,'LESS_THAN')
    s=band(band(c1,c2),rc.outputs['Is Hit'])
    tz=N.new('ShaderNodeMath'); tz.operation='SUBTRACT'; L.new(hz.outputs[2],tz.inputs[0]); tz.inputs[1].default_value=0.06
    cxyz=N.new('ShaderNodeCombineXYZ'); L.new(pz.outputs[0],cxyz.inputs[0]); L.new(pz.outputs[1],cxyz.inputs[1]); L.new(tz.outputs[0],cxyz.inputs[2])
    sp=N.new('GeometryNodeSetPosition'); L.new(sub.outputs[0],sp.inputs['Geometry']); L.new(s,sp.inputs['Selection']); L.new(cxyz.outputs[0],sp.inputs['Position'])
    jo=N.new('GeometryNodeJoinGeometry'); L.new(sp.outputs[0],jo.inputs[0]); L.new(sep.outputs[1],jo.inputs[0])
    L.new(jo.outputs[0],go.inputs[0])
    m=sk.modifiers.new(NM,'NODES'); m.node_group=ng
    sk['UNVERIFIED_qd']='skirt dropped 6 cm under pz/pk where within +0.5/-0.06 m (GN, mesh unedited)'
    dg=bpy.context.evaluated_depsgraph_get(); e=sk.evaluated_get(dg).data
    print('QD_SKIRTDIP applied, eval polys',len(e.polygons),'verts',len(e.vertices))
