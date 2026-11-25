# W57 + W58 edge (ws241): free ground edges standing over the lower raw Context skirt read as dark slots/cliffs.
# probe241b (raw skirt = skirt evaluated with its *_under_* modifiers off): WS68 W edge x~-345, y -80..-26 stands 0.33-1.16 m
# over the skirt (W57, S of the police building); M3a W edge near the NJT deck y 970..1068 stands 0.1-0.9 m over it (W58).
# Fix: lower those boundary verts to raw skirt - 0.02 (ground continues; the skirt hides the seam), 2-ring feather
# (x0.55, x0.2). Never raises; cap 1.2 m. The M3a notch S of the deck SW corner (y < 970) is filled by f241c instead.
import bpy, bmesh, json
from mathutils import Vector
P=json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws241/probe241b.json'))
RULE={'M3a':lambda x,y: y>=970.0, 'WS68':lambda x,y: y<=-25.0 and x<-343.0}
for name,L in P.items():
    o=bpy.data.objects.get(name)
    if o is None: print('F241B missing',name); continue
    key='M3a' if name.startswith('M3a') else 'WS68'
    M=o.matrix_world; Mi=M.inverted(); bm=bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table()
    D={}; mx=0
    for idx,x,y,z0,zs in L:
        if not RULE[key](x,y): continue
        sk=[z for z,n in zs if n=='skirt']
        if not sk: continue
        oth=max(z for z,n in zs)
        v=bm.verts[idx]; p=M@v.co
        t=sk[0]-0.02
        if oth>sk[0]+0.02: continue   # another ground (M3b) meets this edge: leave it
        if p.z-t<=0.03 or p.z-t>1.2: continue
        D[idx]=t-p.z; mx=max(mx,p.z-t)
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
    print('F241B',key,'edge verts lowered',len(D),'max',round(mx,2),'feathered',len(done)-len(D),flush=True)
