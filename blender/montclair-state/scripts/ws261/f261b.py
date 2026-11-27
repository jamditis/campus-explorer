# ws261b (CHAIN via ws208/merge208.py on ws261a): UNIFY #32 — the thin dark crease line on the lawn E of the WS115 walk is a
# 3-11 cm step where the WS113 fan fill's NE edge stops below Terrain_LiDAR_DTM_1m (evaluated probe261d/e: y -218..-208,
# x -226..-218; and a 5-15 cm lip the other way at y -206..-202, x -218..-217 where the fill stands above the terrain).
# Fix: feather the WS113 BASE verts toward the evaluated terrain along that edge: z += dz(nearest boundary, averaged over
# boundary cells within 0.5 m) * (1 - smoothstep(0, 1.5 m, d)). Only boundary cells with |dz| > 1.5 cm are used; WS115 walk is
# >= 1.7 m from them (WS113_paving_edge_grade GN still runs after this on the base mesh). Both surfaces are 1 m DTM grades.
import bpy, json, numpy as np
TAG='F261B'; MS='/workspace/nj-scenes/montclair-state/'
P=np.array([p for p in json.load(open(MS+'scripts/ws261/'+__import__('os').environ.get('BND','bnd261e.json'))) if abs(p[2])>float(__import__('os').environ.get('THR','0.015'))])
print(TAG,'boundary cells',len(P),'dz min/max %.3f %.3f'%(P[:,2].min(),P[:,2].max()),flush=True)
o=[x for x in bpy.data.objects if x.name.startswith('WS113_terrain_fan_fill_DTM1m')][0]
W=o.matrix_world; Wi=W.inverted(); me=o.data; n=0; mx=0
for v in me.vertices:
    g=W@v.co
    d=np.hypot(P[:,0]-g.x,P[:,1]-g.y); i=d.argmin(); dm=d[i]
    if dm>=1.5: continue
    near=P[np.hypot(P[:,0]-P[i,0],P[:,1]-P[i,1])<0.5]; dz=float(np.median(near[:,2]))
    t=dm/1.5; w=1-(t*t*(3-2*t))
    g.z+=dz*w; v.co=Wi@g; n+=1; mx=max(mx,abs(dz*w))
me.update()
print(TAG,o.name,'verts moved',n,'max |dz| %.3f'%mx,flush=True)
