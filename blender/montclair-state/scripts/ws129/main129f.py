# ws129 self-review fix: lawn dragged down by 1 m ground triangles whose inner verts were pushed under the lot -> exposed curb faces
# ("floating plate" look). Lawn apron strips S of the S curb and W of the island curb: inner edge 1.5 cm under the curb top (LiDAR: lawn sits
# at curb-top height for ~1.5 m, e.g. x -218: y -256 120.81 / -257 120.82 / -258 120.67), outer edge seated on the existing terrain.
import bpy, bmesh, os, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SAVE=os.environ.get('SAVE','0')=='1'
col=bpy.data.collections.get('WS129_Chapin_S_lot')
for o in [o for o in bpy.data.objects if o.name.startswith('WS129f_')]: bpy.data.objects.remove(o)
yS=lambda x:-255.5-0.233*(x+218.0)
curbs=[o for o in bpy.data.objects if o.name.startswith(('WS129_Chapin_S_lot_S_curb','WS129e_Chapin_S_lot_S_curb','WS129_Chapin_S_lot_island_E_curb'))]
TC=BVHTree.FromPolygons([o.matrix_world@v.co for o in curbs for v in o.data.vertices],[])
cv=[];off=0;polys=[]
for o in curbs:
    for v in o.data.vertices: cv.append(o.matrix_world@v.co)
    for p in o.data.polygons: polys.append([i+off for i in p.vertices])
    off+=len(o.data.vertices)
TC=BVHTree.FromPolygons(cv,polys)
grounds=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('Terrain_LiDAR_DTM_1m','WS113_terrain_fan_fill','WS110_ground_patch'))]
gv=[];gp=[];off=0
for o in grounds:
    mw=o.matrix_world
    for v in o.data.vertices: gv.append(mw@v.co)
    for p in o.data.polygons: gp.append([i+off for i in p.vertices])
    off+=len(o.data.vertices)
TG=BVHTree.FromPolygons(gv,gp)
def ctop(x,y):
    h=TC.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))[0]; return h.z if h is not None else None
def gz(x,y):
    h=TG.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))[0]; return h.z if h is not None else None
lm=bpy.data.materials.get('COLE_lawn_post2020_bs')
def apron(name,pts,nrm,W=1.6,nv=4):
    bm=bmesh.new(); rows=[]
    for p in pts:
        n=nrm(p); inner=p+n*0.14; zt=ctop(p.x+n.x*0.07,p.y+n.y*0.07)
        if zt is None: zt=gz(p.x,p.y) or 0
        zi=zt-0.015; outer=inner+n*W; zo=gz(outer.x,outer.y)
        if zo is None: zo=zi
        r=[]
        for j in range(nv+1):
            t=j/nv; q=inner.lerp(outer,t); s=t*t*(3-2*t)
            r.append(bm.verts.new((q.x,q.y,zi*(1-s)+(zo+0.004)*s)))
        rows.append(r)
    for a,b in zip(rows,rows[1:]):
        for j in range(nv): bm.faces.new((a[j],b[j],b[j+1],a[j+1]))
    bm.normal_update()
    for f in bm.faces:
        if f.normal.z<0: f.normal_flip()
    for e in [e for e in bm.edges if e.is_boundary]:
        a,b=e.verts; a2=bm.verts.new(a.co-Vector((0,0,0.1))); b2=bm.verts.new(b.co-Vector((0,0,0.1))); bm.faces.new((a,b,b2,a2))
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(lm)
    o=bpy.data.objects.new(name,me); col.objects.link(o); return o
nS=Vector((0.233,-1)).normalized()
S=[Vector((x,yS(x))) for x in np.linspace(-228.6,-190.0,78)]
a1=apron('WS129f_lot_S_curb_lawn_apron_LiDARcurbtop_UNVERIFIED',S,lambda p:nS)
I=[Vector((-228.5,y)) for y in np.linspace(-246.4,yS(-228.5)-0.1,20)]
a2=apron('WS129f_island_E_curb_lawn_apron_LiDAR_UNVERIFIED',I,lambda p:Vector((-1,0)),W=1.4)
TA=[BVHTree.FromPolygons([v.co for v in o.data.vertices],[p.vertices for p in o.data.polygons if p.normal.z>0.5]) for o in (a1,a2)]
nl=0
for o in grounds:
    mw=o.matrix_world; mi=mw.inverted()
    for v in o.data.vertices:
        p=mw@v.co
        if not (-231<p.x<-189 and -263<p.y<-245): continue
        for T in TA:
            h=T.ray_cast(Vector((p.x,p.y,200)),Vector((0,0,-1)))[0]
            if h is not None and p.z>h.z-0.03: p.z=h.z-0.03; v.co=mi@p; nl+=1
print('M129f aprons',len(a1.data.polygons),len(a2.data.polygons),'ground lowered',nl)
px=bpy.data.objects.get('WS113_paving_tops_proxy')
if px and not px.get('ws129f'):
    px['ws129f']=1; pbm=bmesh.new(); pbm.from_mesh(px.data); pmi=px.matrix_world.inverted()
    for o in (a1,a2):
        for p in o.data.polygons:
            if p.normal.z>0.5: pbm.faces.new([pbm.verts.new(pmi@(o.matrix_world@o.data.vertices[i].co)) for i in p.vertices])
    pbm.to_mesh(px.data); pbm.free()
if SAVE: bpy.ops.wm.save_mainfile(); print('M129f SAVED')
