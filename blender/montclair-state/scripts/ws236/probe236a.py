import bpy
F='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(F) as (a,b):
    names=[n for n in a.objects if n.startswith(('M3b_','PK_Feliciano','WS60_terrain','WS68_RHD_ground')) or 'allast' in n]
    b.objects=names
for o in b.objects:
    if o is None: continue
    print('P236A',o.name,o.type,len(o.data.vertices) if o.type=='MESH' else '',[ (m.type,m.name) for m in o.modifiers], tuple(round(x) for x in o.matrix_world.translation),flush=True)
