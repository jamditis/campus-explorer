import bpy, random
from mathutils import Vector
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
o=bpy.data.objects['Eave drip / moss streaks on stucco (3g)']
M=o.matrix_world; me=o.data
random.seed(3)
faces=list(me.polygons)
def region(c):
    if c.x>-2 and c.y>20: return 'LIFE'
    if -25<c.x<33 and -28<c.y<20: return 'CCOM'
    return None
cands={'LIFE':[], 'CCOM':[]}
for f in faces:
    c=M@f.center; r=region(c)
    if r: cands[r].append((c,(M.to_3x3()@f.normal).normalized()))
print('NFACES',{k:len(v) for k,v in cands.items()})
def down(p):
    h,loc,n,i,ob,_=sc.ray_cast(dg,Vector((p.x,p.y,p.z+60)),Vector((0,0,-1)))
    return (loc,ob.name) if h else (None,None)
res={'LIFE':[], 'CCOM':[]}
SGN=-1
cands.pop('LIFE')
for r,L in cands.items():
    random.shuffle(L)
    for c,n in L[:60]:
        hn=Vector((n.x,n.y,0))*SGN
        if hn.length<0.5: continue
        hn.normalize()
        for d in (14,20,26):
            p=c+hn*d
            g,gn=down(p)
            if g is None: continue
            gl=gn.lower()
            if any(k in gl for k in ('tree','leaf','foliage','canopy','shrub','bush','trunk')): continue
            if g.z>c.z-3: continue
            cam=Vector((p.x,p.y,g.z+1.65))
            v=c-cam
            h,loc,_,_,ob,_=sc.ray_cast(dg,cam,v.normalized(),distance=v.length+0.5)
            ok = h and (loc-c).length<1.0
            if ok:
                # also check upward clearance (not inside something)
                hu,_,_,_,obu,_=sc.ray_cast(dg,cam,Vector((0,0,1)),distance=30)
                if hu: continue
                res[r].append((d,tuple(round(x,1) for x in cam),tuple(round(x,1) for x in c),gn,ob.name))
for r,L in res.items():
    print('RES',r,len(L))
    for x in L[:12]: print('  ',x)
