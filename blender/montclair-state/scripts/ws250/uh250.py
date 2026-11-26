# ws250: University Hall footprint (READ-ONLY, from north/montclair_north.blend; nothing saved)
import bpy, os, json
from mathutils import Vector
N='/workspace/nj-scenes/montclair-state/north/montclair_north.blend'
with bpy.data.libraries.load(N) as (a,b):
    b.objects=[n for n in a.objects if n.startswith('University Hall') or (n.startswith('UH') and not n.startswith('UH_'))]
X=[];out={}
for o in b.objects:
    if o is None or o.type!='MESH': continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    r=[min(v.x for v in bb),max(v.x for v in bb),min(v.y for v in bb),max(v.y for v in bb),min(v.z for v in bb),max(v.z for v in bb)]
    out[o.name]=r
json.dump(out,open('/workspace/nj-scenes/montclair-state/scripts/ws250/uh250.json','w'))
for k in sorted(out,key=lambda k:-(out[k][1]-out[k][0])*(out[k][3]-out[k][2]))[:8]: print('UH250',k[:60],['%.1f'%v for v in out[k]])
print('UH250 n',len(out),'union',['%.1f'%f(v[i] for v in out.values()) for i,f in [(0,min),(1,max),(2,min),(3,max),(4,min),(5,max)]],flush=True)
os._exit(0)
