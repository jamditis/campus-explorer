import bpy

F = "/workspace/nj-scenes/montclair-state/montclair_state.blend"
with bpy.data.libraries.load(F) as (a, b):
    b.meshes = ["Tree_RedMaple_LOD1_v2Oct", "Tree_WhitePine_LOD1"]
for me in b.meshes:
    for m in me.materials:
        print("MAT", me.name, m.name)
        for n in m.node_tree.nodes:
            print(
                "   ",
                n.type,
                n.name,
                [(i.name, i.links[0].from_node.name) for i in n.inputs if i.is_linked][:5],
                getattr(n, "image", None) and n.image.filepath,
            )
