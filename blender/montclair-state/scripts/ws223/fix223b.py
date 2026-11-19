# ws223b: seven top faces of the WS72 Kasser landing (the triangle fan left by ws222f/g where the south edge was bent onto
# the W39 curb-return back: f90, f165-f170) had normals pointing DOWN, so the landing corner shaded as a dark crease/fold
# in the eye views. Faces whose verts are all TOP verts (a vert directly below at the slab bottom exists) and whose normal
# points down are flipped. No vertex moves.
import bpy, bmesh
for o in [o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith(('WS72_Kasser_SW_RHD_core_sidewalk_landing','WS215_RHD_SE_core_street_level_sidewalk'))]:
    M=o.matrix_world; bm=bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table()
    W=[M@v.co for v in bm.verts]
    key={}
    for i,w in enumerate(W): key.setdefault((round(w.x,3),round(w.y,3)),[]).append(i)
    top=set()
    for k,ids in key.items():
        if len(ids)>=2:
            zs=sorted(ids,key=lambda i:W[i].z); top.add(zs[-1])
    n=0
    for f in bm.faces:
        if all(v.index in top for v in f.verts) and (M.to_3x3()@f.normal).z< -0.5:
            f.normal_flip(); n+=1
    bm.normal_update(); bm.to_mesh(o.data); bm.free(); o.data.update()
    print('F223B %s flipped %d'%(o.name[:40],n),flush=True)
