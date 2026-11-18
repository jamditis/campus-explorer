# pq: flip inward-facing vertical faces of the old 'Feliciano School of Business walls' mesh (LiDAR walls with inverted normals
# render grey against the white tier walls). Flipped face indices stored in face attr pq_flip; REVERT=1 flips them back.
import bpy, os, json, bmesh
from mathutils import Vector
REV=os.environ.get('REVERT')=='1'
o=bpy.data.objects['Feliciano School of Business walls']; me=o.data; mw=o.matrix_world
D=json.load(open('data/po/polys.json')); C=Vector((D['cx'],D['cy'],0))
bm=bmesh.new(); bm.from_mesh(me); lay=bm.faces.layers.int.get('pq_flip') or bm.faces.layers.int.new('pq_flip')
n=0
if REV:
    for f in bm.faces:
        if f[lay]: f.normal_flip(); n+=1
    bm.faces.layers.int.remove(lay)
else:
    for f in bm.faces:
        if f[lay]: continue
        nw=mw.to_3x3()@f.normal
        if abs(nw.z)>0.3: continue
        c=mw@f.calc_center_median(); r=c-C; r.z=0; nw.z=0
        if nw.length<1e-6: continue
        if nw.normalized().dot(r.normalized())<-0.2: f.normal_flip(); f[lay]=1; n+=1
bm.to_mesh(me); bm.free(); me.update()
print('PQ_FLIP',n,'faces REV',REV,'of',len(me.polygons),'users',me.users,'lib',o.library, me.library)
