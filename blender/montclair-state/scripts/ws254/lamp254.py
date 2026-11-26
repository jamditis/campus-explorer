# ws254 read-only: acorn lamps near W63 — base (bbox min z) vs evaluated ground under the post
import bpy, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
F='/workspace/nj-scenes/montclair-state/'+os.environ.get('F','montclair_state.blend')
N=['Terrain_LiDAR_DTM_1m','WS250_W63_lawn_LiDAR2023_ground_patch_1m','WS251_W63b_passage_LiDAR2023_ground_patch_1m','Footpaths_OSM','WS253_W63d_Feliciano_E_walk_slabs','WS252_W63c_plaza_E_edge_raised_walk_retaining_UNVERIFIED']
with bpy.data.libraries.load(F) as (a,b): b.objects=[n for n in a.objects if n in N or n.startswith(('Lamp_acorn','WS252_W63c_Lamp','WS253_W63d_Lamp'))]
for o in b.objects: bpy.context.scene.collection.objects.link(o)
dg=bpy.context.evaluated_depsgraph_get()
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; em=T.evaluated_get(dg).to_mesh(); M=T.matrix_world; vs=[M@v.co for v in em.vertices]
bt=BVHTree.FromPolygons(vs,[p.vertices[:] for p in em.polygons if any(-260<vs[i].x<-100 and 120<vs[i].y<230 for i in p.vertices)])
cov={n:BVHTree.FromObject(bpy.data.objects[n],dg) for n in N[3:] if n in bpy.data.objects}
for o in bpy.data.objects:
    if not o.name.startswith(('Lamp_acorn','WS252_W63c_Lamp','WS253_W63d_Lamp')): continue
    p=o.matrix_world.translation
    if not (-260<p.x<-100 and 120<p.y<230): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; zb=min(v.z for v in bb)
    g=bt.ray_cast(Vector((p.x,p.y,400)),Vector((0,0,-1)),600)[0]
    c=[(n,h[0].z) for n,b in cov.items() for h in [b.ray_cast(Vector((p.x,p.y,400)),Vector((0,0,-1)),600)] if h[0]]
    print('L254',o.name,'xy %.2f %.2f'%(p.x,p.y),'loc z %.2f base z %.2f'%(p.z,zb),'ground %.2f'%(g.z if g else -1),'covers',[(n[:22],round(z,2)) for n,z in c],flush=True)
os._exit(0)
