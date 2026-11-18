import bpy, os, numpy as np
from mathutils import Vector
M='/workspace/nj-scenes/montclair-state/'+os.environ.get('SRC','montclair_state.blend')
want=lambda n: n.startswith(('Context_skirt','Terrain_LiDAR_DTM_1m','WS110_','WS113_terrain','WS163_','WS162_','WS164_')) or n=='WS163_CAM_eye_NormalAve_W_from_E_walk'
with bpy.data.libraries.load(M) as (s,d): d.objects=[n for n in s.objects if want(n)]
sc=bpy.context.scene
for o in d.objects:
    if o: sc.collection.objects.link(o)
print('LOADED',len(d.objects),flush=True)
dg=bpy.context.evaluated_depsgraph_get()
from collections import Counter
C=Counter(); hits=[]
for x in np.linspace(-282,-293.5,24):
    for y in np.linspace(-258.5,-254.75,16):
        r=sc.ray_cast(dg,Vector((x,y,300)),Vector((0,0,-1)))
        if r[0]: C[r[4].name]+=1; hits.append((x,y,r[4].name,r[1].z,r[2].z))
print('TOP',C.most_common())
for h in hits:
    if h[2].startswith(('Context','Terrain','WS110_ground','WS113')): print('H',round(h[0],2),round(h[1],2),h[2][:40],round(h[3],3),'nz',round(h[4],2))
# also: for each shard hit, z of each candidate surface below
if os.environ.get('SAVE'): bpy.ops.wm.save_as_mainfile(filepath=os.environ['SAVE'])
