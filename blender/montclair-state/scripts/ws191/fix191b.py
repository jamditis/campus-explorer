# ws191b: the "small dark wedge under the WS170b curb-strip end" (ws190 E eye view) = an UNCOVERED gap, not a skirt sliver:
# x ~-299.8..-292.6, y ~-235.2..-238.0 (probe191d.out coverage map) nothing but the far-field skirt between the Lot 3 S edge,
# the WS170b strip E end (x -299), the WS163 patch E edge and the WS110 patch N edge (y -238). 2023 LiDAR there: mostly class 1
# (canopy, 1827 pts) over sparse class-2 ground rising 18.2 -> 18.7 (+100) m S-ward with mixed intensity 900-4400 (not asphalt,
# not the 5000-7000 concrete band) = tree-shaded lawn bank like the WS110 lawn S of it (ortho: canopy). Build: lawn sheet, 0.2 m
# grid, z = inverse-distance blend of the neighbouring top surfaces sampled around the gap (continuous with them at every border;
# matches the LiDAR rise), -1 cm, and 1.5 cm under any existing cover; faces fully under cover dropped. Lawn vs mulch UNVERIFIED.
import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def _b191b(o):
    M=o.matrix_world; return BVHTree.FromPolygons([M@v.co for v in o.data.vertices],[p.vertices[:] for p in o.data.polygons])
NB191b=[o for o in bpy.data.objects if o.name.startswith(('WS163_ground_patch_W_of_WS110','WS170b_Lot3_S_end_curb','WS162_Lot3_asphalt_OSM','WS110_ground_patch_S_of_y-238','WS190b_Lot3_S_end_corner'))]
TB191b=[_b191b(o) for o in NB191b]
print('FIX191B neighbours',[o.name[:40] for o in NB191b],flush=True)
X0c,X1c,Y0c,Y1c=-300.2,-290.4,-238.8,-234.8
def tops(x,y): return [h[0].z for t in TB191b for h in [t.ray_cast(Vector((x,y,300)),Vector((0,0,-1)))] if h[0]]
ring=[]
for x in np.arange(X0c-1.0,X1c+1.01,0.2):
    for y in np.arange(Y0c-1.0,Y1c+1.01,0.2):
        zs=tops(x,y)
        if zs: ring.append((x,y,max(zs)))
R=np.array(ring)
# cone cap (ws191 review fix): the lawn must meet the Lot 3 asphalt / WS170b strip / WS190b fill flush and rise from them at
# <= 30 % (LiDAR rise is ~0.4 m over 2.5 m = 16 %), so it can never bulge over the strip end.
LOWN=[i for i,o in enumerate(NB191b) if o.name.startswith(('WS170b_','WS162_Lot3_asphalt','WS190b_'))]
low=[]
for x in np.arange(X0c-1.0,X1c+1.01,0.2):
    for y in np.arange(Y0c-1.0,Y1c+1.01,0.2):
        zs=[h[0].z for k in LOWN for h in [TB191b[k].ray_cast(Vector((x,y,300)),Vector((0,0,-1)))] if h[0]]
        if zs: low.append((x,y,max(zs)))
LW=np.array(low)
bm=bmesh.new(); nx=int(round((X1c-X0c)/0.2))+1; ny=int(round((Y1c-Y0c)/0.2))+1; vs=[]; cov=[]
for j in range(ny):
    for i in range(nx):
        x=X0c+0.2*i; y=Y0c+0.2*j
        d2=(R[:,0]-x)**2+(R[:,1]-y)**2+0.04; w=1.0/d2**2
        z=float((w*R[:,2]).sum()/w.sum())-0.01
        z=min(z,float((LW[:,2]+0.30*np.sqrt((LW[:,0]-x)**2+(LW[:,1]-y)**2)).min())-0.01)
        zl=tops(x,y)
        if zl: z=min(z,min(zl)-0.015)
        vs.append(bm.verts.new((x,y,z))); cov.append(bool(zl))
nf=0
for j in range(ny-1):
    for i in range(nx-1):
        q=[j*nx+i,j*nx+i+1,(j+1)*nx+i+1,(j+1)*nx+i]
        if all(cov[k] for k in q): continue
        bm.faces.new([vs[k] for k in q]); nf+=1
bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
me=bpy.data.meshes.new('WS191b_Lot3_S_gap_lawn_fill'); bm.to_mesh(me); bm.free()
for p in me.polygons: p.use_smooth=True
uvl=me.uv_layers.new(name='UVMap')
for l in me.loops: v=me.vertices[l.vertex_index].co; uvl.data[l.index].uv=(v.x/10.0,v.y/10.0)
ob=bpy.data.objects.new('WS191b_Lot3_S_gap_lawn_fill_E_of_strip_end_UNVERIFIED',me)
lw=bpy.data.objects['WS110_ground_patch_S_of_y-238_DTM2023_1m_lawn_UNVERIFIED']
for c in lw.users_collection: c.objects.link(ob)
me.materials.append(lw.active_material)
zz=[v.co.z for v in me.vertices]
print('FIX191B fill',ob.name,'faces',nf,'ringpts',len(R),'z',round(min(zz),3),round(max(zz),3),'mat',lw.active_material.name if lw.active_material else None,flush=True)
