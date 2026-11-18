# ws113: UNIFY #14 - evaluated terrain/lawn GN poke-through at the WS111/WS112 walks.
# Adds a LAST modifier (WS113_paving_edge_grade) to Terrain_LiDAR_DTM_1m and WS110_ground_patch:
# inside paving footprints the lawn is held 8 cm under the paving top; within ~1.6 m outside it is
# graded to meet the paving edge (3 cm down at the edge, max +12 cm/m rise, max -50 cm/m drop), fading out.
import bpy, bmesh, os, sys
SAVE=os.environ.get('SAVE','main')
O=lambda p: next(o for o in bpy.data.objects if o.name.startswith(p))
PAV=['WS112_CollegeAve_S_E_walk_N_brick','WS112_W_branch_walk','WS111_CollegeAve_S_E_walk_gap','WS111_CollegeAve_S_W_walk_gap','WS111_CollegeAve_E_corner_apron','WS111_CollegeAve_W_corner_apron']
for n in ('WS113_paving_tops_proxy',):
    if n in bpy.data.objects: bpy.data.objects.remove(bpy.data.objects[n],do_unlink=True)
bm=bmesh.new()
for p in PAV:
    o=O(p); t=bmesh.new(); t.from_mesh(o.data); t.transform(o.matrix_world)
    bmesh.ops.delete(t,geom=[f for f in t.faces if abs(f.normal.z)<0.5],context='FACES')
    me=bpy.data.meshes.new('tmp'); t.to_mesh(me); t.free(); bm.from_mesh(me); bpy.data.meshes.remove(me)
print('E113 proxy faces',len(bm.faces))
me=bpy.data.meshes.new('WS113_paving_tops_proxy'); bm.to_mesh(me); bm.free()
px=bpy.data.objects.new('WS113_paving_tops_proxy',me)
col=bpy.data.collections.get('WS112_CollegeAve_S_branch_walks') or bpy.context.scene.collection
col.objects.link(px); px.hide_render=True; px.hide_viewport=True; px.display_type='WIRE'
ng=bpy.data.node_groups.get('WS113_paving_edge_grade') 
if ng: bpy.data.node_groups.remove(ng)
ng=bpy.data.node_groups.new('WS113_paving_edge_grade','GeometryNodeTree')
ng.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry')
ng.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
N=ng.nodes; L=ng.links.new
gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
oi=N.new('GeometryNodeObjectInfo'); oi.inputs['Object'].default_value=px; oi.transform_space='RELATIVE'
pos=N.new('GeometryNodeInputPosition')
sep_p=N.new('ShaderNodeSeparateXYZ'); L(pos.outputs[0],sep_p.inputs[0])
# proxy: store z, flatten
st=N.new('GeometryNodeStoreNamedAttribute'); st.data_type='FLOAT'; st.domain='POINT'; st.inputs['Name'].default_value='pz'
L(oi.outputs['Geometry'],st.inputs['Geometry']); L(sep_p.outputs['Z'],st.inputs['Value'])
flat=N.new('GeometryNodeSetPosition'); L(st.outputs[0],flat.inputs['Geometry'])
cz=N.new('ShaderNodeCombineXYZ'); L(sep_p.outputs['X'],cz.inputs['X']); L(sep_p.outputs['Y'],cz.inputs['Y'])
L(cz.outputs[0],flat.inputs['Position'])
# terrain sample pos (x,y,0)
cz2=N.new('ShaderNodeCombineXYZ'); L(sep_p.outputs['X'],cz2.inputs['X']); L(sep_p.outputs['Y'],cz2.inputs['Y'])
prox=N.new('GeometryNodeProximity'); prox.target_element='FACES'
L(flat.outputs[0],prox.inputs[0]); L(cz2.outputs[0],prox.inputs['Source Position'] if 'Source Position' in prox.inputs else prox.inputs[1])
na=N.new('GeometryNodeInputNamedAttribute'); na.data_type='FLOAT'; na.inputs['Name'].default_value='pz'
sns=N.new('GeometryNodeSampleNearestSurface'); sns.data_type='FLOAT'
L(flat.outputs[0],sns.inputs['Mesh']); L(na.outputs[0],sns.inputs['Value']); L(cz2.outputs[0],sns.inputs['Sample Position'])
d=prox.outputs['Distance']; pz=sns.outputs['Value']; z=sep_p.outputs['Z']
def math(op,a,b=None,c=None):
    m=N.new('ShaderNodeMath'); m.operation=op
    for i,v in enumerate((a,b,c)):
        if v is None: continue
        if isinstance(v,(int,float)): m.inputs[i].default_value=v
        else: L(v,m.inputs[i])
    return m.outputs[0]
inside=math('LESS_THAN',d,0.02)
hi=math('ADD',math('MULTIPLY_ADD',d,0.12,pz),-0.03)       # pz-0.03+0.12d
lo=math('SUBTRACT',math('ADD',pz,-0.03),math('MULTIPLY',d,0.5))
zin=math('MINIMUM',z,math('ADD',pz,-0.08))
zcl=math('MINIMUM',math('MAXIMUM',z,lo),hi)
mr=N.new('ShaderNodeMapRange'); mr.interpolation_type='SMOOTHSTEP'; L(d,mr.inputs['Value'])
mr.inputs['From Min'].default_value=0.8; mr.inputs['From Max'].default_value=1.6; mr.inputs['To Min'].default_value=1.0; mr.inputs['To Max'].default_value=0.0
w=mr.outputs[0]
zout_band=math('ADD',z,math('MULTIPLY',math('SUBTRACT',zcl,z),w))
sw=N.new('GeometryNodeSwitch'); sw.input_type='FLOAT'; L(inside,sw.inputs['Switch']); L(zout_band,sw.inputs['False']); L(zin,sw.inputs['True'])
cz3=N.new('ShaderNodeCombineXYZ'); L(sep_p.outputs['X'],cz3.inputs['X']); L(sep_p.outputs['Y'],cz3.inputs['Y']); L(sw.outputs[0],cz3.inputs['Z'])
sp=N.new('GeometryNodeSetPosition'); L(gi.outputs[0],sp.inputs['Geometry']); L(cz3.outputs[0],sp.inputs['Position'])
L(sp.outputs[0],go.inputs[0])
for tn in ('Terrain_LiDAR_DTM_1m','WS110_ground_patch'):
    t=O(tn)
    for m in list(t.modifiers):
        if m.name.startswith('WS113_'): t.modifiers.remove(m)
    m=t.modifiers.new('WS113_paving_edge_grade','NODES'); m.node_group=ng
    print('E113 mod added',t.name,len(t.modifiers))
if SAVE=='main': bpy.ops.wm.save_mainfile(); print('E113 SAVED main')
else: bpy.ops.wm.save_as_mainfile(filepath=SAVE,copy=True); print('E113 SAVED',SAVE)
