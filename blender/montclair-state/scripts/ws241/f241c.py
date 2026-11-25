# W58 notch (ws241): M3a has no faces in a notch S of the NJT deck SW corner (x -137..-113, y 935..968); the raw 3DEP skirt
# there dips to 107.3 (2-3 m under the M3a edge at the deck corner) = the "black pit". The deck's lowest slab top is ~110.3
# and the north DTM all round is 109.3-111.4, so a 3 m basin at the deck corner is not credible (UNVERIFIED; 3DEP may hold
# a pre-construction / drainage hollow). New lawn patch WS241_NJT_deck_SW_notch_ground_fill_UNVERIFIED: 1 m grid; verts under
# M3a take M3a z - 0.03 (tucked under, no z-fight); free verts = inverse-distance blend of the notch's M3a edge verts and
# raw skirt heights along the open SW side (probe241a_W). Same materials as M3a; UVs from a least-squares affine fit of M3a's
# (v2) faces appended into M3a's own mesh. Faces only where a corner is off M3a and outside the deck footprint.
import bpy, bmesh, json, math
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
g=bpy.data.objects['M3a_north_LiDAR_DTM_1m_ext_y515_UNVERIFIED_seam']; G=g.matrix_world
me=g.data
GB=BVHTree.FromPolygons([G@v.co for v in me.vertices],[p.vertices[:] for p in me.polygons])
dk=bpy.data.objects['NJ Transit Deck']; M=dk.matrix_world
DB=BVHTree.FromPolygons([M@v.co for v in dk.data.vertices],[p.vertices[:] for p in dk.data.polygons])
X0,X1,Y0,Y1=-141,-111,929,971
bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
ctrl=[]
for v in bm.verts:
    if v.is_boundary:
        p=G@v.co
        if X0-2<=p.x<=X1+2 and Y0-2<=p.y<=Y1+2: ctrl.append((p.x,p.y,p.z))
bm.free()
ne=len(ctrl)
ctrl+= [tuple(c) for c in json.load(open('/workspace/nj-scenes/montclair-state/scripts/ws241/notch_open_ctrl.json'))]
C=np.array(ctrl)
def idw(x,y):
    d=np.hypot(C[:,0]-x,C[:,1]-y); k=np.argsort(d)[:10]; w=1.0/np.maximum(d[k],0.3)**2
    return float((C[k,2]*w).sum()/w.sum())
def m3a(x,y):
    h=GB.ray_cast(Vector((x,y,200)),Vector((0,0,-1))); return h[0].z if h[0] is not None else None
def indeck(x,y):
    h=DB.ray_cast(Vector((x,y,100.0)),Vector((0,0,1)),30.0); return h[0] is not None and h[0].z<112
nb=bmesh.new(); V={}; free={}
for i in range(X1-X0+1):
    for j in range(Y1-Y0+1):
        x=X0+i; y=Y0+j; z=m3a(x,y)
        free[i,j]= z is None and not indeck(x,y)
        V[i,j]=nb.verts.new((x,y,(z-0.03) if z is not None else idw(x,y)))
nf=0
for i in range(X1-X0):
    for j in range(Y1-Y0):
        q=[(i,j),(i+1,j),(i+1,j+1),(i,j+1)]
        if any(free[k] for k in q) and not any(indeck(X0+k[0],Y0+k[1]) for k in q):
            nb.faces.new([V[k] for k in q]); nf+=1
for v in [v for v in nb.verts if not v.link_faces]: nb.verts.remove(v)
# v2: append into M3a itself (same material, object coords and attributes; M3a has no UV layers)
mi=[p.material_index for p in me.polygons if X0-20<=(G@p.center).x<=X1+20 and Y0-20<=(G@p.center).y<=Y1+20]
mi=max(set(mi),key=mi.count) if mi else 0
for f in nb.faces: f.material_index=mi; f.smooth=True
Gi=G.inverted()
for v in nb.verts: v.co=Gi@v.co
tmp=bpy.data.meshes.new('tmp241c'); nb.to_mesh(tmp); nb.free(); zs=[v.co.z for v in tmp.vertices]
bm=bmesh.new(); bm.from_mesh(me); n0=len(bm.verts); bm.from_mesh(tmp); bm.to_mesh(me); me.update(); bm.free(); bpy.data.meshes.remove(tmp)
print('F241C notch fill appended into M3a: faces',nf,'new verts',len(me.vertices)-n0,'edge ctrl',ne,'open ctrl',len(ctrl)-ne,'z',round(min(zs),2),round(max(zs),2),'mat',mi,flush=True)
