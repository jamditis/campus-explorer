import bpy,os,math
from mathutils.bvhtree import BVHTree
from mathutils.kdtree import KDTree
from mathutils import Vector
pre=('WS74_cogen_lot_asphalt','WS75_sprague_lot_asphalt','WS76_accessible_lot_asphalt','WS80_sprague_lot_fill','WS79_lot_E_patch','WS81_lot_seam_underlay','WS94_lot_slit')
O=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(pre)]
for o in O: print("P94S mods",o.name[:30],[m.type for m in o.modifiers])
B={}
for o in O:
    mw=o.matrix_world; B[o.name]=BVHTree.FromPolygons([mw@v.co for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons])
RL=0.6; tot=0
for o in O:
    if o.modifiers or o.name.startswith(('WS94','WS81')): continue
    me=o.data; mw=o.matrix_world; imw=mw.inverted()
    cnt={}
    for e in me.edges: pass
    ef={}
    for p in me.polygons:
        for k in p.edge_keys: ef[k]=ef.get(k,0)+1
    bnd=set()
    for k,c in ef.items():
        if c==1: bnd.update(k)
    W=[mw@v.co for v in me.vertices]
    moved={}
    for i in bnd:
        v=W[i]; best=None
        for n,t in B.items():
            if n==o.name: continue
            h=t.ray_cast(Vector((v.x,v.y,v.z-0.004)),Vector((0,0,-1)),0.16)
            if h[0] and (best is None or h[0].z>best): best=h[0].z
        if best is not None:
            g=v.z-best
            if 0.008<g<=0.06: moved[i]=-(g-0.003)
    if not moved: continue
    kd=KDTree(len(moved))
    for j,(i,dz) in enumerate(moved.items()): kd.insert(Vector((W[i].x,W[i].y,0)),j)
    kd.balance(); keys=list(moved.items())
    n=0
    for i,v in enumerate(W):
        if i in moved: dz=moved[i]
        else:
            if i in bnd: continue
            co,j,d=kd.find(Vector((v.x,v.y,0)))
            if d>RL: continue
            dz=keys[j][1]*(1-d/RL)
        me.vertices[i].co=imw@Vector((v.x,v.y,v.z+dz)); n+=1
    me.update(); tot+=n
    print("P94S",o.name[:30],"bnd moved",len(moved),"verts",n,"max",round(min(moved.values()),3))
print("P94S total",tot)
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print("P94S SAVED")
