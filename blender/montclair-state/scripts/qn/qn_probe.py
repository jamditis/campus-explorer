import bpy,numpy as np
u=bpy.data.objects['QM_terrain_band_underlay_UNVERIFIED']; me=u.data
print('mats',[m.name if m else None for m in me.materials])
mi=np.zeros(len(me.polygons),int); me.polygons.foreach_get('material_index',mi)
print('mi hist',np.bincount(mi))
uv=np.zeros(len(me.loops)*2); me.uv_layers.active.data.foreach_get('uv',uv); uv=uv.reshape(-1,2)
lv=np.zeros(len(me.loops),int); me.loops.foreach_get('vertex_index',lv)
co=np.zeros(len(me.vertices)*3); me.vertices.foreach_get('co',co); co=co.reshape(-1,3)
mw=np.array(u.matrix_world); xy=(co@mw[:3,:3].T+mw[:3,3])[lv][:,:2]
A=np.c_[xy,np.ones(len(xy))]
for it in range(3):
    if it==0: m=np.ones(len(xy),bool)
    s,_,_,_=np.linalg.lstsq(A[m],uv[m],rcond=None); r=np.linalg.norm(A@s-uv,axis=1)
    m=r<np.percentile(r,80)
print('fit',s.T.tolist()); print('resid pct',np.percentile(r,[50,90,95,99,99.9]).tolist(),'n>1e-3',int((r>1e-3).sum()),'of',len(r))
bad=r>2e-3; print('bad xy bbox',xy[bad].min(0) if bad.any() else None, xy[bad].max(0) if bad.any() else None)
np.save('/workspace/nj-scenes/montclair-state/data/qn/uvfit.npy',s)
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; tm=T.data
print('terrain mats',[m.name if m else None for m in tm.materials], 'uv layers',[l.name for l in tm.uv_layers], 'underlay uv',[l.name for l in me.uv_layers])
tuv=np.zeros(len(tm.loops)*2); tm.uv_layers.active.data.foreach_get('uv',tuv); tuv=tuv.reshape(-1,2)
tlv=np.zeros(len(tm.loops),int); tm.loops.foreach_get('vertex_index',tlv)
tco=np.zeros(len(tm.vertices)*3); tm.vertices.foreach_get('co',tco); tco=tco.reshape(-1,3); tw=np.array(T.matrix_world)
txy=(tco@tw[:3,:3].T+tw[:3,3])[tlv][:,:2]; tr=np.linalg.norm(np.c_[txy,np.ones(len(txy))]@s-tuv,axis=1)
print('terrain base resid vs fit pct',np.percentile(tr,[50,90,99]).tolist())
for mod in T.modifiers: print('mod',mod.name,mod.type)
print('ul mods',[m.name for m in u.modifiers],'hide',u.hide_render)
