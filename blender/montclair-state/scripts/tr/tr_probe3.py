import bpy, json
from mathutils import Vector
# Find all walk meshes near Stone SW and check coverage along OSM 546643369
import json as J
D=J.load(open('/workspace/nj-scenes/montclair-state/data/scene_data.json'))
F={str(f['id']):f for f in D['features']}
way=F['546643369']['pts']
# For each OSM vertex, find nearest walk mesh vertex distance
walks=[]
for o in bpy.data.objects:
    if o.type!='MESH': continue
    n=o.name.lower()
    if any(k in n for k in ('walk','footway','path')) and 'wear' not in n and 'soil' not in n:
        corners=[o.matrix_world @ Vector(c) for c in o.bound_box]
        xs=[c.x for c in corners]; ys=[c.y for c in corners]
        if max(xs)>60 and min(xs)<200 and max(ys)>200 and min(ys)<400:
            walks.append(o)
print('walk objs', [o.name for o in walks])
from mathutils.kdtree import KDTree
pts=[]; owners=[]
for o in walks:
    mw=o.matrix_world
    for v in o.data.vertices:
        p=mw@v.co; pts.append(p); owners.append(o.name)
kd=KDTree(len(pts))
for i,p in enumerate(pts): kd.insert(p,i)
kd.balance()
print('OSM 546643369 coverage:')
for i,p in enumerate(way):
    co,idx,d=kd.find((p[0],p[1],0))
    # also 2d
    best=1e9; bn=None
    for j,q in enumerate(pts):
        dd=(q.x-p[0])**2+(q.y-p[1])**2
        if dd<best: best=dd; bn=owners[j]
    print(i, [round(x,1) for x in p[:2]], 'nearest', bn, 'dist2d', round(best**0.5,2))
# 552441744 and 552441882
for wid in ('552441744','552441882'):
    f=F[wid]; print('WAY',wid,f['tags'], 'pts:')
    for i,p in enumerate(f['pts']):
        best=1e9; bn=None
        for j,q in enumerate(pts):
            dd=(q.x-p[0])**2+(q.y-p[1])**2
            if dd<best: best=dd; bn=owners[j]
        print(' ',i,[round(x,1) for x in p[:2]],'->',bn, round(best**0.5,2))
