# ws249 pass 3 (CHAIN on ws249b): (1) the WS249 SE patch replaced by the widened h249.json (x -186..-168, y 42..72);
# (2) WS249_del_fan selection fixed: a BOOLEAN point field read on the FACE domain is true if ANY corner is inside
# (ws249b deleted 12 fan faces reaching 6 m outside the box -> 131 hole samples east of the patch), so the box test is now
# a FLOAT (1/0) averaged over the face corners and must be > 0.999 (= all corners inside); box widened to
# x -201..-169, y 44.2..71 to take the 15.9 m2 fan face (-199.8, 60.4)-(-171.5, 52.5) that made the +0.75 m hump.
import bpy, json
TAG='F249C'; PN='WS249_SE_berm_LiDAR2023_ground_patch_1m'; MN='WS249_SE_berm_LiDAR_terrain_snap'
J=json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws249/h249.json'))
o=bpy.data.objects[PN]; old=o.data; mat=old.materials[0]
me=bpy.data.meshes.new(PN); me.from_pydata(J['V'],[],[tuple(f) for f in J['F']]); me.validate(); me.update()
for p in me.polygons: p.use_smooth=True
me.materials.append(mat); uv=me.uv_layers.new(name='ortho')
for p in me.polygons:
    for li in p.loop_indices: uv.data[li].uv=J['UV'][me.loops[li].vertex_index]
o.data=me; bpy.data.meshes.remove(old); print(TAG,'patch',len(me.vertices),len(me.polygons),flush=True)
ng=bpy.data.node_groups[MN]; N=ng.nodes; L=ng.links
ev=next(n for n in N if n.type=='FIELD_ON_DOMAIN')
if ev.data_type=='BOOLEAN':
    src=ev.inputs[0].links[0].from_socket; dst=[l.to_socket for l in ev.outputs[0].links]
    # the box compares feed the AND chain -> retarget the 4 compare thresholds
    for n in N:
        if n.type=='COMPARE':
            v=n.inputs[1].default_value
            n.inputs[1].default_value={-199.0:-201.0,-175.0:-169.0,45.0:44.2,69.0:71.0}.get(round(v,1),v)
    N.remove(ev)
    sw=N.new('FunctionNodeSwitch' if hasattr(bpy.types,'FunctionNodeSwitch') else 'GeometryNodeSwitch'); sw.input_type='FLOAT'
    sw.inputs['False'].default_value=0.0; sw.inputs['True'].default_value=1.0; L.new(src,sw.inputs['Switch'])
    fd=N.new('GeometryNodeFieldOnDomain'); fd.domain='FACE'; fd.data_type='FLOAT'; L.new(sw.outputs[0],fd.inputs[0])
    c=N.new('FunctionNodeCompare'); c.data_type='FLOAT'; c.operation='GREATER_THAN'; L.new(fd.outputs[0],c.inputs[0]); c.inputs[1].default_value=0.999
    for d in dst: L.new(c.outputs[0],d)
    print(TAG,'del selection -> all-corners; thresholds',sorted(round(n.inputs[1].default_value,2) for n in N if n.type=='COMPARE'),flush=True)
