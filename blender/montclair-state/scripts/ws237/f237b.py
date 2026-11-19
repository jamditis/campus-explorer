# ws237 self-review: one dark speck stayed at PK's north tip in the oblique. Ray-identify: PK's own surface, faces at nz 0.42
# around (-318, 271) rising to 119.6 m = spikes left by f236a, which skipped 19 PK verts near Ballast 0 / rail ties, so they
# kept their old height while their neighbours feathered down to the LiDAR. Fix: PK verts in the seam zone (x -345..-285,
# y 150..305) standing > 0.6 m above the mean of their edge neighbours go to that mean (2 passes), then 2 passes at > 0.3 m in the
# north-tip box only (x -330..-300, y 255..300). Ground only.
import bpy, bmesh
o=bpy.data.objects['PK_Feliciano_west_DTM_fill_UNVERIFIED']; mw=o.matrix_world
bm=bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table(); tot=set(); mx=0
for ps in range(4):
    mv=[]
    for v in bm.verts:
        w=mw@v.co
        if not (-345<w.x<-285 and 150<w.y<305): continue
        nb=[e.other_vert(v) for e in v.link_edges]
        if len(nb)<3: continue
        m=sum(n.co.z for n in nb)/len(nb)
        if v.co.z-m>(0.6 if ps<2 else 0.3) and (ps<2 or (-330<w.x<-300 and 255<w.y<300)): mv.append((v,m))
    for v,m in mv:
        mx=max(mx,v.co.z-m); v.co.z=m; tot.add(v.index)
    print('F237B pass',ps,'spikes',len(mv),flush=True)
bm.to_mesh(o.data); o.data.update(); print('F237B PK verts lowered',len(tot),'max drop %.2f m'%mx,flush=True)
