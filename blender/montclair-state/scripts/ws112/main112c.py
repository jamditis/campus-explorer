import bpy, numpy as np, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def bvh_of(o):
    me=o.data; mw=o.matrix_world
    return BVHTree.FromPolygons([tuple(mw@v.co) for v in me.vertices],[tuple(p.vertices) for p in me.polygons if p.normal.z>0.3 or True])
O=lambda p: next(o for o in bpy.data.objects if o.name.startswith(p))
strips=[O('WS112_CollegeAve_S_E_walk_N_brick'),O('WS111_CollegeAve_S_E_walk'),O('WS112_W_branch_walk')]
# top-only BVH (faces with normal z>0.5)
BV=[]
for o in strips:
    mw=o.matrix_world; me=o.data
    BV.append(BVHTree.FromPolygons([tuple(mw@v.co) for v in me.vertices],[tuple(p.vertices) for p in me.polygons if abs(p.normal.z)>0.5]))
def hit(x,y):
    z=None
    for b in BV:
        h=b.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),150)
        if h[0] is not None: z=h[0].z if z is None else max(z,h[0].z)
    return z
X0,X1,Y0,Y1=-288,-228,-256,-226
cands=[]
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render: continue
    if o.name.startswith(('WS111_','WS112_','WS110_CollegeAve','WS102_','WS103_','T_','Roads_OSM','Footpaths_OSM','Context_skirt','WS110_NormalAve')): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[v.x for v in bb]; ys=[v.y for v in bb]
    if max(xs)<X0 or min(xs)>X1 or max(ys)<Y0 or min(ys)>Y1: continue
    if len(o.data.vertices)>2_000_000: continue
    cands.append(o)
print('E112 cands',[o.name for o in cands])
DIRS=[(math.cos(a),math.sin(a)) for a in np.linspace(0,2*math.pi,12,endpoint=False)]
for o in cands:
    me=o.data; mw=o.matrix_world; mi=mw.inverted(); nc=0; nl=0
    for v in me.vertices:
        p=mw@v.co
        if not (X0<p.x<X1 and Y0<p.y<Y1): continue
        zc=None
        for r in (0,0.35,0.7):
            for dx,dy in (DIRS if r else [(0,0)]):
                z=hit(p.x+dx*r,p.y+dy*r)
                if z is not None and z>p.z-1.5: zc=z if zc is None else min(zc,z)
            if zc is not None: break
        if zc is not None:
            t=zc-0.08
            if p.z>t: p.z=t; v.co=mi@p; nc+=1
            continue
        best=None
        for r in (1.0,1.4,1.8):
            for dx,dy in DIRS:
                z=hit(p.x+dx*r,p.y+dy*r)
                if z is not None and z>p.z-0.6: best=(r,z if best is None else min(best[1],z)) if best is None or best[0]==r else best
            if best: break
        if best:
            r,ze=best; ze-=0.03
            if p.z<ze: w=1-(r-0.7)/1.3; p.z+= (ze-p.z)*max(0,min(1,w)); v.co=mi@p; nl+=1
    me.update(); print('E112c',o.name,'cap',nc,'lift',nl)
bpy.ops.wm.save_mainfile(); print('E112 SAVED')
