# ws18: drip/moss streak strips that sit ABOVE the wall top (inside the eave cavity) show as a pale lens
# between gutter/barrel course and roof. Move each such strip face down so its top sits 2 cm under the soffit.
import bpy, os
from mathutils import Vector
SAVE=os.environ.get('SAVE')=='1'
ob=bpy.data.objects['Eave drip / moss streaks on stucco (3g)']
me=ob.data; mw=ob.matrix_world; mwi=mw.inverted()
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
from mathutils.bvhtree import BVHTree
bb=[mw@Vector(c) for c in ob.bound_box]
lo=Vector((min(v.x for v in bb)-3,min(v.y for v in bb)-3,min(v.z for v in bb)-3)); hi=Vector((max(v.x for v in bb)+3,max(v.y for v in bb)+3,max(v.z for v in bb)+3))
V=[];F=[];FO=[]
for o2 in sc.objects:
    if o2.type!='MESH' or o2==ob or o2.hide_render: continue
    b2=[o2.matrix_world@Vector(c) for c in o2.bound_box]
    if max(v.x for v in b2)<lo.x or min(v.x for v in b2)>hi.x or max(v.y for v in b2)<lo.y or min(v.y for v in b2)>hi.y or max(v.z for v in b2)<lo.z or min(v.z for v in b2)>hi.z: continue
    if len(o2.data.polygons)>400000: continue
    m2=o2.data; base=len(V); M=o2.matrix_world
    V.extend(M@v.co for v in m2.vertices)
    for q in m2.polygons: F.append([base+i for i in q.vertices]); FO.append(o2.name)
print('BVH faces',len(F),flush=True)
T=BVHTree.FromPolygons(V,F,all_triangles=False)
class _H: pass
def ray(o,d,skip):
    loc,n,i,dist=T.ray_cast(o,d,100)
    if loc is None: return None
    h=_H(); h.name=FO[i]; return (loc,h)
shift={}  # vert idx -> dz (world)
stats=[]
for p in me.polygons:
    vs=[mw@me.vertices[v].co for v in p.vertices]
    c=sum(vs,Vector())/len(vs); n=(mw.to_3x3()@p.normal).normalized()
    zt=max(v.z for v in vs); zb=min(v.z for v in vs)
    # outward = side where the wall is NOT
    wa=ray(c+n*0.01, n, ob.name); wb=ray(c-n*0.01, -n, ob.name)
    da=(wa[0]-c).length if wa else 99; db=(wb[0]-c).length if wb else 99
    out = -n if da<db else n
    # soffit/eave above, probed 4 cm outside the wall, from below the strip
    o=c+out*0.04; o.z=zb-1.0
    up=ray(o,Vector((0,0,1)),ob.name)
    if not up: continue
    sz=up[0].z
    if 'eave soffit' in up[1].name and zt > sz-0.005 and sz-zb>-0.5:
        dz=zt-(sz-0.02)
        if dz>1.2: continue
        stats.append((p.index,round(zt,2),round(sz,2),up[1].name,round(dz,2)))
        for v in p.vertices: shift[v]=max(shift.get(v,0),dz)
print('AFFECTED',len(stats))
for s in stats[:400]: print('S',s)
if SAVE:
    for vi,dz in shift.items():
        w=mw@me.vertices[vi].co; w.z-=dz; me.vertices[vi].co=mwi@w
    me.update()
    bpy.ops.wm.save_mainfile()
    print('SAVED')
