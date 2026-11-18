import bpy, json
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get()
OBS=[o for o in bpy.data.objects if o.name.startswith('QP_Richardson') and o.type=='MESH']
def rc(o_,d_):
    best=None
    for ob in OBS:
        ok,loc,nr,fi=ob.ray_cast(o_,d_)
        if ok and (best is None or (loc-o_).length<(best[1]-o_).length): best=(ok,loc,nr,fi,ob,None)
    return best or (False,None,None,None,None,None)
OUT=[Vector((x,y,0)) for x,y in json.load(open('data/qp/rich_poly.json'))['outer']]
bad=[]
for i in range(len(OUT)):
    p0,p1=OUT[i],OUT[(i+1)%len(OUT)]; e=p1-p0; L=e.length; t=e/L; n=Vector((t.y,-t.x,0))
    for k in range(int(L/0.15)):
        u=(k+0.5)*0.15
        for z in (143.5,145.0,146.3,147.5,148.9,149.5,150.4,151.3):
            q=p0+t*u; o=Vector((q.x,q.y,z))+n*2.0
            ok,loc,nr,fi,ob,m=rc(o,-n)
            d=(loc-o).length if ok else 99
            if d>2.5: bad.append((i,round(u,2),z,round(d,2),ob.name if ok else None))
print('EDGES', [(i,round((OUT[(i+1)%len(OUT)]-OUT[i]).length,2)) for i in range(len(OUT))])
print('NBAD',len(bad))
import collections
c=collections.defaultdict(list)
for b in bad: c[(b[0],b[2])].append(b[1])
for k,v in sorted(c.items()): print('BAD',k,min(v),max(v),len(v))
