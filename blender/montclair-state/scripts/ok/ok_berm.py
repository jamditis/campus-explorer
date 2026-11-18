# ok: the Footpaths_OSM slab floats up to ~1.7 m above LiDAR terrain near the Schmitt ESE entrance (seen from the NNE eye view
# as a white slab on a long grey oh cheek wall). Non-destructive fix: a graded LAWN EMBANKMENT strip from each floating open
# slab edge (2 cm under the edge) out and down to the terrain (5 cm under it) at ~1:2, which hides the cheek wall from outside,
# like the at-grade walk + lawn in schmitt_01. OSM plane, LiDAR and the oh cheek wall are NOT edited. UNVERIFIED (no photo of
# this spot's grading). REVERT=1 removes.  Usage: blender -b main --python ok_berm.py -- --save
import bpy, bmesh, os, sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
CN='OK_Schmitt_walk_lawn_embankment_20261031ok'; MN='OK_Schmitt_embankment_lawn_UNVERIFIED'; NAME='OK_Schmitt_entrance_walk_lawn_embankment'
REV=os.environ.get('REVERT')=='1'
c=bpy.data.collections.get(CN)
if c:
    for ob in list(c.objects):
        me=ob.data; bpy.data.objects.remove(ob)
        if me and me.users==0: bpy.data.meshes.remove(me)
    bpy.data.collections.remove(c)
m=bpy.data.materials.get(MN)
if m: bpy.data.materials.remove(m)
if REV:
    print('REVERTED')
    if '--save' in sys.argv: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit(0)
C=Vector((10.6,141.1)); R=float(os.environ.get('R','24'))
fp=bpy.data.objects['Footpaths_OSM']; ter=bpy.data.objects['Terrain_LiDAR_DTM_1m']
dg=bpy.context.evaluated_depsgraph_get()
te=ter.evaluated_get(dg); bt=bmesh.new(); bt.from_mesh(te.to_mesh()); bt.transform(ter.matrix_world); tree=BVHTree.FromBMesh(bt)
def tz(x,y):
    h=tree.ray_cast(Vector((x,y,400)),Vector((0,0,-1))); return h[0].z if h[0] is not None else None
# building guard: don't push lawn into Schmitt / pavilion (stop where a ray hits a wall)
sc=bpy.context.scene
bm=bmesh.new(); bm.from_mesh(fp.data); bm.transform(fp.matrix_world); bm.verts.ensure_lookup_table()
edges=[]
for e in bm.edges:
    if not e.is_boundary: continue
    a,b=e.verts
    if (a.co.xy-C).length>R and (b.co.xy-C).length>R: continue
    za,zb=tz(*a.co.xy),tz(*b.co.xy)
    if za is None or zb is None: continue
    if max(a.co.z-za,b.co.z-zb)<0.12: continue
    f=e.link_faces[0]; fc=f.calc_center_median(); mid=(a.co+b.co)/2
    t=(b.co-a.co); t.z=0; t.normalize(); n=Vector((t.y,-t.x,0))
    if n.dot(Vector(((mid-fc).x,(mid-fc).y,0)))<0: n=-n
    edges.append((a.index,b.index,n))
vn={}
for ia,ib,n in edges:
    for i in (ia,ib): vn.setdefault(i,Vector((0,0,0))); vn[i]+=n
out=bmesh.new(); top={}; bot={}; mx=0; nguard=0
for i,n in vn.items():
    v=bm.verts[i].co; n=n.normalized(); z0=tz(v.x,v.y); hgt=max(v.z-z0,0.0); mx=max(mx,hgt)
    d=max(0.6,2.0*hgt)
    h,l,_,_,ob,_=sc.ray_cast(dg,Vector((v.x,v.y,v.z+0.3)),n,distance=d)
    if h and ob and ob.name!=NAME and ob.name not in ('Footpaths_OSM','Terrain_LiDAR_DTM_1m') and not ob.name.startswith('T_'):
        d=max(0.05,(l-Vector((v.x,v.y,v.z+0.3))).length-0.15); nguard+=1
    q=v+n*d; zq=tz(q.x,q.y) or z0
    top[i]=out.verts.new((v.x,v.y,v.z-0.02)); bot[i]=out.verts.new((q.x,q.y,zq-0.05))
for ia,ib,n in edges:
    try: out.faces.new([top[ia],top[ib],bot[ib],bot[ia]])
    except ValueError: pass
bmesh.ops.recalc_face_normals(out,faces=out.faces)
for f in out.faces:
    if f.normal.z<0: f.normal_flip()
me=bpy.data.meshes.new(NAME); out.to_mesh(me)
col=bpy.data.collections.new(CN); sc.collection.children.link(col)
o=bpy.data.objects.new(NAME,me); col.objects.link(o); o['UNVERIFIED']='ok: grading guessed (schmitt_01 shows walk at grade with lawn)'
# reuse the terrain's own ortho-draped grass (Ground_ortho_grass, UV 'ortho') so the strip blends with the LiDAR lawn:
# fit the terrain's ortho UV as an affine function of world x,y and write the same UVs on the strip
import numpy as np
tm=ter.data; uvl=tm.uv_layers['ortho']; Mw=ter.matrix_world
A=[];U=[]
for lp in tm.loops:   # local fit: terrain loops within 45 m of the entrance
    co=Mw@tm.vertices[lp.vertex_index].co
    if (co.xy-C).length<45: A.append((co.x,co.y,1.0)); U.append(tuple(uvl.data[lp.index].uv))
A=np.array(A); U=np.array(U); coef,res,_,_=np.linalg.lstsq(A,U,rcond=None)
err=float(np.abs(A@coef-U).max()); print('ortho uv affine fit max err',err)
ul=me.uv_layers.new(name='ortho')
for lp in me.loops:
    co=me.vertices[lp.vertex_index].co; ul.data[lp.index].uv=tuple(np.array((co.x,co.y,1.0))@coef)
m=bpy.data.materials['Ground_ortho_grass']
me.materials.append(m)
print('embankment faces',len(me.polygons),'edges',len(edges),'max float',round(mx,2),'guarded',nguard)
if '--save' in sys.argv: bpy.ops.wm.save_mainfile(); print('SAVED')
