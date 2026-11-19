# ws237 self-review fix: ws236 (f236a/b) lowered the synthetic PK/WS60/WS68 edges by up to ~5 m into the M3b LiDAR, but
# QD_skirt_under_pzpk only pushes the skirt down when it sits -0.06..+0.5 m relative to PK, so the coarse context skirt
# (dark 3DEP ortho strip tone) now pokes up to ~2 m through the lowered PK fill (dark blob on the Feliciano west slope,
# dark specks at PK's south tip). New last skirt modifier: in the W53q corridor box (x -480..-130, y -150..540), faces within
# 4 m of PK/PZ/WS60/WS68 are selected (no extra subdivision: QD already subdivides near PK at level 3; level 2 here doubled the skirt to 7.5 M verts and tripped the render watchdog), and every vertex whose vertical ray hits one of those grounds and that
# sits above hit-0.35 m goes to hit-0.35 m; selected vertices in gaps (no ground straight above) go no higher than
# the nearest ground point - 0.35 m (ws237 test: two specks at PK's north tip were skirt verts in such a gap). Lower-only; the skirt is never raised; no ground or paving moves.
import bpy
SK=bpy.data.objects['Context_skirt_3DEP_ortho_4km']
T=['PK_Feliciano_west_DTM_fill_UNVERIFIED','PZ_Feliciano_SW_DTM_edge_feather_UNVERIFIED','WS60_terrain_edge_apron_LiDAR_to_skirt',
   'M3b_north_LiDAR_DTM_1m_west_rail_corridor_UNVERIFIED_seam']+[o.name for o in bpy.data.objects if o.name.startswith('WS68_RHD_ground_northDTM')]
T=[n for n in T if n in bpy.data.objects]
ng=bpy.data.node_groups.new('WS237_skirt_under_W53q_lowered_edges','GeometryNodeTree')
ng.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry')
ng.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
N=ng.nodes; L=ng.links.new
gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
def tgt(TT):
    j=N.new('GeometryNodeJoinGeometry')
    for n in TT:
        oi=N.new('GeometryNodeObjectInfo'); oi.inputs['Object'].default_value=bpy.data.objects[n]; oi.transform_space='RELATIVE'
        L(oi.outputs['Geometry'],j.inputs['Geometry'])
    return j
pos=N.new('GeometryNodeInputPosition'); sep=N.new('ShaderNodeSeparateXYZ'); L(pos.outputs[0],sep.inputs[0])
def cmp(sock,op,b):
    c=N.new('FunctionNodeCompare'); c.data_type='FLOAT'; c.operation=op; L(sock,c.inputs['A']); c.inputs['B'].default_value=b; return c.outputs['Result']
def band(*s):
    out=s[0]
    for x in s[1:]:
        b=N.new('FunctionNodeBooleanMath'); b.operation='AND'; L(out,b.inputs[0]); L(x,b.inputs[1]); out=b.outputs[0]
    return out
TP=[n for n in T if not n.startswith('M3b_')]
j1=tgt(TP); px=N.new('GeometryNodeProximity'); px.target_element='FACES'; L(j1.outputs[0],px.inputs['Target'])
selF=band(cmp(sep.outputs['X'],'GREATER_THAN',-480.0),cmp(sep.outputs['X'],'LESS_THAN',-130.0),
          cmp(sep.outputs['Y'],'GREATER_THAN',-150.0),cmp(sep.outputs['Y'],'LESS_THAN',540.0),cmp(px.outputs['Distance'],'LESS_THAN',float(__import__('os').environ.get('F237_D','4.0'))))
# PK north tip (x -330..-295, y 255..310): the skirt is coarse under a dip in M3b here, so faces within 4 m of any ground
# (M3b included) are selected and subdivided (level 2, tiny box only)
def tipb():
    return band(cmp(sep.outputs['X'],'GREATER_THAN',-330.0),cmp(sep.outputs['X'],'LESS_THAN',-295.0),cmp(sep.outputs['Y'],'GREATER_THAN',255.0),cmp(sep.outputs['Y'],'LESS_THAN',310.0))
