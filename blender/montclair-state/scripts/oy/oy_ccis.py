# oy (B) UNVERIFIED, removable; REVERT=1 undoes: small red tile flecks left on the CCIS flat membrane centre after ow.
# Extra GN modifier OY_ccis_roof_fleck_blur (after OW_ccis_roof_tile_ring): blur the roofc tile flag (alpha) over the mesh
# (ITER iterations); where the blurred flag < TH an isolated 'tile' vert becomes membrane (alpha 0). One-way: never adds tile.
import bpy, os, sys
REV=os.environ.get('REVERT')=='1'; SAVE='--save' in sys.argv
CC='Center for Computing and Information Science roof (LiDAR)'; MOD='OY_ccis_roof_fleck_blur'; NG='OY_ccis_roof_fleck_blur_GN'
r=bpy.data.objects[CC]
if MOD in r.modifiers: r.modifiers.remove(r.modifiers[MOD])
if NG in bpy.data.node_groups: bpy.data.node_groups.remove(bpy.data.node_groups[NG])
if 'UNVERIFIED_oy_fleck_blur' in r.keys(): del r['UNVERIFIED_oy_fleck_blur']
if REV:
    print('REVERTED_OY_CCIS')
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit(0)
IT=int(os.environ.get('ITER','4')); TH=float(os.environ.get('TH','0.5'))
ng=bpy.data.node_groups.new(NG,'GeometryNodeTree')
ng.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry'); ng.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
N=ng.nodes; L=ng.links.new; gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
na=N.new('GeometryNodeInputNamedAttribute'); na.data_type='FLOAT_COLOR'; na.inputs['Name'].default_value='roofc'
sep=N.new('FunctionNodeSeparateColor'); L(na.outputs['Attribute'],sep.inputs['Color'])
bl=N.new('GeometryNodeBlurAttribute'); bl.data_type='FLOAT'; L(sep.outputs['Alpha'],bl.inputs['Value']); bl.inputs['Iterations'].default_value=IT
cmp=N.new('FunctionNodeCompare'); cmp.data_type='FLOAT'; cmp.operation='LESS_THAN'; L(bl.outputs['Value'],cmp.inputs[0]); cmp.inputs[1].default_value=TH
cz=N.new('FunctionNodeCombineColor')
for ch in ('Red','Green','Blue'): L(sep.outputs[ch],cz.inputs[ch])
cz.inputs['Alpha'].default_value=0.0
sw=N.new('GeometryNodeSwitch'); sw.input_type='RGBA'; L(cmp.outputs['Result'],sw.inputs['Switch']); L(na.outputs['Attribute'],sw.inputs['False']); L(cz.outputs['Color'],sw.inputs['True'])
st=N.new('GeometryNodeStoreNamedAttribute'); st.data_type='FLOAT_COLOR'; st.domain='POINT'; st.inputs['Name'].default_value='roofc'
L(gi.outputs[0],st.inputs['Geometry']); L(sw.outputs['Output'],st.inputs['Value']); L(st.outputs['Geometry'],go.inputs[0])
md=r.modifiers.new(MOD,'NODES'); md.node_group=ng
r['UNVERIFIED_oy_fleck_blur']='roofc tile flag blurred x%d, < %.2f -> membrane (one-way)'%(IT,TH)
dg=bpy.context.evaluated_depsgraph_get(); e=r.evaluated_get(dg); m=e.to_mesh()
a=m.attributes.get('roofc'); vals=[0.0]*(len(a.data)*4); a.data.foreach_get('color',vals)
al=vals[3::4]; print('OY_CCIS verts',len(al),'tile',sum(1 for x in al if x>0.5),'mods',[x.name for x in r.modifiers])
e.to_mesh_clear()
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
