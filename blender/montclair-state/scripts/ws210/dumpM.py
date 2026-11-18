import bpy, numpy as np, collections
with bpy.data.libraries.load('/workspace/nj-scenes/montclair-state/montclair_state.blend') as (a,b): b.objects=['Terrain_LiDAR_DTM_1m']
o=b.objects[0]; me=o.data; mw=o.matrix_world
print('DM mats',[m.name if m else None for m in me.materials],flush=True)
c=collections.Counter(); cz={}
for p in me.polygons:
    q=mw@p.center
    if -216<q.x<-203 and -114<q.y<-95:
        c[p.material_index]+=1; cz.setdefault(p.material_index,[]).append((round(q.x,1),round(q.y,1),round(q.z-120,2),round(p.normal.z,2)))
print('DM',dict(c),flush=True)
for k,v in cz.items(): print('DM',k,v[:12],flush=True)
print('DM attrs',[(a.name,a.domain,a.data_type) for a in me.attributes],flush=True)
