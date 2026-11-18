# ws79a: (1) trim WS77 island east tip at x=-217 (tip ran onto lawn past the lot edge, coplanar with terrain -> see-through green triangle in eye-E view)
# (2) delete Footpaths_OSM faces that poke into the lot (x<-216.3; pale slab), (3) asphalt patch filling the lot where those faces were.
import bpy,bmesh
from mathutils import Vector
sc=bpy.context.scene
XC=-217.0
isl=bpy.data.objects['WS77_lot_median_island_ortho2020_UNVERIFIED_edges']
me=isl.data; bm=bmesh.new(); bm.from_mesh(me); mw=isl.matrix_world; inv=mw.inverted()
co=inv@Vector((XC,0,0)); no=(inv.to_3x3().transposed()@Vector((1,0,0))).normalized()
geom=bm.verts[:]+bm.edges[:]+bm.faces[:]
r=bmesh.ops.bisect_plane(bm,geom=geom,plane_co=co,plane_no=no,clear_outer=True,dist=1e-4)
bm.edges.ensure_lookup_table()
cut=[e for e in bm.edges if e.is_boundary and all(abs((mw@v.co).x-XC)<0.01 for v in e.verts)]
print('WS79 island cut boundary edges',len(cut),flush=True)
conc=[i for i,s in enumerate(isl.material_slots) if s.material and 'concrete' in s.material.name.lower()]
nf=0
if cut:
    adj={}
    for e in cut:
        a,b=e.verts; adj.setdefault(a,[]).append(b); adj.setdefault(b,[]).append(a)
    seen=set()
    for st in [v for v in adj if len(adj[v])==1]+list(adj):
        if st in seen: continue
        ch=[st]; seen.add(st); cur=st
        while True:
            nx=[w for w in adj[cur] if w not in seen]
            if not nx: break
            cur=nx[0]; ch.append(cur); seen.add(cur)
        if len(ch)>=3:
            try:
                f=bm.faces.new(ch); nf+=1
                if conc: f.material_index=conc[0]
            except Exception as ex: print('WS79 cap fail',len(ch),ex)
bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:])
bm.to_mesh(me); bm.free(); me.update()
print('WS79 island trimmed; cap faces',nf,'verts',len(me.vertices),flush=True)
# (2) footpath faces inside the lot
fp=bpy.data.objects['Footpaths_OSM']; fm=fp.data; fw=fp.matrix_world
bm=bmesh.new(); bm.from_mesh(fm); bm.faces.ensure_lookup_table()
dl=[f for f in bm.faces if (lambda c:(c.x<-216.3 and -87.5<c.y<-81.0 and c.x>-226))(fw@f.calc_center_median())]
print('WS79 footpath faces deleted',len(dl),flush=True)
bmesh.ops.delete(bm,geom=dl,context='FACES'); bm.to_mesh(fm); bm.free(); fm.update()
# (3) asphalt patch
dg=bpy.context.evaluated_depsgraph_get()
lotnames=('WS76_accessible_lot','WS75_sprague_lot','WS77_lot_median','WS76_lot_','WS74','WS79_')
S=0.4; cells=[]
x=-222.6
while x<-215.8:
    y=-87.2
    while y<-81.0:
        cx,cy=x+S/2,y+S/2
        ok,loc,n,i,ob,m=sc.ray_cast(dg,Vector((cx,cy,200)),Vector((0,0,-1)))
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
print('WS79 patch cells',len(cells),flush=True)
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
