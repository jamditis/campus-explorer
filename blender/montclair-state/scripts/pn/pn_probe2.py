import bpy, numpy as np, json
w=bpy.data.objects['Feliciano School of Business walls']; mw=w.matrix_world
fs=[]
for p in w.data.polygons:
    c=[tuple(round(x,2) for x in (mw@w.data.vertices[v].co)) for v in p.vertices]
    fs.append(c)
r=bpy.data.objects['Feliciano School of Business roof (LiDAR)']; mr=r.matrix_world
V=np.array([tuple(mr@v.co) for v in r.data.vertices])
F=[list(p.vertices) for p in r.data.polygons]; M=[p.material_index for p in r.data.polygons]
json.dump({'walls':fs,'V':V.tolist(),'F':F,'M':M},open('data/pn/feli.json','w'))
print('DONE', w.data.polygons[0].material_index)
