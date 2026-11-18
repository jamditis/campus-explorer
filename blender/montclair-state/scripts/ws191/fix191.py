# ws191 UNIFY #91 remaining far-field skirt slivers (Context_skirt_3DEP_ortho_4km), evidence scripts/ws191/probe191.out:
#  A) x = -348.0 is the W edge of WS163_ground_patch_W_of_WS110 / WS163_skirt_target_hidden (y -262.4..-236). West of it there is
#     NO patch and the raw 3DEP skirt sits 0.11-0.85 m ABOVE the patch edge (e.g. y -244.4: skirt 115.29 vs patch 114.44; Normal
#     Ave W carriageway ends there at 114.53) -> a dark ortho-textured step/bank along the scene's W edge. Fix: feather the skirt
#     DOWN to the patch-edge height over 8 m W of the edge (Geometry Proximity to the target, smoothstep weight; lowering only).
#  B) x -306..-300, y -251..-248.4: WS163 ground patch row at y -248.6 is 0.3-0.4 m below the hidden target, so the skirt (pushed
#     only to target-0.02) stays above the visible patch (+0.1..+0.29). Fix: clamp skirt z <= visible top - 0.05.
#  C) x -354..-347.6, y -236.4..-233: WS181 Lot 36 asphalt runs W of the target (tgt empty) and its S band is 0.02-0.13 m below
#     the raw skirt. Fix: clamp skirt z <= asphalt - 0.05.
# Last modifier on the skirt; lowering only, inside covered boxes (B, C) or uncovered far field (A) -> cannot open holes.
import bpy
SKO191=bpy.data.objects['Context_skirt_3DEP_ortho_4km']
NAME191='WS191_skirt_clamp_feather_UNIFY91'
g=bpy.data.node_groups.get(NAME191) or bpy.data.node_groups.new(NAME191,'GeometryNodeTree')
g.nodes.clear()
if not g.interface.items_tree:
    g.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry')
    g.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
N=g.nodes; L=g.links
gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
pos=N.new('GeometryNodeInputPosition'); sep=N.new('ShaderNodeSeparateXYZ'); L.new(pos.outputs[0],sep.inputs[0])
X,Y,Z=sep.outputs[0],sep.outputs[1],sep.outputs[2]
def cmp(s,op,v):
    c=N.new('FunctionNodeCompare'); c.data_type='FLOAT'; c.operation=op; L.new(s,c.inputs[0]); c.inputs[1].default_value=v; return c.outputs[0]
def AND(a,b):
    n=N.new('FunctionNodeBooleanMath'); n.operation='AND'; L.new(a,n.inputs[0]); L.new(b,n.inputs[1]); return n.outputs[0]
def box(x0,x1,y0,y1): return AND(AND(cmp(X,'GREATER_THAN',x0),cmp(X,'LESS_THAN',x1)),AND(cmp(Y,'GREATER_THAN',y0),cmp(Y,'LESS_THAN',y1)))
def math(op,a,b):
    m=N.new('ShaderNodeMath'); m.operation=op
    for i,v in enumerate((a,b)):
        if isinstance(v,(int,float)): m.inputs[i].default_value=v
        else: L.new(v,m.inputs[i])
    return m.outputs[0]
def objinfo(name):
    oi=N.new('GeometryNodeObjectInfo'); oi.inputs['Object'].default_value=bpy.data.objects[name]; oi.transform_space='RELATIVE'; return oi.outputs['Geometry']
def switchf(sel,a,b):  # sel ? b : a  (float)
    s=N.new('GeometryNodeSwitch'); s.input_type='FLOAT'; L.new(sel,s.inputs[0])
    for i,v in ((1,a),(2,b)):
        if isinstance(v,(int,float)): s.inputs[i].default_value=v
        else: L.new(v,s.inputs[i])
    return s.outputs[0]
z=Z
# --- B and C: clamp under visible tops via downward raycast
up=N.new('ShaderNodeVectorMath'); up.operation='ADD'; L.new(pos.outputs[0],up.inputs[0]); up.inputs[1].default_value=(0,0,50)
CL=[('WS181_Lot36_asphalt_LiDAR2023int_ortho2020_nostalls_UNVERIFIEDe',(-354.6,-347.5,-236.8,-232.8)),
    ('WS163_ground_patch_W_of_WS110_LiDAR2023_1m_UNVERIFIED',(-306.4,-299.6,-251.4,-248.0)),
    ('WS165_aisle_mouth_mulch_bed_graded_to_walk_UNIFY69',(-306.4,-299.6,-251.4,-248.0)),
    ('WS165_aisle_mouth_bed_curb_ramped_at_walk_UNIFY69',(-306.4,-299.6,-251.4,-248.0))]
for nm_pref,bx in CL:
    nm=[o.name for o in bpy.data.objects if o.name.startswith(nm_pref)]
    if not nm: print('FIX191 MISSING',nm_pref,flush=True); continue
    rc=N.new('GeometryNodeRaycast'); L.new(objinfo(nm[0]),rc.inputs['Target Geometry']); L.new(up.outputs[0],rc.inputs['Source Position'])
    rc.inputs['Ray Direction'].default_value=(0,0,-1); rc.inputs['Ray Length'].default_value=200.0
    hz=N.new('ShaderNodeSeparateXYZ'); L.new(rc.outputs['Hit Position'],hz.inputs[0])
    cap=math('SUBTRACT',hz.outputs[2],0.05)
    sel=AND(box(*bx),rc.outputs['Is Hit'])
    z=switchf(sel,z,math('MINIMUM',z,cap))
    print('FIX191 clamp',nm[0],bx,flush=True)
# --- A: feather W of the x=-348.0 patch edge
px=N.new('GeometryNodeProximity'); px.target_element='FACES'
L.new(objinfo('WS163_skirt_target_hidden'),px.inputs[0])
pz=N.new('ShaderNodeSeparateXYZ'); L.new(px.outputs[0],pz.inputs[0])
w=math('SUBTRACT',1.0,math('DIVIDE',px.outputs[1],8.0)); w=math('MAXIMUM',w,0.0)
w=math('MULTIPLY',math('MULTIPLY',w,w),math('SUBTRACT',3.0,math('MULTIPLY',w,2.0)))  # smoothstep
nz=math('SUBTRACT',pz.outputs[2],0.04)
fz=math('ADD',z,math('MULTIPLY',math('SUBTRACT',nz,z),w))
selA=box(-356.5,-348.02,-262.6,-235.8)
z=switchf(selA,z,math('MINIMUM',z,fz))
cb=N.new('ShaderNodeCombineXYZ'); L.new(X,cb.inputs[0]); L.new(Y,cb.inputs[1]); L.new(z,cb.inputs[2])
sp=N.new('GeometryNodeSetPosition'); L.new(gi.outputs[0],sp.inputs['Geometry']); L.new(cb.outputs[0],sp.inputs['Position'])
L.new(sp.outputs[0],go.inputs[0])
m191=SKO191.modifiers.get(NAME191) or SKO191.modifiers.new(NAME191,'NODES'); m191.node_group=g
SKO191.modifiers.move(list(SKO191.modifiers).index(m191),len(SKO191.modifiers)-1)
print('FIX191 modifier',NAME191,'index',list(SKO191.modifiers).index(m191),'of',len(SKO191.modifiers),'skirt matrix identity',SKO191.matrix_world.is_identity if hasattr(SKO191.matrix_world,'is_identity') else SKO191.matrix_world,flush=True)
