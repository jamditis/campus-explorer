# ws22: OZ auto walk joints (grid direction = nearest walk edge) cross at odd angles where the walks north of Life Hall
# meet (X crossing, Y split, triangle tip), reading as jagged cracks at eye level. Drop the overlay in that junction box so the
# underlying Footpaths_OSM (WS3 sawcut concrete) shows. Box is a node-level selection, reversible (mute WS22_cut_junction_box).
import bpy,os
ng=bpy.data.node_groups['OZ_walk_joints_auto_GN']; N=ng.nodes; L=ng.links
go=[n for n in N if n.bl_idname=='NodeGroupOutput'][0]
src=go.inputs[0].links[0].from_socket
pos=N.new('GeometryNodeInputPosition'); sep=N.new('ShaderNodeSeparateXYZ'); L.new(pos.outputs[0],sep.inputs[0])
def cmp(sock,op,val):
    c=N.new('FunctionNodeCompare'); c.data_type='FLOAT'; c.operation=op; L.new(sock,c.inputs['A']); c.inputs['B'].default_value=val; return c
cs=[cmp(sep.outputs['X'],'GREATER_THAN',5.0),cmp(sep.outputs['X'],'LESS_THAN',37.0),cmp(sep.outputs['Y'],'GREATER_THAN',105.0),cmp(sep.outputs['Y'],'LESS_THAN',130.0)]
a=cs[0]
for c in cs[1:]:
    b=N.new('FunctionNodeBooleanMath'); b.operation='AND'; L.new(a.outputs[0],b.inputs[0]); L.new(c.outputs[0],b.inputs[1]); a=b
dl=N.new('GeometryNodeDeleteGeometry'); dl.name='WS22_cut_junction_box'; dl.domain='FACE'
L.new(src,dl.inputs['Geometry']); L.new(a.outputs[0],dl.inputs['Selection']); L.new(dl.outputs[0],go.inputs[0])
ng['ws22']='joint overlay removed in x5-37 y105-130 (walk junctions N of Life Hall); mute WS22_cut_junction_box to revert'
dg=bpy.context.evaluated_depsgraph_get(); dg.update()
o=bpy.data.objects['OZ_walk_joints_auto_GN_UNVERIFIED']; print('OZ faces now',len(o.evaluated_get(dg).data.polygons))
from mathutils import Vector
sc=bpy.context.scene
O=Vector((34,124,139.4))
for tx,ty in [(28,116.5),(26,116),(24,115)]:
    hit,loc,n,i,ob,m=sc.ray_cast(dg,O,(Vector((tx,ty,137.2))-O).normalized()); print('HIT',ob.name if hit else None,[round(x,2) for x in loc])
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
