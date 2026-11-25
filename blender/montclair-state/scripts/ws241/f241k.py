# ws241 pass 4 (f241k): f241d flap applied to M3b's free S/SE/W edges W of the police building (x -398..-347, y -70..-16;
# probe241j: edge 0.35-1.0 m over the evaluated skirt 0.5 m out = the W57 back line and the diagonal band). 3 m flap to the
# skirt 3 m out + 0.03 (never above the edge). Ground only.
# W57 (+ W58 edge) flap (ws241): probe241e on ws241b: beside WS68's W edge (x -345, y -82..-25) the skirt's under-modifiers
# leave a 3.5 m flat trench 0.4-0.8 m under the outer skirt = the dark slot S of the police building. Extrude those free
# edges outward as a lawn flap: new edge verts at W m out, z = evaluated outer skirt there + 0.03 (flap rides over the
# trench and lands on the skirt). WS68: W 4.5 m (outer skirt sampled at 4-5 m). M3a W edge by the deck: W 3 m, only where
# the edge still stands > 5 cm over the skirt 0.5 m out. Ground only; no paving touched. Trench shape from probe; UNVERIFIED.
import bpy, bmesh, json
from mathutils import Vector
P=json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws241/probe241j.json'))
for name,L in P.items():
    o=bpy.data.objects.get(name)
    if o is None: print('F241K missing',name); continue
    ws=False; Wd=3.0
    SEL={}
    for idx,x,y,z,dx,dy,zs in L:
        if None in zs: continue
        if ws: zo=(zs[4]+zs[5])/2+0.03
        else:
            if z-zs[0]<=0.10 or x>-347.0: continue
            zo=min(z-0.02,zs[3]+0.03)
        SEL[idx]=(dx,dy,zo)
    M=o.matrix_world; Mi=M.inverted()
    bm=bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table()
    E=[e for e in bm.edges if e.is_boundary and e.verts[0].index in SEL and e.verts[1].index in SEL]
    src={v.index:v for e in E for v in e.verts}
    pos={tuple(round(c,5) for c in v.co):i for i,v in src.items()}
    r=bmesh.ops.extrude_edge_only(bm,edges=E)
    nv=[g for g in r['geom'] if isinstance(g,bmesh.types.BMVert)]
    n=0
    for v in nv:
        i=pos.get(tuple(round(c,5) for c in v.co))
        if i is None: continue
        dx,dy,zo=SEL[i]; p=M@v.co; p=Vector((p.x+dx*Wd,p.y+dy*Wd,zo)); v.co=Mi@p; n+=1
    bm.normal_update(); bm.to_mesh(o.data); o.data.update(); bm.free()
    print('F241K',name[:20],'edges',len(E),'flap verts',n,'of',len(nv),flush=True)
