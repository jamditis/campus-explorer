# W60 (ws242): the dark saw-tooth along Lot 28S's W side seen from the air = M3a's raster (1 m stair-step) W edge standing
# 0.2-2.9 m over the context skirt, which WS234_skirt_under_M3a_ext pulls down into a trench right beside the edge
# (probe242d_fix: evaluated skirt 0.5 m out is 0.2-2.9 m under the edge, 6 m out it is back within -1.0..+1.1 m of it).
# Fix (f241d pattern): extrude those free edges outward as a lawn flap along ONE fixed outward direction (-0.95, 0.31) =
# perpendicular to the edge's overall run, so stair-step corners don't make crossing flap faces; new verts 6 m out at the
# evaluated skirt z there + 0.03. Only verts y 590..704 where the edge stands > 0.1 m over the skirt 0.5 m out and the
# ground 3 m out is the skirt (2 verts over Lot 28S paving skipped). LiDAR edge, paving and skirt untouched. UNVERIFIED design (fill bank).
import bpy, bmesh, json
from mathutils import Vector
P=json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws242/probe242d_fix.json'))
for name,L in P.items():
    o=bpy.data.objects[name]; Wd=6.0; D=Vector((-0.95,0.31,0)).normalized()
    SEL={}
    for idx,x,y,z,dx,dy,zs,h in L:
        if not (590<=y<=704) or None in zs or not (h or '').startswith('Context_skirt'): continue
        if z-zs[0]<=0.1: continue
        SEL[idx]=zs[6]+0.03
    M=o.matrix_world; Mi=M.inverted()
    bm=bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table()
    E=[e for e in bm.edges if e.is_boundary and e.verts[0].index in SEL and e.verts[1].index in SEL]
    src={v.index:v for e in E for v in e.verts}
    pos={tuple(round(c,5) for c in v.co):i for i,v in src.items()}
    r=bmesh.ops.extrude_edge_only(bm,edges=E)
    nv=[g for g in r['geom'] if isinstance(g,bmesh.types.BMVert)]
    n=0; mx=0
    for v in nv:
        i=pos.get(tuple(round(c,5) for c in v.co))
        if i is None: continue
        p=M@v.co; mx=max(mx,abs(p.z-SEL[i])); p=Vector((p.x+D.x*Wd,p.y+D.y*Wd,SEL[i])); v.co=Mi@p; n+=1
    bm.normal_update(); bm.to_mesh(o.data); o.data.update(); bm.free()
    print('F242B',name[:24],'sel',len(SEL),'edges',len(E),'flap verts',n,'of',len(nv),'max drop',round(mx,2),flush=True)
