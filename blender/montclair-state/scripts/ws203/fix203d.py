# ws203 W13d: the W13 "dark lens" = a 0.4 m SLIT in the WS191c strip-back lawn fillet: its vertex grid skips the x~-302.8 column, so there
# are NO faces between columns x~-303.0 and x~-302.6 (two inner boundary edges, visible in the ws203 boundary map). At a grazing angle the
# W eye looks through the slit onto the WS190b fill ~8 cm below, in shadow. Designer call: one continuous lawn fillet -> bridge the two
# boundary columns with quads (no verts move), then make the fillet's normals face up (several faces pointed down).
import bpy, bmesh
o=[x for x in bpy.data.objects if x.name.startswith('WS191c_Lot3_S_strip_back_lawn')][0]; mw=o.matrix_world
bm=bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table()
def col(xc): return sorted([v for v in bm.verts if v.is_boundary and abs((mw@v.co).x-xc)<0.06],key=lambda v:(mw@v.co).y)
A=col(-303.0); B=col(-302.6)
print('F203d cols',len(A),len(B),[round((mw@v.co).y,2) for v in A],[round((mw@v.co).y,2) for v in B],flush=True)
nf=0
for i in range(min(len(A),len(B))-1):
    a0,a1,b0,b1=A[i],A[i+1],B[i],B[i+1]
    if abs((mw@a0.co).y-(mw@b0.co).y)>0.12 or abs((mw@a1.co).y-(mw@b1.co).y)>0.12: continue
    try: bm.faces.new((a0,b0,b1,a1)); nf+=1
    except ValueError: pass
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
up=sum(1 for f in bm.faces if f.normal.z>0)
if up<len(bm.faces)/2:
    for f in bm.faces: f.normal_flip()
up2=sum(1 for f in bm.faces if f.normal.z>0)
bm.to_mesh(o.data); o.data.update(); bm.free()
for p in o.data.polygons: p.use_smooth=True
print('F203d bridged faces',nf,'normals up',up2,'/',len(o.data.polygons),flush=True)
