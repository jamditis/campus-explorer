# ws224h: the Kasser S walk edge jogs at the WS72/WS71 seam (x -243): WS72's S edge runs 0.37-0.50 m back from the curb,
# WS71's W end only 0.11-0.24 m, so the verge strip kinks. Both walks are otherwise traced 0.30 m back (ortho 2020), so the
# edge verts at x -244..-242 are moved HORIZONTALLY (z kept, skirt bottom verts with them) onto the 0.30 m offset line.
import bpy
from mathutils import Vector
from mathutils.geometry import intersect_point_line
B=bpy.data.objects['WS27_CollegeAve_curb_left_UNVERIFIED']; MB=B.matrix_world
bk=[MB@B.data.vertices[6*k+3].co for k in range(30)]; fr=[MB@B.data.vertices[6*k+1].co for k in range(30)]
def proj(p):
    best=None
    for k in range(29):
        a,b=bk[k],bk[k+1]; q,t=intersect_point_line(p.xy.to_3d(),a.xy.to_3d(),b.xy.to_3d()); t=min(max(t,0),1)
        q=a.lerp(b,t); d=(p.xy-q.xy).length
        if best is None or d<best[0]:
            n=(q-fr[k].lerp(fr[k+1],t)); n.z=0; best=(d,q,n.normalized())
    return best
OFF=0.30
for nm,x0,x1 in (('WS72_Kasser_SW_RHD_core_sidewalk_landing',-244.01,-242.99),('WS71_Kasser_S_sidewalk',-243.01,-241.99)):
    o=[o for o in bpy.data.objects if o.name.startswith(nm)][0]; M=o.matrix_world; MI=M.inverted(); R=M.to_3x3(); me=o.data
    cnt={}
    for p in me.polygons:
        if (R@p.normal).z>0.3:
            for e in p.edge_keys: cnt[e]=cnt.get(e,0)+1
    bv=set(i for e,c in cnt.items() if c==1 for i in e)
    for i in sorted(bv):
        w=M@me.vertices[i].co
        if not (x0<=w.x<=x1 and w.y<-52.6): continue
        d,q,n=proj(w)
        if d>0.7 or abs(d-OFF)<0.02: continue
        tgt=q.xy+n.xy*OFF
        mates=[v for v in me.vertices if ((M@v.co).xy-w.xy).length<1e-3]
        for v in mates:
            u=M@v.co; u.x,u.y=tgt.x,tgt.y; v.co=MI@u
        print('F224H %s v%d gap %.2f -> %.2f m (%d verts)'%(nm[:4],i,d,OFF,len(mates)),flush=True)
    me.update()
