import bpy
from mathutils import Vector
sk=bpy.data.objects['Context_skirt_3DEP_ortho_4km']; me=sk.data; mw=sk.matrix_world
print('SKIRT',len(me.vertices),len(me.polygons),[m.name for m in me.materials],[a.name for a in me.attributes][:12],'mods',[m.type for m in sk.modifiers])
vs=[mw@v.co for v in me.vertices]; near=[v for v in vs if -285<v.x<-240 and 50<v.y<130]
print('near',len(near)); 
xs=sorted(set(round(v.x,1) for v in near)); print('xs',xs[:20])
for on in ('PZ_Feliciano_SW_DTM_edge_feather_UNVERIFIED','PK_Feliciano_west_DTM_fill_UNVERIFIED'):
    o=bpy.data.objects[on]; W=[o.matrix_world@v.co for v in o.data.vertices]
    print(on,len(W),'x %.1f..%.1f y %.1f..%.1f'%(min(w.x for w in W),max(w.x for w in W),min(w.y for w in W),max(w.y for w in W)))
