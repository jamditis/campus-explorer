import bpy
from mathutils import Vector, kdtree
r=bpy.data.objects['Feliciano School of Business roof (LiDAR)']; w=bpy.data.objects['Feliciano School of Business walls']
rm=r.matrix_world; m=r.data
cnt={}
for e in m.edges: pass
import collections
ec=collections.Counter()
for p in m.polygons:
    for k in p.edge_keys: ec[k]+=1
bv=set()
for k,c in ec.items():
    if c==1: bv.update(k)
kd=kdtree.KDTree(len(bv)); bl=list(bv)
for i,vi in enumerate(bl):
    c=rm@m.vertices[vi].co; kd.insert(Vector((c.x,c.y,0)),i)
kd.balance()
wm=w.matrix_world; out=[]
for p in w.data.polygons:
    vs=sorted([(wm@w.data.vertices[i].co) for i in p.vertices],key=lambda v:v.z)
    for v in vs[2:]:
        near=kd.find_range(Vector((v.x,v.y,0)),1.0)
        if not near: out.append((p.index,round(v.x,1),round(v.y,1),round(v.z,1),'none')); continue
        zs=[(rm@m.vertices[bl[i]].co).z for _,i,_ in near]
        if v.z-min(zs)>1.0: out.append((p.index,round(v.x,1),round(v.y,1),round(v.z,1),round(min(zs),1),round(max(zs),1)))
print('WALLTOP_ABOVE',len(out))
for o in out[:40]: print(' ',o)
