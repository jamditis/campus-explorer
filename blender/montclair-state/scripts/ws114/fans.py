import bpy, bmesh, numpy as np
from collections import defaultdict
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=t.data
bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
long=[f for f in bm.faces if max(e.calc_length() for e in f.edges)>6]
print('FAN long faces',len(long),'area %.0f'%sum(f.calc_area() for f in long))
hub=defaultdict(list)
for f in long:
    # hub = vertex with most long faces
    for v in f.verts: hub[v.index].append(f)
top=sorted(hub.items(),key=lambda kv:-len(kv[1]))[:12]
for vi,fs in top:
    v=bm.verts[vi].co; xs=[w.co.x for f in fs for w in f.verts]; ys=[w.co.y for f in fs for w in f.verts]
    print('FAN hub',vi,'(%.1f,%.1f,%.1f)'%tuple(v),'faces',len(fs),'area %.0f'%sum(f.calc_area() for f in fs),'bbox x %.0f..%.0f y %.0f..%.0f'%(min(xs),max(xs),min(ys),max(ys)), 'mats',sorted(set(f.material_index for f in fs)))
# long faces not touching top hubs
hs=set(vi for vi,_ in top[:6])
rest=[f for f in long if not any(v.index in hs for v in f.verts)]
print('FAN rest',len(rest),'area %.0f'%sum(f.calc_area() for f in rest))
for f in rest[:15]:
    c=f.calc_center_median(); print('FAN r (%.1f,%.1f) maxedge %.1f'%(c.x,c.y,max(e.calc_length() for e in f.edges)))
print('FAN mats',[m.name for m in me.materials])
