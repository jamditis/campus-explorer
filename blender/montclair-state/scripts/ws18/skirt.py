# ws18: tile skirt closing the gap between Morehead's LiDAR roof west edge and the separate fascia/barrel course.
import bpy,os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SAVE=os.environ.get('SAVE')=='1'
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
def bvh(names):
    V=[];F=[]
    for n in names:
        o=bpy.data.objects[n]; e=o.evaluated_get(dg).to_mesh(); M=o.matrix_world; b=len(V)
        V.extend(M@v.co for v in e.vertices); F.extend([b+i for i in p.vertices] for p in e.polygons); o.evaluated_get(dg).to_mesh_clear()
    return BVHTree.FromPolygons(V,F,all_triangles=False)
EAVE=bvh(['Morehead Hall eave soffit + fascia + rafter tails','Morehead Hall barrel tile eave course'])
ROOF=bvh(['Morehead Hall roof (LiDAR)'])
OUT=Vector((-0.97,0.24,0)).normalized(); AL=Vector((0.24,0.97,0)).normalized(); P0=Vector((-40.03,-56.5,0)); SL=0.55/0.83
rows=[]
a=-14.0
while a<=14.0:
    base=P0+AL*a
    i0=base+OUT*(-0.30); h,_,_,_=ROOF.ray_cast(Vector((i0.x,i0.y,160)),Vector((0,0,-1)),30)
    if h is None or h.z<144.4: rows.append(None); a+=0.5; continue
    zi=h.z+0.015
    tmax=None
    t=0.0
    while t<1.6:
        o=base+OUT*t; loc,_,_,_=EAVE.ray_cast(Vector((o.x,o.y,h.z+1)),Vector((0,0,-1)),3)
        if loc is not None: tmax=t
        t+=0.05
    if tmax is None or tmax<0.3: rows.append(None); a+=0.5; continue
    L=tmax+0.04; ou=base+OUT*L
    rows.append((Vector((i0.x,i0.y,zi)),Vector((ou.x,ou.y,zi-SL*(L+0.30)))))
    a+=0.5
V=[];F=[]
for k in range(len(rows)-1):
    r0,r1=rows[k],rows[k+1]
    if r0 is None or r1 is None: continue
    b=len(V); V+= [r0[0],r0[1],r1[1],r1[0]]; F.append([b,b+1,b+2,b+3])
print('ROWS valid',sum(r is not None for r in rows),'of',len(rows),'faces',len(F))
for r in rows:
    if r: print('R',[round(x,2) for x in r[0]],[round(x,2) for x in r[1]])
if SAVE and F:
    me=bpy.data.meshes.new('WS18_Morehead_W_eave_tile_skirt_UNVERIFIED'); me.from_pydata([tuple(v) for v in V],[],F); me.update()
    for p in me.polygons:
        if p.normal.z<0: p.flip()
    me.update()
    roof=bpy.data.objects['Morehead Hall roof (LiDAR)']
    me.materials.append(bpy.data.materials['Roof_tile_or_membrane'])
    if 'em_ringforce' in roof.data.attributes:
        at=roof.data.attributes['em_ringforce']; print('ATTR',at.domain,at.data_type)
        na=me.attributes.new('em_ringforce',at.data_type,at.domain)
        for d in na.data: d.value=1
    for p in me.polygons: p.use_smooth=False
    ob=bpy.data.objects.new('WS18_Morehead_W_eave_tile_skirt_UNVERIFIED',me)
    for c in roof.users_collection: c.objects.link(ob)
    bpy.ops.wm.save_mainfile(); print('SAVED')
