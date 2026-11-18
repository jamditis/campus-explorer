# ws19: rebuild WS18 skirt so it ends at the inner edge of the barrel tile course instead of burying it (was 3-8 cm above it).
import bpy,os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SAVE=os.environ.get('SAVE')=='1'
dg=bpy.context.evaluated_depsgraph_get()
def bvh(names):
    V=[];F=[]
    for n in names:
        o=bpy.data.objects[n]; e=o.evaluated_get(dg).to_mesh(); M=o.matrix_world; b=len(V)
        V.extend(M@v.co for v in e.vertices); F.extend([b+i for i in p.vertices] for p in e.polygons); o.evaluated_get(dg).to_mesh_clear()
    return BVHTree.FromPolygons(V,F,all_triangles=False)
BC=bvh(['Morehead Hall barrel tile eave course'])
ROOF=bvh(['Morehead Hall roof (LiDAR)'])
OUT=Vector((-0.97,0.24,0)).normalized(); AL=Vector((0.24,0.97,0)).normalized(); P0=Vector((-40.03,-56.5,0))
def dz(B,p):
    h,_,_,_=B.ray_cast(Vector((p.x,p.y,160)),Vector((0,0,-1)),40); return h.z if h else None
rows=[]; a=-14.0
while a<=14.0:
    base=P0+AL*a; i0=base+OUT*(-0.30); hz=dz(ROOF,i0)
    if hz is None or hz<144.4: rows.append(None); a+=0.5; continue
    tB=None; t=0.0
    while t<1.2:
        if dz(BC,base+OUT*t) is not None: tB=t; break
        t+=0.02
    if tB is None: rows.append(None); a+=0.5; continue
    te=tB+0.04; bz=dz(BC,base+OUT*te) or dz(BC,base+OUT*tB)
    ou=base+OUT*te; mi=base+OUT*(tB-0.06); mz=dz(ROOF,mi)
    if mz is None: mz=hz-0.66*(tB+0.24)
    rows.append((Vector((i0.x,i0.y,hz+0.015)),Vector((mi.x,mi.y,mz+0.015)),Vector((ou.x,ou.y,bz-0.02)),tB)); a+=0.5
V=[];F=[]
for k in range(len(rows)-1):
    r0,r1=rows[k],rows[k+1]
    if r0 is None or r1 is None: continue
    b=len(V); V+=[r0[0],r0[1],r1[1],r1[0]]; F.append([b,b+1,b+2,b+3])
    b=len(V); V+=[r0[1],r0[2],r1[2],r1[1]]; F.append([b,b+1,b+2,b+3])
print('ROWS',sum(r is not None for r in rows),'faces',len(F))
for r in rows[::6]:
    if r: print('R tB',round(r[3],2),[round(x,2) for x in r[0]],[round(x,2) for x in r[1]],[round(x,2) for x in r[2]])
if SAVE and F:
    old=bpy.data.objects['WS18_Morehead_W_eave_tile_skirt_UNVERIFIED']; me=old.data
    me.clear_geometry(); me.from_pydata([tuple(v) for v in V],[],F); me.update()
    for p in me.polygons:
        if p.normal.z<0: p.flip()
        p.use_smooth=False
    if 'em_ringforce' not in me.attributes:
        roof=bpy.data.objects['Morehead Hall roof (LiDAR)']
        if 'em_ringforce' in roof.data.attributes:
            at=roof.data.attributes['em_ringforce']; me.attributes.new('em_ringforce',at.data_type,at.domain)
    if 'em_ringforce' in me.attributes:
        for d in me.attributes['em_ringforce'].data: d.value=1
    me.update(); old['ws19']='outer edge trimmed to barrel course inner edge'
    bpy.ops.wm.save_mainfile(); print('SAVED')
