import bpy,json
dg=bpy.context.evaluated_depsgraph_get()
o=bpy.data.objects['OZ_walk_joints_auto_GN_UNVERIFIED']; oe=o.evaluated_get(dg); me=oe.to_mesh(); M=o.matrix_world
F=[]
for p in me.polygons:
    vs=[M@me.vertices[i].co for i in p.vertices]
    c=sum(vs,type(vs[0])())/len(vs)
    if 0<=c.x<60 and 100<=c.y<135: F.append([[round(v.x,2),round(v.y,2)] for v in vs])
print('OZF',len(me.polygons),len(F))
json.dump(F,open('/workspace/nj-scenes/montclair-state/scripts/ws22/oz_faces.json','w'))
f=bpy.data.objects['Footpaths_OSM']; fe=f.evaluated_get(dg); fm=fe.to_mesh(); FM=f.matrix_world
G=[]
for p in fm.polygons:
    if p.normal.z<0.7: continue
    vs=[FM@fm.vertices[i].co for i in p.vertices]; c=sum(vs,type(vs[0])())/len(vs)
    if 0<=c.x<60 and 100<=c.y<135: G.append([[round(v.x,2),round(v.y,2)] for v in vs])
json.dump(G,open('/workspace/nj-scenes/montclair-state/scripts/ws22/fp_faces.json','w')); print('FPF',len(G))
