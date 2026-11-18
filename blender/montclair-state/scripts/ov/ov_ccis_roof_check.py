import bpy, numpy as np
r=bpy.data.objects['Center for Computing and Information Science roof (LiDAR)']; me=r.data
tot=sum(p.area for p in me.polygons if p.material_index==0)
print('CCIS mats',[m.name for m in me.materials],'tpo',r.get('tpo'),'area0',round(tot,1),'faces',len(me.polygons))
for t in (0.93,0.985): print('NZ<',t,round(sum(p.area for p in me.polygons if p.material_index==0 and p.normal.z<t)/tot,3))
c=np.array([tuple(d.color) for d in me.attributes['roofc'].data]); print('roofc alpha>=0.5',round((c[:,3]>=0.5).mean(),3))
z=np.array([v.co.z for v in me.vertices]); print('z pcts',np.percentile(z,[5,25,50,75,95]).round(2))
