import bpy, os, numpy as np
F='/workspace/nj-scenes/montclair-state/'+os.environ.get('F','montclair_state_ws250f.blend')
with bpy.data.libraries.load(F) as (a,b): b.objects=['Terrain_LiDAR_DTM_1m']
T=b.objects[0]; bpy.context.scene.collection.objects.link(T)
dg=bpy.context.evaluated_depsgraph_get(); me=T.evaluated_get(dg).to_mesh(); M=T.matrix_world
box=(-169,-155,184,192); out=[]
sa=me.attributes.get('pb_seam')
for p in me.polygons:
    c=M@p.center
    if box[0]<c.x<box[1] and box[2]<c.y<box[3] and p.normal.z<0.9:
        vv=[tuple(round(x,3) for x in (M@me.vertices[i].co)) for i in p.vertices]
        out.append((round(p.normal.z,2),round(p.area,4),vv,[round(sa.data[i].value,2) for i in p.vertices] if sa else None))
print('SB250 n',len(out),flush=True)
for o in out[:14]: print('SB250',o,flush=True)
os._exit(0)
