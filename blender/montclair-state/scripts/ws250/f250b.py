# ws250 pass 2 (CHAIN on ws250a): the W63 ground is big PB fan / regrid faces (50-375 m2, spanning Dickson Hall's footprint), so
# the f250a vertex snap only fixed their corners (tilted planes stayed up to 1.8 m off). Inside WS250_W63_LiDAR_terrain_snap,
# after the corner snap: faces with centre in the box (x -194..-142, y 141..213) and area > 1.5 m2 are separated, subdivided
# (simple, level 4 -> ~1 m spacing), and their NEW interior vertices are snapped to the same LiDAR target; vertices on the
# separated piece's boundary keep the straight (already snapped) edges, so they meet the untouched neighbours with no crack
# (T-junctions lie exactly on the neighbour edges). Joined back + merge by distance. No faces deleted (Footpaths_OSM drape stays valid).
import bpy
TAG='F250B'; MN='WS250_W63_LiDAR_terrain_snap'
ng=bpy.data.node_groups[MN]; N=ng.nodes; L=ng.links
if 'WS250_subdiv' not in N:
    go=next(x for x in N if x.type=='GROUP_OUTPUT'); st=next(x for x in N if x.type=='SET_POSITION')
    oi=next(x for x in N if x.type=='OBJECT_INFO')
    def cmp(sock,op,val):
        c=N.new('FunctionNodeCompare'); c.data_type='FLOAT'; c.operation=op; L.new(sock,c.inputs[0]); c.inputs[1].default_value=val; return c.outputs[0]
    def AND(a,b):
        n_=N.new('FunctionNodeBooleanMath'); n_.operation='AND'; L.new(a,n_.inputs[0]); L.new(b,n_.inputs[1]); return n_.outputs[0]
    pos=N.new('GeometryNodeInputPosition'); sp=N.new('ShaderNodeSeparateXYZ'); L.new(pos.outputs[0],sp.inputs[0])
    inb=AND(AND(cmp(sp.outputs['X'],'GREATER_THAN',-194.0),cmp(sp.outputs['X'],'LESS_THAN',-142.0)),AND(cmp(sp.outputs['Y'],'GREATER_THAN',141.0),cmp(sp.outputs['Y'],'LESS_THAN',213.0)))
    ar=N.new('GeometryNodeInputMeshFaceArea')
    sel=AND(inb,cmp(ar.outputs[0],'GREATER_THAN',1.5))   # evaluated on the FACE domain by Separate Geometry: position = face centre
    sg=N.new('GeometryNodeSeparateGeometry'); sg.domain='FACE'; L.new(st.outputs[0],sg.inputs['Geometry']); L.new(sel,sg.inputs['Selection'])
    sd=N.new('GeometryNodeSubdivideMesh'); sd.name='WS250_subdiv'; sd.inputs['Level'].default_value=4; L.new(sg.outputs['Selection'],sd.inputs['Mesh'])
    # boundary vertices of the separated piece
    en=N.new('GeometryNodeInputMeshEdgeNeighbors'); b1=cmp(en.outputs['Face Count'],'EQUAL',1.0)
    sw=N.new('GeometryNodeSwitch'); sw.input_type='FLOAT'; sw.inputs['False'].default_value=0.0; sw.inputs['True'].default_value=1.0; L.new(b1,sw.inputs['Switch'])
    fd=N.new('GeometryNodeFieldOnDomain'); fd.domain='EDGE'; fd.data_type='FLOAT'; L.new(sw.outputs[0],fd.inputs[0])
    bnd=cmp(fd.outputs[0],'GREATER_THAN',0.001)
    nb=N.new('FunctionNodeBooleanMath'); nb.operation='NOT'; L.new(bnd,nb.inputs[0])
    # second snap on the subdivided piece (same target / attribute)
    pos2=N.new('GeometryNodeInputPosition')
    up=N.new('ShaderNodeVectorMath'); up.operation='ADD'; L.new(pos2.outputs[0],up.inputs[0]); up.inputs[1].default_value=(0,0,300)
    rc=N.new('GeometryNodeRaycast'); rc.data_type='FLOAT'
    na=N.new('GeometryNodeInputNamedAttribute'); na.data_type='FLOAT'; na.inputs['Name'].default_value='w250'
    L.new(oi.outputs['Geometry'],rc.inputs['Target Geometry']); L.new(na.outputs['Attribute'],rc.inputs['Attribute'])
    L.new(up.outputs[0],rc.inputs['Source Position']); rc.inputs['Ray Direction'].default_value=(0,0,-1); rc.inputs['Ray Length'].default_value=600
    s2=N.new('ShaderNodeSeparateXYZ'); L.new(pos2.outputs[0],s2.inputs[0]); sh=N.new('ShaderNodeSeparateXYZ'); L.new(rc.outputs['Hit Position'],sh.inputs[0])
    wm=N.new('ShaderNodeMath'); wm.operation='MULTIPLY'; L.new(rc.outputs['Attribute'],wm.inputs[0]); L.new(rc.outputs['Is Hit'],wm.inputs[1])
    wm2=N.new('ShaderNodeMath'); wm2.operation='MULTIPLY'; L.new(wm.outputs[0],wm2.inputs[0]); L.new(nb.outputs[0],wm2.inputs[1])
    cl=N.new('ShaderNodeClamp'); L.new(wm2.outputs[0],cl.inputs[0])
    mx=N.new('ShaderNodeMix'); mx.data_type='FLOAT'; L.new(cl.outputs[0],mx.inputs['Factor']); L.new(s2.outputs['Z'],mx.inputs[2]); L.new(sh.outputs['Z'],mx.inputs[3])
    cb=N.new('ShaderNodeCombineXYZ'); L.new(s2.outputs['X'],cb.inputs[0]); L.new(s2.outputs['Y'],cb.inputs[1]); L.new(mx.outputs[0],cb.inputs[2])
    st2=N.new('GeometryNodeSetPosition'); L.new(sd.outputs['Mesh'],st2.inputs['Geometry']); L.new(cb.outputs[0],st2.inputs['Position'])
    jn=N.new('GeometryNodeJoinGeometry'); L.new(st2.outputs[0],jn.inputs[0]); L.new(sg.outputs['Inverted'],jn.inputs[0])
    mg=N.new('GeometryNodeMergeByDistance'); mg.inputs['Distance'].default_value=0.001; L.new(jn.outputs[0],mg.inputs['Geometry'])
    L.new(mg.outputs[0],go.inputs[0])
    print(TAG,'subdivide+resnap added to',MN,flush=True)
