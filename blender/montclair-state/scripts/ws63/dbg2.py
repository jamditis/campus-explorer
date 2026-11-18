import bpy,numpy as np
exec(open('scripts/ws63/apply63.py').read().split('# verify')[0])
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; D=np.load('data/dtm_1m.npy')
dg=bpy.context.evaluated_depsgraph_get(); dg.update(); m=T.evaluated_get(dg).data
d=[]
for v in m.vertices:
    c=v.co
    if 100<c.x<135 and -75<c.y<-65: d.append(c.z-D[int(c.y+250),int(c.x+250)])
d=np.array(d); print('DBG2 n',len(d),np.percentile(d,[5,50,95]).round(2) if len(d) else '')
h=bpy.data.objects['WS63_E_band_DTM_target']; print('DBG2 helper', len(h.evaluated_get(dg).data.vertices), h.users_collection[0].name)
for mo in T.modifiers: print('DBG2 mod',mo.name,mo.show_viewport,mo.show_render)
