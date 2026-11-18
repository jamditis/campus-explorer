# oz (UNVERIFIED, removable; REVERT=1 undoes): CCIS roof tile band rebuilt as a clean, constant-width ring.
# The ow/oy tile-vs-membrane decision is per LiDAR vertex (~1.1 m grid) -> stair-step band edge + grey holes inside the band.
# Removable GN modifier OZ_ccis_roof_clean_band (after OY_ccis_roof_fleck_blur) on the evaluated mesh only:
#  subdivide x LEV (flat, positions unchanged), distance of every vertex to the outer boundary of the roof-material faces
#  (mat 0 'Roof_tile_or_membrane'), em_ringforce = 1 and roofc alpha = 1 inside W m (tile), alpha = 0 beyond (membrane).
# Mesh, shared material untouched. Band width W is a style guess (campus convention: tile ring round a flat membrane centre).
import bpy, os, sys
REV=os.environ.get('REVERT')=='1'; SAVE='--save' in sys.argv
CC='Center for Computing and Information Science roof (LiDAR)'; MOD='OZ_ccis_roof_clean_band'; NG='OZ_ccis_roof_clean_band_GN'; PR='UNVERIFIED_oz_clean_band'
r=bpy.data.objects[CC]
if MOD in r.modifiers: r.modifiers.remove(r.modifiers[MOD])
if NG in bpy.data.node_groups: bpy.data.node_groups.remove(bpy.data.node_groups[NG])
if PR in r.keys(): del r[PR]
if REV:
    print('REVERTED_OZ_CCIS')
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit(0)
W=float(os.environ.get('W','3.0')); LEV=int(os.environ.get('LEV','2'))
ng=bpy.data.node_groups.new(NG,'GeometryNodeTree')
ng.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry'); ng.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
s=ng.interface.new_socket('Band width',in_out='INPUT',socket_type='NodeSocketFloat'); s.default_value=W
N=ng.nodes; L=ng.links.new; gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput')
# boundary of the roof-material faces
mi=N.new('GeometryNodeInputMaterialIndex'); c0=N.new('FunctionNodeCompare'); c0.data_type='INT'; c0.operation='EQUAL'; L(mi.outputs[0],c0.inputs[2]); c0.inputs[3].default_value=0
sep=N.new('GeometryNodeSeparateGeometry'); sep.domain='FACE'; L(gi.outputs[0],sep.inputs['Geometry']); L(c0.outputs['Result'],sep.inputs['Selection'])
en=N.new('GeometryNodeInputMeshEdgeNeighbors'); c1=N.new('FunctionNodeCompare'); c1.data_type='INT'; c1.operation='EQUAL'; L(en.outputs['Face Count'],c1.inputs[2]); c1.inputs[3].default_value=1
m2c=N.new('GeometryNodeMeshToCurve'); L(sep.outputs['Selection'],m2c.inputs['Mesh']); L(c1.outputs['Result'],m2c.inputs['Selection'])
# smooth the LiDAR stair-step outline before measuring the band (resample 0.4 m, blur positions SMI x)
rs=N.new('GeometryNodeResampleCurve'); rs.inputs['Count'].default_value=2
try: rs.mode='LENGTH'
except Exception: pass
L(m2c.outputs['Curve'],rs.inputs['Curve'])
for k in rs.inputs:
    if k.name=='Length': k.default_value=0.4
SMI=int(os.environ.get('SMI','10'))
bp=N.new('GeometryNodeBlurAttribute'); bp.data_type='FLOAT_VECTOR'; pp=N.new('GeometryNodeInputPosition'); L(pp.outputs[0],bp.inputs['Value']); bp.inputs['Iterations'].default_value=SMI
sp=N.new('GeometryNodeSetPosition'); L(rs.outputs['Curve'],sp.inputs['Geometry']); L(bp.outputs['Value'],sp.inputs['Position'])
c2m=N.new('GeometryNodeCurveToMesh'); L(sp.outputs['Geometry'] if SMI>0 else rs.outputs['Curve'],c2m.inputs['Curve'])
# subdivide whole roof (flat subdivision; positions unchanged)
sub=N.new('GeometryNodeSubdivideMesh'); L(gi.outputs[0],sub.inputs['Mesh']); sub.inputs['Level'].default_value=LEV
px=N.new('GeometryNodeProximity'); px.target_element='EDGES'; L(c2m.outputs['Mesh'],px.inputs[0])
pos=N.new('GeometryNodeInputPosition'); L(pos.outputs[0],px.inputs['Sample Position'])
lt=N.new('FunctionNodeCompare'); lt.data_type='FLOAT'; lt.operation='LESS_THAN'; L(px.outputs['Distance'],lt.inputs[0]); L(gi.outputs['Band width'],lt.inputs[1])
f2=N.new('FunctionNodeBooleanMath'); f2.operation='AND'; L(lt.outputs['Result'],f2.inputs[0]); L(px.outputs['Is Valid'],f2.inputs[1])
st1=N.new('GeometryNodeStoreNamedAttribute'); st1.data_type='FLOAT'; st1.domain='POINT'; st1.inputs['Name'].default_value='em_ringforce'
L(sub.outputs['Mesh'],st1.inputs['Geometry']); L(f2.outputs['Boolean'],st1.inputs['Value'])
na=N.new('GeometryNodeInputNamedAttribute'); na.data_type='FLOAT_COLOR'; na.inputs['Name'].default_value='roofc'
sc=N.new('FunctionNodeSeparateColor'); L(na.outputs['Attribute'],sc.inputs['Color'])
cc=N.new('FunctionNodeCombineColor')
for ch in ('Red','Green','Blue'): L(sc.outputs[ch],cc.inputs[ch])
L(f2.outputs['Boolean'],cc.inputs['Alpha'])
st2=N.new('GeometryNodeStoreNamedAttribute'); st2.data_type='FLOAT_COLOR'; st2.domain='POINT'; st2.inputs['Name'].default_value='roofc'
L(st1.outputs['Geometry'],st2.inputs['Geometry']); L(cc.outputs['Color'],st2.inputs['Value']); L(st2.outputs['Geometry'],go.inputs[0])
md=r.modifiers.new(MOD,'NODES'); md.node_group=ng
r[PR]='tile band = %.1f m constant-width ring from the roof outline (subdiv x%d, outline smoothed x%d); style guess, no CCIS roof photo'%(W,LEV,SMI)
dg=bpy.context.evaluated_depsgraph_get(); e=r.evaluated_get(dg); m=e.to_mesh()
rf=m.attributes.get('em_ringforce'); v=[0.0]*len(rf.data); rf.data.foreach_get('value',v)
print('OZ_CCIS verts',len(m.vertices),'faces',len(m.polygons),'band verts',sum(1 for x in v if x>0.5),'mods',[x.name for x in r.modifiers])
e.to_mesh_clear()
if os.environ.get('TESTCAM')=='1':
    import math
    from mathutils import Vector
    cd=bpy.data.cameras.new('OZT_CAM_ccis_top'); cd.type='ORTHO'; cd.ortho_scale=70
    co=bpy.data.objects.new('OZT_CAM_ccis_top',cd); bpy.context.scene.collection.objects.link(co); co.location=(23,215,260); co.rotation_euler=(0,0,math.radians(0))
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
