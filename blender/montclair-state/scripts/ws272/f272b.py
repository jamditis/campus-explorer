# ws272b (merge208 CHAIN, on ws272a): after the #4c fill, the 1.5-1.9 m strip of WS60_terrain_edge_apron between WS68's S edge
# (y -135) and the Panzer gym N wall (y ~ -136.8) shows as a flat dark grey-green band against the lawn, with a small lip.
# Extend WS68 (same lawn material) over that strip: one new row at y -136.9 (0.1 m inside the wall line, hidden by the wall)
# draped 3 cm over the apron, quads to the S row x -278...-248.6, 'ortho' UVs from an affine fit to the nearby WS68 UVs.
# Lawn up to the wall = UNVERIFIED (no photo of Panzer's N side; the 2020 ortho is in the gym roof's shadow here).
import bpy, bmesh, numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
TAG='F272B'; OB=bpy.data.objects
A=[o for o in OB if o.name.startswith('WS68_RHD_ground_northDTM')][0]
ap=[o for o in OB if o.name.startswith('WS60_terrain_edge_apron')][0]; amw=ap.matrix_world
TA=BVHTree.FromPolygons([amw@v.co for v in ap.data.vertices],[p.vertices[:] for p in ap.data.polygons])
bm=bmesh.new(); bm.from_mesh(A.data); bm.verts.ensure_lookup_table(); uvl=bm.loops.layers.uv['ortho']
P=[];U=[]
for f in bm.faces:
    c=f.calc_center_median()
    if -282<c.x<-246 and -136<c.y<-124:
        for l in f.loops: P.append((l.vert.co.x,l.vert.co.y,1.0)); U.append(tuple(l[uvl].uv))
P=np.array(P);U=np.array(U); M,res,_,_=np.linalg.lstsq(P,U,rcond=None); err=np.abs(P@M-U).max()
print(TAG,'uv affine fit samples',len(P),'max err',err,flush=True)
srow={}
for v in bm.verts:
    if abs(v.co.y+135)<0.01 and -278.01<=v.co.x<=-248.5: srow[round(v.co.x,1)]=v
xs=sorted(srow); print(TAG,'S row verts',len(xs),xs[0],xs[-1],flush=True)
assert all(sum(1 for f in srow[x].link_faces)>0 for x in xs)
YN=-136.9; new={}
for x in xs:
    h=TA.ray_cast(Vector((x,YN,300)),Vector((0,0,-1)))
    if h[0] is None: h=TA.ray_cast(Vector((x,-136.5,300)),Vector((0,0,-1)))
    z=(h[0].z if h[0] else srow[x].co.z)+0.03
    new[x]=bm.verts.new((x,YN,z))
nf=0
for a,b in zip(xs[:-1],xs[1:]):
    e=[srow[a],srow[b]]
    f=bm.faces.new((srow[a],new[a],new[b],srow[b]))
    f.normal_update()
    if f.normal.z<0: f.normal_flip()
    f.material_index=0; f.smooth=srow[a].link_faces[0].smooth
    for l in f.loops: l[uvl].uv=tuple(np.array([l.vert.co.x,l.vert.co.y,1.0])@M)
    nf+=1
print(TAG,'new faces',nf,'z range',round(min(v.co.z for v in new.values()),2),round(max(v.co.z for v in new.values()),2),flush=True)
bm.to_mesh(A.data); bm.free(); A.data.update()
