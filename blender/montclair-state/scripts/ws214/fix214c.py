# ws214c W35 part: pave the unpaved wedge(s) beside the Red Hawk Deck College Ave entrance apron, where only the WS68 grass ground
# shows between the KY road edge / LH gutter, KX_drive_apron and the KY_rhd side-walk fill (Joe's Sep 2021 Street View: continuous
# sidewalk/paving either side of the entrance at street level). 0.25 m cells, kept only if WS68 is the top surface AND paving lies
# within 1.2 m on at least 2 sides; z = IDW of the surrounding paving tops - 4 mm. Material = KY_rhd_drive_side_walk_fill's (or KX concrete).
import bpy, bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree
def ob(p): return next((o for o in bpy.data.objects if o.name.startswith(p)),None)
PV=[ob(p) for p in ('KX_drive_apron','KY_college_ave_carriageway_asphalt','KY_rhd_drive_side_walk_fill','LH_college_ave_gutter_asphalt_fill')]
G=ob('WS68_RHD_ground_northDTM')
if None in PV or G is None or ob('WS214_rhd_entry_wedge'): print('F214 c skip',flush=True)
else:
    def bvh(o): M=o.matrix_world; return BVHTree.FromPolygons([M@v.co for v in o.data.vertices],[p.vertices[:] for p in o.data.polygons])
    TP=[bvh(o) for o in PV]; TG=bvh(G)
    def top(x,y,TT):
        b=None
        for t in TT:
            h=t.ray_cast(Vector((x,y,200)),Vector((0,0,-1)),300)
            if h[0] is not None and (b is None or h[0].z>b): b=h[0].z
        return b
    X0,X1,Y0,Y1,D=-268.5,-263.0,-51.5,-43.5,0.25
    nx=int((X1-X0)/D); ny=int((Y1-Y0)/D)
    hole={}
    for i in range(nx):
        for j in range(ny):
            x=X0+(i+0.5)*D; y=Y0+(j+0.5)*D
            if top(x,y,TP) is None and top(x,y,[TG]) is not None: hole[i,j]=1
    keep=[]
    for (i,j) in hole:
        x=X0+(i+0.5)*D; y=Y0+(j+0.5)*D; sides=0
        for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
            for k in range(1,6):
                if top(x+dx*k*D,y+dy*k*D,TP) is not None: sides+=1; break
        if sides>=3: keep.append((i,j))
    samp=[]
    for i in range(-4,nx+4):
        for j in range(-4,ny+4):
            x=X0+i*D; y=Y0+j*D; z=top(x,y,TP)
            if z is not None: samp.append((x,y,z))
    def zi(x,y):
        ws=[(1/((x-a)**2+(y-b)**2+1e-3)**1.5,z) for a,b,z in samp if (x-a)**2+(y-b)**2<2.0]
        return sum(w*z for w,z in ws)/sum(w for w,z in ws) if ws else None
    bm=bmesh.new(); V={}
    def vv(i,j):
        if (i,j) not in V:
            x=X0+i*D; y=Y0+j*D; z=zi(x,y); V[i,j]=bm.verts.new((x,y,(z if z is not None else 124.5)-0.004))
        return V[i,j]
    for (i,j) in keep:
        bm.faces.new((vv(i-0+0,j),vv(i+1,j),vv(i+1,j+1),vv(i,j+1)))
    for f in bm.faces:
        if f.normal.z<0: f.normal_flip()
    m=bpy.data.meshes.new('WS214_wedge'); bm.to_mesh(m); bm.free()
    o=bpy.data.objects.new('WS214_rhd_entry_wedge_paving_fill_streetview2021_UNVERIFIED',m)
    src=PV[2] if PV[2].data.materials and PV[2].data.materials[0] else PV[0]
    m.materials.append(src.data.materials[0] if src.data.materials else PV[0].data.materials[0])
    for c in PV[0].users_collection: c.objects.link(o)
    print('F214 c holes',len(hole),'filled cells',len(keep),'mat',m.materials[0].name if m.materials[0] else None,flush=True)
