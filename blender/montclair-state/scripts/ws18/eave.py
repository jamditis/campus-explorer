# ws18: Morehead west eave — LiDAR roof ends ~at the wall, separate soffit/fascia sits 0.8 m out and lower, leaving a gap
# where the sunlit wall top shows as a pale lens. Extend the roof's west boundary verts down-slope to the fascia line.
import bpy,bmesh,os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SAVE=os.environ.get('SAVE')=='1'
sc=bpy.context.scene; dg=bpy.context.evaluated_depsgraph_get()
roof=bpy.data.objects['Morehead Hall roof (LiDAR)']
print('mods',[m.type for m in roof.modifiers], 'users',roof.data.users)
def bvh(names):
    V=[];F=[]
    for n in names:
        o=bpy.data.objects[n]; e=o.evaluated_get(dg).to_mesh(); M=o.matrix_world; b=len(V)
        V.extend(M@v.co for v in e.vertices); F.extend([b+i for i in p.vertices] for p in e.polygons); o.evaluated_get(dg).to_mesh_clear()
    return BVHTree.FromPolygons(V,F,all_triangles=False)
EAVE=bvh(['Morehead Hall eave soffit + fascia + rafter tails','Morehead Hall barrel tile eave course'])
OUT=Vector((-0.97,0.24,0)).normalized(); P0=Vector((-40.03,-56.5,0)); SL=0.55/0.83
M=roof.matrix_world; Mi=M.inverted()
bm=bmesh.new(); bm.from_mesh(roof.data); bm.verts.ensure_lookup_table()
moved=0; Ls=[]
for v in bm.verts:
    if not v.is_boundary: continue
    w=M@v.co
    if not (-66<w.y<-45 and w.z>143.8): continue
    s=(Vector((w.x,w.y,0))-P0).dot(OUT)
    if not (-0.7<s<0.6): continue
    tmax=None;ztop=None
    t=0.0
    while t<1.6:
        o=Vector((w.x,w.y,0))+OUT*t; o.z=w.z+1
        loc,n,i,d=EAVE.ray_cast(o,Vector((0,0,-1)),3)
        if loc is not None: tmax=t; ztop=loc.z
        t+=0.05
    if tmax is None or tmax<0.1: continue
    L=tmax+0.04
    nz=w.z-SL*L
    nw=Vector((w.x,w.y,0))+OUT*L; nw.z=max(nz,ztop-0.03)
    Ls.append((round(s,2),round(L,2),round(w.z,2),round(nw.z,2),round(ztop,2)))
    if SAVE: v.co=Mi@nw
    moved+=1
print('MOVED',moved)
for x in Ls[:60]: print('L',x)
if SAVE:
    bm.to_mesh(roof.data); roof.data.update(); bpy.ops.wm.save_mainfile(); print('SAVED')
