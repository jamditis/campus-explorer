# ws223c: the landing top dipped at v152 (-248.0,-52.24) and v142 (-248.5,-52.50) inside the curb-return edge ring
# (edge 125.87-125.90, v152 125.874, v142 125.871), so the corner shaded as tilted facets. One raise-only smoothing pass:
# each listed TOP vert goes to max(z, mean z of its top-face neighbours); its bottom twin is raised by the same amount so
# the slab keeps its thickness. No vert is lowered.
import bpy, bmesh
o=bpy.data.objects['WS72_Kasser_SW_RHD_core_sidewalk_landing_UNVERIFIED_width']; M=o.matrix_world; MI=M.inverted()
bm=bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table()
W=[M@v.co for v in bm.verts]
def twin(i):
    c=[j for j,w in enumerate(W) if j!=i and abs(w.x-W[i].x)<1e-3 and abs(w.y-W[i].y)<1e-3 and w.z<W[i].z]; return c[0] if c else None
new={}
for i in (152,142):
    v=bm.verts[i]; nb=set()
    for f in v.link_faces:
        if (M.to_3x3()@f.normal).z>0.7: nb.update(u.index for u in f.verts)
    nb.discard(i); m=sum(W[j].z for j in nb)/len(nb)
    new[i]=max(W[i].z,m)
for i,z in new.items():
    d=z-W[i].z
    for j in (i,twin(i)):
        if j is None: continue
        w=W[j].copy(); w.z+=d; bm.verts[j].co=MI@w
    print('F223C v%d %.3f -> %.3f (+%.1f cm) twin %s'%(i,W[i].z,z,d*100,twin(i)),flush=True)
bm.normal_update(); bm.to_mesh(o.data); bm.free(); o.data.update()
