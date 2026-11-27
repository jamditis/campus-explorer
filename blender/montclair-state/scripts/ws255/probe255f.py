import sys; sys.stdout.reconfigure(line_buffering=True)
import bpy, os, collections
bpy.ops.wm.open_mainfile(filepath='/workspace/nj-scenes/montclair-state/montclair_state_ws255d.blend', load_ui=False)
T=bpy.data.objects['Terrain_LiDAR_DTM_1m']; me=T.data; M=T.matrix_world
def inner(y): return -194.69+0.0615*(y-172.0)
c=collections.Counter()
for p in me.polygons:
    q=M@p.center
    if 191<q.y<212 and inner(q.y)<q.x<inner(q.y)+6: c[me.materials[p.material_index].name]+=1
print('P255F base faces mats',c)
nt=bpy.data.materials['Ground_ortho_grass'].node_tree
for n in ('WS247_lawn_mix','WS247_lawn_attr','WS75_lawn_mix'):
    nd=nt.nodes.get(n); print('P255F',n, nd and [(l.to_node.name,l.to_socket.name) for o in nd.outputs for l in o.links], nd and [(i.name,[l.from_node.name for l in i.links]) for i in nd.inputs if i.links])
print('P255F B', tuple(nt.nodes['WS247_lawn_mix'].inputs['B'].default_value))
# evaluated attr in box
dg=bpy.context.evaluated_depsgraph_get()
os._exit(0)
