import bpy
from mathutils import Vector
w=bpy.data.objects['Schmitt Hall walls']; me=w.data; M=w.matrix_world
fc=[]
for f in me.polygons:
    vs=[M@me.vertices[i].co for i in f.vertices]; fc.append((f.index,vs))
out=[]
for o in bpy.data.objects:
    if not o.name.startswith('SCH_win_') or o.hide_render or o.hide_get(): continue
    mw=o.matrix_world; X=Vector((mw[0][0],mw[1][0])).normalized(); Y=Vector((mw[0][1],mw[1][1])).normalized()
    c=Vector((mw.translation.x,mw.translation.y)); z0=mw.translation.z
    hw=1.3*o.scale.x; hh=2.6*o.scale.z
    cnt={1:[],-1:[]}
    for i,vs in fc:
        ok=True; side=0
        for v in vs:
            q=Vector((v.x,v.y))-c; a=q.dot(X); n=q.dot(Y)
            if abs(a)>hw+0.02 or not(z0-0.02<=v.z<=z0+hh+0.02) or abs(n)>0.66: ok=False;break
            if n>0.05: side|=1
            if n<-0.05: side|=2
        if ok and side in (1,2): cnt[1 if side==1 else -1].append(i)
    out.append((o.name,len(cnt[1]),len(cnt[-1]),cnt[1],cnt[-1]))
both=[x for x in out if x[1] and x[2]]
print('NWIN',len(out),'BOTH',len(both))
import collections
print('PATTERN',collections.Counter((x[1]>0,x[2]>0) for x in out))
for x in both[:30]: print('B',x)
