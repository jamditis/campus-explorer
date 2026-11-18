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
