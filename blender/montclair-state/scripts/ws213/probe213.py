import bpy, json, numpy as np, collections
from mathutils.bvhtree import BVHTree
from mathutils import Vector
F='/workspace/nj-scenes/montclair-state/montclair_state.blend'
BB=json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws205/bbox205.json'))
X0,X1,Y0,Y1=-286,-218,-96,-54
want=[n for n,v in BB.items() if v[0]=='MESH' and not (v[3]<X0 or v[2]>X1 or v[5]<Y0 or v[4]>Y1) and not n.startswith(('Context_skirt','BD_farfield'))]
want.append('WS76_lot_stall_paint_white_ortho2020_UNVERIFIED')
with bpy.data.libraries.load(F) as (a,b): b.objects=[n for n in set(want) if n in a.objects]
P=[o for o in b.objects if o and o.name=='WS76_lot_stall_paint_white_ortho2020_UNVERIFIED'][0]
mw=P.matrix_world; C=[(mw@p.center) for p in P.data.polygons]
T=[]
for o in b.objects:
    if o is None or o is P or o.type!='MESH' or 'paint' in o.name.lower() or 'DTM_target' in o.name or o.name.startswith('Terrain_LiDAR') or o.hide_render or len(o.data.polygons)==0: continue
    me=o.data; m=o.matrix_world
    V=[m@v.co for v in me.vertices]; T.append((o,BVHTree.FromPolygons(V,[p.vertices[:] for p in me.polygons])))
res=collections.Counter(); dz=collections.defaultdict(list); byf=[]
for i,c in enumerate(C):
    best=None
    for o,t in T:
        h=t.ray_cast(Vector((c.x,c.y,c.z+3)),Vector((0,0,-1)),10)
        if h[0] is not None and (best is None or h[0].z>best[0]):
            mat=o.data.materials[o.data.polygons[h[2]].material_index].name if o.data.materials else None
            best=(h[0].z,o.name,mat)
    k=(best[1],best[2]) if best else (None,None); res[k]+=1
    if best: dz[k].append(c.z-best[0])
    byf.append([c.x,c.y,k[0],k[1]])
for k,v in res.most_common(): print('HIT213',k,v,'dz med',round(float(np.median(dz[k])),3) if dz[k] else None)
json.dump(byf,open('hits213.json','w'))
for l in open('/proc/self/status'):
    if l.startswith('VmHWM'): print('MEM',l.strip())
