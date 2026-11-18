# ws79b: rebuild the lot E patch with multi-hit rays (trees/decals no longer block cells)
import bpy,bmesh
from mathutils import Vector
sc=bpy.context.scene
SKIPPFX=('Tree','tree','LP_','Lamp','WS70_','Leaf','leaf')
old=bpy.data.objects.get('WS79_lot_E_patch_asphalt_ortho2020_UNVERIFIED_edges')
if old:
    m=old.data; bpy.data.objects.remove(old); bpy.data.meshes.remove(m)
# (3) asphalt patch
dg=bpy.context.evaluated_depsgraph_get()
lotnames=('WS76_accessible_lot','WS75_sprague_lot','WS77_lot_median','WS76_lot_','WS74','WS79_')
S=0.4; cells=[]; DBG={}
x=-222.6
while x<-215.8:
    y=-87.2
    while y<-81.0:
        cx,cy=x+S/2,y+S/2
        org=Vector((cx,cy,200)); ok=False
        for _k in range(12):
            ok,loc,n,i,ob,m=sc.ray_cast(dg,org,Vector((0,0,-1)))
            if not ok: break
            if ob.name.startswith(('T_','WS76_lot_','WS76_lot_accessible')) or ob.type!='MESH' or ob.hide_render or 'DTM_target' in ob.name or ob.name.startswith(SKIPPFX): org=loc-Vector((0,0,0.002)); continue
            break
        DBG[ob.name if ok else None]=DBG.get(ob.name if ok else None,0)+1
        if ok and ob.name.startswith(('Terrain_LiDAR','WS68_RHD_ground')):
            cells.append((cx,cy,loc.z))
        elif ok and cx>-218.8 and ob.name.startswith(('WS76_accessible_lot','WS75_sprague_lot')):
            cells.append((cx,cy,loc.z-0.042))
        elif ok and ob.name.startswith('T_'):
            # look under the tree
            ok2,loc2,_,_,ob2,_=sc.ray_cast(dg,Vector((cx,cy,loc.z-0.05)),Vector((0,0,-1)))
            pass
        y+=S
    x+=S
print('WS79 patch cells',len(cells),DBG,flush=True)
from collections import Counter
mat=bpy.data.materials['fn_lot_asphalt']
bm=bmesh.new(); vmap={}
def gv(ix,iy,z):
    k=(ix,iy)
    if k not in vmap: vmap[k]=[bm.verts.new((ix,iy,z)),1]
    else: v=vmap[k]; v[0].co.z=(v[0].co.z*v[1]+z)/(v[1]+1); v[1]+=1
    return vmap[k][0]
for cx,cy,z in cells:
    zz=z+0.03
    q=[gv(round(cx-S/2,2),round(cy-S/2,2),zz),gv(round(cx+S/2,2),round(cy-S/2,2),zz),gv(round(cx+S/2,2),round(cy+S/2,2),zz),gv(round(cx-S/2,2),round(cy+S/2,2),zz)]
    bm.faces.new(q)
pm=bpy.data.meshes.new('WS79_lot_E_patch_asphalt'); bm.to_mesh(pm); bm.free()
po=bpy.data.objects.new('WS79_lot_E_patch_asphalt_ortho2020_UNVERIFIED_edges',pm); pm.materials.append(mat)
coll=bpy.data.objects['WS76_accessible_lot_asphalt_ortho2020_UNVERIFIED_edges'].users_collection[0]
coll.objects.link(po)
for p in pm.polygons: p.use_smooth=False
print('WS79 patch built',len(pm.polygons),flush=True)

lot=bpy.data.objects['WS76_accessible_lot_asphalt_ortho2020_UNVERIFIED_edges']
print('WS79 lot uv',[u.name for u in lot.data.uv_layers],'attrs',[a.name for a in lot.data.attributes],flush=True)
print('WS79 mat nodes',[n.type for n in mat.node_tree.nodes],flush=True)
for u in lot.data.uv_layers:
    nu=pm.uv_layers.new(name=u.name)
    for l in pm.loops:
        c=po.matrix_world@pm.vertices[l.vertex_index].co; nu.data[l.index].uv=(c.x/10,c.y/10)
