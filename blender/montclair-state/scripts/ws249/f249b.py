# ws249 pass 2 (CHAIN on ws249a): SE berm corner of the east stand. The terrain there is big PB fan faces (few verts), so the
# WS249 SE snap (f249a) only fixes their corners. Same remedy as ws248: (1) LiDAR ground patch x -186..-174, y 44..70
# (h249.json; meets the ws248 patch at x = -186), (2) the WS249 SE snap group deletes fan faces > 1.5 m2 wholly inside
# x -199..-175, y 45..69 (both patches cover that box), so the patches show where the fan stood up to 0.9 m too high.
import bpy, json
TAG='F249B'; PN='WS249_SE_berm_LiDAR2023_ground_patch_1m'; MN='WS249_SE_berm_LiDAR_terrain_snap'
J=json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws249/h249.json'))
P8=bpy.data.objects['WS248_E_stand_LiDAR2023_ground_patch_1m']
if PN not in bpy.data.objects:
    me=bpy.data.meshes.new(PN); me.from_pydata(J['V'],[],[tuple(f) for f in J['F']]); me.validate(); me.update()
    for p in me.polygons: p.use_smooth=True
    me.materials.append(P8.data.materials[0])
    uv=me.uv_layers.new(name='ortho')
    for p in me.polygons:
        for li in p.loop_indices: uv.data[li].uv=J['UV'][me.loops[li].vertex_index]
    o=bpy.data.objects.new(PN,me)
    for c in P8.users_collection: c.objects.link(o)
    print(TAG,'patch',PN,len(me.vertices),len(me.polygons),me.materials[0].name,[c.name for c in o.users_collection],flush=True)
ng=bpy.data.node_groups[MN]; N=ng.nodes; L=ng.links
if 'WS249_del_fan' not in N:
    go=next(x for x in N if x.type=='GROUP_OUTPUT'); st=next(x for x in N if x.type=='SET_POSITION')
    pos=N.new('GeometryNodeInputPosition'); sp=N.new('ShaderNodeSeparateXYZ'); L.new(pos.outputs[0],sp.inputs[0])
    def cmp(sock,op,val):
        c=N.new('FunctionNodeCompare'); c.data_type='FLOAT'; c.operation=op; L.new(sock,c.inputs[0]); c.inputs[1].default_value=val; return c.outputs[0]
    def AND(a,b):
        n_=N.new('FunctionNodeBooleanMath'); n_.operation='AND'; L.new(a,n_.inputs[0]); L.new(b,n_.inputs[1]); return n_.outputs[0]
    inb=AND(AND(cmp(sp.outputs['X'],'GREATER_THAN',-199.0),cmp(sp.outputs['X'],'LESS_THAN',-175.0)),AND(cmp(sp.outputs['Y'],'GREATER_THAN',45.0),cmp(sp.outputs['Y'],'LESS_THAN',69.0)))
    ar=N.new('GeometryNodeInputMeshFaceArea'); big=cmp(ar.outputs[0],'GREATER_THAN',1.5)
    ev=N.new('GeometryNodeFieldOnDomain'); ev.domain='FACE'; ev.data_type='BOOLEAN'; L.new(inb,ev.inputs[0])
    dl=N.new('GeometryNodeDeleteGeometry'); dl.name='WS249_del_fan'; dl.domain='FACE'; dl.mode='ONLY_FACE'
    L.new(st.outputs[0],dl.inputs['Geometry']); L.new(AND(ev.outputs[0],big),dl.inputs['Selection']); L.new(dl.outputs[0],go.inputs[0])
    print(TAG,'delete node added',flush=True)
