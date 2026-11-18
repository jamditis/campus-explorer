import bpy, numpy as np
bowl=bpy.data.objects['Kasser_amphitheater_bowl_hl']
bb=np.array([bowl.matrix_world@v.co for v in bowl.data.vertices if v.co.z>0])
x0,y0=bb[:,0].min(),bb[:,1].min()
H={}
for p in bb:
    k=(int((p[0]-x0)/0.25),int((p[1]-y0)/0.25)); H[k]=max(H.get(k,-1e9),p[2])
def hb(x,y): return H.get((int((x-x0)/0.25),int((y-y0)/0.25)))
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; M=t.matrix_world
co=np.empty(len(t.data.vertices)*3); t.data.vertices.foreach_get('co',co); co=co.reshape(-1,3); A=np.array(M); w=co@A[:3,:3].T+A[:3,3]
bad=[]
for f in t.data.polygons:
    c=w[list(f.vertices)].mean(0)
    if c[0]<-202 or c[0]>-151 or c[1]<-10 or c[1]>35: continue
    vv=w[list(f.vertices)]
    for s in [c]+[(vv[i]+vv[(i+1)%len(vv)])/2 for i in range(len(vv))]:
        h=hb(s[0],s[1])
        if h is not None and s[2]>h-0.02: bad.append((f.index,tuple(np.round(s,2)),round(s[2]-h,3))); break
print('BADFACES',len(bad))
for b in bad[:40]: print('BAD',b)
