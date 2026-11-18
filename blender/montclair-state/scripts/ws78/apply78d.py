# ws78d: island/paint verts along the old WS68|Terrain seam (x -252..-246.5) that kept the old high drape (terrain ray missed west of x -249 in ws78a) -> re-drape onto the lot surface below.
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
LOTS=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('WS75_sprague_lot_asphalt','WS76_accessible_lot_asphalt','WS74_cogen_lot'))]
G=[o for o in bpy.data.objects if o.name.startswith('WS68_RHD_ground')][0]
def bvh(o):
    mw=o.matrix_world; return BVHTree.FromPolygons([mw@v.co for v in o.data.vertices],[tuple(f.vertices) for f in o.data.polygons])
TB=[bvh(o) for o in LOTS]; GB=bvh(G)
def lot(x,y):
    zs=[t.ray_cast(Vector((x,y,400)),Vector((0,0,-1)),1000)[0] for t in TB]; zs=[h.z for h in zs if h]
    if zs: return max(zs)
    h=GB.ray_cast(Vector((x,y,400)),Vector((0,0,-1)),1000)[0]; return h.z+0.04 if h else None
X0,X1=-252.5,-246.5
for o in bpy.data.objects:
    if o.type!='MESH': continue
    isl=o.name.startswith('WS77_lot_median_island'); pnt=o.name.startswith('WS76_lot_stall_paint')
    if not (isl or pnt): continue
    me=o.data; mw=o.matrix_world; mi=mw.inverted()
    top=set(); 
    for f in me.polygons:
        if f.material_index==1: top.update(f.vertices)
    nb=[[] for _ in me.vertices]
    for e in me.edges: a,b=e.vertices; nb[a].append(b); nb[b].append(a)
    W=[mw@v.co for v in me.vertices]; k=0
    for i,p in enumerate(W):
        if not (X0<p.x<X1 and -100<p.y<-78): continue
        L=lot(p.x,p.y)
        if L is None: continue
        o_=p.z-L
        if pnt:
            if o_>0.06: z=L+0.015
            else: continue
        else:
            if o_<=0.2: continue
            if i in top: z=L+0.11
            elif any(W[j].z>p.z+0.1 for j in nb[i]): z=L-0.06
            else: z=L+0.15
        me.vertices[i].co=mi@Vector((p.x,p.y,z)); k+=1
    me.update(); print('WS78D redraped',o.name[:45],k,flush=True)
