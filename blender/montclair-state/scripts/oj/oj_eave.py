# oj (Oct 31 2026): deeper ESE wing eave after schmitt_01 (deep red soffit + tall red fascia under the tile edge).
# Adds a 0.8 m extension outside the existing eave edge (o -3.95..-3.15 in the entrance frame; existing eave ends at -3.91,
# so it tucks 4 cm under the eave edge, no coplanar faces), sloped tile top, red soffit underside, red fascia face, and
# 18 red bracket extensions under it at the oi bracket positions. Stops at |a|>=3.85 (pavilion) and 0.9 m short of the corners.
# New collection OJ_Schmitt_wing_eave_deeper_20261031oj; nothing hidden/edited. REVERT=1 removes it. Sizes UNVERIFIED.
import bpy, bmesh, os, sys
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'; CN='OJ_Schmitt_wing_eave_deeper_20261031oj'
c=bpy.data.collections.get(CN)
if c:
    for ob in list(c.objects):
        me=ob.data; bpy.data.objects.remove(ob)
        if me and me.users==0: bpy.data.meshes.remove(me)
    bpy.data.collections.remove(c)
if REV:
    print('REVERTED')
    if '--save' in sys.argv: bpy.ops.wm.save_mainfile(); print('SAVED')
    raise SystemExit(0)
fr=bpy.data.objects['OG_Schmitt_E_entrance_storefront_frame']; la=bpy.data.objects['OG_Schmitt_E_entrance_landing']
fv=[fr.matrix_world@v.co for v in fr.data.vertices]; lb=[la.matrix_world@v.co for v in la.data.vertices]
cen=sum(fv,Vector())/len(fv); lc=sum(lb,Vector())/len(lb); cen.z=0
OUT=Vector(((lc-cen).x,(lc-cen).y,0)).normalized(); AL=Vector((-OUT.y,OUT.x,0))
def P(a,o,z): return cen+AL*a+OUT*o+Vector((0,0,z))
def L(w): d=w-cen; return d.dot(AL),d.dot(OUT),w.z
col=bpy.data.collections.new(CN); bpy.context.scene.collection.children.link(col)
M_tile=bpy.data.materials['OI_Schmitt_pavilion_roof_tile_UNVERIFIED']; M_red=bpy.data.materials['OI_Schmitt_overhang_red_UNVERIFIED']
O0,O1=-3.95,-3.15; ZB=148.04; ZT0,ZT1=148.66,148.38
SEG=[(-28.3,-3.85),(3.85,43.5)]
bm=bmesh.new()
for a0,a1 in SEG:
    v=[bm.verts.new(P(a,o,z)) for a,o,z in ((a0,O0,ZB),(a1,O0,ZB),(a1,O1,ZB),(a0,O1,ZB),(a0,O0,ZT0),(a1,O0,ZT0),(a1,O1,ZT1),(a0,O1,ZT1))]
    for f,mi in (((0,3,2,1),1),((4,5,6,7),0),((0,1,5,4),1),((1,2,6,5),1),((2,3,7,6),1),((3,0,4,7),1)):
        F=bm.faces.new([v[i] for i in f]); F.material_index=mi
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
me=bpy.data.meshes.new('OJ_Schmitt_wing_eave_extension'); bm.to_mesh(me); bm.free(); me.materials.append(M_tile); me.materials.append(M_red)
o=bpy.data.objects.new('OJ_Schmitt_wing_eave_extension',me); col.objects.link(o); o['UNVERIFIED']='oj: eave depth from schmitt_01 proportions'
br=bpy.data.objects['OI_Schmitt_wing_eave_brackets']; ws=[L(br.matrix_world@v.co) for v in br.data.vertices]
bm=bmesh.new(); n=0
for i in range(0,len(ws),8):
    ch=ws[i:i+8]; a=sum(w[0] for w in ch)/8; hw=(max(w[0] for w in ch)-min(w[0] for w in ch))/2
    if not any(a0+0.2<a<a1-0.2 for a0,a1 in SEG): continue
    zb=min(w[2] for w in ch)+0.15
    v=[bm.verts.new(P(aa,oo,zz)) for aa,oo,zz in ((a-hw,-3.99,zb),(a+hw,-3.99,zb),(a+hw,-3.30,ZB-0.005),(a-hw,-3.30,ZB-0.005),(a-hw,-3.99,ZB-0.005),(a+hw,-3.99,ZB-0.005))]
    # wedge: bottom slope from bracket tip to the soffit
    for f in ((0,1,2,3),(0,4,5,1),(3,2,5,4),(0,3,4),(1,5,2)): bm.faces.new([v[k] for k in f])
    n+=1
bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
me=bpy.data.meshes.new('OJ_Schmitt_wing_eave_bracket_extensions'); bm.to_mesh(me); bm.free(); me.materials.append(M_red)
o=bpy.data.objects.new('OJ_Schmitt_wing_eave_bracket_extensions',me); col.objects.link(o); o['UNVERIFIED']='oj'
print('OJ EAVE built, brackets',n)
if '--save' in sys.argv: bpy.ops.wm.save_mainfile(); print('SAVED')
