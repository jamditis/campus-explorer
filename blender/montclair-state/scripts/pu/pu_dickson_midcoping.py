# pu: Dickson Hall roof (LiDAR) edge faces carrying the pe dark-bronze coping (slots 1/2) at the LOWER roof level
# (z~145.3) also run along the west/north walls that continue up to ~150 m, where they stick ~4 cm out of the brick face and
# print as a thin dark line across the facade. Faces with slot 1/2 within 0.6 m of a wall face and >=0.5 m below that
# face's top -> slot 3 (facade brick); their 'facade' UV set to world x/y so the brick varies. Original indices kept in
# face attr pu_orig_mi; REVERT=1 restores them and removes the attr (run before pu_dickson_topstrip's revert).
import bpy, bmesh, os
from mathutils.bvhtree import BVHTree
REV=os.environ.get('REVERT')=='1'
r=bpy.data.objects['Dickson Hall roof (LiDAR)']; me=r.data
if 'pu_co0' in me.attributes:
    a=me.attributes['pu_co0'].data
    for v in me.vertices: v.co=a[v.index].vector
    me.attributes.remove(me.attributes['pu_co0']); print('REVERTED_PU_MIDCOPING_LIP')
if 'pu_orig_mi' in me.attributes:
    a=me.attributes['pu_orig_mi'].data
    for p in me.polygons: p.material_index=a[p.index].value
    me.attributes.remove(me.attributes['pu_orig_mi']); print('REVERTED_PU_MIDCOPING')
if not REV:
    w=bpy.data.objects['Dickson Hall walls']; bw=bmesh.new(); bw.from_mesh(w.data); bw.transform(w.matrix_world); bw.faces.ensure_lookup_table()
    tops=[max(v.co.z for v in f.verts) for f in bw.faces]; bvh=BVHTree.FromBMesh(bw)
    mw=r.matrix_world; at=me.attributes.new('pu_orig_mi','INT','FACE'); uv=me.uv_layers['facade'].data; k=0
    for p in me.polygons:
        at.data[p.index].value=p.material_index
        if p.material_index not in (1,2): continue
        c=mw@p.center; loc,nor,fi,d=bvh.find_nearest(c)
        if fi is None or d>0.6 or tops[fi]-c.z<0.5: continue
        p.material_index=3; k+=1
        for li in p.loop_indices:
            co=mw@me.vertices[me.loops[li].vertex_index].co; uv[li].uv=(co.x,co.y)
    # lip: pull those faces' verts that sit outside the wall face to 3 cm behind it (inside the building)
    co0=me.attributes.new('pu_co0','FLOAT_VECTOR','POINT')
    for v in me.vertices: co0.data[v.index].vector=v.co
    vids={vi for p in me.polygons if p.material_index==3 and at.data[p.index].value in (1,2) for vi in p.vertices}
    mi=mw.inverted(); mv=0
    for vi in vids:
        v=me.vertices[vi]; g=mw@v.co; loc,nor,fi,d=bvh.find_nearest(g)
        if fi is None or d>0.15: continue
        out=-bw.faces[fi].normal; out.z=0; out.normalize()
        if (g-loc).dot(out)>-0.03:
            g2=g-out*((g-loc).dot(out)+0.03); v.co=mi@g2; mv+=1
    me.update(); bw.free(); print('PU_MIDCOPING faces',k,'lip verts moved',mv)
