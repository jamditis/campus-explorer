# ws272 probe (no save): WS68 evaluated (its own modifiers on) vs base in the #4c band; seam step to the apron at y -135.
import bpy, bmesh, numpy as np, os
from mathutils import Vector
from mathutils.bvhtree import BVHTree
OB=bpy.data.objects
A=[o for o in OB if o.name.startswith('WS68_RHD_ground_northDTM')][0]
for m in A.modifiers: m.show_viewport=True
dg=bpy.context.evaluated_depsgraph_get(); oe=A.evaluated_get(dg); me=oe.to_mesh()
bm=bmesh.new(); bm.from_mesh(me)
bmesh.ops.delete(bm,geom=[f for f in bm.faces if not any(-282<v.co.x<-246 and -137<v.co.y<-122 for v in f.verts)],context='FACES')
TE=BVHTree.FromBMesh(bm); bm.free(); oe.to_mesh_clear()
TB=BVHTree.FromPolygons([v.co for v in A.data.vertices],[p.vertices[:] for p in A.data.polygons])
ap=[o for o in OB if o.name.startswith('WS60_terrain_edge_apron')][0]
TA=BVHTree.FromPolygons([ap.matrix_world@v.co for v in ap.data.vertices],[p.vertices[:] for p in ap.data.polygons])
def h(t,x,y):
    r=t.ray_cast(Vector((x,y,300)),Vector((0,0,-1))); return r[0].z if r[0] else np.nan
D=[];S=[]
for y in np.arange(-126.5,-135,-1.0):
    for x in np.arange(-278.5,-249,1.0): D.append(h(TE,x,y)-h(TB,x,y))
for x in np.arange(-277.5,-249,1.0): S.append(h(TE,x,-134.9)-h(TA,x,-135.1))
D=np.array(D);S=np.array(S)
print('P272C eval-base max|d|',np.nanmax(np.abs(D)).round(3),'nan',int(np.isnan(D).sum()))
print('P272C S-edge step (WS68 eval @-134.9 minus apron @-135.1): max',np.nanmax(np.abs(S)).round(2),'mean',np.nanmean(S).round(2))
for y in (-126.5,-130.5,-133.5,-134.9):
    print('P272C eval y',y,' '.join(f'{h(TE,x,y):.1f}' for x in np.arange(-278.5,-249,2.0)))
import sys; sys.stdout.flush(); os._exit(0)
