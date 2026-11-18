# ws83b: 0.6 m asphalt gutter-pan skin on top of the WS82 lane along the WS83 edge band (covers the last dark lane slits by the walk)
import bpy,bmesh,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def bvh(o):
    b=bmesh.new(); b.from_mesh(o.data); b.transform(o.matrix_world); t=BVHTree.FromBMesh(b); b.free(); return t
LN=bpy.data.objects['WS82_sprague_lane_onesurface_asphalt_ortho2020_UNVERIFIED_edges']; BD=bpy.data.objects['WS83_sprague_lane_walk_edge_band_concrete_UNVERIFIED']
LB=bvh(LN)
def hz(x,y):
    h=LB.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))[0]; return h.z if h else None
# outer bottom edge of the band = verts with lowest z per y
rows={}
for v in BD.data.vertices:
    w=BD.matrix_world@v.co; k=round(w.y,2)
    if k not in rows or w.x<rows[k][0]: rows[k]=(w.x,w.z)
ys=sorted(rows)
def xo_at(y):
    for a,b in zip(ys[:-1],ys[1:]):
        if a<=y<=b: t=(y-a)/(b-a); return rows[a][0]*(1-t)+rows[b][0]*t
    return rows[ys[0]][0] if y<ys[0] else rows[ys[-1]][0]
COLS=[-0.62,-0.47,-0.32,-0.17,-0.02]  # x offsets from band outer face
bm=bmesh.new(); grid=[]; miss=0
y=ys[0]
while y<=ys[-1]+1e-6:
    xo=xo_at(y); row=[]
    for dx in COLS:
        x=xo+dx; zs=[hz(x+ax,y+ay) for ax in (-0.1,0,0.1) for ay in (-0.1,0,0.1)]; zs=[z for z in zs if z is not None]
        row.append([x,y,(max(zs)+0.004) if zs else None])
    grid.append(row); y+=0.25
for row in grid:
    kn=[c[2] for c in row if c[2] is not None]
    for c in row:
        if c[2] is None: miss+=1; c[2]=max(kn) if kn else None
for i,row in enumerate(grid):
    for c in row:
        if c[2] is None:
            nb=[g[k][2] for g in grid[max(0,i-3):i+4] for k in range(len(COLS)) if g[k][2] is not None]; c[2]=max(nb)
V=[[bm.verts.new(tuple(c)) for c in row] for row in grid]
for i in range(len(V)-1):
    for k in range(len(COLS)-1): bm.faces.new((V[i][k],V[i][k+1],V[i+1][k+1],V[i+1][k]))
uv=bm.loops.layers.uv.new('UVMap')
for f in bm.faces:
    f.smooth=False
    for l in f.loops: l[uv].uv=(l.vert.co.x*0.25,l.vert.co.y*0.25)
NAME='WS83_lane_gutter_skin_asphalt_UNVERIFIED'
old=bpy.data.objects.get(NAME)
if old: bpy.data.objects.remove(old)
me=bpy.data.meshes.new(NAME); bm.to_mesh(me); bm.free()
ob=bpy.data.objects.new(NAME,me); me.materials.append(LN.data.materials[0])
for c in LN.users_collection: c.objects.link(ob)
print('WS83b skin faces',len(me.polygons),'miss',miss,'z',min(v.co.z for v in me.vertices),max(v.co.z for v in me.vertices),flush=True)
bpy.ops.wm.save_mainfile(); print('WS83b SAVED',flush=True)
