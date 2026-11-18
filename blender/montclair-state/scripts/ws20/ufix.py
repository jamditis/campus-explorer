# ws20: give the raised top-outline verts the same facade U as the wall vertex directly below them (bottom loop twin).
import bpy,bmesh,os
from mathutils import Vector
from mathutils.kdtree import KDTree
SAVE=os.environ.get('SAVE')=='1'
o=bpy.data.objects['Life Hall walls']; M=o.matrix_world
bm=bmesh.new(); bm.from_mesh(o.data); bm.verts.ensure_lookup_table()
uvl=bm.loops.layers.uv['facade']
bot=[v for v in bm.verts if v.is_boundary and (M@v.co).z<139.0]
top=[v for v in bm.verts if v.is_boundary and (M@v.co).z>139.5]
kd=KDTree(len(bot))
for i,v in enumerate(bot): p=M@v.co; kd.insert(Vector((p.x,p.y,0)),i)
kd.balance()
n=0;big=[]
for v in top:
    p=M@v.co; co,i,d=kd.find(Vector((p.x,p.y,0)))
    if d>0.03: continue
    b=bot[i]
    # U per face-corner: match by shared face direction -> use the twin's loops in faces that also contain v
    for l in v.link_loops:
        cand=[bl for bl in b.link_loops if bl.face==l.face]
        if not cand:
            # pick twin loop on a face sharing an edge with this face
            cand=[bl for bl in b.link_loops if any(e in l.face.edges for e in bl.face.edges)]
        if not cand: continue
        du=cand[0][uvl].uv.x-l[uvl].uv.x
        if abs(du)>0.02:
            big.append((round(p.x,1),round(p.y,1),round(p.z,2),round(du,2)))
            if SAVE: l[uvl].uv.x=cand[0][uvl].uv.x
        n+=1
print('CHECKED',n,'DIFF',len(big))
for b in big[:40]: print('D',b)
if SAVE:
    bm.to_mesh(o.data); o.data.update(); bpy.ops.wm.save_mainfile(); print('SAVED')
