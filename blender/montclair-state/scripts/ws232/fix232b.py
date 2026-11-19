# ws232 fix b (on ws232a): the fix232a redrape-dz lift left the overlays -3..+1.1 m off the evaluated walks (probe232d: the raw
# base surface under them is not the one they were built on). Lifted verts are SNAPPED instead to the evaluated Footpaths/Roads top
# at their xy + decal offset (tone 0.008, joints 0.012; probe232e). The CELS road curb lip OW3 + smoothed lip OX in the box (all
# buried before; a curb lip under a draped walk edge can't be placed from this data, UNVERIFIED) are removed in the box.
import bpy, bmesh, json
MS='/workspace/nj-scenes/montclair-state/'
T=json.load(open(MS+'scripts/ws232/snap232_targets.json')); rep={}
for n,res in T.items():
    o=bpy.data.objects[n]; W=o.matrix_world; Wi=W.inverted(); me=o.data
    for k,z in res.items():
        v=me.vertices[int(k)]; w=W@v.co; w.z=z; v.co=Wi@w
    me.update(); rep[n]={'snapped':len(res)}
for n in ('OW3_CELS_walk_road_curb_lip_UNVERIFIED','OX_CELS_walk_road_lip_smoothed_UNVERIFIED'):
    o=bpy.data.objects[n]; W=o.matrix_world; bm=bmesh.new(); bm.from_mesh(o.data)
    df=[f for f in bm.faces if all(112<(W@v.co).x<152 and 182<(W@v.co).y<252 for v in f.verts)]
    bmesh.ops.delete(bm,geom=df,context='FACES'); lv=[v for v in bm.verts if not v.link_faces]; bmesh.ops.delete(bm,geom=lv,context='VERTS')
    bm.to_mesh(o.data); bm.free(); rep[n]={'deleted_faces_in_box':len(df),'faces_left':len(o.data.polygons)}
print('F232B',json.dumps(rep),flush=True)
json.dump(rep,open(MS+'scripts/ws232/fix232b_report.json','w'))
