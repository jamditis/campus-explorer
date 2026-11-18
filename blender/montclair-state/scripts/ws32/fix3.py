# ws32 fix3 (final): angle override did not clear the blotches (they and a standing dark sliver are overlay faces), so the
# joint-overlay faces in the box are deleted instead, like WS22_cut_junction_box; the walk keeps its base sawcut-panel material.
# ws32 fix3 (first try): joint-overlay blotches on the walk crossing the CCOM dock apron came from mixed oz_ang (panel-grid angle,
# blurred from nearest boundary edge) where the walk meets the apron/drive. Force the walk's dominant angle in that box.
import bpy, collections, bmesh
oz=bpy.data.objects['OZ_walk_joints_auto_GN_UNVERIFIED']; ng=oz.modifiers[0].node_group
if 'WS32_oz_ang_box' not in ng.nodes:
    dg=bpy.context.evaluated_depsgraph_get(); dg.update()
    e=oz.evaluated_get(dg); me=e.to_mesh(); a=me.attributes.get('oz_ang'); mw=oz.matrix_world
    print('eval oz_ang',a.domain if a else None)
    vals=[a.data[p.index].value for p in me.polygons if -1<(mw@p.center).x<9 and -39<(mw@p.center).y<-24]
    h=collections.Counter(round(v,2) for v in vals); print('oz_ang hist',h.most_common(6),len(vals))
    dom=h.most_common(1)[0][0]; e.to_mesh_clear()
    st=ng.nodes['Store Named Attribute.002']; name=st.inputs['Name'].default_value
    outs=[(l.to_node,l.to_socket) for l in ng.links if l.from_node==st]
    n=ng.nodes.new('GeometryNodeDeleteGeometry'); n.name='WS32_oz_ang_box'; n.domain='FACE'
    pos=ng.nodes.new('GeometryNodeInputPosition'); sx=ng.nodes.new('ShaderNodeSeparateXYZ'); ng.links.new(pos.outputs[0],sx.inputs[0])
    def cmp(sock,op,val):
        c=ng.nodes.new('FunctionNodeCompare'); c.data_type='FLOAT'; c.operation=op; c.inputs['B'].default_value=val; ng.links.new(sock,c.inputs['A']); return c.outputs[0]
    terms=[cmp(sx.outputs['X'],'GREATER_THAN',-1),cmp(sx.outputs['X'],'LESS_THAN',9),cmp(sx.outputs['Y'],'GREATER_THAN',-39),cmp(sx.outputs['Y'],'LESS_THAN',-24)]
    acc=terms[0]
    for t in terms[1:]:
        b=ng.nodes.new('FunctionNodeBooleanMath'); b.operation='AND'; ng.links.new(acc,b.inputs[0]); ng.links.new(t,b.inputs[1]); acc=b.outputs[0]
    ng.links.new(acc,n.inputs['Selection'])
    ng.links.new(st.outputs[0],n.inputs[0])
    for tn,ts in outs: ng.links.new(n.outputs[0],ts)
    print('WS32 overlay cut box added after',st.name,'rewired',len(outs))
