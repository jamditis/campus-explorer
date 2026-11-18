# ws48: sparse street-tree band (Joe Nov 9 9:54) as ONE low-LOD GN instancer on the 3DEP skirt.
# Points: data/ws47/band_trees.json (OSM ODbL), filtered to 260-760 m from main origin, off the 1 m DTM, >=14 m from far canopy crowns.
import bpy, bmesh, json, math, os, random
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
SAVE=os.environ.get('SAVE')=='1'
D=bpy.data
if D.objects.get('WS48_band_street_trees_OSM_lowLOD'): print('B48 already built'); raise SystemExit
dg=bpy.context.evaluated_depsgraph_get()
def bvh(o):
    e=o.evaluated_get(dg); m=e.to_mesh(); bm=bmesh.new(); bm.from_mesh(m); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); e.to_mesh_clear(); return t
SK=bvh(D.objects['Context_skirt_3DEP_ortho_4km']); TR=bvh(D.objects['Terrain_LiDAR_DTM_1m'])
crowns=[]
for inst in dg.object_instances:
    if inst.is_instance and inst.parent and inst.parent.original.name.startswith('MID_canopy'):
        p=inst.matrix_world.translation
        if abs(p.x)<900 and abs(p.y)<900: crowns.append(p.copy())
for o in D.objects:
    if o.name.startswith('MID_stree_'): crowns.append(o.matrix_world.translation.copy())
kd=KDTree(max(1,len(crowns)))
for i,p in enumerate(crowns): kd.insert(Vector((p.x,p.y,0)),i)
kd.balance()
T=json.load(open('/workspace/nj-scenes/montclair-state/data/ws47/band_trees.json'))['trees']
P=[]
for t in T:
    r=math.hypot(t['x'],t['y'])
    if not (260<=r<=760): continue
    h=TR.ray_cast(Vector((t['x'],t['y'],400)),Vector((0,0,-1)))[0]
    if h and h.z>50: continue
    if crowns:
        co,i,dd=kd.find(Vector((t['x'],t['y'],0)))
        if dd<12: continue
    h=SK.ray_cast(Vector((t['x'],t['y'],400)),Vector((0,0,-1)))[0]
    if not h or h.z<30: continue
    sc=3.8*t['scale']; P.append((t['x'],t['y'],h.z+0.8*sc,sc,t['rot']))
print('B48 points',len(P),'crowns nearby',len(crowns))
me=D.meshes.new('WS48_band_street_trees_pts'); me.from_pydata([p[:3] for p in P],[],[])
a=me.attributes.new('tree_scale','FLOAT','POINT'); a.data.foreach_set('value',[p[3] for p in P])
b=me.attributes.new('tree_rot','FLOAT','POINT'); b.data.foreach_set('value',[p[4] for p in P])
ob=D.objects.new('WS48_band_street_trees_OSM_lowLOD',me)
col=D.collections.get('WS48_band_trees') or D.collections.new('WS48_band_trees')
if col.name not in bpy.context.scene.collection.children: bpy.context.scene.collection.children.link(col)
col.objects.link(ob)
proto=D.objects['MID_street_tree_proto_20261015ag']
ng=D.node_groups.new('WS48_band_tree_instancer','GeometryNodeTree')
ng.interface.new_socket('Geometry',in_out='INPUT',socket_type='NodeSocketGeometry'); ng.interface.new_socket('Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
N=ng.nodes; L=ng.links
gi=N.new('NodeGroupInput'); go=N.new('NodeGroupOutput'); oi=N.new('GeometryNodeObjectInfo'); oi.inputs['Object'].default_value=proto; oi.transform_space='ORIGINAL'
iop=N.new('GeometryNodeInstanceOnPoints'); sa=N.new('GeometryNodeInputNamedAttribute'); sa.data_type='FLOAT'; sa.inputs['Name'].default_value='tree_scale'
ra=N.new('GeometryNodeInputNamedAttribute'); ra.data_type='FLOAT'; ra.inputs['Name'].default_value='tree_rot'
cx=N.new('ShaderNodeCombineXYZ'); rl=N.new('GeometryNodeRealizeInstances') if False else None
L.new(gi.outputs[0],iop.inputs['Points']); L.new(oi.outputs['Geometry'],iop.inputs['Instance'])
sx=N.new('ShaderNodeCombineXYZ'); mz=N.new('ShaderNodeMath'); mz.operation='MULTIPLY'; mz.inputs[1].default_value=1.15
L.new(sa.outputs['Attribute'],sx.inputs['X']); L.new(sa.outputs['Attribute'],sx.inputs['Y']); L.new(sa.outputs['Attribute'],mz.inputs[0]); L.new(mz.outputs[0],sx.inputs['Z']); L.new(sx.outputs[0],iop.inputs['Scale']); L.new(ra.outputs['Attribute'],cx.inputs['Z']); L.new(cx.outputs[0],iop.inputs['Rotation'])
L.new(iop.outputs[0],go.inputs[0])
m=ob.modifiers.new('GN','NODES'); m.node_group=ng
ob['source']='OSM via OSM API /map (ODbL) 2026-11-11; placements procedural along real streets, UNVERIFIED vs ortho; Joe Nov 9 9:54 band request'
dg=bpy.context.evaluated_depsgraph_get(); n=sum(1 for i in dg.object_instances if i.is_instance and i.parent and i.parent.original==ob)
print('B48 instances',n,'proto dims',tuple(round(v,1) for v in proto.dimensions))
if SAVE: bpy.ops.wm.save_mainfile(); print('B48 saved')
