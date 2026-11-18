# ow3 (UNVERIFIED, removable; REVERT=1 undoes): modest concrete curb lip / worn edge where the CELS walk meets the road (ow2 fold-fix box x121-141,y201-218).
# Built from the EVALUATED Footpaths_OSM boundary edges in the box: per edge a 14 cm wide top band (inset toward the walk) + a vertical face down to DTM-6 cm.
# Separate object in collection OW3_walk_edge_curb_20261101ow3_UNVERIFIED; Footpaths/road meshes untouched.
import bpy, os, sys, bmesh
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'; SAVE='--save' in sys.argv
CN='OW3_walk_edge_curb_20261101ow3_UNVERIFIED'; MN='OW3_curb_worn_concrete_UNVERIFIED'
c=bpy.data.collections.get(CN)
if c:
    for o in list(c.objects):
        d=o.data; bpy.data.objects.remove(o)
        if d and d.users==0: bpy.data.meshes.remove(d)
    bpy.data.collections.remove(c)
for d in [d for d in bpy.data.cameras if d.name.startswith('OW3_') and d.users==0]: bpy.data.cameras.remove(d)
m=bpy.data.materials.get(MN)
if m and m.users==0: bpy.data.materials.remove(m)
if REV:
    print('REVERTED_OW3')
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit
F=bpy.data.objects['Footpaths_OSM']; T=bpy.data.objects['Terrain_LiDAR_DTM_1m']
dg=bpy.context.evaluated_depsgraph_get(); fe=F.evaluated_get(dg); me=fe.to_mesh()
bm=bmesh.new(); bm.from_mesh(me); bm.transform(F.matrix_world)
X0,X1,Y0,Y1=121,141,201,218
Te=T.evaluated_get(dg); Ti=T.matrix_world.inverted()
def dtm(p):
    o=Ti@Vector((p.x,p.y,p.z+50)); d=(Ti.to_3x3()@Vector((0,0,-1))).normalized()
    ok,loc,n,i=Te.ray_cast(o,d)
    return (T.matrix_world@loc).z if ok else p.z-0.05
out=bmesh.new(); W=0.10; ne=0
for e in bm.edges:
    if len(e.link_faces)!=1: continue
    a,b=e.verts[0].co.copy(),e.verts[1].co.copy(); mid=(a+b)/2
    if not(X0<=mid.x<=X1 and Y0<=mid.y<=Y1): continue
    if (a-b).length<1e-3: continue
    fc=e.link_faces[0].calc_center_median(); t=(b-a); t.z=0; t.normalize(); n=Vector((-t.y,t.x,0))
    if n.dot(fc-mid)<0: n=-n   # n points into the walk
    lift=Vector((0,0,0.012))
    a2=a+lift; b2=b+lift; ai=a2+n*W; bi=b2+n*W
    za=min(dtm(a),a.z)-0.06; zb=min(dtm(b),b.z)-0.06
    vs=[out.verts.new(v) for v in (a2,b2,bi,ai)]; out.faces.new(vs)
    vd=[out.verts.new(v) for v in (Vector((a.x,a.y,za)),Vector((b.x,b.y,zb)),b2,a2)]; out.faces.new(vd)
    ne+=1
bmesh.ops.remove_doubles(out,verts=out.verts,dist=0.003)
mesh=bpy.data.meshes.new('OW3_CELS_walk_road_curb_lip'); out.to_mesh(mesh); bm.free(); out.free(); fe.to_mesh_clear()
for p in mesh.polygons: p.use_smooth=False
mat=bpy.data.materials.new(MN); mat.use_nodes=True; nt=mat.node_tree; bsdf=nt.nodes['Principled BSDF']
noi=nt.nodes.new('ShaderNodeTexNoise'); noi.inputs['Scale'].default_value=9; noi.inputs['Detail'].default_value=8
ramp=nt.nodes.new('ShaderNodeValToRGB'); ramp.color_ramp.elements[0].color=(0.16,0.155,0.145,1); ramp.color_ramp.elements[1].color=(0.30,0.29,0.27,1)
nt.links.new(noi.outputs['Fac'],ramp.inputs['Fac']); nt.links.new(ramp.outputs['Color'],bsdf.inputs['Base Color']); bsdf.inputs['Roughness'].default_value=0.9
bump=nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=0.25; nt.links.new(noi.outputs['Fac'],bump.inputs['Height']); nt.links.new(bump.outputs['Normal'],bsdf.inputs['Normal'])
mesh.materials.append(mat)
col=bpy.data.collections.new(CN); bpy.context.scene.collection.children.link(col)
ob=bpy.data.objects.new('OW3_CELS_walk_road_curb_lip_UNVERIFIED',mesh); col.objects.link(ob); ob['UNVERIFIED_ow3']='curb lip/worn edge, no photo of this walk end'
print('OW3 edges',ne,'verts',len(mesh.vertices),'faces',len(mesh.polygons))
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
