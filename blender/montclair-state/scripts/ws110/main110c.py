# UNIFY_SWEEP #1: mid-bend dark slot between WS73 verge back edge and WS40 walk -> same lawn material as the verge
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def obvh(o):
    bm=bmesh.new(); bm.from_mesh(o.data); bm.transform(o.matrix_world); t=BVHTree.FromBMesh(bm); bm.free(); return t
ver=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('WS73') and 'verge' in o.name.lower()]
wlk=[o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('WS40') and 'walk' in o.name.lower()]
print('E110c verge',[o.name for o in ver],'walk',[o.name for o in wlk])
VB=[obvh(o) for o in ver]; WB=[obvh(o) for o in wlk]
def near(bs,p):
    ds=[b.find_nearest(p)[3] for b in bs]; ds=[d for d in ds if d is not None]; return min(ds) if ds else 99
t=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=t.data; mw=t.matrix_world
mat=ver[0].data.materials[0]
if mat.name not in [m.name for m in me.materials if m]: me.materials.append(mat)
mi=[m.name if m else None for m in me.materials].index(mat.name)
n=0
for p in me.polygons:
    c=mw@p.center
    if not (-200<c.x<-186 and -119<c.y<-61): continue
    dv=near(VB,c); dw=near(WB,c)
    if dv<2.0 and dw<2.0 and p.material_index!=mi:
        p.material_index=mi; n+=1
print('E110c terrain faces set to verge lawn',n,'mat',mat.name,'slot',mi)
bpy.ops.wm.save_mainfile(); print('M110 SAVED c',flush=True)
exec(open('/workspace/nj-scenes/montclair-state/scripts/ws105/cut105.py').read().replace('ws105/render_cut105','ws110/render_cut110'))
