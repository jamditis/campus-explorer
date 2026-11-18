# ol: lawn CAPS over the small enclosed lawn islands inside the raised Footpaths_OSM walk network near the Schmitt entrance
# (hole loops whose whole rim floats >0.3 m over the LiDAR ground: dark pits from eye level, lawn 'pyramids' from the air).
# The cap is draped on the rim 3 cm under the slab edge (ngon -> beauty triangulation), terrain's own Ground_ortho_grass with
# a locally fitted 'ortho' UV. Assumes the lawn sits at walk grade (as in schmitt_01) — UNVERIFIED. OSM/LiDAR NOT edited.
# REVERT=1 removes.  Usage: blender -b main --python ol_islands.py -- --save
import bpy, bmesh, os, sys
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
REV=os.environ.get('REVERT')=='1'; SAVE='--save' in sys.argv
CN='OL_Schmitt_walk_island_lawn_caps_20261031ol'; NAME='OL_Schmitt_walk_island_lawn_caps'
c=bpy.data.collections.get(CN)
if c:
    for ob in list(c.objects):
        me=ob.data; bpy.data.objects.remove(ob)
        if me and me.users==0: bpy.data.meshes.remove(me)
    bpy.data.collections.remove(c)
if REV:
    print('REVERTED')
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit(0)
C=Vector((10.6,141.1)); R=float(os.environ.get('R','45'))
sc=bpy.context.scene; fp=bpy.data.objects['Footpaths_OSM']; ter=bpy.data.objects['Terrain_LiDAR_DTM_1m']
dg=bpy.context.evaluated_depsgraph_get()
bt=bmesh.new(); bt.from_mesh(ter.evaluated_get(dg).to_mesh()); bt.transform(ter.matrix_world); tree=BVHTree.FromBMesh(bt)
def tz(x,y):
    h=tree.ray_cast(Vector((x,y,400)),Vector((0,0,-1))); return h[0].z if h[0] is not None else None
bm=bmesh.new(); bm.from_mesh(fp.data); bm.transform(fp.matrix_world)
seen=set(); loops=[]
for e in bm.edges:
    if not e.is_boundary or e.index in seen: continue
    loop=[]; cur=e; v=e.verts[0]
    while cur and cur.index not in seen:
        seen.add(cur.index); loop.append(v.co.copy()); v=cur.other_vert(v)
        nxt=[x for x in v.link_edges if x.is_boundary and x.index not in seen]; cur=nxt[0] if nxt else None
    loops.append(loop)
out=bmesh.new(); used=[]
for L in loops:
    cx=sum(p.x for p in L)/len(L); cy=sum(p.y for p in L)/len(L)
    if (Vector((cx,cy))-C).length>R or len(L)<3: continue
    a=0.5*abs(sum(L[i].x*L[(i+1)%len(L)].y-L[(i+1)%len(L)].x*L[i].y for i in range(len(L))))
    if a>400: continue
    fl=[p.z-(tz(p.x,p.y) or p.z) for p in L]
    if min(fl)<0.3: continue
    vs=[out.verts.new((p.x,p.y,p.z-0.03)) for p in L]
    try: f=out.faces.new(vs)
    except ValueError: continue
    used.append((round(cx,1),round(cy,1),round(a,1),round(min(fl),2),round(max(fl),2)))
bmesh.ops.triangulate(out,faces=out.faces[:],quad_method='BEAUTY',ngon_method='BEAUTY')
bmesh.ops.recalc_face_normals(out,faces=out.faces)
for f in out.faces:
    if f.normal.z<0: f.normal_flip()
me=bpy.data.meshes.new(NAME); out.to_mesh(me)
for p in me.polygons: p.use_smooth=True
tm=ter.data; uvl=tm.uv_layers['ortho']; Mw=ter.matrix_world; A=[];U=[]
for lp in tm.loops:
    co=Mw@tm.vertices[lp.vertex_index].co
    if (co.xy-C).length<45: A.append((co.x,co.y,1.0)); U.append(tuple(uvl.data[lp.index].uv))
A=np.array(A); U=np.array(U); coef=np.linalg.lstsq(A,U,rcond=None)[0]; print('uv fit err',float(np.abs(A@coef-U).max()))
ul=me.uv_layers.new(name='ortho')
for lp in me.loops:
    co=me.vertices[lp.vertex_index].co; ul.data[lp.index].uv=tuple(np.array((co.x,co.y,1.0))@coef)
me.materials.append(bpy.data.materials['Ground_ortho_grass'])
col=bpy.data.collections.new(CN); sc.collection.children.link(col)
o=bpy.data.objects.new(NAME,me); col.objects.link(o); o['UNVERIFIED']='ol: lawn assumed at walk grade inside raised walk islands'
print('ISLANDS',used,'tris',len(me.polygons))
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
