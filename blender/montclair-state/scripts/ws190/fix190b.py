# ws190b: fill the pre-existing 1x1 m gap at the Lot 3 S-end corner (x -303.6..-302.0, y -236.9..-235.4): between the WS170b
# curb strip, the ramp's E flare and the WS163 lawn nothing covered it (skirt showed as a dark wedge in the E eye view).
# 2020 ortho: dark vegetation there -> lawn (bed vs lawn UNVERIFIED). Grid 0.2 m, z = plane fit of the neighbouring tops - 1.5 cm,
# so every existing surface stays on top and the fill only shows inside the gap.
import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def _b190b(o):
    M=o.matrix_world; return BVHTree.FromPolygons([M@v.co for v in o.data.vertices],[p.vertices[:] for p in o.data.polygons])
NB190b=[o for o in bpy.data.objects if o.name.startswith(('WS163_ground_patch_W_of_WS110','WS170b_Lot3_S_end_curb','WS163_Lot3_aisle_S_drive','WS162_Lot3_asphalt_OSM','WS162_Lot3_S_end_apron'))]
TB190b=[_b190b(o) for o in NB190b]
X0b,X1b,Y0b,Y1b=-303.8,-301.8,-237.0,-235.3
pts=[]
for x in np.arange(X0b-0.6,X1b+0.61,0.2):
    for y in np.arange(Y0b-0.6,Y1b+0.61,0.2):
        zs=[h[0].z for t in TB190b for h in [t.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))] if h[0]]
        if zs: pts.append((x,y,max(zs)))
P=np.array(pts); A=np.c_[np.ones(len(P)),P[:,0],P[:,1]]; cf=np.linalg.lstsq(A,P[:,2],rcond=None)[0]
bm=bmesh.new(); nx,ny=11,9; vs=[]
for j in range(ny):
    for i in range(nx):
        x=X0b+(X1b-X0b)*i/(nx-1); y=Y0b+(Y1b-Y0b)*j/(ny-1)
        zl=[h[0].z for t in TB190b for h in [t.ray_cast(Vector((x,y,200)),Vector((0,0,-1)))] if h[0]]
        z=cf[0]+cf[1]*x+cf[2]*y-0.015
        if zl: z=min(z,min(zl)-0.015)
        vs.append(bm.verts.new((x,y,z)))
for j in range(ny-1):
    for i in range(nx-1):
        bm.faces.new((vs[j*nx+i],vs[j*nx+i+1],vs[(j+1)*nx+i+1],vs[(j+1)*nx+i]))
me=bpy.data.meshes.new('WS190b_Lot3_S_end_corner_lawn_fill'); bm.to_mesh(me); bm.free()
for p in me.polygons: p.use_smooth=True
uvl=me.uv_layers.new(name='UVMap')
for l in me.loops: v=me.vertices[l.vertex_index].co; uvl.data[l.index].uv=(v.x/10.0,v.y/10.0)
ob=bpy.data.objects.new('WS190b_Lot3_S_end_corner_lawn_fill_UNVERIFIED',me)
lw=bpy.data.objects['WS163_ground_patch_W_of_WS110_LiDAR2023_1m_UNVERIFIED']
for c in lw.users_collection: c.objects.link(ob)
me.materials.append(lw.active_material)
print('FIX190B fill',ob.name,'plane',np.round(cf,4),'fitpts',len(P),'z',round(min(v.co.z for v in me.vertices),3),round(max(v.co.z for v in me.vertices),3),flush=True)
