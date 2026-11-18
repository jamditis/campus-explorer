import bpy, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=bpy.data.objects
BX=(130,160,280,310)
def flat(o):
    m=o.matrix_world; V=[(m@v.co) for v in o.data.vertices]; V=[Vector((v.x,v.y,0)) for v in V]
    return BVHTree.FromPolygons(V,[tuple(p.vertices) for p in o.data.polygons])
FW=flat(O['QS_footway_546643369_UNVERIFIED']); SR=flat(O['QS_service_546643370_UNVERIFIED'])
slabs=[flat(O[n]) for n in O.keys() if O[n].type=='MESH' and n.startswith(('QS_footway_','QS_service_','QW_footway_','QS_road','QW_'))and O[n].type=='MESH' and len(O[n].data.polygons)<20000 and not n.startswith('QW_DTM')]
def over(x,y):
    for b in slabs:
        h=b.ray_cast(Vector((x,y,1)),Vector((0,0,-1)),2)
        if h[0] is not None: return True
    return False
step=0.5; cls={}
for x in np.arange(BX[0],BX[1],step):
  for y in np.arange(BX[2],BX[3],step):
    cx,cy=x+step/2,y+step/2
    if over(cx,cy): continue
    p=Vector((cx,cy,0)); df=FW.find_nearest(p)[3]; ds=SR.find_nearest(p)[3]
    if df is None or ds is None: continue
    c='verge' if (df<4 and ds<4 and df+ds<6) else ('lawn' if df<8 else None)
    if c: cls[(round(x,2),round(y,2))]=(c,df,ds)
print('CELLS',{k:sum(1 for v in cls.values() if v[0]==k) for k in ('verge','lawn')})
import collections
cnt=collections.Counter(); per={}
for gn in ['QS_Richardson_lawn_grass_points_UNVERIFIED','QV_Richardson_NW_lawn_grass_points_UNVERIFIED']:
    g=O[gn]; m=g.matrix_world
    for v in g.data.vertices:
        c=m@v.co
        if not(BX[0]<=c.x<BX[1] and BX[2]<=c.y<BX[3]): continue
        k=(round(BX[0]+np.floor((c.x-BX[0])/step)*step,2),round(BX[2]+np.floor((c.y-BX[2])/step)*step,2))
        if k in cls: cnt[cls[k][0]]+=1; per[k]=per.get(k,0)+1
for k in ('verge','lawn'):
    n=sum(1 for v in cls.values() if v[0]==k); print('DENS',k,cnt[k]/(n*step*step) if n else 0,'pts/m2', n*step*step,'m2')
# verge extent
vx=[k for k,v in cls.items() if v[0]=='verge']; 
import json; json.dump({'verge':[list(k) for k in vx],'lawn':[list(k) for k,v in cls.items() if v[0]=='lawn']},open('/workspace/nj-scenes/montclair-state/scripts/wi2/cells.json','w'))
print('VX',min(k[0] for k in vx),max(k[0] for k in vx),min(k[1] for k in vx),max(k[1] for k in vx))
# attributes on grass points
g=O['QS_Richardson_lawn_grass_points_UNVERIFIED']; print('ATTR',[(a.name,a.data_type,a.domain) for a in g.data.attributes])
ng=g.modifiers['cx_grass'].node_group; print('NODES',[n.bl_idname+':'+n.name for n in ng.nodes])
