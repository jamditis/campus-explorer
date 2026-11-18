# Session ed (Oct 21 2026 ~6:40 PM ET): the CCOM west-entrance brick forecourt is a single-sided draped sheet, so its
# edge floated a few cm over lower terrain (thin dark gap) and DTM triangles poked through it elsewhere (wavy edge).
# (1) add a vertical paver skirt from the top boundary down 0.30 m (same material) -> object 'CCOM forecourt edge skirt (ed)';
# (2) push Terrain_LiDAR_DTM_1m verts strictly inside the forecourt footprint (inset 0.05 m) to forecourt z - 0.04 if higher
#     (orig z in point attribute ed_orig_z). Paving outline unchanged (ortho + photo). SAVE=1 saves; REVERT=1 undoes.
import bpy, bmesh, os, mathutils
from mathutils.bvhtree import BVHTree
fc=bpy.data.objects['CCOM brick forecourt (ortho + photo)']; mw=fc.matrix_world
ter=bpy.data.objects['Terrain_LiDAR_DTM_1m']; tme=ter.data; tmw=ter.matrix_world; tinv=tmw.inverted()
SK='CCOM forecourt edge skirt (ed)'
if os.environ.get('REVERT')=='1':
    if SK in bpy.data.objects: bpy.data.objects.remove(bpy.data.objects[SK])
    a=tme.attributes.get('ed_orig_z')
    if a:
        n=0
        for v,o in zip(tme.vertices,a.data):
            if o.value>-9000: v.co.z=o.value; n+=1
        tme.attributes.remove(a); print('ED_EDGE_REVERTED terrain',n)
else:
    bm=bmesh.new(); bm.from_mesh(fc.data); bm.transform(mw)
    bnd=[e for e in bm.edges if e.is_boundary]
    me=bpy.data.meshes.new(SK); verts=[]; faces=[]
    for e in bnd:
        a,b=e.verts[0].co.copy(),e.verts[1].co.copy(); i=len(verts)
        verts+= [a,b,b-mathutils.Vector((0,0,0.30)),a-mathutils.Vector((0,0,0.30))]; faces.append((i,i+1,i+2,i+3))
    me.from_pydata([tuple(v) for v in verts],[],faces); me.materials.append(fc.data.materials[0])
    for p in me.polygons: p.use_smooth=False
    if SK in bpy.data.objects: bpy.data.objects.remove(bpy.data.objects[SK])
    sk=bpy.data.objects.new(SK,me)
    for c in fc.users_collection: c.objects.link(sk)
    # footprint test via BVH of the forecourt (world), ray down from above
    bvh=BVHTree.FromBMesh(bm)
    if 'ed_orig_z' not in tme.attributes:
        at=tme.attributes.new('ed_orig_z','FLOAT','POINT')
        for d in at.data: d.value=-9999.0
    at=tme.attributes['ed_orig_z']
    xs=[v.co.x for v in bm.verts]; ys=[v.co.y for v in bm.verts]
    n=0
    for idx,v in enumerate(tme.vertices):
        w=tmw@v.co
        if not (min(xs)-0.1<w.x<max(xs)+0.1 and min(ys)-0.1<w.y<max(ys)+0.1): continue
        hits=[]
        for dx,dy in ((0.05,0),(-0.05,0),(0,0.05),(0,-0.05)):
            h=bvh.ray_cast(mathutils.Vector((w.x+dx,w.y+dy,w.z+20)),mathutils.Vector((0,0,-1)))
            hits.append(h[0])
        if all(h is not None for h in hits):
            zt=min(h.z for h in hits)-0.04
            if w.z>zt:
                if at.data[idx].value<-9000: at.data[idx].value=v.co.z
                v.co.z=(tinv@mathutils.Vector((w.x,w.y,zt))).z; n+=1
    tme.update(); print('ED_EDGE_APPLIED skirt faces',len(faces),'terrain lowered',n)
if os.environ.get('SAVE')=='1': bpy.ops.wm.save_mainfile(); print('ED_SAVED')
