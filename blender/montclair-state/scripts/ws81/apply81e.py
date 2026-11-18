# ws81e: put WS75 + WS80 lot verts on ONE surface (the WS81 underlay + 1.2 / 1.5 cm) so the overlapping cell layers stop casting
# step shadows (the "seam cracks"); then list every non-ground mesh with faces on the grandstand lawn (white-line hunt).
import bpy,bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
U=bpy.data.objects['WS81_lot_seam_underlay_asphalt']; b=bmesh.new(); b.from_mesh(U.data); b.transform(U.matrix_world); UB=BVHTree.FromBMesh(b); b.free()
for nm,off in (('WS75_sprague_lot_asphalt_ortho2020_UNVERIFIED_edges',0.012),('WS80_sprague_lot_fill_asphalt_ortho2020_UNVERIFIED_edges',0.015)):
    o=bpy.data.objects[nm]; mw=o.matrix_world; mi=mw.inverted(); n=0; mx=0
    for v in o.data.vertices:
        p=mw@v.co; h=UB.ray_cast(Vector((p.x,p.y,400)),Vector((0,0,-1)))[0]
        if h is None: continue
        z=h.z+off
        if abs(z-p.z)<0.3: mx=max(mx,abs(z-p.z)); v.co=mi@Vector((p.x,p.y,z)); n+=1
    o.data.update(); print('WS81E flattened',nm[:20],n,'of',len(o.data.vertices),'max dz',round(mx,3),flush=True)
uvs={n:[l.name for l in bpy.data.objects[n].data.uv_layers] for n in ('WS75_sprague_lot_asphalt_ortho2020_UNVERIFIED_edges','WS80_sprague_lot_fill_asphalt_ortho2020_UNVERIFIED_edges')}
print('WS81E uvs',uvs,flush=True)
R=(-252,-231,-128,-108)
for o in bpy.data.objects:
    if o.type!='MESH' or o.hide_render or o.name.startswith(('Terrain_LiDAR','Context_','WS68_RHD_ground','WS60_terrain','WS78_','WS81_')): continue
    bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs=[q.x for q in bb]; ys=[q.y for q in bb]
    if max(xs)<R[0] or min(xs)>R[1] or max(ys)<R[2] or min(ys)>R[3]: continue
    mw=o.matrix_world; hits=[]
    for p in o.data.polygons:
        c=mw@p.center
        if R[0]<c.x<R[1] and R[2]<c.y<R[3]: hits.append((p.index,round(c.x,1),round(c.y,1),round(c.z,2)))
    if hits: print('WS81E LAWNOBJ',o.name,len(hits),hits[:5],[m.name for m in o.data.materials][:3],[md.type for md in o.modifiers],flush=True)
bpy.ops.wm.save_mainfile(); print('WS81E SAVED',flush=True)
