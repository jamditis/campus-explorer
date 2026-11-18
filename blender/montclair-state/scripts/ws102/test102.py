import bpy
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
names=['WS27_CollegeAve_carriageway_2020ortho','UA_CollegeAve_spur_1557427669_UNVERIFIED','Terrain_LiDAR_DTM_1m','WS27_CollegeAve_curb_right_UNVERIFIED']
with bpy.data.libraries.load(p) as (s,d):
    d.objects=names; d.materials=[m for m in s.materials if m in ('WS27_curb_concrete_UNVERIFIED',)]
for o in d.objects: bpy.context.scene.collection.objects.link(o)
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws102/apply102.py').read())
o=ob
import numpy as np
co=np.array([o.matrix_world@v.co for v in o.data.vertices]); print('T102 road verts',len(co),'z %.2f..%.2f'%(co[:,2].min(),co[:,2].max()),'faces',len(o.data.polygons))
#bpy.ops.wm.save_as_mainfile(filepath='/workspace/nj-scenes/montclair-state/scripts/ws102/test102.blend')
sp=bpy.data.objects['UA_CollegeAve_spur_1557427669_UNVERIFIED']
cc=np.array([sp.matrix_world@p.center for p in sp.data.polygons]); m=cc[:,1]>-250
print('T102 spur remaining faces',len(cc),'with y>-250:',int(m.sum()), cc[m][:8].round(1).tolist() if m.any() else '')
print('T102 spur ymax %.1f'%cc[:,1].max())
pe,n=frame(S1); print('T102 road end centre',pe.round(2), 'edges',(pe+n*eE(S1)).round(2),(pe+n*EW).round(2))
s_=cc[np.argsort(-cc[:,1])][:6]; print('T102 spur north-most',s_.round(2).tolist())
