import bpy, numpy as np, collections, json
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=bpy.data.objects; step=0.5
c=O['WA1_CAM_eye_stone_footway_from_N']; L=c.location; D=c.matrix_world.to_3x3()@Vector((0,0,-1))
print('CAM',tuple(round(v,2) for v in L),tuple(round(v,3) for v in D))
cnt=collections.Counter()
for gn in [n for n in O.keys() if 'grass_points' in n and O[n].type=='MESH']:
    g=O[gn]; mm=g.matrix_world
    for v in g.data.vertices:
        p=mm@v.co; cnt[(np.floor(p.x/step)*step,np.floor(p.y/step)*step)]+=1
def flat(o):
    m=o.matrix_world; return BVHTree.FromPolygons([Vector(((m@v.co).x,(m@v.co).y,0)) for v in o.data.vertices],[tuple(p.vertices) for p in o.data.polygons])
SL=[(n,flat(O[n])) for n in O.keys() if O[n].type=='MESH' and n.startswith(('QS_footway_','QS_service_','QW_footway_','TR_footway','SG_','QT_soil_edge_'))]
SLn=[flat(O[n]) for n in O.keys() if O[n].type=='MESH' and len(O[n].data.polygons)>0 and len(O[n].data.polygons)<50000 and n.startswith(('TI_','QQ_','TR_','QS_','QW_footway','SG_','QT_'))]
d2=Vector((D.x,D.y,0)).normalized(); side=Vector((-d2.y,d2.x,0))
bare=[]; tot=0
for fwd in np.arange(2,30,step):
  for lat in np.arange(-15,15,step):
    p=Vector((L.x,L.y,0))+d2*fwd+side*lat
    if abs(lat)>fwd*0.7: continue
    k=(np.floor(p.x/step)*step,np.floor(p.y/step)*step)
    q=Vector((k[0]+.25,k[1]+.25,0))
    if any(b.ray_cast(q+Vector((0,0,1)),Vector((0,0,-1)),2)[0] is not None for b in SLn): continue
    tot+=1
    if cnt[k]==0: bare.append(k)
print('VIEWCELLS',tot,'bare',len(bare))
b=np.array(bare); 
if len(b): print('BAREBB',b[:,0].min(),b[:,0].max(),b[:,1].min(),b[:,1].max())
json.dump([list(map(float,k)) for k in set(bare)],open('/workspace/nj-scenes/montclair-state/scripts/wk/bare.json','w'))
