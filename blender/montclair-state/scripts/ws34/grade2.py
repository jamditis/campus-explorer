# ws34: Cole plaza deck west/south raw edge (deck up to 0.6-1.4 m over terrain beside College Ave / Kasser front)
# -> grade terrain up to the deck edge (top -5 cm, 1:2.5 falloff out to 3 m), terrain under deck raised to deck -8 cm.
# Excludes steps/rails (+0.5 m), roads/curbs and walks. Grass points re-seated on the new terrain.
import bpy,bmesh,os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
X0,X1,Y0,Y1=map(float,os.environ.get('BOX','-216,-186,-112,-70').split(','))
dg=bpy.context.evaluated_depsgraph_get()
def bvh(name):
    o=bpy.data.objects.get(name)
    if not o: return None
    e=o.evaluated_get(dg); m=e.to_mesh(); b=bmesh.new(); b.from_mesh(m); b.transform(o.matrix_world)
    t=BVHTree.FromBMesh(b); return t,b
deck=[bvh('COLE_plaza_deck_bs'),bvh('COLE_plaza_edge_bs')]
segs=[]
for t,b in deck:
    for e in b.edges:
        if e.is_boundary:
            a,c=e.verts[0].co.copy(),e.verts[1].co.copy()
            if X0-4<a.x<X1+4 and Y0-4<a.y<Y1+4: segs.append((a,c))
print('deck boundary segs',len(segs))
excl=[]
for n in ('COLE_plaza_west_steps_bu',):
    o=bpy.data.objects[n]; bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    excl.append((min(v.x for v in bb)-0.15,max(v.x for v in bb)+0.15,min(v.y for v in bb)-0.15,max(v.y for v in bb)+0.15))
pav=[bvh(n) for n in ('WS27_CollegeAve_carriageway_2020ortho','WS27_CollegeAve_curb_right_UNVERIFIED','WS27_CollegeAve_curb_left_UNVERIFIED','Roads_OSM')]
walk=[bvh('Footpaths_OSM')]
pav=[p for p in pav if p]
def under(tlist,x,y,r=0.0):
    for dx,dy in ((0,0),(r,0),(-r,0),(0,r),(0,-r)) if r else ((0,0),):
        for t,_ in tlist:
            h=t.ray_cast(Vector((x+dx,y+dy,300)),Vector((0,0,-1)))
            if h[0] is not None: return h[0].z
    return None
def d2(p,a,c):
    ax,ay=c.x-a.x,c.y-a.y; L=ax*ax+ay*ay
    s=0 if L==0 else max(0,min(1,((p.x-a.x)*ax+(p.y-a.y)*ay)/L))
    qx,qy=a.x+s*ax,a.y+s*ay; z=a.z+s*(c.z-a.z)
    return ((p.x-qx)**2+(p.y-qy)**2)**0.5,z
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; tm=T.matrix_world; ti=tm.inverted()
old={}; nU=nG=0; mx=0
for v in T.data.vertices:
    p=tm@v.co
    if not(X0<p.x<X1 and Y0<p.y<Y1): continue
    if any(a<p.x<b and c<p.y<d for a,b,c,d in excl): continue
    dz=under(deck,p.x,p.y)
    if dz is not None:
        tgt=dz-0.08
        if tgt>p.z+0.02: old[v.index]=p.z; v.co=ti@Vector((p.x,p.y,tgt)); nU+=1; mx=max(mx,tgt-p.z)
        continue
    if under(pav,p.x,p.y,0.6) is not None: continue
    onw=under(walk,p.x,p.y,0.5) is not None
    R_=4.0 if onw else 3.0; off=0.10 if onw else 0.05; sl=0.09 if onw else 0.4
    best=None
    for a,c in segs:
        dd,z=d2(p,a,c)
        if dd<R_:
            t=z-off-dd*sl
            if best is None or t>best: best=t
    if best is not None and best>p.z+0.02:
        old[v.index]=p.z; v.co=ti@Vector((p.x,p.y,best)); nG+=1; mx=max(mx,best-p.z)
T.data.update(); print('walk-aware');print('terrain under deck raised',nU,'graded',nG,'max raise',round(mx,2))
# reseat grass on new terrain
dg.update(); te=T.evaluated_get(dg)
def tz(x,y):
    ok,hp,_,_=te.ray_cast(ti@Vector((x,y,300)),(ti.to_3x3()@Vector((0,0,-1))).normalized())
    return (tm@hp).z if ok else None
for name in [o.name for o in bpy.data.objects if o.type=='MESH' and ('grass' in o.name.lower() or 'lawn' in o.name.lower())]:
    o=bpy.data.objects[name]; m=o.matrix_world; mi=m.inverted(); k=0
    if len(o.data.polygons)>0: continue
    for v in o.data.vertices:
        p=m@v.co
        if not(X0<p.x<X1 and Y0<p.y<Y1): continue
        z=tz(p.x,p.y)
        if z is not None and z-p.z>0.03 and z-p.z<1.6:
            v.co=mi@Vector((p.x,p.y,z)); k+=1
    if k: o.data.update(); print('grass reseated',name,k)
if os.environ.get('SAVE')=='1':
    bpy.ops.wm.save_mainfile(); print('SAVED',flush=True)
