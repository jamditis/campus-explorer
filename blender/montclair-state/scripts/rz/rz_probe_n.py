import bpy
for o in bpy.data.objects:
    if o.name.startswith('SC lettering'):
        print('LET',o.name,o.parent.name if o.parent else None,o.parent_type, [list(r) for r in o.matrix_world], [c.type for c in o.constraints], [md.type for md in o.modifiers], o.users_collection[0].name)
