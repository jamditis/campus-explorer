# ws119 UNIFY #23: terrace/landing slab stopped at constant x -209.1 but the Chapin W facade runs NNE
# (x -209.0 at y -198 -> -206.1 at y -186; W low wing -204.5 at y -185 -> -203.75 at y -182), leaving a
# 0-5.4 m strip of trenched terrain + buried Footpaths 0.4-0.9 m below the terrace = the dark crease.
# Fill the strip at landing level to the facade (+0.15 m into the wall), retire Footpaths faces under it,
# push terrain under it.
import bpy, bmesh, numpy as np, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ZL=124.77; XW=-209.1; YS=-201.25; YN=-182.0
dg=bpy.context.evaluated_depsgraph_get()
def bv(o):
    e=o.evaluated_get(dg); me=e.to_mesh(); mw=o.matrix_world
    b=BVHTree.FromPolygons([tuple(mw@v.co) for v in me.vertices],[tuple(p.vertices) for p in me.polygons]); e.to_mesh_clear(); return b
B=[bv(o) for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('WS107_Chapin')]
def xf(y):
    xs=[h[0].x for h in (b.ray_cast(Vector((-215,y,125.6)),Vector((1,0,0)),30) for b in B) if h[0] is not None]
    return min(xs) if xs else None
ys=list(np.arange(YS,YN+0.001,0.25)); rows=[]
for y in ys:
    x=xf(y)
    if x is None or x<=XW+0.02: rows.append((y,XW+0.02)); continue
    rows.append((y,min(x+0.15,-203.0)))
print('M119 facade rows',[(round(y,2),round(x,2)) for y,x in rows][::8])
slab=next(o for o in bpy.data.objects if o.name.startswith('WS117_Chapin_W_entrance_landing'))
me=bpy.data.meshes.new('WS119_terrace_E_infill'); ob=bpy.data.objects.new('WS119_Chapin_W_terrace_E_infill_to_facade_LiDAR124.77_UNIFY23',me)
for c in slab.users_collection: c.objects.link(ob)
me.materials.append(slab.data.materials[0])
bm=bmesh.new(); R=[]
for y,x1 in rows:
    R.append([bm.verts.new(c) for c in ((XW,y,ZL-1.2),(x1,y,ZL-1.2),(x1,y,ZL),(XW,y,ZL))])
for r0,r1 in zip(R[:-1],R[1:]):
    for i in range(4):
        j=(i+1)%4; bm.faces.new((r0[i],r0[j],r1[j],r1[i]))
bm.faces.new(R[0][::-1]); bm.faces.new(R[-1]); bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
bm.to_mesh(me); bm.free()
def inside(x,y,m=0.0):
    if y<YS-m or y>YN+m: return False
    k=min(range(len(rows)),key=lambda i:abs(rows[i][0]-y)); return XW-0.6-m<=x<=rows[k][1]+m
# landing W edge xr(y) for footpath retire test (landing + infill footprint)
xr=lambda y: -213.4 if y<-196.65 else -213.3+(min(y,-184.0)+196.65)*(2.3/12.65)
def foot(x,y): return YS<=y<=YN and xr(y)-0.1<=x and inside(x,y,0.0) or (YS<=y<=YN and xr(y)-0.1<=x<=XW)
fp=bpy.data.objects['Footpaths_OSM']; b=bmesh.new(); b.from_mesh(fp.data); fw=fp.matrix_world
kill=[f for f in b.faces if (lambda c: foot(c.x,c.y) and c.z>ZL-1.0)(fw@f.calc_center_median())]
bmesh.ops.delete(b,geom=kill,context='FACES'); b.to_mesh(fp.data); b.free(); fp.data.update(); print('M119 Footpaths faces retired',len(kill))
nt=0
for nm in ('Terrain_LiDAR_DTM_1m','WS113_terrain_fan_fill'):
    o=next(o for o in bpy.data.objects if o.name.startswith(nm)); mw=o.matrix_world; inv=mw.inverted(); n=0
    for v in o.data.vertices:
        w=mw@v.co
        if inside(w.x,w.y,0.6) and w.z>ZL-0.10:
            w.z=ZL-0.10; v.co=inv@w; n+=1
    o.data.update(); print('M119',nm,'verts pushed',n); nt+=n
SAVE=os.environ.get('SAVE','main')
if SAVE=='main': bpy.ops.wm.save_mainfile(); print('M119 SAVED main')
else: bpy.ops.wm.save_as_mainfile(filepath=SAVE,copy=True); print('M119 SAVED',SAVE)
