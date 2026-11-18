import collections
# ws126 UNIFY #19: pale chevrons E of the WS115 walk = Terrain_LiDAR_DTM_1m poking through the WS113 fan fill (ortho walk tone on the lawn).
# Push base Terrain verts that sit within 6 cm of / above the fan-fill top down to fan-z - 8 cm, only where the fan fill covers the vert and its ±1 m neighbours.
import bpy, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
X0,X1,Y0,Y1=-237,-221,-235,-217
dg=bpy.context.evaluated_depsgraph_get()
ff=bpy.data.objects['WS113_terrain_fan_fill_DTM1m_UNVERIFIEDgrade']; fe=ff.evaluated_get(dg); fm=fe.to_mesh()
ft=BVHTree.FromPolygons([ff.matrix_world@v.co for v in fm.vertices],[tuple(p.vertices) for p in fm.polygons]); fe.to_mesh_clear()
def fz(x,y):
    r=ft.ray_cast(Vector((x,y,300)),Vector((0,0,-1))); return None if r[0] is None else r[0].z
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; mw=T.matrix_world; mi=mw.inverted()
print('TERRAIN mods',[m.type for m in T.modifiers])
n=0; mx=0
for v in T.data.vertices:
    w=mw@v.co
    if not (X0<=w.x<=X1 and Y0<=w.y<=Y1): continue
    z0=fz(w.x,w.y)
    if z0 is None or w.z<z0-0.06: continue
    if any(fz(w.x+dx,w.y+dy) is None for dx in (-1.0,0,1.0) for dy in (-1.0,0,1.0)): continue
    nw=Vector((w.x,w.y,z0-0.08)); mx=max(mx,w.z-nw.z); v.co=mi@nw; n+=1
T.data.update()
print('M126d terrain verts pushed',n,'max drop',round(mx,3))
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('M126d SAVED')
bpy.context.view_layer.update()
X0,X1,Y0,Y1=-236,-222,-234,-218
dg=bpy.context.evaluated_depsgraph_get(); dg.update()
trees=[]
for o in bpy.context.scene.objects:
    if o.type!='MESH' or o.hide_render or o.name.startswith(('WS125_bed','WS126_bed','ShrubLeaf')): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]
    if max(v.x for v in bb)<X0 or min(v.x for v in bb)>X1 or max(v.y for v in bb)<Y0 or min(v.y for v in bb)>Y1: continue
    oe=o.evaluated_get(dg); me=oe.to_mesh(); mw=o.matrix_world
    vs=[mw@v.co for v in me.vertices]; ps=[tuple(p.vertices) for p in me.polygons]
    mats=[(me.materials[p.material_index].name if me.materials and p.material_index<len(me.materials) and me.materials[p.material_index] else '') for p in me.polygons]
    if ps: trees.append((o.name,BVHTree.FromPolygons(vs,ps),mats))
    oe.to_mesh_clear()
print('TREES',[t[0] for t in trees])
cnt=collections.Counter(); ex={}
x=X0
while x<=X1:
    y=Y0
    while y<=Y1:
        best=None
        for n,t,mats in trees:
            r=t.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))
            if r[0] is not None and (best is None or r[0].z>best[1]): best=(n,r[0].z,mats[r[2]])
        if best:
            k=best[0]+'|'+best[2]; cnt[k]+=1; ex.setdefault(k,[]).append((round(x,1),round(y,1),round(best[1],2)))
        y+=0.25
    x+=0.25
for n,c in cnt.most_common(): print('HIT',n,c,ex[n][:3])
