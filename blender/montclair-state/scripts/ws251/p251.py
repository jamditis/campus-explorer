# ws251 read-only: Terrain faces overlapping the W63b passage box, base vs evaluated; modifier stack
import bpy, os, numpy as np
F='/workspace/nj-scenes/montclair-state/'+os.environ.get('F','montclair_state.blend')
with bpy.data.libraries.load(F) as (a,b): b.objects=['Terrain_LiDAR_DTM_1m']
T=b.objects[0]; bpy.context.scene.collection.objects.link(T)
print('P251 mods',[(m.name,m.type,m.show_render) for m in T.modifiers],flush=True)
M=T.matrix_world
box=(-196,-174,138,174)
def scan(me,lab):
    out=[]
    for p in me.polygons:
        vs=[M@me.vertices[i].co for i in p.vertices]
        xs=[v.x for v in vs]; ys=[v.y for v in vs]
        if max(xs)<box[0] or min(xs)>box[1] or max(ys)<box[2] or min(ys)>box[3]: continue
        out.append((round(p.area,1),len(vs),round(min(xs),1),round(max(xs),1),round(min(ys),1),round(max(ys),1),round(min(v.z for v in vs),2),round(max(v.z for v in vs),2),p.index))
    out.sort(reverse=True)
    print('P251',lab,'n',len(out),'big>3',sum(1 for o in out if o[0]>3),flush=True)
    for o in out[:30]: print('P251',lab,o,flush=True)
scan(T.data,'base')
dg=bpy.context.evaluated_depsgraph_get(); me=T.evaluated_get(dg).to_mesh()
scan(me,'eval')
os._exit(0)
