# ws46: fix terrain holes at x 93..140, y -73..-60 (Context_ground 105 m below shows through).
# Cause: QI_east_edge_LiDAR_patch deletes FACES whose CENTRE raycasts onto the delete probe; big fan-regrid
# faces with centres at y>-60 reach down to y -73, so they vanish while the patch stops at y -60.
# Fix: capture Is Hit on the POINT domain, delete faces only when ALL corners hit. Lite-tested ws46: misses 252 -> 0.
import bpy
o=bpy.data.objects['Terrain_LiDAR_DTM_1m']; m=o.modifiers['QI_east_edge_LiDAR_patch']; ng=m.node_group; N=ng.nodes; L=ng.links
if 'WS46_capture_hit_point' in N: print('F46 already applied'); raise SystemExit
dn=N['Delete Geometry']; gi=N['Group Input']; rc=N['Raycast']
cap=N.new('GeometryNodeCaptureAttribute'); cap.name='WS46_capture_hit_point'; cap.domain='POINT'
cap.capture_items.new('BOOLEAN','hit')
for l in list(L):
    if l.to_node==dn: L.remove(l)
L.new(gi.outputs[0],cap.inputs[0]); L.new(rc.outputs['Is Hit'],cap.inputs[1])
L.new(cap.outputs[0],dn.inputs['Geometry']); L.new(cap.outputs[1],dn.inputs['Selection'])
print('F46 patched QI node group'); bpy.ops.wm.save_mainfile()
