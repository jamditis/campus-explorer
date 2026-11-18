# ws81d: revert the WS81 band (it dug a 2-3 m pocket against the still-high terrain south of y -138, grandstand area pending Joe)
# and instead close the see-through gap at the Terrain's west edge (x ~ -249, y -137..-118) with a lawn curtain down to the WS68 ground.
import bpy,bmesh,os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
os.environ['REVERT81']='1'
try: exec(open('/workspace/nj-scenes/montclair-state/scripts/ws81/terrain81.py').read())
except SystemExit: pass
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; print('WS81D mods tail',[m.name for m in T.modifiers][-3:],flush=True)
dg=bpy.context.evaluated_depsgraph_get(); dg.update()
G=[o for o in bpy.data.objects if o.name.startswith('WS68_RHD_ground')][0]
oe=G.evaluated_get(dg); m=oe.to_mesh(); b=bmesh.new(); b.from_mesh(m); b.transform(G.matrix_world); GB=BVHTree.FromBMesh(b); b.free(); oe.to_mesh_clear()
oe=T.evaluated_get(dg); m=oe.to_mesh(); bt=bmesh.new(); bt.from_mesh(m); bt.transform(T.matrix_world); oe.to_mesh_clear()
segs=[]
for e in bt.edges:
    if not e.is_boundary: continue
    a,c=e.verts[0].co.copy(),e.verts[1].co.copy()
    if all(-253<p.x<-244 and -138<p.y<-116 for p in (a,c)): segs.append((a,c))
bt.free(); print('WS81D boundary segs',len(segs),flush=True)
def gz(p):
    h=GB.ray_cast(Vector((p.x-0.6,p.y,400)),Vector((0,0,-1)))[0]
    return (h.z-0.15) if h else p.z-3.0
bm=bmesh.new()
for a,c in segs:
    za,zc=gz(a),gz(c)
    if a.z-za<0.05 and c.z-zc<0.05: continue
    v=[bm.verts.new((a.x,a.y,a.z-0.01)),bm.verts.new((c.x,c.y,c.z-0.01)),bm.verts.new((c.x-0.6,c.y,zc)),bm.verts.new((a.x-0.6,a.y,za))]
    bm.faces.new(v)
bmesh.ops.remove_doubles(bm,verts=bm.verts,dist=0.002)
uv=bm.loops.layers.uv.new('UVMap')
for f in bm.faces:
    for l in f.loops: l[uv].uv=(l.vert.co.y/4,l.vert.co.z/4)
me=bpy.data.meshes.new('WS81_terrain_W_edge_curtain'); bm.to_mesh(me); bm.free()
me.materials.append(bpy.data.materials['Lawn_Varied_Oct_local_fade'])
ob=bpy.data.objects.new('WS81_terrain_W_edge_curtain_lawn_UNVERIFIED_grade',me); T.users_collection[0].objects.link(ob)
print('WS81D curtain faces',len(me.polygons),flush=True)
bpy.ops.wm.save_mainfile(); print('WS81D SAVED',flush=True)
