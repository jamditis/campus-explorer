# ws20: Life Hall wall top outline dips to 140.6-143 in places, leaving see-through gaps under the soffit (black jagged holes).
# Raise every top-outline vertex that sits below the soffit/roof directly above it up to 1 cm into that underside.
import bpy, bmesh, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
SAVE=os.environ.get('SAVE')=='1'
dg=bpy.context.evaluated_depsgraph_get()
names=[n for n in bpy.data.objects.keys() if n.startswith('Life Hall') and any(k in n.lower() for k in ('roof','soffit','eave','barrel'))]
print('ABOVE objs',names)
V=[];F=[];FO=[]
for n in names:
    ob=bpy.data.objects[n]
    if ob.type!='MESH': continue
    e=ob.evaluated_get(dg).to_mesh(); M=ob.matrix_world; b=len(V)
    V.extend(M@v.co for v in e.vertices)
    for p in e.polygons: F.append([b+i for i in p.vertices]); FO.append(n)
    ob.evaluated_get(dg).to_mesh_clear()
T=BVHTree.FromPolygons(V,F,all_triangles=False)
o=bpy.data.objects['Life Hall walls']; M=o.matrix_world; Mi=M.inverted()
bm=bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table()
top=set()
for e in bm.edges:
    if e.is_boundary and min((M@v.co).z for v in e.verts)>139.5: top.update(e.verts)
print('TOP verts',len(top))
uvl=bm.loops.layers.uv['facade']
import statistics
ofs=[l[uvl].uv.y-(M@l.vert.co).z for f in bm.faces for l in f.loops][:4000]
print('VZOFS median',statistics.median(ofs),'sd',statistics.pstdev(ofs))
moved=[]
for v in top:
    p=M@v.co
    loc,n,i,d=T.ray_cast(p+Vector((0,0,-0.05)),Vector((0,0,1)),6)
    if loc is None: continue
    tgt=loc.z-0.005
    if tgt-p.z>0.08:
        moved.append((round(p.x,1),round(p.y,1),round(p.z,2),round(tgt,2),FO[i][:30]))
        if SAVE:
            dz=tgt-p.z
            for l in v.link_loops: l[uvl].uv.y+=dz
            v.co=Mi@Vector((p.x,p.y,tgt))
print('MOVED',len(moved))
for m in sorted(moved,key=lambda m:m[2])[:60]: print('M',m)
if SAVE:
    bm.to_mesh(o.data); o.data.update(); o['ws20']='top outline raised to soffit/roof underside'
    bpy.ops.wm.save_mainfile(); print('SAVED')
