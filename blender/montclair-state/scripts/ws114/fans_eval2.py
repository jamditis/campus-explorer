import bpy, bmesh, numpy as np
dg=bpy.context.evaluated_depsgraph_get()
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; e=t.evaluated_get(dg); me=e.to_mesh()
bm=bmesh.new(); bm.from_mesh(me)
long=[f for f in bm.faces if max(x.calc_length() for x in f.edges)>6]
print('FE2 eval long faces',len(long),'area %.0f'%sum(f.calc_area() for f in long))
import collections
G=collections.defaultdict(float)
for f in long:
    c=f.calc_center_median(); G[(int(c.x//50)*50,int(c.y//50)*50)]+=f.calc_area()
for k,v in sorted(G.items(),key=lambda kv:-kv[1])[:25]: print('FE2 cell',k,'%.0f'%v)
# which other objects cover each 50m cell (ground-ish names)
