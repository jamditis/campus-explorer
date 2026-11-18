import bpy, numpy as np, os, json
rep={}
for n in ['WJ_south_gully_LiDAR_patch_ext_UNVERIFIED','WF_east_dorm_LiDAR_terrain_patch_UNVERIFIED']:
    me=bpy.data.objects[n].data; N=len(me.vertices)
    a=np.zeros(N); e=np.zeros(N)
    me.attributes['wk_litter'].data.foreach_get('value',a); me.attributes['wh_edge'].data.foreach_get('value',e)
    np.save(f'/workspace/nj-scenes/montclair-state/data/wk/{n[:2]}_litter_pre_fade.npy',a)
    w=np.clip(1-e*1.6,0,1); w=w*w*(3-2*w)
    b=a*w; me.attributes['wk_litter'].data.foreach_set('value',b.tolist())
    rep[n]=dict(before=int((a>.5).sum()),after=int((b>.5).sum()))
print('FADE',rep)
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('SAVED')
