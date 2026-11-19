# ws232 fix a: W53b CELS/Calcia NE corner. The walk overlays (scoring joints, panel tone, lips, fillet) were built on the RAW
# Footpaths/Roads heights; the OO/OP redrape GN later lifted those walks 5-10 m onto the LiDAR/3DEP ground (probe232a: evaluated
# top ground = 3DEP within +-0.37 m; evaluated walks +0.05 m on it), leaving the overlays 7-10 m under the ground (invisible).
# Faces whose verts ALL sit over paving are lifted by the exact redrape dz at that xy (probe232b, overlay offset kept); the other
# buried faces in the box (over lawn/fillet edges, extent UNVERIFIED) are deleted - they are invisible and would stretch 9 m.
import bpy, bmesh, json
MS='/workspace/nj-scenes/montclair-state/'
T=json.load(open(MS+'scripts/ws232/lift232_targets.json')); rep={}
for n,res in T.items():
    o=bpy.data.objects[n]; me=o.data
    if me.users>1: o.data=me.copy(); me=o.data
    Wi=o.matrix_world.inverted(); W=o.matrix_world
    bm=bmesh.new(); bm.from_mesh(me); bm.verts.ensure_lookup_table()
    R={int(k):v for k,v in res.items()}
    lift=[f for f in bm.faces if all(v.index in R and R[v.index][1] for v in f.verts)]
    dele=[f for f in bm.faces if any(v.index in R for v in f.verts) and f not in set(lift)]
    lv=set(v for f in lift for v in f.verts)
    # verts shared by a lifted face and a deleted face: lifted (the deleted face goes away)
    for v in lv:
        w=W@v.co; w.z=R[v.index][0]; v.co=Wi@w
    bmesh.ops.delete(bm,geom=dele,context='FACES')
    loose=[v for v in bm.verts if not v.link_faces and v.index in R]
    bmesh.ops.delete(bm,geom=loose,context='VERTS')
    bm.to_mesh(me); bm.free(); me.update()
    rep[n]={'lifted_faces':len(lift),'deleted_faces':len(dele),'lifted_verts':len(lv)}
    print('F232A',n,rep[n],flush=True)
json.dump(rep,open(MS+'scripts/ws232/fix232a_report.json','w'))
