# qe: removable GN modifier QE_door_clear on the OR skirt-window object for CCIS: drops OR lower-storey window units that overlap the new qe entrances
# (avoid doubled windows, 4a). Mesh unedited. REVERT=1 removes modifier + node group. UNVERIFIED.
import bpy, os
from mathutils import Vector
OBS=[[o for o in bpy.data.objects if o.name.startswith('OR_skirt_win_Center for Computing')][0], bpy.data.objects['OS_skirt_sill_drip_grime']]
GN='QE_CCIS_door_clear_GN'
for on in OBS:
    if 'QE_door_clear' in on.modifiers: on.modifiers.remove(on.modifiers['QE_door_clear'])
if GN in bpy.data.node_groups: bpy.data.node_groups.remove(bpy.data.node_groups[GN])
if os.environ.get('REVERT')!='1':
    pts=[Vector(p) for p in bpy.context.scene['qe_door_pts']]
    ng=bpy.data.node_groups.new(GN,'GeometryNodeTree')
    ng.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry'); ng.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
    N=ng.nodes; L=ng.links; gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
    pos=N.new('GeometryNodeInputPosition'); dele=N.new('GeometryNodeDeleteGeometry'); dele.domain='FACE'
    prev=None
    for p in pts:
        # horizontal distance only: scale z to 0
        sc=N.new('ShaderNodeVectorMath'); sc.operation='MULTIPLY'; sc.inputs[1].default_value=(1,1,0); L.new(pos.outputs[0],sc.inputs[0])
        d=N.new('ShaderNodeVectorMath'); d.operation='DISTANCE'; d.inputs[1].default_value=(p.x,p.y,0); L.new(sc.outputs[0],d.inputs[0])
        lt=N.new('FunctionNodeCompare'); lt.data_type='FLOAT'; lt.operation='LESS_THAN'; L.new(d.outputs['Value'],lt.inputs[0]); lt.inputs[1].default_value=float(os.environ.get('DR','3.4'))
        if prev is None: prev=lt.outputs[0]
        else:
            o_=N.new('FunctionNodeBooleanMath'); o_.operation='OR'; L.new(prev,o_.inputs[0]); L.new(lt.outputs[0],o_.inputs[1]); prev=o_.outputs[0]
    L.new(gi.outputs[0],dele.inputs['Geometry']); L.new(prev,dele.inputs['Selection']); L.new(dele.outputs[0],go.inputs[0])
    for on in OBS:
        m=on.modifiers.new('QE_door_clear','NODES'); m.node_group=ng
    dg=bpy.context.evaluated_depsgraph_get()
    for on in OBS: print('QE_doorclear',on.name,len(on.data.polygons),'->',len(on.evaluated_get(dg).data.polygons))
else:
    print('QE_doorclear reverted')
