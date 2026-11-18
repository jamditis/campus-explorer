import bpy
p='/workspace/nj-scenes/montclair-state/montclair_state.blend'
with bpy.data.libraries.load(p) as (a,b):
    b.objects=[n for n in a.objects if n.startswith('WS172_frontyards')]
for o in b.objects:
    print('OBJ',o.name,[m.name for m in o.data.materials],[x.name for x in o.modifiers])
    for m in o.data.materials:
        for n in m.node_tree.nodes:
            if n.bl_idname=='ShaderNodeMath' and n.operation in ('SINE','COSINE'): print(' SIN',m.name,n.name)
            if n.bl_idname=='ShaderNodeTexWave': print(' WAVE',m.name,n.name,n.inputs['Scale'].default_value)
        for l in m.node_tree.links:
            if l.to_node.bl_idname=='ShaderNodeMath' and l.from_node.bl_idname=='ShaderNodeMath' and l.from_node.operation=='SINE': print(' SINLINK',l.from_node.name,'->',l.to_node.name,[ (i.default_value) for i in l.to_node.inputs if not i.is_linked])
