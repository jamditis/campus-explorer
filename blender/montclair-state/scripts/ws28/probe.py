import bpy
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
col=bpy.data.collections['WS27_CollegeAve_Kasser_carriageway_curbs_20261110ws27']
print('WS27 objs',[(o.name,o.type) for o in col.all_objects])
road=[o for o in col.all_objects if 'arriage' in o.name or 'asphalt' in o.name.lower()]
print('road',[o.name for o in road])
from collections import Counter
cnt=Counter(); bad=[]
for o in road[:1]:
    mw=o.matrix_world
    vs=[mw@v.co for v in o.data.vertices]
    for v in vs[::7]:
        h=sc.ray_cast(dg,Vector((v.x,v.y,175)),Vector((0,0,-1)))
        if h[0]:
            n=h[4].name; cnt[n]+=1
            if h[4]!=o and h[1].z>v.z+0.005: bad.append((round(v.x,1),round(v.y,1),n,round(h[1].z-v.z,3)))
print(cnt.most_common(15))
print('poke',len(bad)); 
import collections
by=collections.defaultdict(list)
for b in bad: by[b[2]].append(b)
for k,l in by.items(): print(k,len(l),l[:6])
