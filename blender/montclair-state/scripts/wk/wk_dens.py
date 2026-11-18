import bpy,numpy as np,collections
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=bpy.data.objects
m=O['QS_service_546643370_UNVERIFIED']; mw=m.matrix_world
R=BVHTree.FromPolygons([Vector(((mw@v.co).x,(mw@v.co).y,0)) for v in m.data.vertices],[tuple(p.vertices) for p in m.data.polygons])
G=[n for n in O.keys() if 'grass_points' in n and O[n].type=='MESH']
pts=[]
for n in G:
    g=O[n]; gm=g.matrix_world
    for v in g.data.vertices:
        p=gm@v.co
        if 112<p.x<132 and 262<p.y<292: pts.append((p.x,p.y,n))
print('N',len(pts),collections.Counter(p[2] for p in pts))
# distance bands west of road
xs=np.arange(112,132,0.25); ys=np.arange(264,290,0.25); band=collections.Counter(); area=collections.Counter()
def side(x,y):
    h=R.find_nearest(Vector((x,y,0)))
    if h[0] is None: return None
    return h[3], (h[0].x>x)  # True => road is east of point
for x in xs:
    for y in ys:
        if R.ray_cast(Vector((x,y,1)),Vector((0,0,-1)),2)[0] is not None: continue
        d,e=side(x,y)
        if not e or d>8: continue
        area[int(d*2)/2]+=0.0625
for x,y,n in pts:
    if R.ray_cast(Vector((x,y,1)),Vector((0,0,-1)),2)[0] is not None: continue
    d,e=side(x,y)
    if not e or d>8: continue
    band[int(d*2)/2]+=1
for k in sorted(area): print(k, round(band[k]/area[k],1),'/m2', round(area[k],1),'m2')
