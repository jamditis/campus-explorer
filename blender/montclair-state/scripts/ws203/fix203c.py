# ws203 W13c: the W13 "dark lens" (0432 close-up) is a LAWN LIP: the outer edges of the small Lot 3 S-end lawn fill sheets (WS190b corner fill,
# WS191c/WS192 fillets, WS191b gap fill) stand a few cm above the WS163/WS110 lawn they lap over -> a shadowed overhang at grazing angles.
# Designer call: one continuous lawn; a fill sheet feathers down and tucks 4 mm under the lawn it meets (no lip). Lawn only (paving untouched):
# exposed boundary verts (not within 0.2 m of the WS170b strip / Lot 3 paving, which they must keep meeting) with an underlying lawn surface 3 mm-15 cm below -> z_u - 4 mm; their interior 1-ring neighbours lowered by half that.
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
BX=(-306.5,-296.0,-239.5,-232.0)
LS=('WS191c_Lot3_S_strip_back',)   # ws203: verified on WS191c only (WS192/WS191b lips not render-checked)
LAWN=[o for o in bpy.data.objects if o.type=='MESH' and not o.hide_render and o.material_slots and o.material_slots[0].material and o.material_slots[0].material.name.startswith('COLE_lawn')]
def inb(o):
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[v.x for v in bb]; ys=[v.y for v in bb]
    return not (max(xs)<BX[0] or min(xs)>BX[1] or max(ys)<BX[2] or min(ys)>BX[3])
LAWN=[o for o in LAWN if inb(o)]
def bvh(objs):
    V=[];F=[]
    for o in objs:
        mw=o.matrix_world; b=len(V); V+=[mw@v.co for v in o.data.vertices]; F+=[tuple(b+i for i in p.vertices) for p in o.data.polygons]
    return BVHTree.FromPolygons(V,F)
STR=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('WS170b_Lot3_S_end_curb','WS162_Lot3_asphalt','WS162_Lot3_S_end_apron','WS163_Lot3_aisle_S_drive'))]
TS=bvh(STR)
tot=0; nskip=0
for pre in LS:
    o=[x for x in LAWN if x.name.startswith(pre)]
    if not o: print('F203c missing',pre); continue
    o=o[0]; T=bvh([x for x in LAWN if x is not o]); mw=o.matrix_world; mi=mw.inverted()
    bm=bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table()
    drop={}
    for v in bm.verts:
        if not v.is_boundary: continue
        p=mw@v.co
        if not (BX[0]<p.x<BX[1] and BX[2]<p.y<BX[3]): continue
        nr=TS.find_nearest(p)
        if nr[0] is not None and nr[3]<0.2 and nr[0].z>p.z-0.03: nskip+=1; continue   # verts that meet the strip/paving keep their height
        up=T.ray_cast(Vector((p.x,p.y,p.z+0.002)),Vector((0,0,1)),0.5)
        if up[0] is not None: continue   # covered by another lawn sheet
        h=T.ray_cast(Vector((p.x,p.y,p.z+0.001)),Vector((0,0,-1)),0.16)
        if h[0] is None: continue
        lip=p.z-h[0].z
        if 0.003<lip<0.15: drop[v.index]=lip+0.004
    ring={}
    for i,dz in drop.items():
        for e in bm.verts[i].link_edges:
            w=e.other_vert(bm.verts[i])
            if w.index not in drop: ring.setdefault(w.index,[]).append(dz*0.5)
    mx=0
    for i,dz in list(drop.items())+[(k,sum(v)/len(v)) for k,v in ring.items()]:
        vv=o.data.vertices[i]; p=mw@vv.co; p.z-=dz; vv.co=mi@p; mx=max(mx,dz)
    o.data.update(); bm.free(); tot+=len(drop)
    print('F203c',o.name[:30],'lip verts',len(drop),'ring',len(ring),'max drop %.3f'%mx,flush=True)
print('F203c total',tot,'kept at paving',nskip,flush=True)
