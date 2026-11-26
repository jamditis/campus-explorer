# ws249 pass 4 (CHAIN on ws249c): Field-on-Domain(FACE) evaluates POSITION on the face domain = the face CENTRE, so both the
# ws249b bool and the ws249c float versions tested "centre inside the box" (ws248's WS248_del_fan does the same; noted, not
# changed). True all-corners test: Capture Attribute on the POINT domain (1/0 inside-box float) before Delete Geometry;
# the captured field read by the FACE-domain selection is the corner average -> > 0.999 = all corners inside.
import bpy
TAG='F249D'; MN='WS249_SE_berm_LiDAR_terrain_snap'
ng=bpy.data.node_groups[MN]; N=ng.nodes; L=ng.links
fd=next((n for n in N if n.type=='FIELD_ON_DOMAIN'),None)
if fd is not None:
    sw=fd.inputs[0].links[0].from_socket.node; c=fd.outputs[0].links[0].to_node
    dl=N['WS249_del_fan']; st=next(x for x in N if x.type=='SET_POSITION')
    cap=N.new('GeometryNodeCaptureAttribute'); cap.domain='POINT'
    it=cap.capture_items.new('FLOAT','inbox')
    L.new(st.outputs[0],cap.inputs[0]); L.new(sw.outputs[0],cap.inputs[1]); L.new(cap.outputs[0],dl.inputs['Geometry'])
    L.new(cap.outputs[1],c.inputs[0]); N.remove(fd)
    print(TAG,'capture inserted; delete geometry input from',dl.inputs['Geometry'].links[0].from_node.name,flush=True)
