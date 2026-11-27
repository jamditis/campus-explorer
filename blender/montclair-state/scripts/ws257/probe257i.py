# ws257 read-only: WS257 UNIFY10 strip in ws257d - slope image (PIL, via /tmp json) + per-row x-roughness (ridge check, ws257c test had N-S ridges)
import sys; sys.stdout.reconfigure(line_buffering=True)
import bpy, os, json, numpy as np
F=os.environ.get('F','/workspace/nj-scenes/montclair-state/montclair_state_ws257d.blend')
with bpy.data.libraries.load(F) as (a,b): b.objects=['WS257_UNIFY10_S_edge_feather_DTM2023_to_skirt_UNVERIFIED']
o=b.objects[0]; M=o.matrix_world
fa=o.data.attributes['fade172'].data
V=[(round((M@v.co).x,2),round((M@v.co).y,2),(M@v.co).z,fa[i].value) for i,v in enumerate(o.data.vertices)]
json.dump(V,open('/tmp/strip257.json','w'))
import collections
X=collections.defaultdict(dict)
for x,y,z,f in V: X[x][y]=z
xs=sorted(X)
# second difference along x at fixed row index d (rows share y offsets from each column's edge) -> ridge metric
rough=[]
for d in range(0,28,3):
    zz=[]
    for x in xs:
        ys=sorted(X[x],reverse=True)
        if d+1<len(ys): zz.append(X[x][ys[d+1]])
    zz=np.array(zz); sd=np.abs(np.diff(zz,2)) if len(zz)>3 else np.array([0])
    rough.append((d,round(float(np.percentile(sd,95)),3),round(float(sd.max()),3)))
print('P257I verts',len(V),'row d: p95 / max |2nd diff along x| (m)',rough)
os._exit(0)
