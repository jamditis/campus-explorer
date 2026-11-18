# ws81: build WS81_lot_seam_underlay (one mesh, 0.2 m cells) 1.2 cm under the union of the Sprague/RHD lot meshes,
# only at INTERIOR points (all 4 neighbours at ±0.3 m covered) so it fills seam cracks/slivers between the
# WS75/WS76/WS79/WS80 cell meshes without poking out past any lot's outer edge. Runs either on main or in a lite session.
import bpy,bmesh,os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
LOTS=['WS75_sprague_lot_asphalt_ortho2020_UNVERIFIED_edges','WS80_sprague_lot_fill_asphalt_ortho2020_UNVERIFIED_edges','WS76_accessible_lot_asphalt_ortho2020_UNVERIFIED_edges','WS79_lot_E_patch_asphalt_ortho2020_UNVERIFIED_edges']
if os.environ.get('LITE'):
    with bpy.data.libraries.load('/workspace/nj-scenes/montclair-state/montclair_state.blend',link=False) as (fr,to): to.objects=list(LOTS)
    for o in to.objects: bpy.context.scene.collection.objects.link(o)
T=[]
for n in LOTS:
    o=bpy.data.objects[n]; b=bmesh.new(); b.from_mesh(o.data); b.transform(o.matrix_world); T.append(BVHTree.FromBMesh(b)); b.free()
def lz(x,y):
    zs=[h[0].z for h in (t.ray_cast(Vector((x,y,400)),Vector((0,0,-1))) for t in T) if h[0]]
    return min(zs) if zs else None
xs=[];ys=[]
for n in LOTS:
    o=bpy.data.objects[n]; bb=[o.matrix_world@Vector(c) for c in o.bound_box]; xs+= [p.x for p in bb]; ys+=[p.y for p in bb]
S=0.2; D=0.3
x0,x1,y0,y1=min(xs),max(xs),min(ys),max(ys)
nx=int((x1-x0)/S)+1; ny=int((y1-y0)/S)+1
cells={}
for i in range(nx):
    for j in range(ny):
        cx=x0+(i+.5)*S; cy=y0+(j+.5)*S
        zn=[lz(cx+dx,cy+dy) for dx,dy in ((D,0),(-D,0),(0,D),(0,-D))]
        if any(z is None for z in zn): continue
        zc=lz(cx,cy); zz=min([z for z in zn+[zc] if z is not None])-0.012
        cells[(i,j)]=zz
print('WS81U cells',len(cells),flush=True)
bm=bmesh.new(); vm={}
def gv(i,j):
    if (i,j) not in vm:
        zs=[cells[k] for k in ((i,j),(i-1,j),(i,j-1),(i-1,j-1)) if k in cells]
        vm[(i,j)]=bm.verts.new((x0+i*S,y0+j*S,min(zs)))
    return vm[(i,j)]
for (i,j) in cells: bm.faces.new([gv(i,j),gv(i+1,j),gv(i+1,j+1),gv(i,j+1)])
uv=bm.loops.layers.uv.new('UVMap')
for f in bm.faces:
    for l in f.loops: l[uv].uv=(l.vert.co.x/4,l.vert.co.y/4)
me=bpy.data.meshes.new('WS81_lot_seam_underlay'); bm.to_mesh(me); bm.free()
src=bpy.data.objects[LOTS[0]]
me.materials.append(src.data.materials[0])
ob=bpy.data.objects.new('WS81_lot_seam_underlay_asphalt',me)
src.users_collection[0].objects.link(ob)
print('WS81U faces',len(me.polygons),'z',round(min(v.co.z for v in me.vertices),2),round(max(v.co.z for v in me.vertices),2),flush=True)
if os.environ.get('LITE'):
    for n in LOTS: bpy.data.objects.remove(bpy.data.objects[n])
    bpy.ops.wm.save_as_mainfile(filepath='/workspace/nj-scenes/montclair-state/scripts/ws81/underlay81_lite.blend')
    print('WS81U lite saved',flush=True)
