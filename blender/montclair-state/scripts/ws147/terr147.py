import bpy, collections
P='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(P, link=False) as (src,dst):
    dst.objects=['Terrain_LiDAR_DTM_1m','Context_skirt_3DEP_ortho_4km']
for o in dst.objects:
    me=o.data; mw=o.matrix_world
    cnt=collections.Counter(); ex={}
    for p in me.polygons:
        c=mw@p.center
        if -95<c.x<-55 and -180<c.y<-140:
            mn=o.material_slots[p.material_index].material.name if p.material_index<len(o.material_slots) and o.material_slots[p.material_index].material else None
            cnt[mn]+=1; ex.setdefault(mn,[]).append((round(c.x,1),round(c.y,1),round(c.z,2)))
    print("OBJ",o.name,dict(cnt))
    for k,v in ex.items(): print("  ",k,v[:8])
