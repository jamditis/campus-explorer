import bpy, hashlib
h=hashlib.sha1()
for o in sorted(bpy.data.objects,key=lambda o:o.name):
    h.update((o.name+'|'.join(m.name for m in o.modifiers)+str(tuple(round(c,4) for c in o.matrix_world.translation))).encode())
h.update('|'.join(sorted(g.name for g in bpy.data.node_groups)).encode())
print('MODSIG',len(bpy.data.node_groups),h.hexdigest()[:12])
