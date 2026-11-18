import bpy, numpy as np
for nm in ['Feliciano School of Business roof (LiDAR)','Dickson Hall roof (LiDAR)','Calcia Hall roof (LiDAR)']:
    me=bpy.data.objects[nm].data
    c=np.array([tuple(d.color) for d in me.attributes['roofc'].data])
    st=np.zeros(len(me.vertices),bool); fl=np.zeros(len(me.vertices),bool)
    for p in me.polygons:
        (st if p.normal.z<0.93 else fl)[list(p.vertices)]=True
    for lab,mk in (('steep',st&~fl),('flat',fl&~st),('both',st&fl)):
        if mk.sum(): x=c[mk]; print(nm[:20],lab,mk.sum(),'rgb',x[:,:3].mean(0).round(3),'red-ness',(x[:,0]-x[:,2]).mean().round(3),'bright>0.3 frac',((x[:,:3]@[0.3,0.59,0.11])>0.3).mean().round(2),'alpha',x[:,3].mean().round(2))
for nm in ['Feliciano School of Business roof (LiDAR)','Dickson Hall roof (LiDAR)','Calcia Hall roof (LiDAR)']:
    o=bpy.data.objects[nm]; me=o.data; tot=sum(p.area for p in me.polygons)
    print('SUM',nm[:24],'tpo',o.get('tpo'),'mods',[m.name for m in o.modifiers],'faces',len(me.polygons),'area',round(tot),'steep<0.93',round(sum(p.area for p in me.polygons if p.normal.z<0.93)/tot,3))
