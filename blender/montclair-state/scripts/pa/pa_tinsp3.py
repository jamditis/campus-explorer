import bpy
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=T.data; V=me.vertices
big=[]
for p in me.polygons:
    cs=[V[k].co for k in p.vertices]
    L=max((cs[i]-cs[i-1]).length for i in range(len(cs)))
    if L>3: big.append((p.index,L,len(cs),[tuple(round(c.x,1) for c in [v]) for v in cs]))
print('TI nbig',len(big))
import collections
far=collections.Counter()
for i,L,n,c in big:
    for k in me.polygons[i].vertices:
        far[k]+=1
print('TI hubs',[(k,cnt,tuple(round(x,1) for x in V[k].co)) for k,cnt in far.most_common(6)])
xs=[V[k].co.x for i,_,_,_ in big for k in me.polygons[i].vertices]; ys=[V[k].co.y for i,_,_,_ in big for k in me.polygons[i].vertices]
print('TI bigbbox',min(xs),max(xs),min(ys),max(ys))
print('TI ngon sizes',collections.Counter(len(p.vertices) for p in me.polygons))
# grid vertices in region
reg=[v.co for v in V if 110<v.co.x<150 and 140<v.co.y<200]; print('TI reg verts',len(reg))
