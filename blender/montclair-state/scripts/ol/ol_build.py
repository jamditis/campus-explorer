# ol (Oct 31 2026): Schmitt entrance walk follow-ups from ok's Next list:
# (1) a poured-concrete CURB/edge band along every floating open edge of the Footpaths_OSM slab near the entrance (the edges
#     ok's lawn embankment starts from): 12 cm wide inside the edge, 2 cm proud outside, top 1.5 cm over the slab, bottom
#     0.35 m down so the bank tucks under it; (2) the ok embankment gets smooth shading (faceted quads from the air).
# OSM, LiDAR, oh cheek wall NOT edited. UNVERIFIED (no photo of this edge). REVERT=1 removes the curb + restores flat shading.
import bpy, bmesh, os, sys
from mathutils import Vector
from mathutils.bvhtree import BVHTree
REV=os.environ.get('REVERT')=='1'; SAVE='--save' in sys.argv
CN='OL_Schmitt_walk_edge_curb_20261031ol'; MN='OL_Schmitt_walk_curb_concrete_UNVERIFIED'; NAME='OL_Schmitt_entrance_walk_edge_curb'
EMB='OK_Schmitt_entrance_walk_lawn_embankment'
c=bpy.data.collections.get(CN)
if c:
    for ob in list(c.objects):
        me=ob.data; bpy.data.objects.remove(ob)
        if me and me.users==0: bpy.data.meshes.remove(me)
    bpy.data.collections.remove(c)
m=bpy.data.materials.get(MN)
if m: bpy.data.materials.remove(m)
e=bpy.data.objects.get(EMB)
if e:
    for p in e.data.polygons: p.use_smooth = not REV
if REV:
    print('REVERTED')
    if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit(0)
C=Vector((10.6,141.1)); R=24.0
sc=bpy.context.scene; fp=bpy.data.objects['Footpaths_OSM']; ter=bpy.data.objects['Terrain_LiDAR_DTM_1m']
dg=bpy.context.evaluated_depsgraph_get()
te=ter.evaluated_get(dg); bt=bmesh.new(); bt.from_mesh(te.to_mesh()); bt.transform(ter.matrix_world); tree=BVHTree.FromBMesh(bt)
def tz(x,y):
    h=tree.ray_cast(Vector((x,y,400)),Vector((0,0,-1))); return h[0].z if h[0] is not None else None
bm=bmesh.new(); bm.from_mesh(fp.data); bm.transform(fp.matrix_world)
out=bmesh.new(); n_e=0
for ed in bm.edges:
    if not ed.is_boundary: continue
    a,b=ed.verts
    if (a.co.xy-C).length>R and (b.co.xy-C).length>R: continue
    za,zb=tz(*a.co.xy),tz(*b.co.xy)
    if za is None or zb is None or max(a.co.z-za,b.co.z-zb)<0.12: continue
    f=ed.link_faces[0]; fc=f.calc_center_median(); mid=(a.co+b.co)/2
    t=(b.co-a.co); t.z=0; L=t.length
    if L<0.05: continue
    t.normalize(); n=Vector((t.y,-t.x,0))
    if n.dot(Vector(((mid-fc).x,(mid-fc).y,0)))<0: n=-n
    ext=0.03  # small overlap at joints
    pa=a.co-t*ext; pb=b.co+t*ext
    vs=[]
    for p in (pa,pb):
        for off in (-0.12,0.02):
            for dz in (0.015,-0.35):
                q=p+n*off; vs.append(out.verts.new((q.x,q.y,p.z+dz)))
    # vs order: a_in_top,a_in_bot,a_out_top,a_out_bot,b_in_top,b_in_bot,b_out_top,b_out_bot
    F=[(0,4,6,2),(1,3,7,5),(2,6,7,3),(0,1,5,4),(0,2,3,1),(4,5,7,6)]
    for q in F: out.faces.new([vs[i] for i in q])
    n_e+=1
bmesh.ops.recalc_face_normals(out,faces=out.faces)
me=bpy.data.meshes.new(NAME); out.to_mesh(me)
mat=bpy.data.materials.new(MN); mat.use_nodes=True; nt=mat.node_tree; p=nt.nodes['Principled BSDF']
p.inputs['Base Color'].default_value=(0.56,0.55,0.53,1); p.inputs['Roughness'].default_value=0.86
nz=nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value=60; nz.inputs['Detail'].default_value=8
mr=nt.nodes.new('ShaderNodeMapRange'); mr.inputs[3].default_value=0.85; mr.inputs[4].default_value=1.08
mx=nt.nodes.new('ShaderNodeMix'); mx.data_type='RGBA'; mx.blend_type='MULTIPLY'; mx.inputs['Factor'].default_value=1.0
mx.inputs[6].default_value=(0.56,0.55,0.53,1)
nt.links.new(nz.outputs['Fac'],mr.inputs[0]); nt.links.new(mr.outputs[0],mx.inputs[7]); nt.links.new(mx.outputs[2],p.inputs['Base Color'])
bp=nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value=0.1; nt.links.new(nz.outputs['Fac'],bp.inputs['Height']); nt.links.new(bp.outputs['Normal'],p.inputs['Normal'])
me.materials.append(mat)
col=bpy.data.collections.new(CN); sc.collection.children.link(col)
o=bpy.data.objects.new(NAME,me); col.objects.link(o); o['UNVERIFIED']='ol: curb at the raised walk/lawn-bank edge guessed'
print('curb segments',n_e,'faces',len(me.polygons),'emb smooth',bool(e))
if SAVE: bpy.ops.wm.save_mainfile(); print('SAVED')
