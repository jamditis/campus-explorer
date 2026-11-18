import bpy, json, numpy as np, collections
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=bpy.data.objects; step=0.5
C=json.load(open('/workspace/nj-scenes/montclair-state/scripts/wi2/cells.json'))
WV=O['WV_stone_west_LiDAR_patch_UNVERIFIED']; m=WV.matrix_world
GB=BVHTree.FromPolygons([m@v.co for v in WV.data.vertices],[tuple(p.vertices) for p in WV.data.polygons])
bl=[]
for o in O:
    if o.type!='MESH' or 'grass' in o.name or len(o.data.polygons)==0 or o.name.startswith(('Context','WV_','QS_','QT_','QW_','WM_','QY_')): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    if min(b.x for b in bb)<160 and max(b.x for b in bb)>130 and min(b.y for b in bb)<310 and max(b.y for b in bb)>280 and max(b.z for b in bb)-min(b.z for b in bb)>1.0:
        mm=o.matrix_world; bl.append((o.name,BVHTree.FromPolygons([mm@v.co for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])))
def ok(x,y):
    g=GB.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))
    if g[0] is None: return False
    for n,b in bl:
        h=b.ray_cast(Vector((x,y,500)),Vector((0,0,-1)))
        if h[0] is not None and h[0].z>g[0].z+0.3: return False
    return True
cnt=collections.Counter()
for gn in ['QS_Richardson_lawn_grass_points_UNVERIFIED','QV_Richardson_NW_lawn_grass_points_UNVERIFIED']:
    g=O[gn]; mm=g.matrix_world
    for v in g.data.vertices:
        c=mm@v.co; cnt[(round(130+np.floor((c.x-130)/step)*step,2),round(280+np.floor((c.y-280)/step)*step,2))]+=1
for cl in ('verge','lawn'):
    ks=[tuple(k) for k in C[cl] if ok(k[0]+.25,k[1]+.25)]
    c=[cnt[k] for k in ks]; print('D2',cl,len(ks),'cells',np.mean(c)/0.25 if c else 0,'pts/m2 zero%',np.mean([x==0 for x in c]) if c else 0)
print('BL',[n for n,_ in bl][:15])
FW=O['QS_footway_546643369_UNVERIFIED']; mf=FW.matrix_world
FB=BVHTree.FromPolygons([Vector(((mf@v.co).x,(mf@v.co).y,0)) for v in FW.data.vertices],[tuple(p.vertices) for p in FW.data.polygons])
near=[tuple(k) for k in C['lawn'] if ok(k[0]+.25,k[1]+.25) and FB.find_nearest(Vector((k[0]+.25,k[1]+.25,0)))[3]<3]
c=[cnt[k] for k in near]; print('NEARLAWN',len(near),np.mean(c)/0.25,'zero%',np.mean([x==0 for x in c]))
nz=[cnt[tuple(k)]/0.25 for k in C['lawn'] if cnt[tuple(k)]>0]; print('NZ',np.percentile(nz,[25,50,75]))
