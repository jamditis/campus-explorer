# dump boundary loops (world xy) of named objects to json
import bpy, bmesh, json, os
M='/workspace/nj-scenes/montclair-state/montclair_state.blend'
PF=tuple(os.environ['PF'].split('|'))
with bpy.data.libraries.load(M) as (a,b):
    b.objects=[n for n in a.objects if n.startswith(PF)]
out={}
for o in b.objects:
    bm=bmesh.new(); bm.from_mesh(o.data); mw=o.matrix_world
    E=[[tuple((mw@v.co)[:3]) for v in e.verts] for e in bm.edges if e.is_boundary]
    out[o.name]=E; print('O206',o.name,len(o.data.vertices),len(E)); bm.free()
json.dump(out,open(os.environ['OUT'],'w'))
