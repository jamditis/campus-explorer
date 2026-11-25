# ws241 pass 3 (f241f): RAISE the f241c notch fill's free outer edge (0.1-0.5 m UNDER the raw skirt -> skirt lip cast a dark band) to raw skirt + 0.02, 2-ring feather on fill verts only. Derived from f241e (pass 2): same as f241b on probe241f.json: outer free edge of the f241c notch fill (M3a) and M3b's S edge W of the police building (W57 back line, 1.4 m over the skirt); cap 1.5 m.
# W57 + W58 edge (ws241): free ground edges standing over the lower raw Context skirt read as dark slots/cliffs.
# probe241b (raw skirt = skirt evaluated with its *_under_* modifiers off): WS68 W edge x~-345, y -80..-26 stands 0.33-1.16 m
# over the skirt (W57, S of the police building); M3a W edge near the NJT deck y 970..1068 stands 0.1-0.9 m over it (W58).
# Fix: lower those boundary verts to raw skirt - 0.02 (ground continues; the skirt hides the seam), 2-ring feather
# (x0.55, x0.2). Never raises; cap 1.2 m. The M3a notch S of the deck SW corner (y < 970) is filled by f241c instead.
import bpy, bmesh, json
from mathutils import Vector
P=json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws241/probe241f.json'))
RULE={'M3a':lambda x,y: True, 'M3b':lambda x,y: False}
for name,L in P.items():
    o=bpy.data.objects.get(name)
    if o is None: print('F241F missing',name); continue
    key=name[:3]
    M=o.matrix_world; Mi=M.inverted(); bm=bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table()
    D={}; mx=0
    COVER=None
    if key=='M3a':
        from mathutils.bvhtree import BVHTree
        NPV,NPF=963,892   # f241c notch-fill verts/faces are the last ones appended to M3a
        nv0=len(o.data.vertices)-NPV; nf0=len(o.data.polygons)-NPF
        COVER=BVHTree.FromPolygons([M@v.co for v in o.data.vertices],[o.data.polygons[i].vertices[:] for i in range(nf0)])
    for idx,x,y,z0,zs in L:
        if not RULE[key](x,y): continue
        sk=[z for z,n in zs if n=='skirt']
        if not sk: continue
        oth=max(z for z,n in zs)
        v=bm.verts[idx]; p=M@v.co
        if COVER is not None:
            if idx<nv0: continue   # original M3a edge, now covered by the notch fill
            h=COVER.ray_cast(p+Vector((0,0,-0.5)),Vector((0,0,1)),1.0)
            if h[0] is not None: continue   # fill vert tucked under original M3a
        t=sk[0]-0.02
        if oth>sk[0]+0.02: continue   # another ground (M3b) meets this edge: leave it
        t=sk[0]+0.02
        if t-p.z<=0.03 or t-p.z>0.8: continue
        D[idx]=t-p.z; mx=max(mx,t-p.z)
    ring=dict(D); done=set(D)
    for fac in (0.55,0.2):
        nxt={}
        for i in ring:
            for e in bm.verts[i].link_edges:
                j=e.other_vert(bm.verts[i]).index
                if j in done: continue
                nxt.setdefault(j,[]).append(ring[i])
        ring={j:fac*sum(v)/len(v)/ (0.55 if fac==0.2 else 1.0) for j,v in nxt.items()}
        # ring values: ring1 = 0.55*mean(edge deltas); ring2 = 0.2*mean(edge deltas) (rescaled from ring1)
        for j,dl in ring.items():
            p=M@bm.verts[j].co; p.z+=dl; bm.verts[j].co=Mi@p
        done|=set(ring)
    for i,dl in D.items():
        p=M@bm.verts[i].co; p.z+=dl; bm.verts[i].co=Mi@p
    bm.to_mesh(o.data); o.data.update(); bm.free()
    print('F241F',key,'edge verts raised',len(D),'max',round(mx,2),'feathered',len(done)-len(D),flush=True)
