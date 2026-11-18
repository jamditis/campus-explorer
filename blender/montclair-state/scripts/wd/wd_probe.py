import bpy, json
from mathutils import Vector
dg=bpy.context.evaluated_depsgraph_get()
W=json.load(open('data/td/east_osm.json'))['ways']
ids=['1132693523','600258640','313029912','1132693524']
pts=[]
for k in ids:
    P=W[k]['pts']
    for i in range(len(P)-1):
        a=Vector(P[i]);b=Vector(P[i+1]);n=max(2,int((b-a).length/1.0))
        for j in range(n+1):
            c=a.lerp(b,j/n); pts.append((k,c.x,c.y))
res={}
objs=[o for o in bpy.data.objects if o.type=='MESH' and not o.hide_render]
# bbox prefilter
cand=[]
for o in objs:
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    x0=min(v.x for v in bb);x1=max(v.x for v in bb);y0=min(v.y for v in bb);y1=max(v.y for v in bb)
    if x1<190 or x0>240 or y1<395 or y0>440: continue
    if (x1-x0)>300 or (y1-y0)>300: continue
    cand.append(o)
print('CAND',len(cand))
for k,x,y in pts:
    hits=[]
    for o in cand:
        e=o.evaluated_get(dg); mw=o.matrix_world; iw=mw.inverted()
        try:
            r=e.ray_cast(iw@Vector((x,y,400)),(iw.to_3x3()@Vector((0,0,-1))).normalized())
        except Exception: continue
        if r[0]: hits.append(((mw@r[1]).z,o.name))
    hits.sort(reverse=True)
    res.setdefault(k,[]).append(dict(x=round(x,1),y=round(y,1),top=[(round(z,2),n) for z,n in hits[:4]]))
json.dump(res,open('data/wd/probe.json','w'),indent=1)
for k,v in res.items():
    print('==',k)
    for p in v: print(p['x'],p['y'],p['top'][:3])
# nearby named objects
print('NEAR', sorted(set(o.name for o in cand))[:200])
