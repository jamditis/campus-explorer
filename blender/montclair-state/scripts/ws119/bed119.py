# ws119: terrain (WS113 fill / Terrain_LiDAR) poked green patches through the regraded WS116 E1/E2/W mulch beds; push it under.
import bpy, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
dg=bpy.context.evaluated_depsgraph_get()
def bv(o):
    e=o.evaluated_get(dg); me=e.to_mesh(); mw=o.matrix_world
    b=BVHTree.FromPolygons([tuple(mw@v.co) for v in me.vertices],[tuple(p.vertices) for p in me.polygons]); e.to_mesh_clear(); return b
BB=[bv(o) for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('WS116_Chapin_W_bed')]
def bedz(x,y):
    zs=[h[0].z for h in (b.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),150) for b in BB) if h[0] is not None]
    return min(zs) if zs else None
def probe():
    G=[bv(o) for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('Terrain_LiDAR','WS113_terrain'))]
    n=bad=0
    for i in range(-232*4,-205*4):
        for j in range(-205*4,-180*4):
            x=i/4; y=j/4; zb=bedz(x,y)
            if zb is None: continue
            n+=1
            if any(h[0] is not None and h[0].z>zb-0.003 for h in (g.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),150) for g in G)): bad+=1
    return n,bad
print('B119 before samples,poke',probe())
for nm in ('Terrain_LiDAR_DTM_1m','WS113_terrain_fan_fill'):
    o=next(o for o in bpy.data.objects if o.name.startswith(nm)); mw=o.matrix_world; inv=mw.inverted(); n=0
    for v in o.data.vertices:
        w=mw@v.co
        if -233<w.x<-204 and -206<w.y<-179:
            zs=[bedz(w.x+dx,w.y+dy) for dx in (-0.7,0,0.7) for dy in (-0.7,0,0.7)]
            zs=[z for z in zs if z is not None]
            if zs and w.z>min(zs)-0.10: w.z=min(zs)-0.10; v.co=inv@w; n+=1
    o.data.update(); print('B119',nm,'pushed',n)
dg.update()
print('B119 after samples,poke',probe())
SAVE=os.environ.get('SAVE','main')
if SAVE=='main': bpy.ops.wm.save_mainfile(); print('B119 SAVED main')
else: bpy.ops.wm.save_as_mainfile(filepath=SAVE,copy=True); print('B119 SAVED',SAVE)
