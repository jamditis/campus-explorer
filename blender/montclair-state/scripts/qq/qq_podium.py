# qq_podium: pale membrane patch on the CCIS podium tile roof (~(31.7-32.4, 216.8-221.3), z 141.09) = faces flattened by
# QL_ccis_wall_top_clamp; flat faces (nz>0.985) render as membrane unless em_ringforce=1. New last GN modifier
# QQ_ccis_podium_patch_ring stores em_ringforce=1 on points inside the box x 30.8-33.6, y 215.8-222.2, z 140.95-141.25.
# UNVERIFIED (tile continuity assumed from the surrounding ring). REVERT=1 removes the modifier and node group.
import bpy, os
R=os.environ.get('REVERT')=='1'
o=bpy.data.objects['Center for Computing and Information Science roof (LiDAR)']; NM='QQ_ccis_podium_patch_ring'
m=o.modifiers.get(NM)
if m: o.modifiers.remove(m)
g=bpy.data.node_groups.get(NM+'_GN')
if g: bpy.data.node_groups.remove(g)
if not R:
    Mi=o.matrix_world.inverted(); from mathutils import Vector
    lo=Mi@Vector((30.8,215.8,140.95)); hi=Mi@Vector((33.6,222.2,141.25))
    lo,hi=Vector([min(a,b) for a,b in zip(lo,hi)]),Vector([max(a,b) for a,b in zip(lo,hi)])
    g=bpy.data.node_groups.new(NM+'_GN','GeometryNodeTree')
    g.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry'); g.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
    N=g.nodes; L=g.links.new; gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
    pos=N.new('GeometryNodeInputPosition'); sep=N.new('ShaderNodeSeparateXYZ'); L(pos.outputs[0],sep.inputs[0])
    acc=None
    for k,ax in enumerate('XYZ'):
        for cmp,val in (('GREATER_THAN',lo[k]),('LESS_THAN',hi[k])):
            c=N.new('FunctionNodeCompare'); c.data_type='FLOAT'; c.operation=cmp; L(sep.outputs[k],c.inputs[0]); c.inputs[1].default_value=val
            if acc is None: acc=c.outputs[0]
            else:
                b=N.new('FunctionNodeBooleanMath'); b.operation='AND'; L(acc,b.inputs[0]); L(c.outputs[0],b.inputs[1]); acc=b.outputs[0]
    st=N.new('GeometryNodeStoreNamedAttribute'); st.data_type='FLOAT'; st.domain='POINT'; st.inputs['Name'].default_value='em_ringforce'
    st.inputs['Value'].default_value=1.0
    L(gi.outputs[0],st.inputs['Geometry']); L(acc,st.inputs['Selection']); L(st.outputs[0],go.inputs[0])
    md=o.modifiers.new(NM,'NODES'); md.node_group=g
    dg=bpy.context.evaluated_depsgraph_get(); e=o.evaluated_get(dg).data; a=e.attributes['em_ringforce']
    print('QQP set', sum(1 for v in a.data if v.value>0.5), 'verts', len(e.vertices))
else: print('QQP reverted')
exec(open('scripts/pn/pn_sig.py').read())
if os.environ.get('QQSAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
elif os.environ.get('QQSAVEAS'): bpy.ops.wm.save_as_mainfile(filepath=os.environ['QQSAVEAS'],copy=True); print('SAVED_AS')
