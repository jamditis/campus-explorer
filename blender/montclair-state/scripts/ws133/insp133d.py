import bpy, math
from mathutils import Vector
X0,X1,Y0,Y1=-140,-112,-275,-258
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[v.x for v in bb]; ys=[v.y for v in bb]
    if any(math.isnan(q) for q in xs+ys) or max(xs)<X0 or min(xs)>X1 or max(ys)<Y0 or min(ys)>Y1: continue
    if len(o.data.polygons)>300000 and not o.name.startswith('Terrain'): print('BIG',o.name); continue
    mw=o.matrix_world; zc=[]; xy=[]
    for p in o.data.polygons:
        c=mw@p.center
        if X0<c.x<X1 and Y0<c.y<Y1: zc.append(c.z); xy.append((c.x,c.y))
    if zc: print('OBJ %-60s n=%d z%.2f..%.2f x%.1f..%.1f y%.1f..%.1f %s'%(o.name,len(zc),min(zc),max(zc),min(a for a,b in xy),max(a for a,b in xy),min(b for a,b in xy),max(b for a,b in xy),[m.name for m in o.data.materials if m][:2]))
import collections
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; mw=t.matrix_world; cnt=collections.Counter(); zs=[]
for p in t.data.polygons:
    c=mw@p.center
    if -135<c.x<-110 and -270<c.y<-225: cnt[t.data.materials[p.material_index].name if t.data.materials[p.material_index] else None]+=1
print('OBJ TERRAIN mats',cnt.most_common(6))
mods=[(m.name,m.type) for m in t.modifiers]; print('OBJ TERRAIN mods',mods)
w=bpy.data.objects['WS133_Russ_E_walk_concrete_LiDAR2023int_UNVERIFIEDjoints']; zz=[(w.matrix_world@v.co).z for v in w.data.vertices]; print('OBJ WALK z %.2f..%.2f'%(min(zz),max(zz)))
dg=bpy.context.evaluated_depsgraph_get()
from mathutils.bvhtree import BVHTree
import bmesh
e=t.evaluated_get(dg); m=e.to_mesh(); bm=bmesh.new(); bm.from_mesh(m); bm.transform(mw); T=BVHTree.FromBMesh(bm)
for (x,y) in [(-122.5,-262),(-121.5,-255),(-120.5,-250),(-119.5,-245),(-118.5,-240),(-117.5,-235),(-116,-245),(-112,-250),(-128,-266),(-133,-266)]:
    h=T.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))
    print('OBJ EVALTERR %.1f %.1f z=%s'%(x,y,'%.2f'%h[0].z if h[0] else None))