ja=tgt(T); pa=N.new('GeometryNodeProximity'); pa.target_element='FACES'; L(ja.outputs[0],pa.inputs['Target'])
tsel=band(tipb(),cmp(pa.outputs['Distance'],'LESS_THAN',4.0))
bo=N.new('FunctionNodeBooleanMath'); bo.operation='OR'; L(selF,bo.inputs[0]); L(tsel,bo.inputs[1]); selF=bo.outputs[0]
sg=N.new('GeometryNodeSeparateGeometry'); sg.domain='FACE'; L(gi.outputs[0],sg.inputs['Geometry']); L(selF,sg.inputs['Selection'])
st=N.new('GeometryNodeSeparateGeometry'); st.domain='FACE'; L(sg.outputs['Selection'],st.inputs['Geometry']); L(tipb(),st.inputs['Selection'])
sdt=N.new('GeometryNodeSubdivideMesh'); sdt.inputs['Level'].default_value=int(__import__('os').environ.get('F237_LV','2')); L(st.outputs['Selection'],sdt.inputs['Mesh'])
sd=N.new('GeometryNodeJoinGeometry'); L(sdt.outputs[0],sd.inputs[0]); L(st.outputs['Inverted'],sd.inputs[0])
j2=tgt(T); rc=N.new('GeometryNodeRaycast'); L(j2.outputs[0],rc.inputs['Target Geometry'])
pos2=N.new('GeometryNodeInputPosition'); va=N.new('ShaderNodeVectorMath'); va.operation='ADD'; va.inputs[1].default_value=(0,0,400.0)
L(pos2.outputs[0],va.inputs[0]); L(va.outputs[0],rc.inputs['Source Position']); rc.inputs['Ray Direction'].default_value=(0,0,-1); rc.inputs['Ray Length'].default_value=2000.0
hs=N.new('ShaderNodeSeparateXYZ'); L(rc.outputs['Hit Position'],hs.inputs[0]); ps=N.new('ShaderNodeSeparateXYZ'); L(pos2.outputs[0],ps.inputs[0])
lim=N.new('ShaderNodeMath'); lim.operation='SUBTRACT'; L(hs.outputs['Z'],lim.inputs[0]); lim.inputs[1].default_value=0.35
mn=N.new('ShaderNodeMath'); mn.operation='MINIMUM'; L(ps.outputs['Z'],mn.inputs[0]); L(lim.outputs[0],mn.inputs[1])
j3=tgt(T); p2=N.new('GeometryNodeProximity'); p2.target_element='FACES'; L(j3.outputs[0],p2.inputs['Target']); L(pos2.outputs[0],p2.inputs['Source Position'])
qs=N.new('ShaderNodeSeparateXYZ'); L(p2.outputs['Position'],qs.inputs[0])
lq=N.new('ShaderNodeMath'); lq.operation='SUBTRACT'; L(qs.outputs['Z'],lq.inputs[0]); lq.inputs[1].default_value=0.35
mq=N.new('ShaderNodeMath'); mq.operation='MINIMUM'; L(ps.outputs['Z'],mq.inputs[0]); L(lq.outputs[0],mq.inputs[1])
sw=N.new('GeometryNodeSwitch'); sw.input_type='FLOAT'; L(rc.outputs['Is Hit'],sw.inputs['Switch']); L(mq.outputs[0],sw.inputs['False']); L(mn.outputs[0],sw.inputs['True'])
cz=N.new('ShaderNodeCombineXYZ'); L(ps.outputs['X'],cz.inputs['X']); L(ps.outputs['Y'],cz.inputs['Y']); L(sw.outputs[0],cz.inputs['Z'])
sp=N.new('GeometryNodeSetPosition'); L(sd.outputs[0],sp.inputs['Geometry']); L(cz.outputs[0],sp.inputs['Position'])
jo=N.new('GeometryNodeJoinGeometry'); L(sp.outputs[0],jo.inputs[0]); L(sg.outputs['Inverted'],jo.inputs[0]); L(jo.outputs[0],go.inputs[0])
m=SK.modifiers.new('WS237_skirt_under_W53q_lowered_edges','NODES'); m.node_group=ng
print('F237A skirt modifier added; targets',len(T),'stack tail',[x.name for x in SK.modifiers][-3:],flush=True)
