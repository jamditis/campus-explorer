# ws223g (W45): the V-notch / trench along the WS72 landing S edge by the W39 curb (x -250.5..-248.9, y -55.6..-53.8) is the
# WS72_KasserSW_walk_cut GN on the coarse WS70 verge mesh: a few verts under the slab are pulled to slab-6 cm and the long
# triangles from them ramp the visible grass outside the slab down 3-12 cm. The grass faces touching that box are subdivided
# (4 cuts, linear, base z 125.786-125.789 unchanged) so the cut only drops verts that are actually under the slab.
# Grass only; no paving or curb touched.
import bpy, bmesh
o=bpy.data.objects['WS70_gap_strip_grass_berms']; M=o.matrix_world
bm=bmesh.new(); bm.from_mesh(o.data)
def inb(v):
    w=M@v.co; return -250.6<=w.x<=-248.85 and -55.7<=w.y<=-53.7
faces=[f for f in bm.faces if any(inb(v) for v in f.verts)]
edges=list({e for f in faces for e in f.edges})
nv0=len(bm.verts)
bmesh.ops.subdivide_edges(bm,edges=edges,cuts=4,use_grid_fill=True)
bmesh.ops.triangulate(bm,faces=[f for f in bm.faces if len(f.verts)>4])
print('F223G faces',len(faces),'edges',len(edges),'new verts',len(bm.verts)-nv0,flush=True)
bm.normal_update(); bm.to_mesh(o.data); bm.free(); o.data.update()
